# Kivy UI Design Skill

## Purpose
Apply consistent visual design across all Kivy screens for the book notes app.
Always reference this skill before creating or editing any .kv file or screen class.

## Color Palette
Import colors from skills/kivy-ui-design/colors.py — never use raw hex values.

Primary background:   #F5F0E8  (warm off-white)
Secondary background: #EDE8DF  (card surfaces)
Primary text:         #2C2C2C  (near-black)
Secondary text:       #6B6560  (muted, for metadata)
Accent:               #8B4513  (warm brown, for CTAs)
Accent light:         #D4956A  (hover states, highlights)
Dividers:             #D9D3C7

## Typography
Body text:     14sp
Captions:      11sp  (page numbers, timestamps)
Entry title:   16sp, bold
Screen title:  20sp, bold
Font:          Use Roboto (ships with Kivy) for body,
               RobotoSlab for titles if available

## Spacing
Base unit: 8dp
Padding (standard):   16dp
Padding (compact):    8dp
Card border radius:   6dp
Button height:        44dp  (minimum touch target)

## Component Patterns

### Buttons
- Primary: accent background, white text, 6dp radius
- Secondary: transparent background, accent-colored text, accent border
- Destructive: #C0392B background, white text

### Cards (book covers, entry items)
- Secondary background color
- 6dp border radius
- 8dp internal padding
- Subtle shadow via canvas instructions

### Input Fields
- White background
- 1dp accent-colored border on focus
- 4dp border radius
- 16dp horizontal padding

### List Items (entries)
- Full width, 1dp divider between items
- 16dp horizontal padding, 12dp vertical
- Entry type shown as a small colored pill label
  - Quote:   #D4956A
  - Note:    #6B8E9F
  - Fact:    #7A9E7E
  - Person:  #9B8BB4

## Screen Layout Rules
- Always include a top bar with screen title and back navigation
- Action buttons (add entry etc) as FloatLayout FAB bottom-right
- Keep vertical rhythm consistent using the 8dp base unit
- On desktop, max content width 800dp centered

## Kivy-Specific Notes
- Define all reusable styles in theme.kv using class rules
- Use dp() and sp() functions — never raw pixel values
- Background colors via canvas.before Rectangle, not background_color alone