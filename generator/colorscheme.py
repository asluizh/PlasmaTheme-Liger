"""Liger / DarkLiger colour scheme (kdeglobals format)."""
import palette as P
from svgkit import hexrgb, mix, shade


def c(h):
    return '%d,%d,%d' % hexrgb(h)


def section(name, bg, bg_alt, fg, fg_inactive=None, focus=P.FOCUS_RING, hover=P.HOVER):
    fg_inactive = fg_inactive or mix(fg, bg, 0.5)
    return '\n'.join([
        '[%s]' % name,
        'BackgroundAlternate=%s' % c(bg_alt),
        'BackgroundNormal=%s' % c(bg),
        'DecorationFocus=%s' % c(focus),
        'DecorationHover=%s' % c(hover),
        'ForegroundActive=%s' % c(P.D('#1a5fd0', '#6aa8ff')),
        'ForegroundInactive=%s' % c(fg_inactive),
        'ForegroundLink=%s' % c(P.LINK),
        'ForegroundNegative=%s' % c(P.NEGATIVE),
        'ForegroundNeutral=%s' % c(P.NEUTRAL),
        'ForegroundNormal=%s' % c(fg),
        'ForegroundPositive=%s' % c(P.POSITIVE),
        'ForegroundVisited=%s' % c(P.VISITED),
        '',
    ])


def render(for_plasma_theme=False):
    out = []
    out.append('[ColorEffects:Disabled]\nColor=%s\nColorAmount=0\nColorEffect=0\nContrastAmount=0.65\nContrastEffect=1\n'
               'IntensityAmount=0.1\nIntensityEffect=2\n' % c(P.D('#b8b8b8', '#3a3c40')))
    out.append('[ColorEffects:Inactive]\nChangeSelectionColor=true\nColor=%s\nColorAmount=0.025\nColorEffect=2\n'
               'ContrastAmount=0.1\nContrastEffect=2\nEnable=false\nIntensityAmount=0\nIntensityEffect=0\n' % c('#707070'))
    D = P.D
    out.append(section('Colors:Button', D('#f6f6f6', '#35383c'), D('#e3e3e3', '#2c2e32'), P.TEXT))
    out.append(section('Colors:Complementary', D('#2b2b2b', '#1a1b1e'), D('#3a3a3a', '#232528'), D('#f2f2f2', P.TEXT)))
    out.append(section('Colors:Header', D('#d9d9d9', '#202124'), D('#cfcfcf', '#1c1d20'), P.TEXT))
    out.append(section('Colors:Header][Inactive', D('#ececec', '#26282b'), D('#e3e3e3', '#222428'), D('#6b6b6b', P.TEXT_DIM)))
    out.append(section('Colors:Selection', P.SELECTION, D('#2f63b8', '#2a5fb8'), '#ffffff', fg_inactive=D('#dbe7fb', '#c9dbf7')))
    out.append(section('Colors:Tooltip', P.TOOLTIP_BG, D('#f6f3b8', '#232528'), D('#1d1d1d', P.TEXT)))
    out.append(section('Colors:View', P.VIEW_BG, P.ALT_ROW, P.TEXT))
    out.append(section('Colors:Window', P.WINDOW_BG, D('#e3e3e3', '#2c2e32'), P.TEXT))
    if not for_plasma_theme:
        out.append('[General]\nColorScheme=%s\nName=%s\nshadeSortColumn=true\n' % (P.THEME_ID, P.THEME_NAME))
        out.append('[KDE]\ncontrast=4\n')
        out.append('[WM]\nactiveBackground=%s\nactiveBlend=%s\nactiveForeground=%s\n'
                   'inactiveBackground=%s\ninactiveBlend=%s\ninactiveForeground=%s\n'
                   % (c(D('#d6d6d6', '#2c2e32')), c(D('#d6d6d6', '#2c2e32')), c(P.TITLE_TEXT),
                      c(D('#ececec', '#26282b')), c(D('#ececec', '#26282b')), c(P.TITLE_TEXT_INACTIVE)))
    return '\n'.join(out)


def build(out):
    import os
    d = os.path.join(out, 'color-schemes')
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, P.THEME_ID + '.colors')
    with open(path, 'w') as fh:
        fh.write(render())
    return path
