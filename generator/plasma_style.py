"""
Builds the Liger / DarkLiger Plasma Style (desktoptheme).

Output: <out>/plasma/desktoptheme/<THEME_ID>/
Each widget function below owns one SVG file; tweak values here or in palette.py.
"""
import json
import os

import palette as P
import gel as G
from palette import D
from svgkit import SVG, RR, RING, Layer, Linear, Radial, rrect_poly, ellipse_poly, vgrad, hgrad, shadow_image, add_shadow, Raster

CS = {'Text': P.TEXT, 'Background': P.WINDOW_BG, 'Highlight': P.SELECTION}

FRAME_NAMES = ['topleft', 'top', 'topright', 'left', 'center', 'right', 'bottomleft', 'bottom', 'bottomright']


def nxt(svg):
    return svg.maxy + 12


def glass_edge(x0, y0, x1, y1, r, k=1.0):
    """DarkLiger: faint light ring inside dark glass so it separates from dark backdrops."""
    if not P.GLASS_EDGE:
        return []
    c, a = P.GLASS_EDGE
    return [RING(x0, y0, x1, y1, r, 1, vgrad(y0, y1, [(0, c, a * 1.4 * k), (0.4, c, a * 0.5 * k), (1, c, a * 0.6 * k)]))]


# ==========================================================================
# dialogs/background  (plasmoid popups, KRunner, notifications ...)
# ==========================================================================

def dialog_svg(alpha=0.97, shadow=True, radius=6):
    svg = SVG(CS)
    W = H = 48
    m = (8, 8, 8, 8)
    body = [
        RR(0, 0, W, H, radius, P.POPUP_BORDER[0], P.POPUP_BORDER[1]),
        Layer(rrect_poly(1, 1, W - 1, H - 1, radius - 1), vgrad(1, H - 1, P.POPUP), alpha),
        # crisp 1px inner top highlight
        Layer(rrect_poly(1, 1, W - 1, 3, (radius - 1, radius - 1, 0, 0)), '#ffffff', D(0.9, 0.16) * alpha,
              hole=rrect_poly(1, 2, W - 1, 4, 0)),
    ] + glass_edge(1, 1, W - 1, H - 1, radius - 1)
    svg.frame('', 0, 0, W, H, m, body,
              hints={'top-margin': 6, 'bottom-margin': 6, 'left-margin': 6, 'right-margin': 6})
    # blur / input mask
    svg.frame('mask-', 0, nxt(svg), W, H, m, [RR(0, 0, W, H, radius, '#000000')])
    if shadow:
        add_shadow(svg, 'shadow-', 0, nxt(svg), pad=(22, 14, 22, 30), radius=radius, blur=26, dy=8, alpha=0.42)
    return svg


# ==========================================================================
# widgets/panel-background
#   north-  : Snow Leopard menu bar
#   (none)/south-/east-/west- : 2D frosted dock
# ==========================================================================

def menubar_layers(W, H, alpha, line=True):
    L = [Layer(rrect_poly(0, 0, W, H, 0), vgrad(0, H, P.MENUBAR), alpha)]
    L.append(Layer(rrect_poly(0, 0, W, 1, 0), '#ffffff', D(0.9, 0.16) * alpha))  # top specular line
    if line:
        L.append(Layer(rrect_poly(0, H - 1, W, H, 0), P.MENUBAR_LINE, min(1, alpha + 0.1)))
    return L


def dock_layers(W, H, r, alpha_mul, style):
    if style == 'smoke':
        fill, border, outline = P.DOCK_SMOKE, P.DOCK_SMOKE_BORDER, P.DOCK_SMOKE_OUTLINE
    else:
        fill, border, outline = P.DOCK_FROST, P.DOCK_FROST_BORDER, P.DOCK_FROST_OUTLINE
    stops = [(o, c, min(1, a * alpha_mul)) for o, c, a in fill]
    L = [
        RING(0, 0, W, H, r, 1, outline[0], outline[1]),
        RR(1, 1, W - 1, H - 1, r - 1, vgrad(1, H - 1, stops)),
        RING(1, 1, W - 1, H - 1, r - 1, 1, border[0], border[1] * min(1, alpha_mul)),
        # glassy upper sheen (DarkLiger: a faint band that stops hard at the reflection line)
        Layer(rrect_poly(2, 2, W - 2, H * D(0.45, 0.5), (r - 2, r - 2, D(2, 0), D(2, 0))),
              vgrad(2, H * D(0.45, 0.5), [(0, '#ffffff', D(0.35, 0.14) * min(1, alpha_mul)),
                                          (1, '#ffffff', D(0.0, 0.03))])),
    ]
    return L


def transposed(layers):
    """Mirror layers across the diagonal (x<->y): a horizontal frame becomes a vertical one
    whose gradients run across its thickness, lit side on the left like the scroller thumb."""
    def pts(poly):
        return [(y, x) for x, y in poly] if poly else poly

    def paint(pt):
        if isinstance(pt, Linear):
            return Linear(pt.y1, pt.x1, pt.y2, pt.x2, pt.stops)
        if isinstance(pt, Radial):
            return Radial(pt.cy, pt.cx, pt.r, pt.stops, pt.fy, pt.fx, pt.sy, pt.sx)
        return pt
    return [Layer(pts(L.shape), paint(L.paint), L.opacity, pts(L.hole), L.cls) for L in layers]


