from __future__ import annotations

import tempfile

from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget


class CropOverlay(Widget):
    """Transparent overlay that draws the darkened scrim and crop-selection rectangle.

    Canvas is rebuilt entirely in Python on each call to redraw() rather than
    using a KV canvas block, so the selection rectangle updates on every drag
    event without KV observer overhead.
    """

    def redraw(self, sel: tuple[float, float, float, float] | None = None) -> None:
        """Redraw the scrim overlay. sel = (x1, y1, x2, y2) already normalised."""
        self.canvas.clear()
        with self.canvas:
            # Full dark scrim
            Color(0, 0, 0, 0.55)
            Rectangle(size=self.size, pos=self.pos)

            if sel:
                x1, y1, x2, y2 = sel
                sw, sh = x2 - x1, y2 - y1

                # Semi-transparent reveal over selected region
                Color(0.976, 0.965, 0.941, 0.15)
                Rectangle(pos=(x1, y1), size=(sw, sh))

                # Selection border (Scholar Sage accent)
                Color(0.239, 0.420, 0.341, 1)
                Line(rectangle=(x1, y1, sw, sh), width=2)

                # Corner handles — white fill with accent border
                hr = dp(11)
                for hx, hy in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
                    Color(1, 1, 1, 1)
                    Ellipse(pos=(hx - hr, hy - hr), size=(hr * 2, hr * 2))
                    Color(0.239, 0.420, 0.341, 1)
                    Line(circle=(hx, hy, hr), width=1.5)


