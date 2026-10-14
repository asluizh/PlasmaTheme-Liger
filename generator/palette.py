"""
Liger palette — Aqua, Snow Leopard (10.6) .. Mavericks (10.9).

All the "lickable" gel recipes live here so the whole theme can be retuned
from one place.  Gradient stops are (offset, colour, opacity).

Two variants share every generator (build.py runs one process per variant):
  LIGER_VARIANT=light  Liger      brushed Aqua greys
  LIGER_VARIANT=dark   DarkLiger  smoked glass after QuickTime X, Aero-like sharp
                                  gloss, modern dark-theme contrast (light text,
                                  no large bright areas); same proportions and
                                  the same Aqua-blue accent
The light values are defined first; the dark block at the end overrides them.
Generators use D(light, dark) for one-off literals.
"""
import os

VARIANT = os.environ.get('LIGER_VARIANT', 'light')
DARK = VARIANT == 'dark'


def D(light, dark):
    """Pick the value for the current variant."""
    return dark if DARK else light


THEME_NAME = 'Liger'
THEME_ID = 'Liger'
LAF_ID = 'org.kde.liger.desktop'
DESCRIPTION = 'Aqua, the lickable way: Snow Leopard to Mavericks'
AUTHOR = 'Liger contributors'
VERSION = '1.1.0'

# --------------------------------------------------------------------------
# base colours
# --------------------------------------------------------------------------
WINDOW_BG = '#ececec'        # Mavericks window grey (SL was #e8e8e8)
TEXT = '#1d1d1d'
TEXT_DIM = '#7f7f7f'
VIEW_BG = '#ffffff'
ALT_ROW = '#edf3fe'          # Aqua alternating rows
SELECTION = '#3875d7'        # Aqua list selection blue
SELECTION_INACTIVE = '#cacaca'
LINK = '#1a5fd0'
VISITED = '#7a3fb5'
FOCUS_RING = '#6f9fe3'
HOVER = '#8db5ea'
TOOLTIP_BG = '#ffffc6'       # classic Snow Leopard pale-yellow tooltip
TOOLTIP_BORDER = '#9f9f86'
NEGATIVE = '#c8352d'
NEUTRAL = '#d99400'
POSITIVE = '#2f9a3b'

# --------------------------------------------------------------------------
# gels
# --------------------------------------------------------------------------
# Classic Aqua "lickable" blue gel (default push button, scroller thumb,
# progress bar).  Upper half: pale with a hard specular edge at ~50%;
# lower half: deeper blue blooming into a cyan glow at the bottom.
BLUE_GEL = [
    (0.00, '#d3e8fd', 1), (0.12, '#acd2fa', 1), (0.48, '#7db5f2', 1),
    (0.50, '#4f97e9', 1), (0.80, '#77c1f7', 1), (1.00, '#b8e9ff', 1),
]
BLUE_RIM = '#2e5ea6'         # rim / border of blue gel
BLUE_RIM_BOTTOM = '#3c79c9'

BLUE_GEL_PRESSED = [
    (0.00, '#a6c9ef', 1), (0.12, '#80b0e8', 1), (0.48, '#5592dc', 1),
    (0.50, '#2a6bc9', 1), (0.80, '#4e9ae6', 1), (1.00, '#8fd2fa', 1),
]
BLUE_RIM_PRESSED = '#1f4a8a'

# White / "graphite" gel for normal push buttons.
WHITE_GEL = [
    (0.00, '#ffffff', 1), (0.48, '#f4f4f4', 1), (0.50, '#e6e6e6', 1),
    (0.85, '#f0f0f0', 1), (1.00, '#fbfbfb', 1),
]
WHITE_RIM = '#8a8a8a'
WHITE_RIM_TOP = '#a3a3a3'
WHITE_RIM_BOTTOM = '#6e6e6e'

# Graphite gel (inactive traffic lights, graphite variant)
GRAPHITE_GEL = [
    (0.00, '#eeeeee', 1), (0.50, '#c9c9c9', 1), (1.00, '#e2e2e2', 1),
]

# Selection gel (source-list / menu highlight, Snow Leopard)
SELECT_GEL = [(0.0, '#6b9ce8', 1), (1.0, '#2d68d8', 1)]
SELECT_TOPLINE = '#4a80d8'
SELECT_BOTTOMLINE = '#1f55c0'

