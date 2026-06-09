# Kivy RGBA tuples (0.0–1.0 range).
# Source of truth for all color usage across screens and canvas instructions.
# In .kv files use the raw tuples directly; in Python import from here.

BACKGROUND_PRIMARY = (0.976, 0.965, 0.941, 1)  # #F9F6F0 — Alabaster/Paper
BACKGROUND_SECONDARY = (
    0.937,
    0.925,
    0.902,
    1,
)  # #EFECE6 — Soft Linen (cards, input bg)
TEXT_PRIMARY = (0.133, 0.145, 0.165, 1)  # #22252A — Dark Charcoal
TEXT_SECONDARY = (0.42, 0.40, 0.38, 1)  # #6B6560 — muted, for metadata
ACCENT = (0.239, 0.420, 0.341, 1)  # #3D6B57 — Scholar Sage (header, CTAs)
ACCENT_LIGHT = (0.420, 0.620, 0.525, 1)  # #6B9E86 — lighter sage (hover, highlights)
ACCENT_DARK = (0.176, 0.314, 0.251, 1)  # #2D5040 — pressed state
DIVIDER = (0.87, 0.85, 0.82, 1)  # #DED9D1

# Entry type pill colors (categorical, independent of accent)
TYPE_QUOTE = (0.83, 0.58, 0.42, 1)
TYPE_NOTE = (0.42, 0.56, 0.62, 1)
TYPE_FACT = (0.48, 0.62, 0.49, 1)
TYPE_PERSON = (0.61, 0.55, 0.71, 1)
