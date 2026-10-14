# Liger / DarkLiger — progress log

Aqua (Mac OS X 10.6 Snow Leopard → 10.9 Mavericks) for KDE Plasma 6, aiming for
Jobs' "lickable" gel look. Reference for colours/proportions:
https://github.com/B00merang-Project/OS-X-Mavericks (GTK). No artwork is copied;
everything is generated procedurally.

**Read this file first when resuming.** Update it at the end of each work session.

## How the project works

```
palette.py      every colour / gel recipe (single source of truth); LIGER_VARIANT=light|dark
                selects Liger or DarkLiger (dark block at the end overrides, D(light, dark)
                picks one-off literals inside the generators)
svgkit.py       SVG toolkit: rounded-rect polygons clipped into 9-slice pieces,
                gradients, size hints, raster (PIL) soft shadows embedded as PNG
gel.py          reusable Aqua gel recipes: gel(), blue(), white(), glow_ring()
plasma_style.py Plasma Style  -> build/plasma/desktoptheme/Liger
colorscheme.py  colour scheme -> build/color-schemes/Liger.colors (+ theme 'colors')
aurorae.py      window deco   -> build/aurorae/themes/Liger
kvantum.py      app widgets   -> build/kvantum/Liger (Liger.svg + Liger.kvconfig)
lookandfeel.py  global theme  -> build/plasma/look-and-feel/org.kde.liger.desktop
build.py        wipes ./build, then runs all of the above once per variant (subprocess each:
                modules read the palette at import time); --variant X builds one
install.sh      copies both themes to ~/.local/share  (--apply, --layout, --remove, --dark)
tools/testsession.sh  headless nested Plasma session -> previews/desktop.png, launcher.png
                      (THEME=DarkLiger for the dark variant)
tools/gallery.py      PySide6 widget gallery (--popup: real QMenu popup, needs QT_QPA_PLATFORM=xcb)
```

* SVGs are **never hand edited**; change the generator and rebuild (`python3 build.py`).
* Why polygons instead of clipPath: Plasma (KSvg/QtSvg) uses element *bounds*,
  which ignore clip paths. svgkit clips every layer polygon into each 9-slice
  piece itself (Sutherland–Hodgman), so every element contains only its own pixels.
* Shadows (dialogs, panels, tooltips, Aurorae) are gaussian-blurred with PIL and
  embedded as PNG `<image>` elements at 2x.
* Aurorae has no native shadow support → the shadow is baked into the decoration
  padding (`PaddingLeft/Top/Right/Bottom` in `Ligerrc`), and separate
  `decoration-maximized-*` frames are provided without padding/shadow.

