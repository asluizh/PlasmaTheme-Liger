#!/bin/bash
# Install (or remove) Liger and DarkLiger for the current user.
#   ./install.sh            build + copy both themes into ~/.local/share
#   ./install.sh --apply    ...and apply the Liger global theme (keeps your panel layout)
#   ./install.sh --layout   ...apply the global theme AND its menu bar + dock layout
#   ./install.sh --remove   uninstall both
# add --dark to --apply / --layout to apply DarkLiger instead, e.g.  ./install.sh --dark --apply
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
D="${XDG_DATA_HOME:-$HOME/.local/share}"
K="${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum"
THEMES="Liger DarkLiger"
laf() { echo "org.kde.${1,,}.desktop"; }

MODE=; ID=Liger
for a in "$@"; do
  case "$a" in
    --dark) ID=DarkLiger ;;
    --apply|--layout|--remove) MODE="$a" ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done
LAF=$(laf "$ID")
KV=$ID

remove() {
  for T in $THEMES; do
    rm -rf "$D/plasma/desktoptheme/$T" "$D/plasma/look-and-feel/$(laf "$T")" "$D/aurorae/themes/$T" \
           "$D/color-schemes/$T.colors" "$K/$T"
  done
  echo "Liger and DarkLiger removed."
}

if [ "$MODE" = "--remove" ]; then remove; exit 0; fi

python3 "$HERE/build.py"
B="$HERE/build"
mkdir -p "$D/plasma/desktoptheme" "$D/plasma/look-and-feel" "$D/aurorae/themes" "$D/color-schemes" "$K"
for T in $THEMES; do
  L=$(laf "$T")
  rm -rf "$D/plasma/desktoptheme/$T" "$D/plasma/look-and-feel/$L" "$D/aurorae/themes/$T" "$K/$T"
  cp -r "$B/plasma/desktoptheme/$T" "$D/plasma/desktoptheme/"
  cp -r "$B/plasma/look-and-feel/$L" "$D/plasma/look-and-feel/"
  cp -r "$B/aurorae/themes/$T" "$D/aurorae/themes/"
  cp "$B/color-schemes/$T.colors" "$D/color-schemes/"
  cp -r "$B/kvantum/$T" "$K/"
  # Plasma keeps a per-theme SVG cache
  rm -f "${XDG_CACHE_HOME:-$HOME/.cache}/plasma_theme_$T.kcache"
done
echo "Liger and DarkLiger installed into $D"

# make running sessions pick up the new files: Aurorae v2 keeps a loaded theme in memory
# while any window uses it (a plain KWin reconfigure does not re-read it), so briefly
# switch the decoration away and back.
reload_decoration() {
  local Q; Q=$(command -v qdbus6 || command -v qdbus) || return 0
  local G=org.kde.kdecoration2 lib theme
  # read only the user's own kwinrc (kreadconfig6 would also return cascaded defaults)
  local F="${XDG_CONFIG_HOME:-$HOME/.config}/kwinrc"
  lib=$(sed -n "/^\[$G\]/,/^\[/{s/^library=//p}" "$F" 2>/dev/null | head -1) || true
  theme=$(sed -n "/^\[$G\]/,/^\[/{s/^theme=//p}" "$F" 2>/dev/null | head -1) || true
  kwriteconfig6 --file kwinrc --group $G --key library org.kde.breeze
  kwriteconfig6 --file kwinrc --group $G --key theme Breeze
  "$Q" org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
  sleep 1
  # restore exactly what was there (empty = inherited from the global theme defaults)
  # (not kwriteconfig6 --delete: that writes "key[$d]", which also hides the inherited value)
  sed -i "/^\[$G\]/,/^\[/{/^library=/d;/^theme=/d}" "$F"
  [ -z "$lib" ] || kwriteconfig6 --file kwinrc --group $G --key library "$lib"
  [ -z "$theme" ] || kwriteconfig6 --file kwinrc --group $G --key theme "$theme"
  "$Q" org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
}

select_kvantum() {
  # point Kvantum at the theme (the global theme sets widgetStyle=kvantum)
  if command -v kvantummanager >/dev/null; then
    kvantummanager --set "$KV" >/dev/null 2>&1 && return
  fi
  local F="$K/kvantum.kvconfig"
  if grep -q '^theme=' "$F" 2>/dev/null; then sed -i "s/^theme=.*/theme=$KV/" "$F"
  else printf '[General]\ntheme=%s\n' "$KV" >> "$F"; fi
}

reload_decoration

case "$MODE" in
  --apply)  select_kvantum; plasma-apply-lookandfeel -a "$LAF" ;;
  --layout) select_kvantum; plasma-apply-lookandfeel -a "$LAF" --resetLayout ;;
esac