# Specular gloss overlay for any gel (white, top half)
GLOSS = [(0.0, '#ffffff', 0.85), (1.0, '#ffffff', 0.15)]

# --------------------------------------------------------------------------
# chrome
# --------------------------------------------------------------------------
# Menu bar (top panel): Snow Leopard light, slightly translucent
MENUBAR = [(0.0, '#f3f3f3', 1), (0.55, '#e3e3e3', 1), (1.0, '#cbcbcb', 1)]
MENUBAR_LINE = '#8a8a8a'

# Dock (bottom panel, 2D "frosted" Mavericks side-dock look)
DOCK_STYLE = 'frost'   # 'frost' (light, Mavericks) | 'smoke' (dark, Leopard/SL 2D)
DOCK_FROST = [(0.0, '#f1f1f1', 0.86), (0.5, '#dfe3e9', 0.80), (1.0, '#cdd4de', 0.86)]
DOCK_FROST_BORDER = ('#ffffff', 0.75)
DOCK_FROST_OUTLINE = ('#000000', 0.22)
DOCK_SMOKE = [(0.0, '#4a4a4a', 0.62), (1.0, '#262626', 0.70)]
DOCK_SMOKE_BORDER = ('#ffffff', 0.35)
DOCK_SMOKE_OUTLINE = ('#000000', 0.45)

# Popups / dialogs (menus, plasmoid popups, KRunner)
POPUP = [(0.0, '#ffffff', 1), (1.0, '#f6f6f6', 1)]
POPUP_BORDER = ('#000000', 0.28)

# Window title bar (Aurorae)
# Snow Leopard: #cdcdcd at the top fading to ~#a5a5a5, closed by the classic
# dark #515151 line where the title bar meets the window content.
TITLE_ACTIVE = [(0.0, '#d0d0d0', 1), (0.1, '#cbcbcb', 1), (1.0, '#a3a3a3', 1)]
TITLE_ACTIVE_HILITE = ('#ffffff', 0.75)
TITLE_ACTIVE_SEPARATOR = '#515151'
TITLE_INACTIVE = [(0.0, '#ececec', 1), (1.0, '#d3d3d3', 1)]
TITLE_INACTIVE_SEPARATOR = '#9a9a9a'
WINDOW_OUTLINE = ('#000000', 0.40)
WINDOW_OUTLINE_INACTIVE = ('#000000', 0.25)
TITLE_TEXT = '#232323'
TITLE_TEXT_INACTIVE = '#8a8a8a'

# Traffic lights: (rim, dark edge, mid, bright bottom glow, glyph)
TRAFFIC = {
    'close':    ('#8e231b', '#c8352b', '#e85c4f', '#ffb7a6', '#5a0d06'),
    'minimize': ('#9b6b0c', '#d39a12', '#f5c63a', '#fff0a8', '#6a4300'),
    'maximize': ('#2f6c16', '#4f9a25', '#7fc94b', '#d8ffb0', '#174a05'),
    # extra buttons (no Apple original): keep above = blue, on all desktops = purple
    'keepabove':   ('#1d4f9a', '#2f6fd0', '#5aa0f0', '#c4e6ff', '#0a2a5c'),
    'alldesktops': ('#5a2a8a', '#7d45b8', '#a878e0', '#ecd8ff', '#2e0f4e'),
    'graphite': ('#8a8a8a', '#a9a9a9', '#cfcfcf', '#f3f3f3', '#4a4a4a'),
}

# Inner light edge drawn just inside a glass rim (dark variant only)
GLASS_EDGE = None

