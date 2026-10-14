"""
svgkit — tiny toolkit to procedurally build Plasma / Aurorae / Kvantum SVGs.

Key idea: a "frame" (9-slice) is described ONCE as a stack of layers drawn on a
full-size template (W x H).  The toolkit then cuts every layer into the nine
pieces (topleft, top, ..., center) by real polygon clipping, so each named
element only contains its own geometry.  No clipPath/mask is used, because
QtSvg's boundsOnElement() ignores clipping and Plasma relies on element bounds.

Coordinates are in SVG user units == logical pixels.
"""
from __future__ import annotations

import base64
import gzip
import io
import math
import os
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# colours
# --------------------------------------------------------------------------

def hexrgb(c: str):
    c = c.lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    """Linear mix of two hex colours, t=0 -> a, t=1 -> b."""
    ra, ga, ba = hexrgb(a)
    rb, gb, bb = hexrgb(b)
    return '#%02x%02x%02x' % (round(ra + (rb - ra) * t), round(ga + (gb - ga) * t), round(ba + (bb - ba) * t))


def shade(c: str, f: float) -> str:
    """f>1 lightens towards white, f<1 darkens towards black."""
    if f >= 1:
        return mix(c, '#ffffff', min(1.0, f - 1))
    return mix(c, '#000000', 1 - f)


# --------------------------------------------------------------------------
# paints
# --------------------------------------------------------------------------

@dataclass
class Linear:
    """Linear gradient in frame-local user space."""
    x1: float
    y1: float
    x2: float
    y2: float
    stops: list  # [(offset, '#rrggbb', opacity)]


@dataclass
class Radial:
    cx: float
    cy: float
    r: float
    stops: list
    fx: float | None = None
    fy: float | None = None
    sx: float = 1.0  # horizontal stretch (ellipse) around cx,cy
    sy: float = 1.0


def vgrad(y0, y1, stops):
    return Linear(0, y0, 0, y1, stops)


def hgrad(x0, x1, stops):
    return Linear(x0, 0, x1, 0, stops)


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def rrect_poly(x0, y0, x1, y1, r):
    """Rounded rectangle polygon (clockwise).  r: number or (tl,tr,br,bl)."""
    if not isinstance(r, (tuple, list)):
        r = (r, r, r, r)
    w, h = x1 - x0, y1 - y0
    lim = min(w, h) / 2
    tl, tr, br, bl = (max(0.0, min(v, lim)) for v in r)
    pts = []

    def arc(cx, cy, rad, a0, a1):
        if rad <= 0:
            pts.append((cx, cy))
            return
        n = max(4, int(rad * 2.2))
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))

    arc(x0 + tl, y0 + tl, tl, 180, 270)
    arc(x1 - tr, y0 + tr, tr, 270, 360)
    arc(x1 - br, y1 - br, br, 0, 90)
    arc(x0 + bl, y1 - bl, bl, 90, 180)
    return pts


def ellipse_poly(cx, cy, rx, ry, n=48):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def clip_poly(poly, rect):
    """Sutherland–Hodgman clip of a (convex or not) polygon against an axis-aligned rect."""
    x0, y0, x1, y1 = rect

    def clip(pts, inside, inter):
        out = []
        if not pts:
            return out
        prev = pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(inter(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(inter(prev, cur))
            prev = cur
        return out

    def ix(x):
        return lambda p, q: (x, p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0]))

    def iy(y):
        return lambda p, q: (p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1]), y)

    pts = list(poly)
    pts = clip(pts, lambda p: p[0] >= x0, ix(x0))
    pts = clip(pts, lambda p: p[0] <= x1, ix(x1))
    pts = clip(pts, lambda p: p[1] >= y0, iy(y0))
    pts = clip(pts, lambda p: p[1] <= y1, iy(y1))
    # drop degenerate results
    if len(pts) < 3:
        return []
    area = 0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        area += a[0] * b[1] - b[0] * a[1]
    return pts if abs(area) > 1e-4 else []


