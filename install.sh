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

# make running sessions pick up the new files: Plasma keeps a per-theme SVG cache and
# KWin only reloads the window decoration when asked to
rm -f "${XDG_CACHE_HOME:-$HOME/.cache}/plasma_theme_$ID.kcache"
if command -v qdbus6 >/dev/null; then qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
elif command -v qdbus >/dev/null; then qdbus org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true; fi

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

case "${1:-}" in
  --apply)  select_kvantum; plasma-apply-lookandfeel -a "$LAF" ;;
  --layout) select_kvantum; plasma-apply-lookandfeel -a "$LAF" --resetLayout ;;
esac