def panel_svg(alpha=0.92, dock_alpha=1.0, shadow=True, opaque=False):
    svg = SVG(CS)
    style = P.DOCK_STYLE
    # ---- dock (default prefix, plus explicit south/east/west) ----
    W = H = 64
    r = 10
    m = (10, 10, 10, 10)
    hints = {'top-margin': 4, 'bottom-margin': 4, 'left-margin': 6, 'right-margin': 6}
    vhints = {'top-margin': 6, 'bottom-margin': 6, 'left-margin': 4, 'right-margin': 4}
    dl = dock_layers(W, H, r, 1.6 if opaque else dock_alpha, style)
    for pre in ['', 'south-', 'east-', 'west-']:
        # vertical docks: the gradient runs across the dock's thickness, not along it
        vertical = pre in ('east-', 'west-')
        svg.frame(pre, 0, nxt(svg), W, H, m, transposed(dl) if vertical else dl, hints=vhints if vertical else hints)
        svg.frame('mask-' + pre, 0, nxt(svg), W, H, m, [RR(0, 0, W, H, r, '#000000')])
    # ---- menu bar (north) ----
    MW, MH = 64, 26
    mm = (1, 1, 1, 2)
    a = 1.0 if opaque else alpha
    svg.frame('north-', 0, nxt(svg), MW, MH, mm, menubar_layers(MW, MH, a),
              hints={'top-margin': 0, 'bottom-margin': 1, 'left-margin': 2, 'right-margin': 2})
    svg.frame('mask-north-', 0, nxt(svg), MW, MH, mm, [RR(0, 0, MW, MH, 0, '#000000')])
    # 'thick' margins drive applet padding inside the panel
    y = nxt(svg)
    for k, v in {'top-margin': 1, 'bottom-margin': 1, 'left-margin': 2, 'right-margin': 2}.items():
        if 'top' in k or 'bottom' in k:
            svg.hint('thick-hint-' + k, 0, y, 1, v)
        else:
            svg.hint('thick-hint-' + k, 0, y, v, 1)
        y += 4
    svg.raw('<rect id="thick-center" x="10" y="%d" width="4" height="4" fill="#000" opacity="0.01" fill-opacity="0.01"/>' % (y))
    if shadow:
        add_shadow(svg, 'shadow-', 0, nxt(svg), pad=(12, 6, 12, 14), radius=r, blur=14, dy=3, alpha=0.38)
    return svg


# ==========================================================================
# widgets/tooltip — Snow Leopard pale-yellow tooltips
# ==========================================================================

def tooltip_svg(alpha=1.0, shadow=True):
    svg = SVG(CS)
    W = H = 32
    r = 4
    m = (5, 5, 5, 5)
    L = [
        RR(0, 0, W, H, r, P.TOOLTIP_BORDER, 0.9),
        Layer(rrect_poly(1, 1, W - 1, H - 1, r - 1), vgrad(1, H - 1, [(0, D('#ffffd8', '#36383d'), 1), (1, P.TOOLTIP_BG, 1)]), alpha),
    ] + glass_edge(1, 1, W - 1, H - 1, r - 1)
    svg.frame('', 0, 0, W, H, m, L, hints={'top-margin': 5, 'bottom-margin': 5, 'left-margin': 7, 'right-margin': 7})
    svg.frame('mask-', 0, nxt(svg), W, H, m, [RR(0, 0, W, H, r, '#000000')])
    if shadow:
        add_shadow(svg, 'shadow-', 0, nxt(svg), pad=(10, 6, 10, 14), radius=r, blur=12, dy=4, alpha=0.35)
    return svg


# ==========================================================================
# widgets/background — desktop widgets
# ==========================================================================

def widget_bg_svg():
    svg = SVG(CS)
    W = H = 48
    r = 8
    m = (10, 10, 10, 10)
    L = [
        RR(0, 0, W, H, r, '#000000', D(0.25, 0.7)),
        Layer(rrect_poly(1, 1, W - 1, H - 1, r - 1), vgrad(1, H - 1, [(0, D('#fdfdfd', '#2d2f33'), 1), (1, D('#eeeeee', '#222427'), 1)]), D(0.92, 0.88)),
        RING(1, 1, W - 1, H - 1, r - 1, 1, '#ffffff', D(0.7, 0.09)),
    ]
    svg.frame('', 0, 0, W, H, m, L, hints={'top-margin': 8, 'bottom-margin': 8, 'left-margin': 8, 'right-margin': 8})
    svg.frame('mask-', 0, nxt(svg), W, H, m, [RR(0, 0, W, H, r, '#000000')])
    add_shadow(svg, 'shadow-', 0, nxt(svg), pad=(16, 10, 16, 22), radius=r, blur=18, dy=6, alpha=0.35)
    return svg


