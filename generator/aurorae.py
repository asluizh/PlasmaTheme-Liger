"""
Liger window decoration (Aurorae SVG theme).

Aqua Snow Leopard..Mavericks title bar: 22px unified grey gradient, centred
engraved title, traffic-light gel buttons on the left, big soft shadow.

Aurorae has no native shadow support, so the shadow is baked into the
decoration padding as embedded PNG pieces (see svgkit.Raster).
"""
import math
import os

import palette as P
from svgkit import SVG, RR, RING, Layer, Linear, Radial, Raster, rrect_poly, ellipse_poly, clip_poly, vgrad, shadow_image

TITLE_H = 23
RADIUS = 5
BTN = 15                        # button cell: 12.8px gem + 1.1px inset well = 15px circle
GEM_R = 6.4
PAD = (26, 16, 26, 36)          # shadow padding: left, top, right, bottom
PAD_INACTIVE = PAD


def _crescent(x0, x1, y0, r, h):
    """Band of thickness h along the top edge of a rect with top corner radius r."""
    def edge(dy):
        pts = []
        n = max(4, int(r * 3))
        for cx, a0 in ((x0 + r, 180), (x1 - r, 270)):
            for i in range(n + 1):
                a = math.radians(a0 + 90 * i / n)
                pts.append((cx + r * math.cos(a), y0 + r + dy + r * math.sin(a)))
        return pts
    return edge(0) + list(reversed(edge(h)))


def _decoration_layers(W, H, pad, active, shadow=True, radius=RADIUS):
    pl, pt, pr, pb = pad
    x0, y0, x1, y1 = pl, pt, W - pr, H - pb
    L = []
    if shadow:
        alpha = 0.55 if active else 0.32
        blur = 28 if active else 18
        img = shadow_image(W, H, (x0, y0, x1, y1), (radius, radius, 0, 0), blur=blur, dy=10 if active else 6, alpha=alpha)
        # thin ambient contact shadow
        img2 = shadow_image(W, H, (x0, y0, x1, y1), (radius, radius, 0, 0), blur=3, dy=1, alpha=0.25)
        from PIL import Image
        img = Image.alpha_composite(img, img2)
        L.append(Raster(img, 2))
    title = P.TITLE_ACTIVE if active else P.TITLE_INACTIVE
    outline = P.WINDOW_OUTLINE if active else P.WINDOW_OUTLINE_INACTIVE
    sep = P.TITLE_ACTIVE_SEPARATOR if active else P.TITLE_INACTIVE_SEPARATOR
    r = (radius, radius, 0, 0)
    # outline ring around the whole window
    L.append(RING(x0, y0, x1, y1, r, 1, outline[0], outline[1]))
    # window body (mostly covered by the client)
    L.append(RR(x0 + 1, y0 + 1, x1 - 1, y1 - 1, (radius - 1, radius - 1, 0, 0), P.WINDOW_BG))
    # title bar gradient
    L.append(Layer(rrect_poly(x0 + 1, y0 + 1, x1 - 1, y0 + TITLE_H, (radius - 1, radius - 1, 0, 0)),
                   vgrad(y0 + 1, y0 + TITLE_H, title)))
    # top specular line: a crescent following the rounded corners (the title's top edge
    # minus the same edge shifted down), so it never pokes outside the corner
    L.append(Layer(_crescent(x0 + 1, x1 - 1, y0 + 1, radius - 1, 1.2), '#ffffff',
                   P.TITLE_ACTIVE_HILITE[1] if active else 0.9))
    # separator under the title bar
    L.append(Layer(rrect_poly(x0 + 1, y0 + TITLE_H - 1, x1 - 1, y0 + TITLE_H, 0), sep))
    return L


def _maximized_layers(W, active):
    title = P.TITLE_ACTIVE if active else P.TITLE_INACTIVE
    sep = P.TITLE_ACTIVE_SEPARATOR if active else P.TITLE_INACTIVE_SEPARATOR
    H = TITLE_H + 20
    return H, [
        RR(0, 0, W, H, 0, P.WINDOW_BG),
        RR(0, 0, W, TITLE_H, 0, vgrad(0, TITLE_H, title)),
        RR(0, 0, W, 1, 0, '#ffffff', 0.8),
        RR(0, TITLE_H - 1, W, TITLE_H, 0, sep),
    ]


