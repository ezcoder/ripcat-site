#!/bin/bash
# capture-watch.sh — capture the RipCat Apple Watch app on a watch simulator.
# The watch UI tests are disabled in the app project (CI flakiness), so this
# drives the standalone watch app directly: build, install, launch, screenshot.
#
# Usage: tools/capture-watch.sh [--repo PATH] [--device "Apple Watch Series 11 (46mm)"]
#                               [--out DIR] [--skip-build]
set -euo pipefail

REPO="${RIPCAT_APP_REPO:-$HOME/Code/ripcat-marketing}"
DEVICE="Apple Watch Series 11 (46mm)"
OUT="$(cd "$(dirname "$0")/.." && pwd)/i/raw"
SKIP_BUILD=0
DD="/tmp/ripcat-watch-dd"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2;;
    --device) DEVICE="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --skip-build) SKIP_BUILD=1; shift;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done
mkdir -p "$OUT"

# Resolve to a UDID up front — device names are ambiguous across runtime versions.
UDID=$(xcrun simctl list devices available | grep -F "$DEVICE (" | head -1 | grep -oE '[0-9A-F-]{36}')
[[ -n "$UDID" ]] || { echo "watch simulator '$DEVICE' not found" >&2; exit 1; }

if [[ $SKIP_BUILD -eq 0 ]]; then
  echo "==> Building RipCatWatch"
  xcodebuild -project "$REPO/RipCat.xcodeproj" -scheme RipCatWatch \
    -destination "id=$UDID" \
    -derivedDataPath "$DD" -quiet build
fi

APP=$(find "$DD/Build/Products" -maxdepth 2 -name "*.app" | head -1)
[[ -n "$APP" ]] || { echo "watch app not found under $DD" >&2; exit 1; }
BUNDLE_ID=$(defaults read "$APP/Info" CFBundleIdentifier)

echo "==> Booting $DEVICE"
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl status_bar "$UDID" override --time "9:41" 2>/dev/null || true
xcrun simctl install "$UDID" "$APP"
xcrun simctl terminate "$UDID" "$BUNDLE_ID" 2>/dev/null || true
xcrun simctl launch "$UDID" "$BUNDLE_ID" -screenshot-mode true >/dev/null
echo "==> Waiting for live tide data"
sleep 18
slug=$(echo "$DEVICE" | tr ' ()' '---' | tr -s '-' | sed 's/-$//')
xcrun simctl io "$UDID" screenshot --type png "$OUT/${slug}-watch-main.png"
echo "==> Saved $OUT/${slug}-watch-main.png"