# ==========================================================================
# widgets/button — Aqua push buttons
# ==========================================================================

def button_svg():
    svg = SVG(CS)
    W, H, r = 48, 28, 6
    m = (7, 7, 7, 7)
    hints = {'top-margin': 5, 'bottom-margin': 6, 'left-margin': 9, 'right-margin': 9}
    box = (0.5, 0.5, W - 0.5, H - 1.5)
    svg.frame('normal-', 0, 0, W, H, m, G.white(*box, r), hints=hints)
    svg.frame('pressed-', 0, nxt(svg), W, H, m, G.blue(*box, r, pressed=True), hints=hints)
    # focused push button = Aqua default (blue) button
    svg.frame('focus-background-', 0, nxt(svg), W, H, m, G.blue(*box, r), hints=hints)

    # glow overlays placed *around* the button (margins == glow width)
    g = 4
    GW, GH = W + 2 * g, H + 2 * g
    gb = (g, g, GW - g, GH - g - 1)
    svg.frame('focus-', 0, nxt(svg), GW, GH, (g + 4, g + 4, g + 4, g + 4),
              G.glow_ring(*gb, r, P.FOCUS_RING, width=3.5),
              hints={'top-margin': g, 'bottom-margin': g, 'left-margin': g, 'right-margin': g})
    svg.frame('hover-', 0, nxt(svg), GW, GH, (g + 4, g + 4, g + 4, g + 4),
              G.glow_ring(*gb, r, P.HOVER, width=2.5, opacity=0.6),
              hints={'top-margin': g, 'bottom-margin': g, 'left-margin': g, 'right-margin': g})

    # flat tool buttons (panels, plasmoid headers)
    tb = (0.5, 0.5, W - 0.5, H - 0.5)
    svg.frame('toolbutton-hover-', 0, nxt(svg), W, H, m, [
        RR(*tb, r, '#000000', D(0.18, 0.55)),
        Layer(rrect_poly(tb[0] + 1, tb[1] + 1, tb[2] - 1, tb[3] - 1, r - 1),
              vgrad(1, H - 1, D([(0, '#ffffff', 0.75), (0.5, '#f4f4f4', 0.55), (0.5, '#e8e8e8', 0.5), (1, '#ffffff', 0.6)],
                                [(0, '#ffffff', 0.20), (0.5, '#ffffff', 0.11), (0.5, '#ffffff', 0.05), (1, '#ffffff', 0.08)]))),
    ], hints=hints)
    svg.frame('toolbutton-pressed-', 0, nxt(svg), W, H, m, [
        RR(*tb, r, '#000000', D(0.32, 0.7)),
        Layer(rrect_poly(tb[0] + 1, tb[1] + 1, tb[2] - 1, tb[3] - 1, r - 1),
              vgrad(1, H - 1, D([(0, '#9a9a9a', 0.55), (0.3, '#b9b9b9', 0.45), (1, '#d4d4d4', 0.4)],
                                [(0, '#000000', 0.45), (0.3, '#000000', 0.30), (1, '#ffffff', 0.06)]))),
    ], hints=hints)
    svg.frame('toolbutton-focus-', 0, nxt(svg), GW, GH, (g + 4, g + 4, g + 4, g + 4),
              G.glow_ring(g, g, GW - g, GH - g, r, P.FOCUS_RING, width=3),
              hints={'top-margin': g, 'bottom-margin': g, 'left-margin': g, 'right-margin': g})
    return svg


# ==========================================================================
# widgets/tasks — dock running indicators
# ==========================================================================

def _indicator(W, H, color_core, color_glow, y_from_bottom=2):
    """Glowing capsule 'running light' along the bottom edge (cut into corners/bottom)."""
    cy = H - y_from_bottom - 1.5
    cx0, cx1 = 18, W - 18
    return [
        RR(cx0 - 3, cy - 3, cx1 + 3, cy + 3, 3, color_glow, 0.35),
        RR(cx0 - 1.5, cy - 1.5, cx1 + 1.5, cy + 1.5, 1.5, color_glow, 0.6),
        RR(cx0, cy - 1, cx1, cy + 1, 1, color_core, 1.0),
    ]


