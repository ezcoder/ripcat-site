#!/usr/bin/env bash
# Create or refresh one semantic blog feature screenshot from the real app screenshot scenes.
# Usage:
#   tools/capture-blog-feature.sh --list
#   tools/capture-blog-feature.sh <feature>
#   tools/capture-blog-feature.sh <feature> --refresh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FEATURE=""
REFRESH=0

usage() {
  cat <<'EOF'
capture-blog-feature.sh --list
capture-blog-feature.sh <feature> [--refresh]

Features:
  station-selection  -> i/blog-tide-stations.{png,webp}
  tide-curve         -> i/blog-tide-curve.{png,webp}
  buoy-context       -> i/blog-buoy-context.{png,webp}
  local-geography    -> i/blog-local-geography.{png,webp}
  forecast-context   -> i/blog-use-predictions.{png,webp}

Without --refresh, copies the current processed app screenshot into the semantic
blog asset name. With --refresh, first runs capture-screens.sh for the mapped
scene and process-screens.sh, then copies the processed asset.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0 ;;
    --list)
      usage
      exit 0 ;;
    --refresh)
      REFRESH=1 ;;
    -*)
      echo "capture-blog-feature.sh: unknown option '$1'" >&2
      usage >&2
      exit 2 ;;
    *)
      if [[ -n "$FEATURE" ]]; then
        echo "capture-blog-feature.sh: unexpected extra argument '$1'" >&2
        exit 2
      fi
      FEATURE="$1" ;;
  esac
  shift
done

[[ -n "$FEATURE" ]] || { usage >&2; exit 2; }

case "$FEATURE" in
  station-selection)
    SCENE="favorites"
    SOURCE="app-iPhone-17-Pro-favorites"
    DEST="blog-tide-stations" ;;
  tide-curve)
    SCENE="today"
    SOURCE="app-iPhone-17-Pro-today"
    DEST="blog-tide-curve" ;;
  buoy-context)
    SCENE="buoy-detail"
    SOURCE="app-iPhone-17-Pro-buoy-detail"
    DEST="blog-buoy-context" ;;
  local-geography)
    SCENE="map-sca-timeline"
    SOURCE="app-iPhone-17-Pro-map-sca-timeline"
    DEST="blog-local-geography" ;;
  forecast-context)
    SCENE="zone-forecast"
    SOURCE="app-iPhone-17-Pro-zone-forecast"
    DEST="blog-use-predictions" ;;
  *)
    echo "capture-blog-feature.sh: unknown feature '$FEATURE'" >&2
    usage >&2
    exit 2 ;;
esac

if [[ "$REFRESH" -eq 1 ]]; then
  "$ROOT/tools/capture-screens.sh" --only "$SCENE"
  "$ROOT/tools/process-screens.sh"
fi

for ext in png webp; do
  src="$ROOT/i/$SOURCE.$ext"
  dest="$ROOT/i/$DEST.$ext"
  [[ -s "$src" ]] || {
    echo "capture-blog-feature.sh: missing processed source $src" >&2
    echo "Run tools/capture-screens.sh --only $SCENE && tools/process-screens.sh, or pass --refresh." >&2
    exit 1
  }
  cp "$src" "$dest"
  echo "wrote ${dest#$ROOT/}"
done