# ==========================================================================
# DarkLiger: QuickTime X smoked glass
# ==========================================================================
if DARK:
    THEME_NAME = 'DarkLiger'
    THEME_ID = 'DarkLiger'
    LAF_ID = 'org.kde.darkliger.desktop'
    DESCRIPTION = 'Aqua after dark: QuickTime X smoked glass with sharp gloss'

    WINDOW_BG = '#26282b'
    TEXT = '#e6e7e9'
    TEXT_DIM = '#8e9095'
    VIEW_BG = '#1c1d20'
    ALT_ROW = '#222428'
    SELECTION = '#2f6bd0'        # the same Aqua blue, a touch deeper for white text
    SELECTION_INACTIVE = '#46494e'
    LINK = '#6aa8ff'
    VISITED = '#b892f2'
    FOCUS_RING = '#4a8cf0'
    HOVER = '#3a6cc0'
    TOOLTIP_BG = '#2b2d31'
    TOOLTIP_BORDER = '#000000'
    NEGATIVE = '#ff6a5e'
    NEUTRAL = '#f2b13a'
    POSITIVE = '#5ccb6c'

    # gels become glass: the gradient breaks hard at 50% (the reflection line)
    # instead of melting, and the bottom glow is only a faint refraction
    BLUE_GEL = [
        (0.00, '#6d9fe6', 1), (0.47, '#3f78cf', 1),
        (0.50, '#1d4fa6', 1), (0.82, '#2462bb', 1), (1.00, '#3f86dc', 1),
    ]
    BLUE_RIM = '#0a1d42'
    BLUE_RIM_BOTTOM = '#10295a'
    BLUE_GEL_PRESSED = [
        (0.00, '#4f7fc8', 1), (0.47, '#2d5fb0', 1),
        (0.50, '#143c84', 1), (0.82, '#1a4b98', 1), (1.00, '#2d6bbd', 1),
    ]
    BLUE_RIM_PRESSED = '#06142f'

    # "smoke" glass for normal buttons (replaces the white gel)
    WHITE_GEL = [
        (0.00, '#4b4e54', 1), (0.47, '#3a3d42', 1), (0.50, '#2a2c30', 1),
        (0.85, '#2c2f33', 1), (1.00, '#35383d', 1),
    ]
    WHITE_RIM = '#0c0d0f'
    WHITE_RIM_TOP = '#141518'
    WHITE_RIM_BOTTOM = '#060607'
    GRAPHITE_GEL = [
        (0.00, '#5b5e63', 1), (0.50, '#3d3f43', 1), (1.00, '#4a4c51', 1),
    ]
    SELECT_GEL = [(0.0, '#3c77d6', 1), (0.5, '#2c63c4', 1), (0.5, '#2257b8', 1), (1.0, '#2a62c4', 1)]
    SELECT_TOPLINE = '#6b9be6'
    SELECT_BOTTOMLINE = '#123a80'

    # sharp, faint specular band (glass, not candy)
    GLOSS = [(0.0, '#ffffff', 0.34), (1.0, '#ffffff', 0.07)]
    GLASS_EDGE = ('#ffffff', 0.10)

    MENUBAR = [(0.0, '#3b3e43', 1), (0.48, '#2c2e32', 1), (0.5, '#202124', 1), (1.0, '#1a1b1e', 1)]
    MENUBAR_LINE = '#000000'

    DOCK_STYLE = 'smoke'
    DOCK_SMOKE = [(0.0, '#3c3f45', 0.80), (0.5, '#25272b', 0.80), (0.5, '#16171a', 0.84), (1.0, '#1c1e21', 0.86)]
    DOCK_SMOKE_BORDER = ('#ffffff', 0.16)
    DOCK_SMOKE_OUTLINE = ('#000000', 0.80)

    POPUP = [(0.0, '#2d2f33', 1), (1.0, '#232528', 1)]
    POPUP_BORDER = ('#000000', 0.75)

    # title bar: smoked glass, reflection edge at ~45%, a hairline of light on top
    TITLE_ACTIVE = [(0.0, '#4a4d53', 1), (0.45, '#36383d', 1), (0.45, '#28292d', 1), (1.0, '#1f2023', 1)]
    TITLE_ACTIVE_HILITE = ('#ffffff', 0.26)
    TITLE_ACTIVE_SEPARATOR = '#050506'
    TITLE_INACTIVE = [(0.0, '#303236', 1), (0.45, '#2a2c30', 1), (0.45, '#26282b', 1), (1.0, '#232528', 1)]
    TITLE_INACTIVE_SEPARATOR = '#111214'
    WINDOW_OUTLINE = ('#000000', 0.90)
    WINDOW_OUTLINE_INACTIVE = ('#000000', 0.70)
    TITLE_TEXT = '#e6e7e9'
    TITLE_TEXT_INACTIVE = '#7c7f84'

    TRAFFIC = dict(TRAFFIC)
    # inactive gems: dark graphite glass instead of light grey
    TRAFFIC['graphite'] = ('#0c0d0e', '#2a2c30', '#45484d', '#6b6e74', '#c8cacd')
