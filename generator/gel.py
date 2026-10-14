"""Reusable Aqua "gel" recipes built on svgkit layers."""
from svgkit import RR, RING, Layer, Linear, rrect_poly
import palette as P


def _lin(axis, a0, a1, stops):
    return Linear(0, a0, 0, a1, stops) if axis == 'v' else Linear(a0, 0, a1, 0, stops)


def gel(x0, y0, x1, y1, r, stops, rim_top, rim_bottom, axis='v', gloss=0.55, drop=0.16, rim_opacity=1.0):
    """
    Lickable Aqua gel capsule/rounded-rect.
    axis='v': gradient runs top->bottom (horizontal controls).
    axis='h': gradient runs left->right (vertical controls, e.g. scroller thumb).
    A 1px drop shadow is drawn *below* (or right of) the box, so leave room for it.
    """
    L = []
    if drop:
        if axis == 'v':
            L.append(RR(x0 + 0.5, y0 + 1, x1 - 0.5, y1 + 1, r, '#000000', drop))
        else:
            L.append(RR(x0, y0 + 1, x1, y1 + 1, r, '#000000', drop))
    a0, a1 = (y0, y1) if axis == 'v' else (x0, x1)
    L.append(RR(x0, y0, x1, y1, r, _lin(axis, a0, a1, [(0, rim_top, 1), (1, rim_bottom, 1)]), rim_opacity))
    ri = r - 1 if not isinstance(r, tuple) else tuple(max(0, v - 1) for v in r)
    L.append(RR(x0 + 1, y0 + 1, x1 - 1, y1 - 1, ri, _lin(axis, a0 + 1, a1 - 1, stops)))
    if P.GLASS_EDGE:
        # glass: thin light edge just inside the rim, brightest on the lit side
        c, a = P.GLASS_EDGE
        L.append(RING(x0 + 1, y0 + 1, x1 - 1, y1 - 1, ri, 1,
                      _lin(axis, a0 + 1, a1 - 1, [(0, c, a * 1.8), (0.5, c, a * 0.4), (1, c, a * 0.9)])))
    if gloss:
        if axis == 'v':
            mid = y0 + (y1 - y0) * 0.5
            gr = max(1.0, (r if not isinstance(r, tuple) else max(r)) - 1.5)
            L.append(Layer(rrect_poly(x0 + 2, y0 + 1.5, x1 - 2, mid, (gr, gr, gr * 0.5, gr * 0.5)),
                           Linear(0, y0 + 1.5, 0, mid, P.GLOSS), gloss))
        else:
            mid = x0 + (x1 - x0) * 0.5
            gr = max(1.0, (r if not isinstance(r, tuple) else max(r)) - 1.5)
            L.append(Layer(rrect_poly(x0 + 1.5, y0 + 2, mid, y1 - 2, (gr, gr * 0.5, gr * 0.5, gr)),
                           Linear(x0 + 1.5, 0, mid, 0, P.GLOSS), gloss))
    return L


def blue(x0, y0, x1, y1, r, axis='v', pressed=False, **kw):
    if pressed:
        return gel(x0, y0, x1, y1, r, P.BLUE_GEL_PRESSED, P.BLUE_RIM_PRESSED, P.BLUE_RIM_PRESSED, axis, **kw)
    return gel(x0, y0, x1, y1, r, P.BLUE_GEL, P.BLUE_RIM, P.BLUE_RIM_BOTTOM, axis, **kw)


def white(x0, y0, x1, y1, r, axis='v', **kw):
    return gel(x0, y0, x1, y1, r, P.WHITE_GEL, P.WHITE_RIM_TOP, P.WHITE_RIM_BOTTOM, axis, **kw)


def glow_ring(x0, y0, x1, y1, r, color, width=3, opacity=0.9):
    """Soft Aqua focus glow drawn *outside* the box (x0..x1 is the control edge)."""
    L = []
    steps = [(width, 0.25), (width * 0.66, 0.45), (width * 0.33, 0.8)]
    for w, a in steps:
        rr = r + w if not isinstance(r, tuple) else tuple(v + w for v in r)
        L.append(RING(x0 - w, y0 - w, x1 + w, y1 + w, rr, w, color, a * opacity))
    return L
