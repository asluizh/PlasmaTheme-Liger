"""
Liger / DarkLiger Kvantum theme — Aqua widgets inside applications.

Kvantum naming: frames  <element>-<state>-<piece>, interiors <element>-<state>,
"expand-" objects for maximally rounded (capsule) widgets, "-focus" stateless
focus frames, "-inactive" sub-states.  See Kvantum's doc/Theme-Making.pdf.

Orientation rules (Kvantum rotates the rest): scrollbar + slider groove are drawn
VERTICAL, progress bars HORIZONTAL, tabs HORIZONTAL (top).
"""
import os

import palette as P
import gel as G
from palette import D
from svgkit import SVG, RR, RING, Layer, Linear, Radial, rrect_poly, clip_poly, ellipse_poly, vgrad, hgrad, add_shadow, shade

KV_ID = P.THEME_ID
PROGRESS_H = 12                # Aqua determinate bar thickness (text goes beside it)
PIECES = ['top', 'bottom', 'left', 'right', 'topleft', 'topright', 'bottomleft', 'bottomright']


class KV:
    def __init__(self):
        self.svg = SVG()
        self.x = 0
        self.y = 0
        self.rowh = 0

    def _slot(self, w, h):
        if self.x + w > 900:
            self.x = 0
            self.y += self.rowh + 12
            self.rowh = 0
        pos = (self.x, self.y)
        self.x += w + 40
        self.rowh = max(self.rowh, h + 20)
        return pos

    def frame(self, name, W, H, m, layers, interior=True):
        """name = '<element>-<state>' ; emits name-top.. and (optionally) the interior `name`."""
        ox, oy = self._slot(W, H)
        pieces = PIECES + (['center'] if interior else [])
        self.svg.frame(name + '-', ox, oy, W, H, m, layers, pieces=pieces, center=name)

    def element(self, name, W, H, layers):
        ox, oy = self._slot(W, H)
        self.svg.element(name, ox, oy, W, H, layers)

    def hint(self, name, w, h):
        ox, oy = self._slot(max(w, 2), max(h, 2))
        self.svg.hint(name, ox, oy, w, h)


# --------------------------------------------------------------------------
# shapes
# --------------------------------------------------------------------------

def tri(cx, cy, size, direction):
    s = size / 2
    h = size * 0.5
    if direction == 'down':
        return [(cx - s, cy - h / 2), (cx + s, cy - h / 2), (cx, cy + h / 2)]
    if direction == 'up':
        return [(cx - s, cy + h / 2), (cx + s, cy + h / 2), (cx, cy - h / 2)]
    if direction == 'right':
        return [(cx - h / 2, cy - s), (cx - h / 2, cy + s), (cx + h / 2, cy)]
    return [(cx + h / 2, cy - s), (cx + h / 2, cy + s), (cx - h / 2, cy)]


def check_poly(x, y, s):
    """A bold check mark inside the square (x,y,s)."""
    pts = [(0.18, 0.52), (0.30, 0.40), (0.44, 0.56), (0.78, 0.14), (0.90, 0.26), (0.44, 0.80)]
    return [(x + px * s, y + py * s) for px, py in pts]


def bar_rect(cx, cy, w, h):
    return rrect_poly(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, min(w, h) / 2)


def graphite(x0, y0, x1, y1, r, axis='v', **kw):
    # DarkLiger: toggled = pressed-in smoked glass, darker than the window
    stops = D([(0, '#d9d9d9', 1), (0.48, '#bdbdbd', 1), (0.5, '#a9a9a9', 1), (1, '#c9c9c9', 1)],
              [(0, '#1b1c1f', 1), (0.48, '#18191b', 1), (0.5, '#121315', 1), (1, '#1a1b1e', 1)])
    return G.gel(x0, y0, x1, y1, r, stops, D('#5e5e5e', '#000000'), D('#4a4a4a', '#000000'), axis, **kw)


def faded(layers, k):
    return [Layer(L.shape, L.paint, L.opacity * k, L.hole, L.cls) for L in layers]


# --------------------------------------------------------------------------
# widgets
# --------------------------------------------------------------------------

def buttons(kv: KV):
    # regular (tall) buttons: rounded rect r=4 inside a 2px glow margin
    W, H, f = 64, 30, 6
    box = (2, 2, W - 2, H - 3)
    r = 4.5
    looks = {
        'normal': G.white(*box, r),
        'focused': G.white(*box, r) + [RR(box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1, r - 1, '#ffffff', D(0.25, 0.06))],
        'pressed': G.blue(*box, r, pressed=True),
        'toggled': graphite(*box, r),
        'disabled': faded(G.white(*box, r), 0.55),
    }
    for st, L in looks.items():
        kv.frame('button-' + st, W, H, (f, f, f, f), L)
    kv.frame('button-default', W, H, (f, f, f, f), G.blue(*box, r))
    kv.frame('button-focus', W, H, (f, f, f, f), G.glow_ring(*box, r, P.FOCUS_RING, width=2), interior=False)

    # capsules (frame expansion): height 2R, only top/bottom/corners are used
    R = 15
    CW, CH = 70, 2 * R
    cbox = (2, 2, CW - 2, CH - 3)
    cr = (cbox[3] - cbox[1]) / 2
    clooks = {
        'normal': G.white(*cbox, cr),
        'focused': G.white(*cbox, cr) + [RR(cbox[0] + 1, cbox[1] + 1, cbox[2] - 1, cbox[3] - 1, cr - 1, '#ffffff', D(0.25, 0.06))],
        'pressed': G.blue(*cbox, cr, pressed=True),
        'toggled': graphite(*cbox, cr),
        'disabled': faded(G.white(*cbox, cr), 0.55),
    }
    for st, L in clooks.items():
        kv.frame('expand-button-' + st, CW, CH, (R, R, R, R), L, interior=False)
    kv.frame('expand-button-default', CW, CH, (R, R, R, R), G.blue(*cbox, cr), interior=False)
    kv.frame('expand-button-focus', CW, CH, (R, R, R, R), G.glow_ring(*cbox, cr, P.FOCUS_RING, width=2), interior=False)
    # Kvantum marks default buttons with a corner triangle and falls back to its built-in
    # art when the theme has none; the Aqua default button is already blue, so draw nothing
    for name in ('button-default-indicator', 'flat-button-default-indicator'):
        kv.element(name, 8, 8, [])