def decoration_svg():
    svg = SVG()
    pl, pt, pr, pb = PAD
    W = pl + pr + 120
    H = pt + pb + TITLE_H + 60
    # slice: corners wide enough to hold the rounded corner + shadow
    m = (pl + RADIUS + 1, pt + TITLE_H, pr + RADIUS + 1, pb + 1)
    y = 0
    for pre, active in (('decoration-', True), ('decoration-inactive-', False)):
        svg.frame(pre, 0, y, W, H, m, _decoration_layers(W, H, PAD, active))
        y = svg.maxy + 12
    # maximized: no shadow, no rounded corners, no side borders
    for pre, active in (('decoration-maximized-', True), ('decoration-maximized-inactive-', False)):
        MW = 120
        MH, layers = _maximized_layers(MW, active)
        svg.frame(pre, 0, y, MW, MH, (2, TITLE_H, 2, 1), layers)
        y = svg.maxy + 12
    return svg


# --------------------------------------------------------------------------
# traffic lights
# --------------------------------------------------------------------------

def _rect_poly(cx, cy, w, h, angle):
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def glyph(kind, cx, cy, color, opacity=0.75):
    t = 1.5   # stroke
    s = 7.0   # glyph extent
    if kind == 'close':
        return [Layer(_rect_poly(cx, cy, s, t, 45), color, opacity), Layer(_rect_poly(cx, cy, s, t, -45), color, opacity)]
    if kind == 'minimize':
        return [Layer(_rect_poly(cx, cy, s + 0.5, t, 0), color, opacity)]
    if kind in ('maximize', 'restore'):
        return [Layer(_rect_poly(cx, cy, s + 0.5, t, 0), color, opacity), Layer(_rect_poly(cx, cy, s + 0.5, t, 90), color, opacity)]
    if kind == 'keepabove':
        # triangle pointing up
        return [Layer([(cx - 3.2, cy + 1.7), (cx + 3.2, cy + 1.7), (cx, cy - 2.3)], color, opacity)]
    if kind == 'alldesktops':
        # a pin head seen from above: dot
        return [Layer(ellipse_poly(cx, cy, 1.9, 1.9), color, opacity)]
    return []


def well(cx, cy, rad, width=1.1):
    """Inset socket the gem sits in: dark rim at the top, light reflection at the bottom."""
    R = rad + width
    return [Layer(ellipse_poly(cx, cy, R, R), Linear(0, cy - R, 0, cy + R,
                                                      [(0, '#000000', 0.42), (0.45, '#000000', 0.16),
                                                       (0.7, '#ffffff', 0.25), (1, '#ffffff', 0.85)]),
                  hole=ellipse_poly(cx, cy, rad, rad))]


def gem(cx, cy, rad, colors, pressed=False, dim=1.0):
    rim, edge, mid, glow, _ = colors
    if pressed:
        from svgkit import shade
        edge, mid, glow = shade(edge, 0.8), shade(mid, 0.8), shade(glow, 0.85)
    L = well(cx, cy, rad) + [
        Layer(ellipse_poly(cx, cy, rad, rad), Linear(0, cy - rad, 0, cy + rad, [(0, rim, 1), (1, edge, 1)]), dim),
        Layer(ellipse_poly(cx, cy, rad - 0.8, rad - 0.8),
              Radial(cx, cy + rad * 0.55, rad * 1.25, [(0, glow, 1), (0.45, mid, 1), (1, edge, 1)]), dim),
        # ambient occlusion: the socket's upper lip shades the top of the gem
        Layer(ellipse_poly(cx, cy, rad, rad), Linear(0, cy - rad, 0, cy - rad * 0.2,
                                                     [(0, '#000000', 0.38), (1, '#000000', 0)])),
        # specular cap
        Layer(ellipse_poly(cx, cy - rad * 0.42, rad * 0.62, rad * 0.40),
              Linear(0, cy - rad, 0, cy, [(0, '#ffffff', 0.95), (1, '#ffffff', 0.15)]), dim),
    ]
    return L