def tasks_svg():
    svg = SVG(CS)
    W, H = 56, 48
    m = (20, 6, 20, 8)
    hints = {'top-margin': 2, 'bottom-margin': 4, 'left-margin': 2, 'right-margin': 2}
    run = _indicator(W, H, '#ffffff', '#6fb4ff')
    act = _indicator(W, H, '#ffffff', '#3d8cff')
    hover_glow = [RR(4, 1, W - 4, H - 1, 8, Radial(W / 2, H * 0.55, W * 0.55,
                                                     [(0, '#ffffff', D(0.55, 0.20)), (1, '#ffffff', D(0.08, 0.03))], sy=0.8))]
    att = _indicator(W, H, '#fff6d0', '#ff9a1f')
    progress = [RR(3, H - 9, W - 3, H - 2, 3.5, Linear(0, H - 9, 0, H - 2, P.BLUE_GEL), 0.95)]
    for pre in ['', 'south-', 'north-']:
        svg.frame(pre + 'normal-', 0, nxt(svg), W, H, m, run, hints=hints)
        svg.frame(pre + 'minimized-', 0, nxt(svg), W, H, m, run, hints=hints)
        svg.frame(pre + 'focus-', 0, nxt(svg), W, H, m, act, hints=hints)
        svg.frame(pre + 'hover-', 0, nxt(svg), W, H, m, hover_glow, hints=hints)
        svg.frame(pre + 'attention-', 0, nxt(svg), W, H, m, att, hints=hints)
        svg.frame(pre + 'progress-', 0, nxt(svg), W, H, m, progress, hints=hints)
    # vertical docks: indicator on the screen-side edge
    for pre, side in (('west-', 'left'), ('east-', 'right')):
        WW, HH = 48, 56
        mm = (8, 20, 8, 20) if side == 'left' else (8, 20, 8, 20)
        x = 2.5 if side == 'left' else WW - 2.5 - 3
        ind = [RR(x - 2, 16, x + 5, HH - 16, 3, '#6fb4ff', 0.4),
               RR(x, 18, x + 3, HH - 18, 1.5, '#ffffff', 1.0)]
        for st in ('normal-', 'minimized-', 'focus-'):
            svg.frame(pre + st, 0, nxt(svg), WW, HH, mm, ind, hints=hints)
        svg.frame(pre + 'hover-', 0, nxt(svg), WW, HH, mm, [RR(1, 4, WW - 1, HH - 4, 8, '#ffffff', D(0.3, 0.12))], hints=hints)
        svg.frame(pre + 'attention-', 0, nxt(svg), WW, HH, mm, [RR(x, 18, x + 3, HH - 18, 1.5, '#ff9a1f', 1.0)], hints=hints)
        svg.frame(pre + 'progress-', 0, nxt(svg), WW, HH, mm, [RR(2, HH - 9, WW - 2, HH - 2, 3.5, Linear(0, HH - 9, 0, HH - 2, P.BLUE_GEL))], hints=hints)
    return svg


# ==========================================================================
# widgets/viewitem & listitem — Aqua selection
# ==========================================================================

def selection_layers(W, H, r, alpha=1.0):
    return [
        RR(0, 0, W, H, r, vgrad(0, H, P.SELECT_GEL), alpha),
        Layer(rrect_poly(0, 0, W, 1.2, (r, r, 0, 0)), P.SELECT_TOPLINE, alpha),
        Layer(rrect_poly(0.5, 1, W - 0.5, H * 0.5, (r, r, 0, 0)),
              vgrad(1, H * 0.5, [(0, '#ffffff', 0.28), (1, '#ffffff', 0.05)]), alpha),
    ]


def viewitem_svg():
    svg = SVG(CS)
    W, H, r = 40, 28, 4
    m = (5, 5, 5, 5)
    hints = {'top-margin': 4, 'bottom-margin': 4, 'left-margin': 6, 'right-margin': 6}
    svg.frame('selected-', 0, 0, W, H, m, selection_layers(W, H, r), hints=hints)
    svg.frame('selected+hover-', 0, nxt(svg), W, H, m, selection_layers(W, H, r) + [RR(0, 0, W, H, r, '#ffffff', 0.08)], hints=hints)
    svg.frame('hover-', 0, nxt(svg), W, H, m, [
        RR(0, 0, W, H, r, P.SELECTION, 0.16),
        RING(0, 0, W, H, r, 1, P.SELECTION, 0.30),
    ], hints=hints)
    svg.frame('normal-', 0, nxt(svg), W, H, m, [RR(0, 0, W, H, r, '#ffffff', 0.0)], hints=hints)
    return svg


def listitem_svg():
    svg = SVG(CS)
    W, H, r = 40, 28, 0
    m = (2, 2, 2, 2)
    hints = {'top-margin': 4, 'bottom-margin': 4, 'left-margin': 6, 'right-margin': 6}
    svg.frame('normal-', 0, 0, W, H, m, [RR(0, 0, W, H, 0, '#ffffff', 0.0)], hints=hints)
    svg.frame('pressed-', 0, nxt(svg), W, H, m, selection_layers(W, H, 0), hints=hints)
    svg.frame('hover-', 0, nxt(svg), W, H, m, [RR(0, 0, W, H, 0, P.SELECTION, 0.16)], hints=hints)
    svg.frame('section-', 0, nxt(svg), W, H, m, [
        RR(0, 0, W, H, 0, vgrad(0, H, [(0, D('#e9edf2', '#303338'), 1), (1, D('#d7dde6', '#26282c'), 1)])),
        Layer(rrect_poly(0, H - 1, W, H, 0), D('#b3bac5', '#0b0c0d')),
    ], hints=hints)
    svg.hint('separator', 0, nxt(svg), 20, 1)
    return svg


# ==========================================================================
# widgets/lineedit — inset Aqua text field with blue focus glow
# ==========================================================================