def toolbuttons(kv: KV):
    W, H, f = 56, 28, 5
    box = (1, 1, W - 1, H - 2)
    r = 4
    looks = {
        'normal': [RR(*box, r, '#000000', 0.0)],
        'focused': [RR(box[0], box[1], box[2], box[3], r, '#000000', D(0.14, 0.6)),
                    RR(box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1, r - 1,
                       vgrad(box[1], box[3], D([(0, '#ffffff', 0.85), (0.5, '#f2f2f2', 0.7), (0.5, '#e4e4e4', 0.7), (1, '#f6f6f6', 0.8)],
                                               [(0, '#ffffff', 0.20), (0.5, '#ffffff', 0.10), (0.5, '#ffffff', 0.04), (1, '#ffffff', 0.08)])))],
        'pressed': [RR(*box, r, '#000000', D(0.35, 0.75)),
                    RR(box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1, r - 1,
                       vgrad(box[1], box[3], D([(0, '#8f8f8f', 0.6), (0.25, '#a9a9a9', 0.55), (1, '#c4c4c4', 0.5)],
                                               [(0, '#000000', 0.5), (0.25, '#000000', 0.35), (1, '#ffffff', 0.05)])))],
        'toggled': [RR(*box, r, '#000000', D(0.40, 0.8)),
                    RR(box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1, r - 1,
                       vgrad(box[1], box[3], D([(0, '#7d7d7d', 0.65), (0.25, '#9a9a9a', 0.6), (1, '#b6b6b6', 0.55)],
                                               [(0, '#000000', 0.55), (0.25, '#000000', 0.42), (1, '#ffffff', 0.06)])))],
    }
    for st, L in looks.items():
        kv.frame('tbutton-' + st, W, H, (f, f, f, f), L)
    kv.frame('tbutton-focus', W, H, (f, f, f, f), G.glow_ring(box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1, r, P.FOCUS_RING, width=1.5), interior=False)


def lineedit(kv: KV):
    W, H, f = 48, 26, 4
    box = (1, 1, W - 1, H - 1)
    base = [
        RR(*box, 3, vgrad(box[1], box[3], [(0, D('#8c8c8c', '#050506'), 1), (0.25, D('#aeaeae', '#0c0d0e'), 1), (1, D('#c8c8c8', '#3b3d42'), 1)])),
        RR(box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1, 2, D('#ffffff', '#17181b')),
        Layer(rrect_poly(box[0] + 1, box[1] + 1, box[2] - 1, box[1] + 4, (2, 2, 0, 0)),
              vgrad(box[1] + 1, box[1] + 4, [(0, '#000000', D(0.14, 0.5)), (1, '#000000', 0)])),
    ]
    kv.frame('lineedit-normal', W, H, (f, f, f, f), base)
    focus = base + [RING(0, 0, W, H, 4, 3, P.FOCUS_RING, 0.45), RING(0.5, 0.5, W - 0.5, H - 0.5, 3.5, 2, P.FOCUS_RING, 0.65)]
    kv.frame('lineedit-focused', W, H, (f, f, f, f), focus)
    kv.frame('lineedit-disabled', W, H, (f, f, f, f), faded(base, 0.6))
    # toolbar line edits / editable combos share the look
    kv.frame('tlineedit-normal', W, H, (f, f, f, f), base)
    kv.frame('tlineedit-focused', W, H, (f, f, f, f), focus)


def spin(kv: KV):
    W, H, f = 24, 28, 4
    box = (0.5, 1, W - 1, H - 2)
    looks = {'normal': G.white(*box, 3.5), 'focused': G.white(*box, 3.5), 'pressed': G.blue(*box, 3.5, pressed=True),
             'disabled': faded(G.white(*box, 3.5), 0.55)}
    for st, L in looks.items():
        kv.frame('spin-' + st, W, H, (f, f, f, f), L)


def checks(kv: KV):
    S = 16
    box = (1, 0.5, S - 1, S - 1.5)
    r = 3
    white = G.white(*box, r)
    blue = G.blue(*box, r)
    mark = D('#16243a', '#ffffff')
    check = Layer(check_poly(1, 0, S - 2), mark, 0.9)
    dash = Layer(bar_rect(S / 2, S / 2 - 0.5, S - 7, 2.4), mark, 0.9)
    for st in ('normal', 'focused', 'pressed', 'disabled'):
        b = white if st != 'pressed' else G.blue(*box, r, pressed=True)
        bb = blue if st != 'pressed' else G.blue(*box, r, pressed=True)
        k = 0.55 if st == 'disabled' else 1
        kv.element('checkbox-' + st, S, S, faded(b, k))
        kv.element('checkbox-checked-' + st, S, S, faded(bb + [check], k))
        kv.element('checkbox-tristate-' + st, S, S, faded(bb + [dash], k))
        # menus use the same art
        kv.element('menu-checkbox-' + st, S, S, faded(b, k))
        kv.element('menu-checkbox-checked-' + st, S, S, faded(bb + [check], k))
        kv.element('menu-checkbox-tristate-' + st, S, S, faded(bb + [dash], k))

    c = S / 2

    def disc(stops, rim, rim2):
        return [
            Layer(ellipse_poly(c, c + 0.6, c - 0.8, c - 0.8), '#000000', 0.16),
            Layer(ellipse_poly(c, c, c - 0.8, c - 0.8), Linear(0, 0, 0, S, [(0, rim, 1), (1, rim2, 1)])),
            Layer(ellipse_poly(c, c, c - 1.8, c - 1.8), Linear(0, 1, 0, S - 1, stops)),
            Layer(ellipse_poly(c, c - 2.6, c * 0.62, c * 0.38), Linear(0, 1, 0, c, P.GLOSS), 0.6),
        ]
    dot = Layer(ellipse_poly(c, c, 2.5, 2.5), D('#16243a', '#ffffff'), 0.9)
    for st in ('normal', 'focused', 'pressed', 'disabled'):
        k = 0.55 if st == 'disabled' else 1
        w = disc(P.WHITE_GEL, P.WHITE_RIM_TOP, P.WHITE_RIM_BOTTOM)
        b = disc(P.BLUE_GEL if st != 'pressed' else P.BLUE_GEL_PRESSED, P.BLUE_RIM, P.BLUE_RIM_BOTTOM)
        kv.element('radio-' + st, S, S, faded(w, k))
        kv.element('radio-checked-' + st, S, S, faded(b + [dot], k))
        kv.element('menu-radio-' + st, S, S, faded(w, k))
        kv.element('menu-radio-checked-' + st, S, S, faded(b + [dot], k))


