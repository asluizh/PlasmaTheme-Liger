#!/bin/bash
# Render Liger (or DarkLiger) in an isolated, headless Plasma session and take screenshots.
# Nothing touches your real desktop: config + data dirs are private, KWin
# runs with the virtual backend on its own D-Bus session.
#
# usage: tools/testsession.sh [outdir]
# env:   RUNDIR  short path for XDG_RUNTIME_DIR (wayland socket path must be < 108 chars)
#        APPS    shell command(s) to start apps (default: widget gallery)
#        W,H     screen size (default 1440x900)
#        WAIT    seconds to wait for plasmashell (default 14)
#        THEME   Liger (default) or DarkLiger
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$HERE/previews}"
mkdir -p "$OUT"
WORK="$HERE/.testsession"
RUNDIR="${RUNDIR:-$(mktemp -d /tmp/liger-XXXXXX)}"
mkdir -p "$RUNDIR"; chmod 700 "$RUNDIR"
W="${W:-1440}"; H="${H:-900}"; WAIT="${WAIT:-14}"
APPS="${APPS:-python3 $HERE/tools/gallery.py}"
T="${THEME:-Liger}"
LAF="org.kde.${T,,}.desktop"

python3 "$HERE/build.py" >/dev/null

rm -rf "$WORK"
mkdir -p "$WORK/config" "$WORK/data/plasma/desktoptheme" "$WORK/data/plasma/look-and-feel" \
         "$WORK/data/aurorae/themes" "$WORK/data/color-schemes"
ln -s "$HERE/build/plasma/desktoptheme/$T" "$WORK/data/plasma/desktoptheme/$T"
ln -s "$HERE/build/plasma/look-and-feel/$LAF" "$WORK/data/plasma/look-and-feel/$LAF"
ln -s "$HERE/build/aurorae/themes/$T" "$WORK/data/aurorae/themes/$T"
ln -s "$HERE/build/color-schemes/$T.colors" "$WORK/data/color-schemes/$T.colors"

C="$WORK/config"
{
  cat "$HERE/build/color-schemes/$T.colors"
  printf '\n[KDE]\nLookAndFeelPackage=%s\nwidgetStyle=kvantum\nAnimationDurationFactor=0\n' "$LAF"
  printf '\n[Icons]\nTheme=breeze\n'
} > "$C/kdeglobals"
printf '[Theme]\nname=%s\n' "$T" > "$C/plasmarc"
mkdir -p "$C/Kvantum"
ln -s "$HERE/build/kvantum/$T" "$C/Kvantum/$T"
printf '[General]\ntheme=%s\n' "$T" > "$C/Kvantum/kvantum.kvconfig"
printf '[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae.v2\ntheme=__aurorae__svg__%s\nButtonsOnLeft=XIA\nButtonsOnRight=SF\n\n[Plugins]\nblurEnabled=true\n' "$T" > "$C/kwinrc"
printf '[General]\nShouldShow=false\nLastSeenVersion=9.9.9\n' > "$C/plasma-welcomerc"
printf '[General]\nloginMode=emptySession\n' > "$C/ksmserverrc"

cat > "$WORK/session.sh" <<EOF
#!/bin/bash
plasmashell >"$WORK/plasmashell.log" 2>&1 &
sleep $WAIT
( $APPS ) >"$WORK/apps.log" 2>&1 &
sleep 5
spectacle -b -n -f -o "$OUT/desktop.png" >/dev/null 2>&1
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.activateLauncherMenu >/dev/null 2>&1 || true
sleep 3
spectacle -b -n -f -o "$OUT/launcher.png" >/dev/null 2>&1
sleep 1
EOF
chmod +x "$WORK/session.sh"

env -u WAYLAND_DISPLAY -u DISPLAY -u SESSION_MANAGER \
  XDG_CONFIG_HOME="$C" XDG_DATA_HOME="$WORK/data" XDG_CACHE_HOME="$WORK/cache" \
  XDG_RUNTIME_DIR="$RUNDIR" XDG_CURRENT_DESKTOP=KDE KDE_FULL_SESSION=true \
  timeout 120 dbus-run-session -- kwin_wayland --xwayland --virtual --width "$W" --height "$H" \
  --no-lockscreen --exit-with-session "$WORK/session.sh" >"$WORK/kwin.log" 2>&1 || true

ls -1 "$OUT"/desktop.png "$OUT"/launcher.png 2>/dev/null