def lineedit_svg():
    svg = SVG(CS)
    W, H, r = 40, 26, 3
    m = (5, 5, 5, 5)
    base = [
        RR(0, 0, W, H, r, vgrad(0, H, [(0, D('#8c8c8c', '#050506'), 1), (0.2, D('#b0b0b0', '#0c0d0e'), 1), (1, D('#c9c9c9', '#3b3d42'), 1)])),
        RR(1, 1, W - 1, H - 1, r - 1, D('#ffffff', '#17181b')),
        # inner top shadow
        Layer(rrect_poly(1, 1, W - 1, 4, (r - 1, r - 1, 0, 0)), vgrad(1, 4, [(0, '#000000', D(0.16, 0.5)), (1, '#000000', 0)])),
    ]
    svg.frame('base-', 0, 0, W, H, m, base, hints={'top-margin': 4, 'bottom-margin': 4, 'left-margin': 6, 'right-margin': 6})
    g = 4
    GW, GH = W + 2 * g, H + 2 * g
    gm = (g + 4, g + 4, g + 4, g + 4)
    gh = {'top-margin': g, 'bottom-margin': g, 'left-margin': g, 'right-margin': g}
    svg.frame('focus-', 0, nxt(svg), GW, GH, gm, G.glow_ring(g, g, GW - g, GH - g, r, P.FOCUS_RING, width=3.5), hints=gh)
    svg.frame('hover-', 0, nxt(svg), GW, GH, gm, G.glow_ring(g, g, GW - g, GH - g, r, P.HOVER, width=2, opacity=0.45), hints=gh)
    svg.hint('hint-focus-over-base', 0, nxt(svg), 4, 4)
    return svg


# ==========================================================================
# widgets/scrollbar — white track + blue gel thumb
# ==========================================================================

def scrollbar_svg():
    svg = SVG(CS)
    S = 14            # scrollbar thickness
    L = 40
    r = S / 2 - 0.5
    m = (6, 7, 6, 7)
    rim = [(0, D('#b9b9b9', '#060607'), 1), (1, D('#d6d6d6', '#2e3034'), 1)]
    well = [(0, D('#d9d9d9', '#121315'), 1), (0.35, D('#f1f1f1', '#1a1b1e'), 1), (1, D('#fbfbfb', '#212326'), 1)]
    track_v = [
        RR(0, 0, S, L, r, hgrad(0, S, rim)),
        RR(1, 1, S - 1, L - 1, r - 1, hgrad(1, S - 1, well)),
    ]
    track_h = [
        RR(0, 0, L, S, r, vgrad(0, S, rim)),
        RR(1, 1, L - 1, S - 1, r - 1, vgrad(1, S - 1, well)),
    ]
    svg.frame('background-vertical-', 0, 0, S, L, m, track_v)
    svg.frame('background-horizontal-', 0, nxt(svg), L, S, (m[1], m[0], m[3], m[2]), track_h)
    # thumb (one prefix for both orientations: designed for the common vertical case)
    thumb = G.blue(1, 1, S - 1, L - 1, r - 1, axis='h', drop=0)
    thumb_hover = G.blue(1, 1, S - 1, L - 1, r - 1, axis='h', drop=0, pressed=True)
    svg.frame('slider-', 0, nxt(svg), S, L, m, thumb)
    svg.frame('mouseover-slider-', 0, nxt(svg), S, L, m, thumb_hover)
    svg.hint('hint-scrollbar-size', 0, nxt(svg), S, S)
    return svg


# ==========================================================================
# widgets/slider — groove + glossy Aqua knob
# ==========================================================================

def knob_layers(cx, cy, rad, pressed=False):
    stops = P.BLUE_GEL_PRESSED if pressed else P.BLUE_GEL
    rim = P.BLUE_RIM_PRESSED if pressed else P.BLUE_RIM
    return [
        Layer(ellipse_poly(cx, cy + 1, rad, rad), '#000000', 0.22),
        Layer(ellipse_poly(cx, cy, rad, rad), rim),
        Layer(ellipse_poly(cx, cy, rad - 1, rad - 1), Linear(0, cy - rad, 0, cy + rad, stops)),
        Layer(ellipse_poly(cx, cy - rad * 0.42, rad * 0.62, rad * 0.42), Linear(0, cy - rad, 0, cy, P.GLOSS), 0.85),
    ]


