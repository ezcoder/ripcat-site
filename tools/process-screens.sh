#!/bin/bash
# process-screens.sh — normalize raw simulator captures into optimized site assets.
# Resizes to web-friendly sizes (per styleguide-web.md §8) and writes into i/.
#
# Usage: tools/process-screens.sh [--raw DIR] [--dest DIR]
set -euo pipefail

SITE="$(cd "$(dirname "$0")/.." && pwd)"
RAW="$SITE/i/raw"
DEST="$SITE/i"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --raw) RAW="$2"; shift 2;;
    --dest) DEST="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done

shopt -s nullglob
make_webp() {
  local src="$1"; local q="${2:-88}"; local out="${src%.*}.webp"
  command -v cwebp >/dev/null 2>&1 || return 0
  cwebp -quiet -q "$q" -m 6 "$src" -o "$out"
  echo "processed $out ($(du -h "$out" | cut -f1))"
}

for f in "$RAW"/*.png; do
  base=$(basename "$f" .png)
  # Animation frames become light JPEGs (the site cross-fades several at once).
  if [[ "$base" == *sca-frame-* ]]; then
    n="${base##*sca-frame-}"
    out="$DEST/anim-sca-${n}.jpg"
    sips -Z 900 -s format jpeg -s formatOptions 74 "$f" --out "$out" >/dev/null
    echo "processed $out ($(du -h "$out" | cut -f1))"
    make_webp "$out" 88
    continue
  fi
  case "$base" in
    iPad*)  MAX=1600;;   # iPad landscape/portrait hero
    *watch*) MAX=800;;   # watch face
    *)      MAX=1200;;   # iPhone portrait
  esac
  out="$DEST/app-${base}.png"
  sips -Z "$MAX" "$f" --out "$out" >/dev/null
  size=$(du -h "$out" | cut -f1)
  echo "processed $out ($size)"
  make_webp "$out" 88
done
echo "Done. Reference site HTML to the generated .webp files; PNG/JPEG originals remain alongside them."