def arrows(kv: KV):
    S = 10
    for d in ('up', 'down', 'left', 'right'):
        ink, ink_hi = D('#262626', '#cfd0d3'), D('#000000', '#ffffff')
        for st, col, a in (('normal', ink, 0.9), ('focused', ink_hi, 1), ('pressed', ink_hi, 1),
                           ('toggled', ink_hi, 1), ('disabled', ink, 0.35)):
            kv.element('arrow-%s-%s' % (d, st), S, S, [Layer(tri(S / 2, S / 2, S * 0.8, d), col, a)])
            # white "flat" variant for dark backgrounds (selected menu items etc.)
            kv.element('flat-arrow-%s-%s' % (d, st), S, S, [Layer(tri(S / 2, S / 2, S * 0.8, d), ink, a)])
    # combo indicator: Aqua popup-button blue cap with up/down chevrons
    C = 18
    for st in ('normal', 'focused', 'pressed', 'toggled', 'disabled'):
        L = G.blue(1, 1, C - 1, C - 2, (C - 3) / 2, pressed=(st == 'pressed'), drop=0)
        L += [Layer(tri(C / 2, C / 2 - 3.2, 6.5, 'up'), '#ffffff', 0.95), Layer(tri(C / 2, C / 2 + 2.6, 6.5, 'down'), '#ffffff', 0.95)]
        kv.element('carrow-' + st, C, C, faded(L, 0.5 if st == 'disabled' else 1))
    # spin +/- as arrows (inline)
    for st in ('normal', 'focused', 'pressed', 'disabled'):
        a = 0.35 if st == 'disabled' else 0.9
        kv.element('sarrow-up-' + st, S, S, [Layer(tri(S / 2, S / 2, S * 0.75, 'up'), D('#262626', '#cfd0d3'), a)])
        kv.element('sarrow-down-' + st, S, S, [Layer(tri(S / 2, S / 2, S * 0.75, 'down'), D('#262626', '#cfd0d3'), a)])


def _thumb_waves(x0, x1, y0, period, rows):
    """
    Subtle Aqua "water" ripples for a vertical scroller thumb: wavy bands across the
    thumb whose blue saturation rises and falls along its length.  One period tall so
    Kvantum can tile it (interior.y.patternsize) without stretching.
    """
    import math
    L = []
    w = x1 - x0
    step = period / rows
    for i in range(-1, rows + 1):
        k = math.sin(2 * math.pi * (i + 0.5) / rows)          # -1..1 along the length
        col, a = (D('#1f6fe0', '#0b2f78'), D(0.18, 0.30) * k) if k > 0 else ('#ffffff', -D(0.26, 0.10) * k)
        if a < 0.02:
            continue
        top = [(x0 + w * j / 8, y0 + i * step + 1.4 * math.sin(math.pi * j / 8)) for j in range(9)]
        bot = [(x, y + step) for x, y in reversed(top)]
        # keep it inside one period: what spills over one end wraps in from the other
        band = clip_poly(top + bot, (x0, y0, x1, y0 + period))
        if band:
            L.append(Layer(band, col, a))
    return L


# surface of the arrow buttons; the groove's ends use it too so the track's
# rounded wells look carved into the same piece (Snow Leopard "at top and bottom")
def _arrow_surface(S, y0, y1):
    return [RR(0, y0, S, y1, 0, hgrad(0, S, D([(0, '#c2c2c2', 1), (0.18, '#e9e9e9', 1), (0.5, '#fbfbfb', 1),
                                               (0.85, '#ececec', 1), (1, '#d9d9d9', 1)],
                                              [(0, '#121315', 1), (0.18, '#2a2c30', 1), (0.5, '#33353a', 1),
                                               (0.5, '#2a2c30', 1), (1, '#232528', 1)]))),
            RR(0, y0, 1, y1, 0, D('#a8a8a8', '#060607'))]


def scroll_arrows(kv: KV, S):
    """Indicator elements `scrollarrow-up/down-<state>` filling the whole S x S button (drawn vertical)."""
    def button(up, state):
        L = _arrow_surface(S, 0, S)
        if state == 'pressed':
            L = G.blue(1, 0, S, S, 0, axis='h', drop=0, gloss=0.5) + [RR(0, 0, 1, S, 0, D('#a8a8a8', '#060607'))]
        elif state == 'focused':
            L += [RR(1, 0, S, S, 0, '#ffffff', D(0.35, 0.07))]
        # flat outer end: soft rounded-off shading against the view's frame
        e0, e1 = (0, 4.5) if up else (S - 4.5, S)
        sh = D(0.16, 0.45)
        L += [RR(1, e0, S, e1, 0, vgrad(e0, e1, [(0, '#000000', sh), (1, '#000000', 0)] if up
                                        else [(0, '#000000', 0), (1, '#000000', sh)]))]
        # (the view's frame provides the closing line itself: scrollbar_in_view=true)
        L += [RR(1, 0, S, 1, 0, '#ffffff', D(0.7, 0.08))] if up else []
        # glyph
        col, a = ('#ffffff', 0.95) if state == 'pressed' else (D('#3d3d3d', '#c8c9cc'), 0.35 if state == 'disabled' else 0.9)
        cy = S / 2 + (0.5 if up else -0.5)
        L += [Layer(tri(S / 2 + 0.5, cy, 7, 'up' if up else 'down'), col, a)]
        return L
    for st in ('normal', 'focused', 'pressed', 'disabled'):
        kv.element('scrollarrow-up-' + st, S, S, button(True, st))
        kv.element('scrollarrow-down-' + st, S, S, button(False, st))