def slider_svg():
    svg = SVG(CS)
    K = 18
    for orient in ('horizontal', 'vertical'):
        y = nxt(svg)
        svg.element(orient + '-slider-handle', 0, y, K, K + 1, knob_layers(K / 2, K / 2, K / 2 - 0.5))
        svg.element(orient + '-slider-hover', K + 4, y, K, K + 1, knob_layers(K / 2, K / 2, K / 2 - 0.5) +
                    [Layer(ellipse_poly(K / 2, K / 2, K / 2 - 1, K / 2 - 1), '#ffffff', 0.12)])
        svg.element(orient + '-slider-focus', 2 * (K + 4), y, K, K + 1,
                    [Layer(ellipse_poly(K / 2, K / 2, K / 2, K / 2), P.FOCUS_RING, 0.6,
                           hole=ellipse_poly(K / 2, K / 2, K / 2 - 2, K / 2 - 2))])
        svg.element(orient + '-slider-shadow', 3 * (K + 4), y, K, K + 1, [Layer(ellipse_poly(K / 2, K / 2 + 1, K / 2, K / 2), '#000000', 0.08)])
    svg.hint('hint-handle-size', 0, nxt(svg), K, K + 1)
    W, H, r = 40, 6, 3
    m = (3, 3, 3, 3)
    svg.frame('groove-', 0, nxt(svg), W, H, m, [
        RR(0, 0, W, H, r, vgrad(0, H, [(0, D('#8d8d8d', '#060607'), 1), (1, D('#b9b9b9', '#34363a'), 1)])),
        RR(1, 1, W - 1, H - 1, r - 1, vgrad(1, H - 1, [(0, D('#c8c8c8', '#111214'), 1), (1, D('#efefef', '#202225'), 1)])),
    ])
    svg.frame('groove-highlight-', 0, nxt(svg), W, H, m, [
        RR(0, 0, W, H, r, P.BLUE_RIM),
        RR(1, 1, W - 1, H - 1, r - 1, vgrad(1, H - 1, [(0, D('#5c9ff0', '#2459b4'), 1), (1, D('#a9dcff', '#4a8ae0'), 1)])),
    ])
    return svg


# ==========================================================================
# widgets/bar_meter_* — blue gel progress bar ("candy")
# ==========================================================================

def bar_meter_svg(vertical=False):
    svg = SVG(CS)
    T = 12  # bar thickness
    L = 40
    r = T / 2 - 0.5
    axis = 'h' if vertical else 'v'
    W, H = (T, L) if vertical else (L, T + 1)
    m = (6, 6, 6, 6)
    if vertical:
        inactive = [RR(0, 0, T, L, r, hgrad(0, T, [(0, D('#a9a9a9', '#060607'), 1), (1, D('#c9c9c9', '#33353a'), 1)])),
                    RR(1, 1, T - 1, L - 1, r - 1, hgrad(1, T - 1, [(0, D('#dcdcdc', '#121315'), 1), (1, D('#fafafa', '#212326'), 1)]))]
        active = G.blue(0, 0, T, L, r, axis='h', drop=0)
    else:
        inactive = [RR(0, 0, L, T, r, vgrad(0, T, [(0, D('#a9a9a9', '#060607'), 1), (1, D('#c9c9c9', '#33353a'), 1)])),
                    RR(1, 1, L - 1, T - 1, r - 1, vgrad(1, T - 1, [(0, D('#dcdcdc', '#121315'), 1), (0.5, D('#f0f0f0', '#1a1b1e'), 1),
                                                                   (1, D('#fafafa', '#212326'), 1)]))]
        active = G.blue(0, 0, L, T, r, axis='v', drop=0)
    svg.frame('bar-inactive-', 0, 0, W, H, m, inactive)
    svg.frame('bar-active-', 0, nxt(svg), W, H, m, active)
    svg.hint('hint-bar-size', 0, nxt(svg), T if vertical else L, L if vertical else T)
    return svg


# ==========================================================================
# widgets/menubaritem — global menu & menu-extra highlight (blue)
# widgets/tabbar     — active applet highlight in panels
# ==========================================================================

def menubaritem_svg():
    svg = SVG(CS)
    W, H = 40, 24
    m = (3, 3, 3, 3)
    hints = {'top-margin': 2, 'bottom-margin': 2, 'left-margin': 8, 'right-margin': 8}
    svg.frame('normal-', 0, 0, W, H, m, [RR(0, 0, W, H, 0, '#ffffff', 0.0)], hints=hints)
    svg.frame('hover-', 0, nxt(svg), W, H, m, [RR(0, 0, W, H, 0, D('#000000', '#ffffff'), D(0.07, 0.08))], hints=hints)
    svg.frame('pressed-', 0, nxt(svg), W, H, m, selection_layers(W, H, 0), hints=hints)
    return svg


def tabbar_svg():
    svg = SVG(CS)
    W, H = 40, 26
    m = (3, 3, 3, 3)
    sel = selection_layers(W, H, 0)
    hints = {'top-margin': 2, 'bottom-margin': 2, 'left-margin': 4, 'right-margin': 4}
    # north-active-tab: menu bar (global menu / menu extras) -> Aqua blue highlight
    svg.frame('north-active-tab-', 0, 0, W, H, m, sel, hints=hints)
    # dock / generic: soft white glow pill
    glow = [RR(1, 1, W - 1, H - 1, 6, '#ffffff', D(0.45, 0.12)), RING(1, 1, W - 1, H - 1, 6, 1, '#ffffff', D(0.6, 0.22))]
    for pre in ('south-active-tab-', 'east-active-tab-', 'west-active-tab-', 'active-tab-'):
        svg.frame(pre, 0, nxt(svg), W, H, (7, 7, 7, 7), glow, hints=hints)
    return svg


# ==========================================================================
# widgets/plasmoidheading — popup header/footer (SL unified gradient strip)
# ==========================================================================