class CropPopup(Popup):
    """Full-screen popup that lets the user draw a crop rectangle on a captured image.

    Usage:
        popup = CropPopup(image_path=normalized_path)
        popup.on_crop_done = self._handle_crop
        popup.open()

    on_crop_done(cropped_path: str | None) is called with the temp-file path of the
    cropped JPEG on confirm, or None on cancel.
    """

    image_path = StringProperty("")
    has_selection = BooleanProperty(False)

    # Set by caller before open()
    on_crop_done: callable = None  # type: ignore[assignment]

    # Non-Kivy instance state
    _img_w: int = 0
    _img_h: int = 0
    _img_ready: bool = False
    _drag_mode: str | None = None  # "new" | "tl" | "tr" | "bl" | "br"
    _anchor: tuple[float, float] = (0.0, 0.0)
    _sel: tuple[float, float, float, float] | None = None  # display-space floats

    _HANDLE_HIT_DP: int = 22

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def on_open(self) -> None:
        from PIL import Image as PILImage

        with PILImage.open(self.image_path) as img:
            self._img_w, self._img_h = img.size

        # Wait for Kivy to finish laying out the Image widget before accepting touches
        self.ids.crop_image.bind(norm_image_size=self._on_layout_ready)

    def _on_layout_ready(self, widget, value) -> None:
        w, h = value
        if w > 0 and h > 0:
            self._img_ready = True

    # ── Coordinate helpers ─────────────────────────────────────────────────────

    def _image_display_rect(self) -> tuple[float, float, float, float]:
        """Return (ix, iy, iw, ih) — image content rect in widget-local coords."""
        img = self.ids.crop_image
        disp_w, disp_h = img.norm_image_size
        ix = img.x + (img.width - disp_w) / 2
        iy = img.y + (img.height - disp_h) / 2
        return ix, iy, disp_w, disp_h

    def _to_local(self, touch) -> tuple[float, float]:
        """Convert window-space touch coords to crop_image widget-local coords."""
        return self.ids.crop_image.to_local(touch.x, touch.y)

    def _to_image_px(self, fx: float, fy: float) -> tuple[int, int]:
        """Map display-space (widget-local) float coords → PIL image pixels."""
        ix, iy, iw, ih = self._image_display_rect()
        rel_x = (fx - ix) / iw
        rel_y = (fy - iy) / ih  # 0.0 = bottom, 1.0 = top (Kivy Y-up)
        px = int(rel_x * self._img_w)
        py = int((1.0 - rel_y) * self._img_h)  # flip Y: PIL is top-down
        return (
            max(0, min(px, self._img_w)),
            max(0, min(py, self._img_h)),
        )

    def _normalised_sel(self) -> tuple[float, float, float, float] | None:
        """Return selection as (min_x, min_y, max_x, max_y), or None."""
        if self._sel is None:
            return None
        x1, y1, x2, y2 = self._sel
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

    def _hit_corner(self, lx: float, ly: float) -> str | None:
        """Return corner name if (lx, ly) is within hit radius of a selection corner."""
        sel = self._normalised_sel()
        if sel is None:
            return None
        x1, y1, x2, y2 = sel
        hr = dp(self._HANDLE_HIT_DP)
        corners = {
            "bl": (x1, y1),
            "br": (x2, y1),
            "tl": (x1, y2),
            "tr": (x2, y2),
        }
        for name, (cx, cy) in corners.items():
            if abs(lx - cx) <= hr and abs(ly - cy) <= hr:
                return name
        return None

    # ── Touch events ──────────────────────────────────────────────────────────

    def on_touch_down(self, touch) -> bool:
        if not self._img_ready:
            return super().on_touch_down(touch)

        lx, ly = self._to_local(touch)
        ix, iy, iw, ih = self._image_display_rect()

        # Only handle touches within the image display area
        if not (ix <= lx <= ix + iw and iy <= ly <= iy + ih):
            return super().on_touch_down(touch)

        if self.has_selection:
            corner = self._hit_corner(lx, ly)
            if corner:
                self._drag_mode = corner
                sel = self._normalised_sel()
                x1, y1, x2, y2 = sel
                # Anchor is the opposite corner
                opposite = {
                    "tl": (x2, y1),
                    "tr": (x1, y1),
                    "bl": (x2, y2),
                    "br": (x1, y2),
                }
                self._anchor = opposite[corner]
            else:
                # Touch outside handles — start a new selection
                self._drag_mode = "new"
                self._anchor = (lx, ly)
        else:
            self._drag_mode = "new"
            self._anchor = (lx, ly)

        touch.grab(self)
        return True

    def on_touch_move(self, touch) -> bool:
        if touch.grab_current is not self:
            return False

        lx, ly = self._to_local(touch)
        ax, ay = self._anchor

        if self._drag_mode == "new":
            self._sel = (ax, ay, lx, ly)
        elif self._drag_mode in ("tl", "tr", "bl", "br"):
            self._sel = (ax, ay, lx, ly)

        self.ids.overlay.redraw(self._normalised_sel())
        return True

    def on_touch_up(self, touch) -> bool:
        if touch.grab_current is not self:
            return False

        touch.ungrab(self)
        self._drag_mode = None
        sel = self._normalised_sel()
        # Discard selections that are too small to be meaningful
        if sel and (sel[2] - sel[0]) > dp(10) and (sel[3] - sel[1]) > dp(10):
            self.has_selection = True
        else:
            self._sel = None
            self.has_selection = False
            self.ids.overlay.redraw(None)
        return True

    # ── Actions ───────────────────────────────────────────────────────────────

    def _confirm_crop(self) -> None:
        from services.image_crop import apply_crop

        sel = self._normalised_sel()
        if sel is None:
            return

        x1, y1, x2, y2 = sel
        # y1 = bottom edge (Kivy Y-up), y2 = top edge
        # PIL: upper = row nearest top-of-image = from display y2 (the higher display coord)
        left, upper = self._to_image_px(x1, y2)
        right, lower = self._to_image_px(x2, y1)

        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.close()

        apply_crop(self.image_path, (left, upper, right, lower), tmp.name)
        self.dismiss()
        if self.on_crop_done:
            self.on_crop_done(tmp.name)

    def _cancel(self) -> None:
        self.dismiss()
        if self.on_crop_done:
            self.on_crop_done(None)
