# Kivy RGBA tuples (0.0–1.0 range).
# Source of truth for all color usage across screens and canvas instructions.
# In .kv files use the raw tuples directly; in Python import from here.

BACKGROUND_PRIMARY = (0.96, 0.94, 0.91, 1)  # #F5F0E8 — screen background
BACKGROUND_SECONDARY = (0.93, 0.91, 0.87, 1)  # #EDE8DF — cards, input bg
TEXT_PRIMARY = (0.17, 0.17, 0.17, 1)  # #2C2C2C
TEXT_SECONDARY = (0.42, 0.40, 0.38, 1)  # #6B6560 — metadata, captions
ACCENT = (0.55, 0.27, 0.07, 1)  # #8B4513 — header, CTAs
ACCENT_LIGHT = (0.83, 0.58, 0.42, 1)  # #D4956A — hover, highlights
ACCENT_DARK = (0.45, 0.20, 0.05, 1)  # pressed state
DIVIDER = (0.85, 0.83, 0.78, 1)  # #D9D3C7

# Entry type pill colors
TYPE_QUOTE = (0.83, 0.58, 0.42, 1)
TYPE_NOTE = (0.42, 0.56, 0.62, 1)
TYPE_FACT = (0.48, 0.62, 0.49, 1)
TYPE_PERSON = (0.61, 0.55, 0.71, 1)