def scrollbars(kv: KV):
    S = 15                      # scroll_width (= arrow button size)
    cap = 8                     # frame.top/bottom: holds the rounded ends
    side = 2                    # frame.left/right
    # groove (vertical): flat Aqua track with a recessed capsule well whose
    # rounded ends are where the gel thumb comes to rest.  Around the well's ends
    # the arrow buttons' surface continues, so button and track read as one piece.
    Lh = 2 * cap + 20
    track = hgrad(0, S, [(0, D('#c9c9c9', '#101113'), 1), (0.25, D('#e4e4e4', '#17181a'), 1), (1, D('#f6f6f6', '#1d1e21'), 1)])
    wr = (S - 2) / 2
    groove = [RR(0, 0, S, Lh, 0, track), RR(0, 0, 1, Lh, 0, D('#a8a8a8', '#060607'))]
    groove += _arrow_surface(S, 0, cap) + _arrow_surface(S, Lh - cap, Lh)
    groove += [
        # soft contact shadow the button surface casts into the round end of the well
        RR(0.5, 0, S - 0.5, Lh, wr + 0.5, '#000000', D(0.08, 0.3)),
        # well: darker inset capsule, shadow on its upper/left lip, light lower lip
        RR(1, 0.5, S - 1, Lh - 0.5, wr, vgrad(0.5, Lh - 0.5, [(0, '#000000', D(0.34, 0.8)), (0.5, '#000000', D(0.22, 0.65)),
                                                              (1, '#000000', D(0.12, 0.5))])),
        RR(1.5, 1.5, S - 1.5, Lh - 0.5, wr - 0.5, '#ffffff', D(0.9, 0.10)),
        RR(1.5, 1.5, S - 1.5, Lh - 1.2, wr - 0.5, hgrad(1.5, S - 1.5, [(0, D('#c4c4c4', '#0d0e10'), 1), (0.35, D('#dedede', '#141517'), 1),
                                                                       (1, D('#f1f1f1', '#1a1b1e'), 1)])),
        Layer(rrect_poly(1.5, 1.5, S - 1.5, Lh - 1.2, wr - 0.5),
              hgrad(1.5, S / 2, [(0, '#000000', D(0.12, 0.3)), (1, '#000000', 0)])),
    ]
    kv.frame('scrollbargroove-normal', S, Lh, (side, cap, side, cap), groove)
    scroll_arrows(kv, S)
    # thumb (vertical blue gel capsule) with a tiled ripple interior
    T = 24                       # ripple period = interior.y.patternsize
    Lt = 2 * cap + T
    box = (2, 1.5, S - 2, Lt - 1.5)
    rr = (box[2] - box[0]) / 2

    def thumb(pressed=False, hover=False):
        L = G.blue(*box, rr, axis='h', drop=0, pressed=pressed, gloss=0)
        # ripples only on the straight (tiled) part, inside the rim
        L += _thumb_waves(box[0] + 1, box[2] - 1, cap, T, 12)
        if hover:
            L += [RR(box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1, rr - 1, '#ffffff', 0.12)]
        # specular gloss on the left half, on top of the ripples
        mid = box[0] + (box[2] - box[0]) * 0.5
        L += [Layer(rrect_poly(box[0] + 1.5, box[1] + 2, mid, box[3] - 2, (rr - 1.5, rr * 0.4, rr * 0.4, rr - 1.5)),
                    hgrad(box[0] + 1.5, mid, P.GLOSS), 0.55)]
        return L
    for st, L in (('normal', thumb()), ('focused', thumb(hover=True)), ('pressed', thumb(pressed=True))):
        kv.frame('scrollbarslider-' + st, S, Lt, (side, cap, side, cap), L)
    kv.frame('scrollbarslider-disabled', S, Lt, (side, cap, side, cap),
             faded(G.white(*box, rr, axis='h', drop=0), 0.6))


def progress(kv: KV):
    # groove: a 12px capsule made purely of 6px frames (no frame expansion, see PROGRESS.md)
    W, H = 60, PROGRESS_H
    f = H // 2
    r = H / 2
    groove = [
        RR(0, 0, W, H, r, vgrad(0, H, [(0, D('#9f9f9f', '#060607'), 1), (1, D('#c6c6c6', '#34363a'), 1)])),
        RR(1, 1, W - 1, H - 1, r - 1, vgrad(1, H - 1, [(0, D('#d6d6d6', '#121315'), 1), (0.5, D('#ececec', '#1a1b1e'), 1),
                                                       (1, D('#fafafa', '#212326'), 1)])),
    ]
    kv.frame('progress-normal', W, H, (f, f, f, f), groove)
    kv.frame('progress-disabled', W, H, (f, f, f, f), faded(groove, 0.6))
    # contents: capsule end caps (left/right pieces, full height) + striped candy interior tile
    pat = G.blue(0, 0, W, H, r, drop=0, gloss=0.5)
    for st, k in (('normal', 1), ('focused', 1), ('disabled', 0.5)):
        ox, oy = kv._slot(W, H)
        kv.svg.frame('progress-pattern-%s-' % st, ox, oy, W, H, (f, 0, f, 0), faded(pat, k), pieces=['left', 'right'])
    T = 14
    stripes = [RR(-1, 0, T + 1, H, 0, P.BLUE_RIM)]
    stripes.append(RR(-1, 1, T + 1, H - 1, 0, vgrad(1, H - 1, P.BLUE_GEL)))
    for j in (-1, 0, 1):
        x = j * T
        stripes.append(Layer([(x + 2, H - 1), (x + 8, H - 1), (x + 8 + H * 0.75, 1), (x + 2 + H * 0.75, 1)], '#ffffff', D(0.28, 0.13)))
    stripes.append(RR(-1, 1, T + 1, H * 0.5, 0, vgrad(1, H * 0.5, [(0, '#ffffff', D(0.5, 0.30)), (1, '#ffffff', D(0.12, 0.07))])))
    for st, k in (('normal', 1), ('focused', 1), ('disabled', 0.5)):
        ox, oy = kv._slot(T, H)
        kv.svg.frame('progress-pattern-%s-' % st, ox, oy, T, H, (0, 0, 0, 0), faded(stripes, k), pieces=['center'],
                     center='progress-pattern-' + st)


def sliders(kv: KV):
    # groove: vertical, slider_width=6
    S, Lh = 6, 40
    r = S / 2
    groove = [RR(0, 0, S, Lh, r, hgrad(0, S, [(0, D('#8d8d8d', '#060607'), 1), (1, D('#b5b5b5', '#34363a'), 1)])),
              RR(1, 1, S - 1, Lh - 1, r - 1, hgrad(1, S - 1, [(0, D('#c4c4c4', '#111214'), 1), (1, D('#ededed', '#202225'), 1)]))]
    filled = [RR(0, 0, S, Lh, r, P.BLUE_RIM),
              RR(1, 1, S - 1, Lh - 1, r - 1, hgrad(1, S - 1, [(0, D('#5d9ff0', '#2459b4'), 1), (1, D('#b2e2ff', '#4a8ae0'), 1)]))]
    kv.frame('slider-normal', S, Lh, (3, 3, 3, 3), groove)
    kv.frame('slider-toggled', S, Lh, (3, 3, 3, 3), filled)
    kv.frame('slider-disabled', S, Lh, (3, 3, 3, 3), faded(groove, 0.6))
    # knob 18x18
    K = 18
    c = K / 2
    from plasma_style import knob_layers
    for st in ('normal', 'focused', 'pressed', 'disabled'):
        L = knob_layers(c, c - 0.5, c - 1, pressed=(st == 'pressed'))
        if st == 'focused':
            L += [Layer(ellipse_poly(c, c - 0.5, c - 2, c - 2), '#ffffff', 0.15)]
        if st == 'disabled':
            L = faded(L, 0.5)
        kv.element('slidercursor-' + st, K, K, L)


