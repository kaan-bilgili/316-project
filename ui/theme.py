"""Shared light UI palette and cyberpunk button styling."""

CUSTOMTKINTER_APPEARANCE = "light"

# White base
BG_COLOR = "#f5f6fa"
TEXT_COLOR = "#1a1a2e"
TEXT_MUTED = "#6b7280"
BTN_TEXT_COLOR = "#ffffff"

# Panels & surfaces
GLASS_BG = "#ffffff"
GLASS_BG_INNER = "#f0f1f6"
GLASS_BORDER = "#dfe3ef"
GLASS_BORDER_LIGHT = "#c8cfe0"

GLASS_RADIUS = 24
GLASS_RADIUS_SM = 16
GLASS_RADIUS_PILL = 20

# Treeview (light)
TREE_HEADING_BG = "#e8ebf4"
TREE_HEADING_ACTIVE = "#dce1ef"
TREE_ROW_FG = "#1e1e2e"
TREE_ROW_FG_MUTED = "#5c6370"

CLICK_CURSOR = "hand2"

# Accent & cyberpunk buttons (purple → pink)
ACCENT_COLOR = "#9333EA"
CYBER_PURPLE = "#7C3AED"
CYBER_PINK = "#EC4899"
BUTTON_COLOR = (CYBER_PURPLE, CYBER_PINK)
BUTTON_HOVER = ("#6D28D9", "#DB2777")
CYBER_GLOW = "#DDD6FE"


def mix_hex(color_a, color_b, ratio=0.5):
    a = color_a.lstrip("#")
    b = color_b.lstrip("#")
    rgb_a = tuple(int(a[i : i + 2], 16) for i in (0, 2, 4))
    rgb_b = tuple(int(b[i : i + 2], 16) for i in (0, 2, 4))
    mixed = tuple(int(rgb_a[i] * (1 - ratio) + rgb_b[i] * ratio) for i in range(3))
    return "#{:02x}{:02x}{:02x}".format(*mixed)