def _f(v):
    s = ('%.3f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def poly_d(pts, dx=0, dy=0):
    return 'M' + ' '.join('%s,%s' % (_f(x + dx), _f(y + dy)) for x, y in pts) + 'Z'


# --------------------------------------------------------------------------
# layers
# --------------------------------------------------------------------------

@dataclass
class Layer:
    """A filled shape: polygon `shape` minus optional polygon `hole`."""
    shape: list
    paint: object  # '#rrggbb' | Linear | Radial
    opacity: float = 1.0
    hole: list | None = None
    cls: str | None = None  # e.g. ColorScheme-Text (paint must then be 'currentColor')


@dataclass
class Raster:
    """A PIL RGBA image covering the template area (0,0)-(w,h) at `scale`x resolution."""
    image: object
    scale: int = 2


def RR(x0, y0, x1, y1, r, paint, opacity=1.0):
    return Layer(rrect_poly(x0, y0, x1, y1, r), paint, opacity)


def RING(x0, y0, x1, y1, r, width, paint, opacity=1.0):
    """Rounded-rect outline of `width`, drawn inside the given box."""
    if isinstance(r, (tuple, list)):
        ri = tuple(max(0, v - width) for v in r)
    else:
        ri = max(0, r - width)
    return Layer(rrect_poly(x0, y0, x1, y1, r), paint, opacity,
                 hole=rrect_poly(x0 + width, y0 + width, x1 - width, y1 - width, ri))


# --------------------------------------------------------------------------
# document
# --------------------------------------------------------------------------

class SVG:
    def __init__(self, colorscheme: dict | None = None):
        self.defs = []
        self.body = []
        self._gid = 0
        self.maxx = 10
        self.maxy = 10
        self.colorscheme = colorscheme

    # -- bookkeeping
    def _grow(self, x, y):
        self.maxx = max(self.maxx, math.ceil(x))
        self.maxy = max(self.maxy, math.ceil(y))

    def paint(self, p, dx, dy):
        """Register a paint (offset by dx,dy) and return the fill attribute value."""
        if isinstance(p, str):
            return p
        self._gid += 1
        gid = 'g%d' % self._gid
        stops = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (_f(o), c, _f(a))
                        for o, c, a in p.stops)
        if isinstance(p, Linear):
            self.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'
                             % (gid, _f(p.x1 + dx), _f(p.y1 + dy), _f(p.x2 + dx), _f(p.y2 + dy), stops))
        else:
            cx, cy = p.cx + dx, p.cy + dy
            fx = cx if p.fx is None else p.fx + dx
            fy = cy if p.fy is None else p.fy + dy
            tr = ''
            if p.sx != 1 or p.sy != 1:
                tr = ' gradientTransform="matrix(%s 0 0 %s %s %s)"' % (_f(p.sx), _f(p.sy), _f(cx - cx * p.sx), _f(cy - cy * p.sy))
            self.defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s" fx="%s" fy="%s"%s>%s</radialGradient>'
                             % (gid, _f(cx), _f(cy), _f(p.r), _f(fx), _f(fy), tr, stops))
        return 'url(#%s)' % gid

    def layer_path(self, layer, rect, dx, dy):
        if isinstance(layer, Raster):
            x0, y0, x1, y1 = rect
            k = layer.scale
            im = layer.image.crop((round(x0 * k), round(y0 * k), round(x1 * k), round(y1 * k)))
            if im.getextrema()[3][1] == 0:  # fully transparent
                return ''
            buf = io.BytesIO()
            im.save(buf, 'PNG', optimize=True)
            return ('<image x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="none" xlink:href="data:image/png;base64,%s"/>'
                    % (_f(x0 + dx), _f(y0 + dy), _f(x1 - x0), _f(y1 - y0), base64.b64encode(buf.getvalue()).decode()))
        sh = clip_poly(layer.shape, rect)
        if not sh:
            return ''
        d = poly_d(sh, dx, dy)
        if layer.hole:
            ho = clip_poly(layer.hole, rect)
            if ho:
                d += poly_d(ho, dx, dy)
        fill = self.paint(layer.paint, dx, dy)
        extra = ' class="%s"' % layer.cls if layer.cls else ''
        op = '' if layer.opacity >= 1 else ' opacity="%s"' % _f(layer.opacity)
        return '<path d="%s" fill="%s" fill-rule="evenodd"%s%s/>' % (d, fill, op, extra)

    def bbox_rect(self, x, y, w, h):
        return '<rect x="%s" y="%s" width="%s" height="%s" fill="#000000" opacity="0.01" fill-opacity="0.01"/>' % (_f(x), _f(y), _f(w), _f(h))

    # -- public API
    def raw(self, xml: str):
        self.body.append(xml)

    def hint(self, eid, x, y, w, h):
        """Size-only hint element (Plasma reads its width/height)."""
        self.body.append('<rect id="%s" x="%s" y="%s" width="%s" height="%s" fill="#ff00ff" opacity="0.01" fill-opacity="0.01"/>'
                         % (eid, _f(x), _f(y), _f(w), _f(h)))
        self._grow(x + w, y + h)

    def element(self, eid, x, y, w, h, layers, local_origin=(0, 0)):
        """A single (non-sliced) element at (x,y) of size w,h.  Layers are in local coords."""
        ox, oy = x - local_origin[0], y - local_origin[1]
        parts = [self.bbox_rect(x, y, w, h)]
        rect = (local_origin[0], local_origin[1], local_origin[0] + w, local_origin[1] + h)
        for L in layers:
            parts.append(self.layer_path(L, rect, ox, oy))
        self.body.append('<g id="%s">%s</g>' % (eid, ''.join(parts)))
        self._grow(x + w, y + h)

    def frame(self, prefix, ox, oy, W, H, m, layers, hints=None, gap=0, pieces=None, center=None):
        """
        9-slice frame.  m = (left, top, right, bottom) border sizes.
        Layers are drawn in frame-local coords on a W x H template.
        hints: dict like {'top-margin': 3, ...} -> prefix+'hint-top-margin' elements.
        gap: optional spacing so pieces are visually separated in an editor (0 = none).
        center: id for the center piece (default prefix+'center'; Kvantum uses the bare
                '<element>-<state>' name for interiors).
        """
        l, t, r, b = m
        xs = [0, l, W - r, W]
        ys = [0, t, H - b, H]
        names = [['topleft', 'top', 'topright'], ['left', 'center', 'right'], ['bottomleft', 'bottom', 'bottomright']]
        for j in range(3):
            for i in range(3):
                name = names[j][i]
                if pieces and name not in pieces:
                    continue
                x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
                if x1 - x0 <= 0 or y1 - y0 <= 0:
                    continue
                dx, dy = ox + gap * i, oy + gap * j
                parts = [self.bbox_rect(x0 + dx, y0 + dy, x1 - x0, y1 - y0)]
                for L in layers:
                    parts.append(self.layer_path(L, (x0, y0, x1, y1), dx, dy))
                eid = center if (name == 'center' and center) else prefix + name
                self.body.append('<g id="%s">%s</g>' % (eid, ''.join(parts)))
        self._grow(ox + W + 2 * gap, oy + H + 2 * gap)
        if hints:
            hx = ox + W + 2 * gap + 2
            hy = oy
            for k, v in hints.items():
                if k.startswith(('top', 'bottom')) or k.endswith(('-top-margin', '-bottom-margin')):
                    self.hint('%shint-%s' % (prefix, k), hx, hy, 1, v)
                else:
                    self.hint('%shint-%s' % (prefix, k), hx, hy, v, 1)
                hy += max(v, 1) + 1
        return (ox + W + 2 * gap + 8, oy + H + 2 * gap + 8)

    def image(self, eid, x, y, w, h, png_bytes):
        b64 = base64.b64encode(png_bytes).decode()
        self.body.append('<image id="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="none" xlink:href="data:image/png;base64,%s"/>'
                         % (eid, _f(x), _f(y), _f(w), _f(h), b64))
        self._grow(x + w, y + h)

    def tostring(self):
        style = ''
        if self.colorscheme:
            style = '<style type="text/css" id="current-color-scheme">' + ''.join(
                '.ColorScheme-%s{color:%s;stop-color:%s}' % (k, v, v) for k, v in self.colorscheme.items()) + '</style>'
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" '
                'width="%d" height="%d" viewBox="0 0 %d %d">\n<defs>%s\n%s</defs>\n%s\n</svg>\n'
                % (self.maxx, self.maxy, self.maxx, self.maxy, style, '\n'.join(self.defs), '\n'.join(self.body)))

    def save(self, path, compress=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = self.tostring().encode()
        if compress is None:
            compress = path.endswith('.svgz')
        if compress:
            with open(path, 'wb') as fh:
                fh.write(gzip.compress(data, mtime=0))
        else:
            with open(path, 'wb') as fh:
                fh.write(data)


# --------------------------------------------------------------------------
# raster soft shadows (PIL) – embedded as PNG <image> elements
# --------------------------------------------------------------------------

def shadow_tiles(pad, radius, blur, dy=0.0, alpha=0.5, color=(0, 0, 0), cutout=True, scale=2, inner=None):
    """
    Build a soft drop shadow for a rounded rect and cut it into 8 tiles.

    pad   = (left, top, right, bottom): how far the shadow extends outside the shape.
    inner = how far corner tiles reach into the shape (default = radius) so that
            the area outside the rounded corner is covered.
    Returns dict name -> (w, h, png_bytes) in logical pixels.
    """
    from PIL import Image, ImageDraw, ImageFilter
    pl, pt, pr, pb = pad
    inner = radius if inner is None else inner
    core = 4 * radius + 40  # body size of the template shape
    W = pl + pr + core
    H = pt + pb + core
    s = scale
    shape = Image.new('L', (W * s, H * s), 0)
    d = ImageDraw.Draw(shape)
    d.rounded_rectangle([pl * s, pt * s, (pl + core) * s - 1, (pt + core) * s - 1], radius=radius * s, fill=255)
    sh = Image.new('L', (W * s, H * s), 0)
    sh.paste(shape, (0, int(round(dy * s))))
    if blur > 0:
        sh = sh.filter(ImageFilter.GaussianBlur(blur * s / 2))
    if cutout:
        # remove shadow beneath the shape itself
        import numpy as np
        a = np.asarray(sh, dtype=np.float32) * (1 - np.asarray(shape, dtype=np.float32) / 255.0)
        sh = Image.fromarray(a.clip(0, 255).astype('uint8'))
    sh = sh.point(lambda v: int(v * alpha))
    rgba = Image.new('RGBA', sh.size, color + (0,))
    rgba.putalpha(sh)

    def crop(x0, y0, x1, y1):
        im = rgba.crop((x0 * s, y0 * s, x1 * s, y1 * s))
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        return (x1 - x0, y1 - y0, buf.getvalue())

    cx0, cy0 = pl + inner, pt + inner        # inner corner limits
    cx1, cy1 = pl + core - inner, pt + core - inner
    mid_x, mid_y = W // 2, H // 2
    return {
        'topleft': crop(0, 0, cx0, cy0),
        'top': crop(mid_x - 2, 0, mid_x + 2, pt),
        'topright': crop(cx1, 0, W, cy0),
        'left': crop(0, mid_y - 2, pl, mid_y + 2),
        'right': crop(pl + core, mid_y - 2, W, mid_y + 2),
        'bottomleft': crop(0, cy1, cx0, H),
        'bottom': crop(mid_x - 2, pt + core, mid_x + 2, H),
        'bottomright': crop(cx1, cy1, W, H),
    }


def shadow_image(W, H, box, radius, blur, dy=0.0, alpha=0.5, color=(0, 0, 0), cutout=True, scale=2):
    """Full-template RGBA shadow image for a rounded rect `box`=(x0,y0,x1,y1) on a W x H canvas."""
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np
    s = scale
    x0, y0, x1, y1 = box
    shape = Image.new('L', (W * s, H * s), 0)
    r = radius if isinstance(radius, (tuple, list)) else (radius,) * 4
    ImageDraw.Draw(shape).rounded_rectangle([x0 * s, y0 * s, x1 * s - 1, y1 * s - 1], radius=max(r) * s, fill=255,
                                            corners=tuple(v > 0 for v in r))
    sh = Image.new('L', shape.size, 0)
    sh.paste(shape, (0, int(round(dy * s))))
    if blur > 0:
        sh = sh.filter(ImageFilter.GaussianBlur(blur * s / 2))
    a = np.asarray(sh, dtype=np.float32) * alpha
    if cutout:
        a *= 1 - np.asarray(shape, dtype=np.float32) / 255.0
    img = Image.new('RGBA', shape.size, tuple(color) + (0,))
    img.putalpha(Image.fromarray(a.clip(0, 255).astype('uint8')))
    return img


def add_shadow(svg: SVG, prefix, ox, oy, pad, radius, blur, dy=0.0, alpha=0.5, cutout=True, inner=None):
    """Adds prefix+'topleft'.. tiles plus prefix+'hint-*-margin' = pad."""
    tiles = shadow_tiles(pad, radius, blur, dy, alpha, cutout=cutout, inner=inner)
    x = ox
    for name in ['topleft', 'top', 'topright', 'left', 'right', 'bottomleft', 'bottom', 'bottomright']:
        w, h, png = tiles[name]
        svg.image(prefix + name, x, oy, w, h, png)
        x += w + 4
    # the shadow "center" must exist for FrameSvg; keep it fully transparent
    svg.body.append('<rect id="%scenter" x="%s" y="%s" width="4" height="4" fill="#000" opacity="0.01" fill-opacity="0.01"/>' % (prefix, _f(x), _f(oy)))
    x += 8
    pl, pt, pr, pb = pad
    svg.hint(prefix + 'hint-left-margin', x, oy, pl, 1)
    svg.hint(prefix + 'hint-top-margin', x, oy + 2, 1, pt)
    svg.hint(prefix + 'hint-right-margin', x, oy + 4 + pt, pr, 1)
    svg.hint(prefix + 'hint-bottom-margin', x, oy + 6 + pt, 1, pb)
    return oy + max(pt, pb) + 2 * radius + 60