def menus(kv: KV):
    W, H, f = 48, 48, 4
    d = 7  # menu_shadow_depth
    r = 5
    # DarkLiger menus are translucent smoked glass (Kvantum blurs behind them: popup_blurring)
    MENU = D([(0, '#ffffff', 0.97), (1, '#f8f8f8', 0.97)], [(0, '#2e3034', 0.93), (1, '#232528', 0.93)])
    body = [RR(0, 0, W, H, r, P.POPUP_BORDER[0], D(0.22, 0.75)),
            RR(1, 1, W - 1, H - 1, r - 1, vgrad(1, H - 1, MENU))]
    if P.DARK:
        body.append(RING(1, 1, W - 1, H - 1, r - 1, 1, '#ffffff', 0.08))
    kv.frame('menu-normal', W, H, (f, f, f, f), body)
    # menu-shadow-*: shadow + menu frame pieces of depth d+f
    from svgkit import shadow_image, Raster
    SW, SH = W + 2 * d, H + 2 * d
    img = shadow_image(SW, SH, (d, d, SW - d, SH - d), r, blur=d * 1.2, dy=2, alpha=0.38)
    shadow_layers = [Raster(img, 2)] + [Layer([(x + d, y + d) for x, y in L.shape], L.paint, L.opacity,
                                              [(x + d, y + d) for x, y in L.hole] if L.hole else None) for L in body]
    # gradients inside body are in body coords; re-create them offset
    shadow_layers[2] = RR(d + 1, d + 1, SW - d - 1, SH - d - 1, r - 1, vgrad(d + 1, SH - d - 1, MENU))
    ox, oy = kv._slot(SW, SH)
    kv.svg.frame('menu-shadow-', ox, oy, SW, SH, (d + f, d + f, d + f, d + f), shadow_layers, pieces=PIECES)
    for side in ('top', 'bottom', 'left', 'right'):
        kv.hint('menu-shadow-hint-' + side, d if side in ('left', 'right') else 1, d if side in ('top', 'bottom') else 1)
    # menu item highlight = Snow Leopard blue
    MW, MH = 40, 22
    sel = [RR(0, 0, MW, MH, 0, vgrad(0, MH, D([(0, '#6d9ef0', 1), (1, '#2f69dc', 1)], P.SELECT_GEL))),
           Layer(rrect_poly(0, 0, MW, 1, 0), D('#5a8be6', P.SELECT_TOPLINE))]
    kv.frame('menuitem-focused', MW, MH, (2, 2, 2, 2), sel)
    kv.frame('menuitem-pressed', MW, MH, (2, 2, 2, 2), sel)
    kv.frame('menuitem-toggled', MW, MH, (2, 2, 2, 2), sel)
    kv.frame('menuitem-normal', MW, MH, (2, 2, 2, 2), [RR(0, 0, MW, MH, 0, '#ffffff', 0)])
    # menu separator: thin Aqua grey line (Kvantum uses '<indicator>-separator')
    kv.element('marrow-separator', 40, 7, [RR(0, 3, 40, 4, 0, D('#d6d6d6', '#121315'))] +
               ([RR(0, 4, 40, 5, 0, '#ffffff', 0.06)] if P.DARK else []))
    # submenu arrows on menus
    for st, col in (('normal', D('#262626', '#cfd0d3')), ('focused', '#ffffff'), ('pressed', '#ffffff'), ('disabled', D('#a0a0a0', '#5c5f64'))):
        kv.element('marrow-right-' + st, 10, 10, [Layer(tri(5, 5, 8, 'right'), col)])
        kv.element('marrow-left-' + st, 10, 10, [Layer(tri(5, 5, 8, 'left'), col)])
    # menu bar (apps without global menu): Snow Leopard bar
    BW, BH = 40, 24
    bar = [RR(0, 0, BW, BH, 0, vgrad(0, BH, P.MENUBAR)), Layer(rrect_poly(0, BH - 1, BW, BH, 0), D('#b3b3b3', '#000000'))]
    kv.frame('menubar-normal', BW, BH, (1, 1, 1, 1), bar)
    kv.frame('menubaritem-pressed', MW, MH, (2, 2, 2, 2), sel)
    kv.frame('menubaritem-toggled', MW, MH, (2, 2, 2, 2), sel)
    kv.frame('menubaritem-focused', MW, MH, (2, 2, 2, 2), [RR(0, 0, MW, MH, 0, D('#000000', '#ffffff'), D(0.06, 0.08))])


def tooltip(kv: KV):
    W, H, f, d, r = 40, 32, 3, 6, 3
    TIP = [(0, D('#ffffd8', '#36383d'), 1), (1, P.TOOLTIP_BG, 1)]
    body = [RR(0, 0, W, H, r, P.TOOLTIP_BORDER), RR(1, 1, W - 1, H - 1, r - 1, vgrad(1, H - 1, TIP))]
    if P.DARK:
        body.append(RING(1, 1, W - 1, H - 1, r - 1, 1, '#ffffff', 0.08))
    kv.frame('tooltip-normal', W, H, (f, f, f, f), body)
    from svgkit import shadow_image, Raster
    SW, SH = W + 2 * d, H + 2 * d
    img = shadow_image(SW, SH, (d, d, SW - d, SH - d), r, blur=d, dy=2, alpha=0.32)
    L = [Raster(img, 2), RR(d, d, SW - d, SH - d, r, P.TOOLTIP_BORDER),
         RR(d + 1, d + 1, SW - d - 1, SH - d - 1, r - 1, vgrad(d + 1, SH - d - 1, TIP))]
    if P.DARK:
        L.append(RING(d + 1, d + 1, SW - d - 1, SH - d - 1, r - 1, 1, '#ffffff', 0.08))
    ox, oy = kv._slot(SW, SH)
    kv.svg.frame('tooltip-shadow-', ox, oy, SW, SH, (d + f, d + f, d + f, d + f), L, pieces=PIECES)
    for side in ('top', 'bottom', 'left', 'right'):
        kv.hint('tooltip-shadow-hint-' + side, d if side in ('left', 'right') else 1, d if side in ('top', 'bottom') else 1)


def itemview(kv: KV):
    W, H, f = 40, 24, 2
    sel = [RR(0, 0, W, H, 2, vgrad(0, H, P.SELECT_GEL)), Layer(rrect_poly(0, 0, W, 1, (2, 2, 0, 0)), P.SELECT_TOPLINE)]
    sel_in = [RR(0, 0, W, H, 2, vgrad(0, H, [(0, D('#d8d8d8', '#4a4d52'), 1), (1, D('#bcbcbc', '#3c3e43'), 1)])),
              Layer(rrect_poly(0, 0, W, 1, (2, 2, 0, 0)), D('#b4b4b4', '#5a5d62'))]
    kv.frame('itemview-pressed', W, H, (f, f, f, f), sel)
    kv.frame('itemview-toggled', W, H, (f, f, f, f), sel)
    kv.frame('itemview-toggled-inactive', W, H, (f, f, f, f), sel_in)
    kv.frame('itemview-pressed-inactive', W, H, (f, f, f, f), sel_in)
    kv.frame('itemview-focused', W, H, (f, f, f, f), [RR(0, 0, W, H, 2, P.SELECTION, 0.14)])