### Testing without touching the real desktop
```
RUNDIR=/tmp/<short> tools/testsession.sh        # RUNDIR path must be short (<108 chars socket)
```
Starts `kwin_wayland --xwayland --virtual` + plasmashell with private XDG dirs
(`.testsession/`, Kvantum enabled), opens the widget gallery, screenshots the
desktop and the launcher. Env: `APPS="<command>"`, `W`/`H`, `WAIT`.
Menu check: `APPS="env QT_QPA_PLATFORM=xcb python3 $PWD/tools/gallery.py --popup" tools/testsession.sh /some/dir`
(Wayland refuses popups without an input serial, XWayland doesn't.)

## Status

### Done (session 1, 2026-10-13)
- [x] Generator infrastructure (svgkit, gel recipes, palette, build, install, test harness)
- [x] Plasma Style `Liger`
  - panel-background: `north-` = Snow Leopard menu bar (light gradient, white top
    line, dark bottom line); default/`south-`/`east-`/`west-` = 2D frosted dock;
    mask-*, shadow-*, thick-hint-* ; variants translucent/ opaque/ solid/
  - dialogs/background (white popup, soft shadow, mask) + variants
  - tooltip: Snow Leopard pale yellow + variants
  - widgets/background (desktop widgets)
  - button: white gel (normal), blue gel (pressed + focus-background = Aqua default
    button), glow rings for focus/hover, toolbutton-hover/pressed/focus
  - tasks: glowing "running light" capsule under dock icons; hover glow; attention
    (amber); progress (blue gel); west/east variants put the light on the side
  - viewitem/listitem: Snow Leopard blue selection gradient
  - lineedit: inset field + blue focus glow
  - scrollbar: white capsule track + blue gel thumb (gel oriented for vertical bars)
  - slider: groove + blue gel knob; switch; radiobutton; bar_meter (blue candy)
  - menubaritem + tabbar `north-active-tab`: blue highlight for open menus/menu extras
  - plasmoidheading: light unified-gradient header/footer
  - `colors` file so Plasma text stays dark on the light Aqua chrome
- [x] Colour scheme `Liger` (window #ececec, Aqua selection #3875d7, alternating rows
  #edf3fe, pale-yellow tooltips)
- [x] Aurorae `Liger`: 22px title bar, SL/Mavericks gradient, centred engraved title,
  traffic-light gel buttons (glyphs on hover, `ButtonGroupHover=true`, graphite when
  inactive), baked soft shadow, maximized variant
- [x] Global theme `org.kde.liger.desktop`: defaults + layout (top menu bar with
  launcher/global menu/tray/clock; bottom floating fit-width dock with icon tasks + trash)
- [x] Kvantum `Liger` (apps): capsule push buttons via `expand-button-*` objects
  (frame.expansion=34), **blue default button** (`button-default-*`), graphite toggled,
  blue focus glow (`button-focus`), Aqua popup button (white capsule + blue gel
  `carrow` cap), inset text fields with focus glow, gel check/radio, blue gel
  scroller thumbs (vertical, Kvantum rotates), SL inset track, **candy-striped
  progress bar** (16px tiled interior), blue-knob slider with filled groove,
  segmented-control tabs (blue selected, graphite when window inactive), SL menus
  (blue `menuitem-toggled` highlight, grey separators), yellow tooltips, blue
  list selection (grey when inactive), header with blue sorted column, group boxes.
- [x] Verified in the headless session: previews/desktop.png, launcher.png, menu.png

### Done (session 2, 2026-10-14) — user feedback after applying on the real desktop
- [x] Kvantum progress bar 27px → 12px capsule (`PROGRESS_H`, `progressbar_thickness=12`;
  thickness < font height makes Kvantum put the % text beside the bar)
- [x] Kvantum header gradient stronger (split gel, white top line, darker rule)
- [x] Scrollbar track: recessed capsule well with rounded ends (frame top/bottom = 8)
- [x] Scrollbar thumb: subtle wavy "water" ripples tiled via `interior.y.patternsize=24`
  (frame left/right = 2 so the tiled interior spans the whole gel width)
- [x] Title bar darker, SL-like: #d0d0d0 → #a3a3a3 + #515151 separator line
  (user sampled ~#cdcdcd top / ~#515151 bottom; interpreted #515151 as the bottom line)
- [x] Title-bar highlight is now a crescent following the rounded corners (it used to
  poke outside them: old `path33`/`path43` in decoration-topleft/-topright)
- [x] Traffic lights sit in an inset well (dark upper lip, light lower lip) with ambient
  occlusion on the gem top; BTN 14 → 16, gem r = 6.4
- [x] Extra buttons: keep above (blue gem, ▲) and on all desktops (purple gem, ●),
  `keepabove.svg`/`alldesktops.svg`; layout ButtonsOnRight=SF. Toggled = `pressed` state.
  The all-desktops button is hidden by KWin when only one virtual desktop exists.
- [x] Menu bar and frosted dock one shade darker
- [x] Scrollbar arrows, Snow Leopard "at top and bottom" style (`scroll_arrows=true`).
  Kvantum hard-codes one arrow per end (no "together" layout without patching Kvantum).
  Each button is one `scrollarrow-up/down-<state>` indicator image (indicator.size=15 =
  scroll_width) holding the whole button: cylinder surface, flat outer end with a
  closing line and soft shading, glyph; pressed = blue gel. The groove's end pieces
  repaint that surface around the well's rounded ends so button and track read as one piece.
- [x] Title bar 23px; traffic-light circles 15px (gem r 6.4 + 1.1 well; 16 looked too big),
  TitleEdgeTop=4, ButtonSpacing=6
- [x] `scrollbar_in_view=true`: the view frame now surrounds contents AND scrollbars
  (before, the frame only wrapped the contents, so the scrollbar had a line on one side only)
- Not possible: engraved (text-shadow) title. Aurorae v2 has no text-shadow keys and the
  v1 QML draws plain Text; the UseTextShadow keys stay in Ligerrc in case it returns.
- Won't fix: vertical (row) table headers reuse the horizontal header art transposed
  (Kvantum CE_HeaderSection rotates it; there is no separate element).

### Done (session 3, 2026-10-14) — DarkLiger 1.1.0
- [x] Variant system: `LIGER_VARIANT` env → `palette.DARK`, ids `DarkLiger` /
  `org.kde.darkliger.desktop`; build.py builds both; Liger output verified byte-identical
  to 1.0.1 apart from comments (diffed `build/` before/after)
- [x] DarkLiger look (after QuickTime X, "OS X by way of Vista"): smoked glass instead of
  brushed metal; every gel breaks hard at a reflection line (47–50%) instead of melting;
  faint sharp `GLOSS` band; `GLASS_EDGE` = 1px light inner rim on gels (gel.py), popups,
  tooltips, menus, group boxes so dark surfaces separate from dark backdrops
- [x] Modern dark conventions: window #26282b, views #1c1d20, text #e6e7e9, recessed dark
  fields/grooves; bright colour only on small accents (Aqua blue kept, a touch deeper:
  #2f6bd0 selection, dark-blue glass default button/thumb/progress); traffic lights keep
  their colours, graphite inactive gems are dark glass; dark tooltips (no SL yellow)
- [x] Translucent smoked-glass menu bar, dock (hard sheen line), popups and Kvantum menus
  (alpha 0.93 + popup_blurring); plasmarc ContrastEffect darkens the blurred backdrop
  (contrast 0.45, intensity 0.55, saturation 1.4); opaque/ and solid/ fallbacks as Liger
- [x] Both: Kvantum `button-default-indicator` (+ `flat-`) now an empty element — Kvantum
  fell back to its built-in corner triangle, visible as a wedge on default buttons
- [x] install.sh: installs both, `--dark`, rejects unknown options, tolerates a missing kwinrc
- [x] Both: every Plasma SVG now carries `hint-stretch-borders`. FrameSvg *tiles* border
  pieces by default while the centre stretches, so a gradient frame showed its edge slice
  repeated (doubled gradients at the dock caps, saw-toothed sides on vertical panels).
  KSvg reads this hint (like hint-tile-center) unprefixed, once per SVG.
- [x] Both: `east-`/`west-` dock frames are the dock layers transposed (`transposed()`), so
  vertical docks have their gradient across the thickness, lit side left like the scroller
  thumb; their margins hints are swapped to match. Checked in the test session with the
  dock scripted to 84px thick and moved to the left edge (qdbus evaluateScript as APPS).
- [x] previews/dark-desktop.png, dark-menu.png, dark-launcher.png
- Not yet checked on a real session: blur strength/contrast of the smoked glass (the
  virtual test backend does not render blur), notification popups, system tray popups.

### Aurorae v2 gotcha (keep!)
- A loaded theme is shared in a global list and kept while ANY window uses it; a KWin
  reconfigure does not re-read Ligerrc/SVGs. To see edits without re-login, switch the
  decoration away and back (install.sh `reload_decoration` does it). Don't use
  `kwriteconfig6 --delete` to restore inherited keys: it writes `key[$d]`, which masks the
  global-theme default. Use `qdbus6 || qdbus` (Fedora ships only `qdbus`).

### Kvantum gotchas learned (keep!)
- Selected menu items use state `toggled` (Kvantum getState: Selected → toggled).
- Menu separator element = `<MenuItem indicator.element>-separator` (here `marrow-separator`).
- Progress contents inherit the *Progressbar* `frame.expansion`; when expanded only
  top/bottom/corner pieces are drawn (no interior) → we use expansion 0 and a 7px
  frame capsule groove; contents = left/right caps + tiled striped interior.
- Scrollbar groove is only drawn when its width <= scroll_width.
- Orientation: scrollbar/slider groove drawn vertical, progress/tabs horizontal.
- Tiled interiors: `interior.x/y.patternsize`; the center piece must be exactly one period.

### Next (priority order)
1. Real-desktop check (install.sh --apply) with blur: tune translucent/ alphas,
   menubar translucency, popup shadow strength, KWin blur + contrast via plasmarc.
2. Dock polish: stronger frosted base when no blur; optional `smoke` style
   (palette.DOCK_STYLE); check east/west docks; consider tasks indicator being
   too wide on big docks (corner width 20px each in tasks_svg).
3. Remaining Plasma SVGs still falling back to Breeze: frame, tabbar (non-panel),
   arrows, checkmarks, pager, toolbar, line, actionbutton, calendar, busywidget,
   notes, scrollwidget, configuration-icons, containment-controls.
4. Icons / cursors (out of scope so far; maybe pick an existing Aqua-ish set).
5. Wallpaper (procedural "aurora" blue, not Apple artwork), splash screen, SDDM, lock screen.
6. 3D glass dock (explicitly postponed by the user).
7. Kvantum leftovers: combo popup list, spin box buttons, tool button arrows, MDI, dial,
   `button-default` while pressed, toolbar unified with title bar (SL "unified" look).

### Known issues / notes
- Kvantum menu shadow wasn't visible in the XWayland test session (may be fine on a real session).
- Scrollbar thumb gel is horizontal-gradient (designed for vertical scrollbars); Plasma
  uses one `slider` prefix for both orientations.
- `focus-background` makes a focused Plasma button blue (Aqua default-button look).
  Revisit if that turns out confusing.
- Test session uses the virtual backend; blur is enabled in its kwinrc but not visibly
  rendered, so translucency judgements must be made on a real session.
- Sorted header column is not drawn blue in the gallery (header-toggled not used for sort indicator?) — investigate.
- v1.0.0: project renamed Ligre → Liger (ids: `Liger`, `org.kde.liger.desktop`); install.sh now
  reconfigures KWin and drops `plasma_theme_Liger.kcache` so changes show without re-login.
