import logging
from typing import Callable

logger = logging.getLogger(__name__)


def get_image(callback: Callable[[str | None], None]) -> None:
    from kivy.utils import platform

    if platform == "android":
        logger.info("Android camera not yet implemented")
        callback(None)
        return

    from kivy.metrics import dp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.filechooser import FileChooserIconView
    from kivy.uix.popup import Popup

    content = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
    chooser = FileChooserIconView(
        filters=["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"],
        size_hint=(1, 1),
    )

    btn_row = BoxLayout(
        orientation="horizontal",
        size_hint=(1, None),
        height=dp(44),
        spacing=dp(8),
    )

    popup = Popup(title="Select Image", content=content, size_hint=(0.9, 0.85))

    def on_select(*args):
        if chooser.selection:
            popup.dismiss()
            callback(chooser.selection[0])

    def on_cancel(*args):
        popup.dismiss()
        callback(None)

    btn_row.add_widget(Button(text="Select", on_release=on_select))
    btn_row.add_widget(Button(text="Cancel", on_release=on_cancel))

    content.add_widget(chooser)
    content.add_widget(btn_row)

    popup.open()