def header(kv: KV):
    W, H, f = 40, 22, 2
    hn = [RR(0, 0, W, H, 0, vgrad(0, H, D([(0, '#ffffff', 1), (0.5, '#e7e7e7', 1), (0.5, '#d3d3d3', 1), (1, '#e8e8e8', 1)],
                                          [(0, '#3a3d42', 1), (0.5, '#2f3135', 1), (0.5, '#25272a', 1), (1, '#2a2c30', 1)]))),
          Layer(rrect_poly(0, 0, W, 1, 0), D('#ffffff', '#4a4d53')),
          Layer(rrect_poly(0, H - 1, W, H, 0), D('#9c9c9c', '#060607')), Layer(rrect_poly(W - 1, 2, W, H - 2, 0), D('#b3b3b3', '#141517'))]
    ht = [RR(0, 0, W, H, 0, vgrad(0, H, D([(0, '#d6e8fc', 1), (0.5, '#a9cbf5', 1), (0.5, '#86b4ee', 1), (1, '#c3e2fd', 1)],
                                          [(0, '#4f83d2', 1), (0.5, '#3168bd', 1), (0.5, '#1f4f9e', 1), (1, '#2a5fb2', 1)]))),
          Layer(rrect_poly(0, 0, W, 1, 0), D('#e8f2fe', '#79a6e6')),
          Layer(rrect_poly(0, H - 1, W, H, 0), D('#6f92c6', P.BLUE_RIM)), Layer(rrect_poly(W - 1, 0, W, H, 0), D('#7f9ecc', P.BLUE_RIM_BOTTOM))]
    kv.frame('header-normal', W, H, (f, f, f, f), hn)
    kv.frame('header-focused', W, H, (f, f, f, f), hn + [RR(0, 0, W, H - 1, 0, '#ffffff', D(0.25, 0.05))])
    kv.frame('header-pressed', W, H, (f, f, f, f), ht)
    kv.frame('header-toggled', W, H, (f, f, f, f), ht)


def tabs(kv: KV):
    # Aqua tabs = segmented control: white gel, selected = blue gel
    W, H, f = 56, 26, 5
    box = (0, 1, W, H - 2)
    r = 4.5
    looks = {
        'normal': G.white(*box, r),
        'focused': G.white(*box, r) + [RR(1, 2, W - 1, H - 3, r - 1, '#ffffff', D(0.25, 0.06))],
        'toggled': G.blue(*box, r),
        'pressed': G.blue(*box, r, pressed=True),
        'disabled': faded(G.white(*box, r), 0.55),
    }
    for st, L in looks.items():
        kv.frame('tab-' + st, W, H, (f, f, f, f), L)
    kv.frame('tab-toggled-inactive', W, H, (f, f, f, f), graphite(*box, r))
    # tab pane: Aqua recessed box
    TW, TH, tf = 48, 48, 5
    pane = [RR(0, 0, TW, TH, 5, '#000000', D(0.2, 0.7)), RR(1, 1, TW - 1, TH - 1, 4, D('#e3e3e3', '#212326')),
            RR(1, 1, TW - 1, 3, 1, '#000000', D(0.04, 0.2))]
    kv.frame('tabframe-normal', TW, TH, (tf, tf, tf, tf), pane)
    # close button: grey disc with x (Safari-style)
    C = 14
    for st, base, a in (('normal', '#a6a6a6', 0.0), ('focused', D('#8c8c8c', '#5a5d62'), 1), ('pressed', D('#6e6e6e', '#76797e'), 1),
                        ('disabled', '#c8c8c8', 0.0), ('toggled', '#ffffff', 0.0)):
        L = [Layer(ellipse_poly(C / 2, C / 2, C / 2 - 0.5, C / 2 - 0.5), base, a)]
        glyph_col = '#ffffff' if a else D('#6a6a6a', '#a3a6ab')
        from aurorae import _rect_poly
        L += [Layer(_rect_poly(C / 2, C / 2, 7, 1.5, 45), glyph_col, 0.95), Layer(_rect_poly(C / 2, C / 2, 7, 1.5, -45), glyph_col, 0.95)]
        kv.element('tab-close-' + st, C, C, L)


def frames(kv: KV):
    W = H = 32
    common = [RING(0, 0, W, H, 0, 1, D('#b2b2b2', '#0b0c0d'))]
    kv.frame('common-normal', W, H, (1, 1, 1, 1), common, interior=False)
    group = [RR(0, 0, W, H, 5, '#000000', D(0.16, 0.6)), RR(1, 1, W - 1, H - 1, 4, D('#e4e4e4', '#2b2d31'))]
    if P.DARK:
        group.append(RING(1, 1, W - 1, H - 1, 4, 1, vgrad(1, H - 1, [(0, '#ffffff', 0.07), (1, '#ffffff', 0.02)])))
    kv.frame('group-normal', W, H, (5, 5, 5, 5), group)
    focus = [RING(0, 0, W, H, 3, 2, P.FOCUS_RING, 0.75)]
    kv.frame('focus', W, H, (2, 2, 2, 2), focus, interior=False)
    # dock widget title + generic titlebar
    tb = [RR(0, 0, W, 20, 0, vgrad(0, 20, P.TITLE_ACTIVE)), Layer(rrect_poly(0, 19, W, 20, 0), P.TITLE_ACTIVE_SEPARATOR)]
    kv.frame('titlebar-normal', W, 20, (1, 1, 1, 1), tb)
    kv.frame('titlebar-focused', W, 20, (1, 1, 1, 1), tb)
    kv.frame('dock-normal', W, 20, (1, 1, 1, 1), [RR(0, 0, W, 20, 0, vgrad(0, 20, P.TITLE_INACTIVE)),
                                                   Layer(rrect_poly(0, 19, W, 20, 0), P.TITLE_INACTIVE_SEPARATOR)])
    # toolbar: subtle, blends with window
    kv.frame('toolbar-normal', W, 36, (0, 0, 0, 1), [RR(0, 0, W, 36, 0, vgrad(0, 36, [(0, D('#ececec', '#26282b'), 1), (1, D('#e2e2e2', '#222427'), 1)])),
                                                     Layer(rrect_poly(0, 35, W, 36, 0), D('#bcbcbc', '#0b0c0d'))])
    # splitter dimple & size grip
    kv.element('splitter-grip-normal', 8, 8, [Layer(ellipse_poly(4, 4, 2.5, 2.5), D('#8a8a8a', '#0e0f11')),
                                              Layer(ellipse_poly(4, 3.6, 1.6, 1.4), '#ffffff', D(0.7, 0.18))])
    kv.element('splitter-grip-focused', 8, 8, [Layer(ellipse_poly(4, 4, 2.5, 2.5), '#5f8fd6')])
    kv.element('splitter-grip-pressed', 8, 8, [Layer(ellipse_poly(4, 4, 2.5, 2.5), '#3d6fbf')])
    grip = []
    for i in range(3):
        o = 4 * i
        grip.append(Layer([(14 - o - 1.2, 14), (14, 14 - o - 1.2), (14, 14 - o), (14 - o, 14)], D('#7d7d7d', '#6a6d72'), 0.8))
    kv.element('sizegrip-normal', 14, 14, grip)