def plasmoidheading_svg():
    svg = SVG(CS)
    W, H = 40, 32
    m = (2, 2, 2, 2)
    header = [RR(0, 0, W, H, 0, vgrad(0, H, D([(0, '#f6f6f6', 1), (1, '#e3e3e3', 1)],
                                              [(0, '#36393e', 1), (0.5, '#2d2f33', 1), (0.5, '#26282b', 1), (1, '#24262a', 1)]))),
              Layer(rrect_poly(0, H - 1, W, H, 0), D('#b9b9b9', '#09090a'))]
    footer = [RR(0, 0, W, H, 0, vgrad(0, H, [(0, D('#e9e9e9', '#1f2124'), 1), (1, D('#f6f6f6', '#25272a'), 1)])),
              Layer(rrect_poly(0, 0, W, 1, 0), D('#c4c4c4', '#09090a'))]
    svg.frame('header-', 0, 0, W, H, m, header)
    svg.frame('footer-', 0, nxt(svg), W, H, m, footer)
    svg.hint('hint-stretch-borders', 0, nxt(svg), 2, 2)
    y = nxt(svg)
    svg.hint('hint-top-margin', 0, y, 1, 6)
    svg.hint('hint-bottom-margin', 2, y, 1, 6)
    svg.hint('hint-left-margin', 4, y, 8, 1)
    svg.hint('hint-right-margin', 4, y + 3, 8, 1)
    return svg


# ==========================================================================
# widgets/switch — Aqua-ish toggle (blue gel track when on)
# ==========================================================================

def switch_svg():
    svg = SVG(CS)
    BW, BH = 36, 18
    r = BH / 2
    hm = (9, 9, 9, 9)
    svg.frame('inactive-', 0, 0, BW, BH, hm, [
        RR(0, 0, BW, BH, r, vgrad(0, BH, [(0, D('#8d8d8d', '#060607'), 1), (1, D('#b3b3b3', '#34363a'), 1)])),
        RR(1, 1, BW - 1, BH - 1, r - 1, vgrad(1, BH - 1, [(0, D('#d2d2d2', '#131416'), 1), (1, D('#f6f6f6', '#222427'), 1)])),
    ])
    svg.frame('active-', 0, nxt(svg), BW, BH, hm, G.blue(0, 0, BW, BH, r, drop=0))
    svg.hint('hint-bar-size', 0, nxt(svg), BW, BH)
    y = nxt(svg)
    K = BH
    knob = [Layer(ellipse_poly(K / 2, K / 2 + 0.5, K / 2, K / 2), '#000000', 0.25),
            Layer(ellipse_poly(K / 2, K / 2, K / 2 - 0.5, K / 2 - 0.5), P.WHITE_RIM),
            Layer(ellipse_poly(K / 2, K / 2, K / 2 - 1.5, K / 2 - 1.5), Linear(0, 0, 0, K, P.WHITE_GEL)),
            Layer(ellipse_poly(K / 2, K / 2 - K * 0.2, K * 0.3, K * 0.2), Linear(0, 0, 0, K / 2, P.GLOSS), 0.8)]
    svg.element('handle', 0, y, K, K, knob)
    svg.element('handle-hover', K + 4, y, K, K, knob + [Layer(ellipse_poly(K / 2, K / 2, K / 2 - 1.5, K / 2 - 1.5), '#6fb4ff', 0.15)])
    svg.element('handle-pressed', 2 * (K + 4), y, K, K, knob + [Layer(ellipse_poly(K / 2, K / 2, K / 2 - 1.5, K / 2 - 1.5), '#000000', 0.10)])
    svg.element('handle-shadow', 3 * (K + 4), y, K, K, [Layer(ellipse_poly(K / 2, K / 2 + 1, K / 2, K / 2), '#000000', 0.12)])
    svg.element('handle-focus', 4 * (K + 4), y, K, K, [Layer(ellipse_poly(K / 2, K / 2, K / 2, K / 2), P.FOCUS_RING, 0.7,
                                                             hole=ellipse_poly(K / 2, K / 2, K / 2 - 2, K / 2 - 2))])
    return svg


# ==========================================================================
# widgets/radiobutton — gel radio
# ==========================================================================

