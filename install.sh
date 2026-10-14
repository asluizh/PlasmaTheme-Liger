#!/bin/bash
# Install (or remove) Liger for the current user.
#   ./install.sh            build + copy into ~/.local/share
#   ./install.sh --apply    ...and apply the global theme (keeps your panel layout)
#   ./install.sh --layout   ...apply the global theme AND its menu bar + dock layout
#   ./install.sh --remove   uninstall
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
D="${XDG_DATA_HOME:-$HOME/.local/share}"
ID=Liger
LAF=org.kde.liger.desktop
KV=Liger

remove() {
  rm -rf "$D/plasma/desktoptheme/$ID" "$D/plasma/look-and-feel/$LAF" "$D/aurorae/themes/$ID" \
         "$D/color-schemes/$ID.colors" "${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum/$KV"
  echo "Liger removed."
}

if [ "${1:-}" = "--remove" ]; then remove; exit 0; fi

python3 "$HERE/build.py"
B="$HERE/build"
mkdir -p "$D/plasma/desktoptheme" "$D/plasma/look-and-feel" "$D/aurorae/themes" "$D/color-schemes"
rm -rf "$D/plasma/desktoptheme/$ID" "$D/plasma/look-and-feel/$LAF" "$D/aurorae/themes/$ID"
cp -r "$B/plasma/desktoptheme/$ID" "$D/plasma/desktoptheme/"
cp -r "$B/plasma/look-and-feel/$LAF" "$D/plasma/look-and-feel/"
cp -r "$B/aurorae/themes/$ID" "$D/aurorae/themes/"
cp "$B/color-schemes/$ID.colors" "$D/color-schemes/"
if [ -d "$B/kvantum/$KV" ]; then
  K="${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum"
  mkdir -p "$K"; rm -rf "$K/$KV"; cp -r "$B/kvantum/$KV" "$K/"
fi
echo "Liger installed into $D"

# make running sessions pick up the new files: Plasma keeps a per-theme SVG cache, and
# Aurorae v2 keeps a loaded theme in memory while any window uses it (a plain KWin
# reconfigure does not re-read it), so briefly switch the decoration away and back.
rm -f "${XDG_CACHE_HOME:-$HOME/.cache}/plasma_theme_$ID.kcache"
reload_decoration() {
  local Q; Q=$(command -v qdbus6 || command -v qdbus) || return 0
  local G=org.kde.kdecoration2 lib theme
  # read only the user's own kwinrc (kreadconfig6 would also return cascaded defaults)
  local F="${XDG_CONFIG_HOME:-$HOME/.config}/kwinrc"
  lib=$(sed -n "/^\[$G\]/,/^\[/{s/^library=//p}" "$F" 2>/dev/null | head -1)
  theme=$(sed -n "/^\[$G\]/,/^\[/{s/^theme=//p}" "$F" 2>/dev/null | head -1)
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
  # point Kvantum at Liger (the global theme sets widgetStyle=kvantum)
  if command -v kvantummanager >/dev/null; then
    kvantummanager --set "$KV" >/dev/null 2>&1 && return
  fi
  K="${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum/kvantum.kvconfig"
  mkdir -p "$(dirname "$K")"
  if grep -q '^theme=' "$K" 2>/dev/null; then sed -i "s/^theme=.*/theme=$KV/" "$K"
  else printf '[General]\ntheme=%s\n' "$KV" >> "$K"; fi
}

[ "${1:-}" = "--remove" ] || reload_decoration

case "${1:-}" in
  --apply)  select_kvantum; plasma-apply-lookandfeel -a "$LAF" ;;
  --layout) select_kvantum; plasma-apply-lookandfeel -a "$LAF" --resetLayout ;;
esac