GENERAL = """[%General]
author={author}
comment={comment}
x11drag=menubar_and_primary_toolbar
alt_mnemonic=true
left_tabs=false
center_normal_tabs=true
center_doc_tabs=false
joined_inactive_tabs=false
attach_active_tab=false
embedded_tabs=false
no_active_tab_separator=false
group_toolbar_buttons=false
spread_progressbar=true
progressbar_thickness=12
composite=true
menu_shadow_depth=7
tooltip_shadow_depth=6
menu_blur_radius=4
tooltip_blur_radius=3
splitter_width=8
scroll_width=15
scroll_min_extent=36
scroll_arrows=true
transient_scrollbar=false
scrollbar_in_view=true
slider_width=6
slider_handle_width=18
slider_handle_length=18
check_size=16
textless_progressbar=false
menubar_mouse_tracking=true
toolbutton_style=1
spread_menuitems=true
spread_header=true
combo_as_lineedit=true
combo_menu=true
combo_focus_rect=false
square_combo_button=false
inline_spin_indicators=true
vertical_spin_indicators=true
spin_button_width=16
animate_states=true
translucent_windows=false
blurring=false
popup_blurring=true
layout_spacing=6
layout_margin=9
small_icon_size=16
large_icon_size=32
button_icon_size=16
toolbar_icon_size=22
toolbar_interior_spacing=2
toolbar_item_spacing=1
submenu_overlap=0
menu_separator_height=7
tooltip_delay=-1
respect_DE=true
dialog_button_layout=0
no_inactiveness=false
groupbox_top_label=true
tree_branch_line=false
fill_rubberband=false
bold_active_tab=false
button_contents_shift=false

[GeneralColors]
window.color={window}
base.color={base}
alt.base.color={alt}
button.color={button}
light.color={light}
mid.light.color={midlight}
dark.color={dark}
mid.color={mid}
shadow.color={shadow}
highlight.color={sel}
inactive.highlight.color={inactsel}
tooltip.base.color={tip}
text.color={text}
window.text.color={text}
button.text.color={text}
disabled.text.color={disabled}
tooltip.text.color={tiptext}
highlight.text.color=#ffffff
inactive.highlight.text.color={text}
link.color={link}
link.visited.color={visited}
progress.indicator.text.color={text}
progress.inactive.indicator.text.color={text}

[Hacks]
transparent_dolphin_view=false
blur_konsole=false
transparent_ktitle_label=true
transparent_menutitle=true
respect_darkness=true
kcapacitybar_as_progressbar=true
force_size_grip=false
iconless_pushbutton=false
iconless_menu=false
disabled_icon_opacity=60
normal_default_pushbutton=true
single_top_toolbar=true
tint_on_mouseover=0
no_selection_tint=true
middle_click_scroll=false
centered_forms=false
kinetic_scrolling=false
noninteger_translucency=false

[PanelButtonCommand]
frame=true
frame.element=button
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6
frame.expansion=34
focusFrame=true
interior=true
interior.element=button
indicator.size=10
indicator.element=arrow
text.margin=0
text.iconspacing=4
text.margin.top=1
text.margin.bottom=1
text.margin.left=10
text.margin.right=10
text.shadow=false
text.normal.color={text}
text.focus.color={text}
text.press.color={text}
text.toggle.color=#ffffff
text.disabled.color={disabled}
min_width=+0.6font
min_height=+0.3font

[PanelButtonTool]
inherits=PanelButtonCommand
frame.element=tbutton
interior.element=tbutton
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5
frame.expansion=0
focusFrame=false
text.margin.left=4
text.margin.right=4
text.margin.top=1
text.margin.bottom=1
text.toggle.color={text}
indicator.element=arrow
indicator.size=8

[ToolbarButton]
inherits=PanelButtonTool
text.normal.color={text}
text.focus.color={text}
text.press.color={text}
text.toggle.color=#ffffff

[DropDownButton]
inherits=PanelButtonCommand
indicator.element=arrow-down
frame.expansion=0

[IndicatorArrow]
indicator.element=arrow
indicator.size=9

[IndicatorSpinBox]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=spin
interior.element=spin
frame.top=4
frame.bottom=4
frame.left=4
frame.right=4
frame.expansion=0
focusFrame=false
indicator.element=sarrow
indicator.size=8

[ComboBox]
inherits=PanelButtonCommand
indicator.element=carrow
indicator.size=18
text.margin.right=4

[RadioButton]
inherits=PanelButtonCommand
frame=false
interior.element=radio
focusFrame=false
text.margin.left=3
text.margin.right=3
text.toggle.color={text}

[CheckBox]
inherits=PanelButtonCommand
frame=false
interior.element=checkbox
focusFrame=false
text.margin.left=3
text.margin.right=3
text.toggle.color={text}

[Focus]
inherits=PanelButtonCommand
frame=true
interior=false
frame.element=focus
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
frame.expansion=0

[GenericFrame]
inherits=PanelButtonCommand
frame=true
interior=false
frame.element=common
interior.element=common
frame.top=1
frame.bottom=1
frame.left=1
frame.right=1
frame.expansion=0
focusFrame=false

[LineEdit]
inherits=PanelButtonCommand
frame.element=lineedit
interior.element=lineedit
frame.top=4
frame.bottom=4
frame.left=4
frame.right=4
frame.expansion=0
focusFrame=false
text.margin.left=2
text.margin.right=2

[ToolbarLineEdit]
inherits=LineEdit
frame.element=tlineedit
interior.element=tlineedit

[ToolboxTab]
inherits=PanelButtonCommand
frame.expansion=0

[Tab]
inherits=PanelButtonCommand
frame.element=tab
interior.element=tab
indicator.element=tab
indicator.size=14
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5
frame.expansion=0
focusFrame=false
text.margin.left=10
text.margin.right=10
text.margin.top=1
text.margin.bottom=1
text.toggle.color={text}
text.focus.color={text}

[TabFrame]
inherits=PanelButtonCommand
frame.element=tabframe
interior.element=tabframe
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5
frame.expansion=0
focusFrame=false

[TabBarFrame]
inherits=GenericFrame
frame=false
interior=false

[TreeExpander]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=arrow
indicator.size=9

[HeaderSection]
inherits=PanelButtonCommand
frame.element=header
interior.element=header
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
frame.expansion=0
focusFrame=false
text.margin.left=4
text.margin.right=4
text.toggle.color={text}
text.press.color={text}

[SizeGrip]
indicator.element=sizegrip

[Toolbar]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=toolbar
interior.element=toolbar
frame.top=0
frame.bottom=1
frame.left=0
frame.right=0
frame.expansion=0
focusFrame=false
indicator.element=toolbar
indicator.size=5
text.margin=0

[Slider]
inherits=PanelButtonCommand
frame.element=slider
interior.element=slider
frame.top=3
frame.bottom=3
frame.left=3
frame.right=3
frame.expansion=0
focusFrame=false

[SliderCursor]
inherits=PanelButtonCommand
frame=false
interior=true
interior.element=slidercursor

[Progressbar]
inherits=PanelButtonCommand
frame.element=progress
interior.element=progress
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6
frame.expansion=0
focusFrame=false
text.margin=0
text.bold=false
text.normal.color={text}
text.focus.color={text}
text.press.color={text}
text.toggle.color={text}

[ProgressbarContents]
inherits=PanelButtonCommand
frame=true
frame.element=progress-pattern
interior=true
interior.element=progress-pattern
interior.x.patternsize=14
frame.top=0
frame.bottom=0
frame.left=6
frame.right=6
frame.expansion=0
focusFrame=false

[ItemView]
inherits=PanelButtonCommand
frame.element=itemview
interior.element=itemview
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
frame.expansion=0
focusFrame=false
text.margin=0
text.margin.left=4
text.margin.right=4
text.margin.top=2
text.margin.bottom=2
text.normal.color={text}
text.focus.color={text}
text.press.color=#ffffff
text.toggle.color=#ffffff
text.toggle.inactive.color={text}
text.press.inactive.color={text}

[Splitter]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=splitter-grip
indicator.size=8

[Scrollbar]
inherits=PanelButtonCommand
indicator.element=scrollarrow
indicator.size=15

[ScrollbarSlider]
inherits=PanelButtonCommand
frame.element=scrollbarslider
interior.element=scrollbarslider
interior.y.patternsize=24
frame.top=8
frame.bottom=8
frame.left=2
frame.right=2
frame.expansion=0
focusFrame=false
indicator.size=0

[ScrollbarGroove]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=scrollbargroove
interior.element=scrollbargroove
frame.top=8
frame.bottom=8
frame.left=2
frame.right=2
frame.expansion=0
focusFrame=false

[MenuItem]
inherits=PanelButtonCommand
frame=true
frame.element=menuitem
interior.element=menuitem
indicator.element=marrow
indicator.size=8
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
frame.expansion=0
focusFrame=false
text.margin.top=2
text.margin.bottom=2
text.margin.left=6
text.margin.right=6
text.normal.color={text}
text.focus.color=#ffffff
text.press.color=#ffffff
text.toggle.color=#ffffff
min_height=+0.25font

[MenuBar]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=menubar
interior.element=menubar
frame.top=0
frame.bottom=1
frame.left=0
frame.right=0
frame.expansion=0
focusFrame=false

[MenuBarItem]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=menubaritem
interior.element=menubaritem
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
frame.expansion=0
focusFrame=false
text.margin.left=6
text.margin.right=6
text.margin.top=1
text.margin.bottom=1
text.normal.color={text}
text.focus.color={text}
text.press.color=#ffffff
text.toggle.color=#ffffff

[TitleBar]
inherits=PanelButtonCommand
frame=false
interior=true
interior.element=titlebar
indicator.element=mdi
indicator.size=12
frame.expansion=0
text.bold=false
text.normal.color={titletext}
text.focus.color={titletext}

[Menu]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=menu
interior.element=menu
frame.top=4
frame.bottom=4
frame.left=4
frame.right=4
frame.expansion=0
focusFrame=false
text.normal.color={text}

[GroupBox]
inherits=GenericFrame
frame=true
interior=true
frame.element=group
interior.element=group
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5
text.margin=0
text.bold=false

[ToolTip]
inherits=GenericFrame
frame=true
interior=true
frame.element=tooltip
interior.element=tooltip
frame.top=3
frame.bottom=3
frame.left=3
frame.right=3
text.margin=2
text.normal.color={tiptext}

[StatusBar]
inherits=GenericFrame
frame=false
interior=false

[Window]
interior=false
frame=false

[Dialog]
inherits=Window

[Dock]
inherits=PanelButtonCommand
frame=false
interior=false

[DockTitle]
inherits=PanelButtonCommand
frame=false
interior=true
interior.element=dock
frame.expansion=0
text.bold=false
text.margin.top=2
text.margin.bottom=2
text.margin.left=4
text.margin.right=4
"""