def radiobutton_svg():
    svg = SVG(CS)
    S = 16
    c = S / 2
    svg.element('normal', 0, 0, S, S, [
        Layer(ellipse_poly(c, c, c - 0.5, c - 0.5), vgrad(0, S, [(0, D('#8a8a8a', P.WHITE_RIM_TOP), 1), (1, D('#6e6e6e', P.WHITE_RIM_BOTTOM), 1)])),
        Layer(ellipse_poly(c, c, c - 1.5, c - 1.5), Linear(0, 1, 0, S - 1, P.WHITE_GEL)),
        Layer(ellipse_poly(c, c - 2.5, c * 0.6, c * 0.4), Linear(0, 1, 0, c, P.GLOSS), 0.7),
    ])
    svg.element('checked', S + 4, 0, S, S, [
        Layer(ellipse_poly(c, c, c - 0.5, c - 0.5), P.BLUE_RIM),
        Layer(ellipse_poly(c, c, c - 1.5, c - 1.5), Linear(0, 1, 0, S - 1, P.BLUE_GEL)),
        Layer(ellipse_poly(c, c - 2.5, c * 0.6, c * 0.4), Linear(0, 1, 0, c, P.GLOSS), 0.7),
    ])
    svg.element('symbol', 2 * (S + 4), 0, S, S, [Layer(ellipse_poly(c, c, 2.6, 2.6), D('#1b2a44', '#ffffff'), D(0.9, 0.95))])
    svg.element('focus', 3 * (S + 4), 0, S, S, [Layer(ellipse_poly(c, c, c, c), P.FOCUS_RING, 0.7, hole=ellipse_poly(c, c, c - 1.6, c - 1.6))])
    svg.element('hover', 4 * (S + 4), 0, S, S, [Layer(ellipse_poly(c, c, c, c), P.HOVER, 0.5, hole=ellipse_poly(c, c, c - 1.2, c - 1.2))])
    svg.element('shadow', 5 * (S + 4), 0, S, S, [Layer(ellipse_poly(c, c + 0.8, c - 0.3, c - 0.3), '#000000', 0.12)])
    svg.hint('hint-size', 0, nxt(svg), S, S)
    return svg


# ==========================================================================
# metadata, colours, plasmarc
# ==========================================================================

def write_metadata(root):
    meta = {
        "KPlugin": {
            "Authors": [{"Name": P.AUTHOR}],
            "Category": "",
            "Description": P.DESCRIPTION + " for Plasma",
            "EnabledByDefault": True,
            "Id": P.THEME_ID,
            "License": "GPL-3.0-or-later",
            "Name": P.THEME_NAME,
            "Version": P.VERSION,
            "Website": ""
        },
        "X-Plasma-API": "5.0",
        "X-Plasma-API-Minimum-Version": "6.0"
    }
    with open(os.path.join(root, 'metadata.json'), 'w') as fh:
        json.dump(meta, fh, indent=4)
    with open(os.path.join(root, 'plasmarc'), 'w') as fh:
        # DarkLiger: the blurred backdrop is darkened (intensity < 1) so it reads as smoked glass
        fh.write('[ContrastEffect]\nenabled=true\ncontrast=%s\nintensity=%s\nsaturation=%s\n\n'
                 '[BlurBehindEffect]\nenabled=true\n\n[AdaptiveTransparency]\nenabled=true\n'
                 % D(('0.9', '1.1', '1.6'), ('0.45', '0.55', '1.4')))


def build(out):
    root = os.path.join(out, 'plasma', 'desktoptheme', P.THEME_ID)

    def save(rel, svg):
        # FrameSvg tiles border pieces unless told otherwise; a tiled border repeats its
        # slice of a gradient (doubled caps, saw-toothed sides) while the centre stretches
        if 'id="hint-stretch-borders"' not in ''.join(svg.body):
            svg.hint('hint-stretch-borders', 0, svg.maxy + 12, 2, 2)
        svg.save(os.path.join(root, rel + '.svgz'))

    # base (compositing, no blur assumed)
    save('dialogs/background', dialog_svg(alpha=0.97))
    save('widgets/panel-background', panel_svg(alpha=0.94, dock_alpha=1.0))
    save('widgets/tooltip', tooltip_svg())
    # translucent/ (used when blur is available)
    save('translucent/dialogs/background', dialog_svg(alpha=0.90))
    save('translucent/widgets/panel-background', panel_svg(alpha=0.82, dock_alpha=0.78))
    save('translucent/widgets/tooltip', tooltip_svg(alpha=0.96))
    # opaque/ (no compositing) and solid/ (opaque panel mode)
    save('opaque/dialogs/background', dialog_svg(alpha=1.0, shadow=False))
    save('opaque/widgets/panel-background', panel_svg(opaque=True, shadow=False))
    save('opaque/widgets/tooltip', tooltip_svg(shadow=False))
    save('solid/dialogs/background', dialog_svg(alpha=1.0))
    save('solid/widgets/panel-background', panel_svg(opaque=True))
    save('solid/widgets/tooltip', tooltip_svg())

    save('widgets/background', widget_bg_svg())
    save('widgets/button', button_svg())
    save('widgets/tasks', tasks_svg())
    save('widgets/viewitem', viewitem_svg())
    save('widgets/listitem', listitem_svg())
    save('widgets/lineedit', lineedit_svg())
    save('widgets/scrollbar', scrollbar_svg())
    save('widgets/slider', slider_svg())
    save('widgets/bar_meter_horizontal', bar_meter_svg(False))
    save('widgets/bar_meter_vertical', bar_meter_svg(True))
    save('widgets/menubaritem', menubaritem_svg())
    save('widgets/tabbar', tabbar_svg())
    save('widgets/plasmoidheading', plasmoidheading_svg())
    save('widgets/switch', switch_svg())
    save('widgets/radiobutton', radiobutton_svg())

    write_metadata(root)
    import colorscheme
    with open(os.path.join(root, 'colors'), 'w') as fh:
        fh.write(colorscheme.render(for_plasma_theme=True))
    return root
