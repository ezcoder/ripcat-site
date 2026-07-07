#!/bin/bash
# capture-screens.sh — durable, scriptable capture of real RipCat app screenshots
# for ripcat.dev. Builds the app once, then drives the iOS/iPadOS simulator with
# the app's screenshot-mode deep-link launch args and grabs pixel-perfect PNGs
# via `simctl io screenshot` — no fragile XCUITest tapping.
#
# Usage:
#   tools/capture-screens.sh [--repo PATH] [--device "iPhone 17 Pro"] [--out DIR]
#                            [--skip-build] [--only SCENE[,SCENE...]]
#
# Scenes are defined in tools/scenes.conf (one per line):
#   name | extra launch args | settle seconds
#
# Requirements: Xcode + simulators; the app repo with screenshot-mode hooks
# (-open-tab / -select-buoy / -select-zone / -sca-step) in ContentView.swift
# and StationMapView.swift.
set -euo pipefail

REPO="${RIPCAT_APP_REPO:-$HOME/Code/ripcat-marketing}"
DEVICE="iPhone 17 Pro"
OUT="$(cd "$(dirname "$0")/.." && pwd)/i/raw"
SKIP_BUILD=0
ONLY=""
BUNDLE_ID="com.ripcat.ios"
DD="/tmp/ripcat-dd"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2;;
    --device) DEVICE="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --skip-build) SKIP_BUILD=1; shift;;
    --only) ONLY="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done

SCENES_FILE="$(dirname "$0")/scenes.conf"
mkdir -p "$OUT"

echo "==> Device: $DEVICE"
UDID=$(xcrun simctl list devices available | grep -F "$DEVICE (" | head -1 | grep -oE '[0-9A-F-]{36}')
[[ -n "$UDID" ]] || { echo "simulator '$DEVICE' not found" >&2; exit 1; }

if [[ $SKIP_BUILD -eq 0 ]]; then
  echo "==> Building RipCat ($REPO)"
  xcodebuild -project "$REPO/RipCat.xcodeproj" -scheme RipCat \
    -destination "id=$UDID" \
    -derivedDataPath "$DD" -quiet build
fi

APP=$(find "$DD/Build/Products" -maxdepth 2 -name "RipCat.app" | head -1)
[[ -n "$APP" ]] || { echo "RipCat.app not found under $DD" >&2; exit 1; }

echo "==> Booting $DEVICE ($UDID)"
xcrun simctl bootstatus "$UDID" -b >/dev/null
# Clean, consistent chrome: 9:41, full bars/wifi/battery — the Apple way.
xcrun simctl status_bar "$UDID" override --time "9:41" \
  --dataNetwork wifi --wifiMode active --wifiBars 3 \
  --cellularMode active --cellularBars 4 --batteryState charged --batteryLevel 100
xcrun simctl ui "$UDID" appearance dark
xcrun simctl install "$UDID" "$APP"

slug=$(echo "$DEVICE" | tr ' ()' '---' | tr -s '-' | sed 's/-$//')

capture() {
  local name="$1"; local settle="$2"; shift 2
  if [[ -n "$ONLY" ]] && ! grep -qw "$name" <<< "${ONLY//,/ }"; then return; fi
  echo "==> Scene: $name"
  xcrun simctl terminate "$UDID" "$BUNDLE_ID" 2>/dev/null || true
  xcrun simctl launch "$UDID" "$BUNDLE_ID" \
    -screenshot-mode true -skip-onboarding true -seed-favorites true "$@" >/dev/null
  sleep "$settle"
  xcrun simctl io "$UDID" screenshot --type png "$OUT/${slug}-${name}.png"
  echo "    saved $OUT/${slug}-${name}.png"
}

# scenes.conf format:  name | launch args | settle seconds
while IFS='|' read -r name args settle; do
  name=$(echo "$name" | xargs); args=$(echo "$args" | xargs); settle=$(echo "${settle:-8}" | xargs)
  [[ -z "$name" || "$name" == \#* ]] && continue
  # shellcheck disable=SC2086
  capture "$name" "$settle" $args
done < "$SCENES_FILE"

echo "==> Done. Raw captures in $OUT"
echo "    Next: tools/process-screens.sh"