def build(out):
    kv = KV()
    buttons(kv)
    toolbuttons(kv)
    lineedit(kv)
    spin(kv)
    checks(kv)
    arrows(kv)
    scrollbars(kv)
    progress(kv)
    sliders(kv)
    menus(kv)
    tooltip(kv)
    itemview(kv)
    header(kv)
    tabs(kv)
    frames(kv)
    root = os.path.join(out, 'kvantum', KV_ID)
    os.makedirs(root, exist_ok=True)
    kv.svg.save(os.path.join(root, KV_ID + '.svg'), compress=False)
    cfg = GENERAL.format(author=P.AUTHOR, window=P.WINDOW_BG, alt=P.ALT_ROW, sel=P.SELECTION, tip=P.TOOLTIP_BG,
                         text=P.TEXT, link=P.LINK, visited=P.VISITED, titletext=P.TITLE_TEXT,
                         comment=P.DESCRIPTION.replace(': ', ' — '), base=P.VIEW_BG,
                         button=D('#f4f4f4', '#35383c'), light=D('#ffffff', '#4a4d52'), midlight=D('#f2f2f2', '#3a3c41'),
                         dark=D('#9a9a9a', '#101113'), mid=D('#c8c8c8', '#1c1d20'), shadow=D('#00000040', '#000000a0'),
                         inactsel=D('#c8c8c8', P.SELECTION_INACTIVE), disabled=D('#00000066', '#ffffff55'),
                         tiptext=D('#1d1d1d', P.TEXT))
    with open(os.path.join(root, KV_ID + '.kvconfig'), 'w') as fh:
        fh.write(cfg)
    return root