def button_svg(kind):
    svg = SVG()
    S = BTN
    c = S / 2
    rad = GEM_R
    colors = P.TRAFFIC['maximize' if kind == 'restore' else kind]
    gray = P.TRAFFIC['graphite']
    states = {
        'active': gem(c, c, rad, colors),
        'hover': gem(c, c, rad, colors) + glyph(kind, c, c, colors[4]),
        'pressed': gem(c, c, rad, colors, pressed=True) + glyph(kind, c, c, colors[4], 0.9),
        'inactive': gem(c, c, rad, gray, dim=0.85),
        'hover-inactive': gem(c, c, rad, colors) + glyph(kind, c, c, colors[4]),
        'pressed-inactive': gem(c, c, rad, colors, pressed=True) + glyph(kind, c, c, colors[4], 0.9),
        'deactivated': gem(c, c, rad, gray, dim=0.45),
        'deactivated-inactive': gem(c, c, rad, gray, dim=0.35),
    }
    x = 0
    for name, layers in states.items():
        svg.element(name + '-center', x, 0, S, S, layers)
        x += S + 4
    return svg


RC = """[General]
ActiveTextColor={at}
InactiveTextColor={it}
UseTextShadow=true
ActiveTextShadowColor=255,255,255,200
InactiveTextShadowColor=255,255,255,160
TextShadowOffsetX=0
TextShadowOffsetY=1
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=120
Shadow=false
HaloActive=false
HaloInactive=false
ButtonGroupHover=true

[Layout]
BorderLeft=1
BorderRight=1
BorderBottom=1
BorderLeftMaximized=0
BorderRightMaximized=0
BorderBottomMaximized=0
TitleEdgeTop=4
TitleEdgeBottom=4
TitleEdgeLeft=8
TitleEdgeRight=8
TitleEdgeTopMaximized=4
TitleEdgeBottomMaximized=4
TitleEdgeLeftMaximized=8
TitleEdgeRightMaximized=8
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight=15
ButtonWidth={b}
ButtonHeight={b}
ButtonSpacing=6
ButtonMarginTop=0
ExplicitButtonSpacer=8
PaddingLeft={pl}
PaddingTop={pt}
PaddingRight={pr}
PaddingBottom={pb}
"""


def build(out):
    from svgkit import hexrgb
    root = os.path.join(out, 'aurorae', 'themes', P.THEME_ID)
    os.makedirs(root, exist_ok=True)
    decoration_svg().save(os.path.join(root, 'decoration.svg'))
    for kind in ('close', 'minimize', 'maximize', 'restore', 'keepabove', 'alldesktops'):
        button_svg(kind).save(os.path.join(root, kind + '.svg'))
    with open(os.path.join(root, P.THEME_ID + 'rc'), 'w') as fh:
        fh.write(RC.format(at='%d,%d,%d' % hexrgb(P.TITLE_TEXT), it='%d,%d,%d' % hexrgb(P.TITLE_TEXT_INACTIVE),
                           b=BTN, pl=PAD[0], pt=PAD[1], pr=PAD[2], pb=PAD[3]))
    with open(os.path.join(root, 'metadata.desktop'), 'w') as fh:
        fh.write('[Desktop Entry]\nName=%s\nComment=Aqua (Snow Leopard..Mavericks) window decoration\n'
                 'X-KDE-PluginInfo-Author=%s\nX-KDE-PluginInfo-Name=%s\nX-KDE-PluginInfo-Version=%s\n'
                 'X-KDE-PluginInfo-License=GPL-3.0-or-later\nX-KDE-PluginInfo-EnabledByDefault=true\n'
                 'X-Plasma-API=declarativeappletscript\n' % (P.THEME_NAME, P.AUTHOR, P.THEME_ID, P.VERSION))
    return root
