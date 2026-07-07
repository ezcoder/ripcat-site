# ripcat.dev screenshot tooling

Durable workflows for pulling **real app screenshots** into the website. No fragile
UI-test tapping: the app exposes screenshot-mode deep-link launch args, and these
scripts drive simulators with `simctl`.

## The pipeline

```
tools/capture-screens.sh                     # iPhone (default) — builds, boots, captures all scenes
tools/capture-screens.sh --device "iPad Pro 13-inch (M5)"
tools/capture-watch.sh                       # Apple Watch main screen
tools/process-screens.sh                     # resize/optimize i/raw/* -> i/app-*.png
```

Full refresh:

```bash
tools/capture-screens.sh && \
tools/capture-screens.sh --skip-build --device "iPad Pro 13-inch (M5)" && \
tools/capture-watch.sh && \
tools/process-screens.sh
```

(`--skip-build` reuses the derived data from the previous run when the app hasn't
changed. `--only scene1,scene2` re-captures a subset.)

## Scenes (`tools/scenes.conf`)

| Scene | What it shows | Launch args |
|---|---|---|
| `today` | Today tide chart, current-height hero, countdown | — |
| `favorites` | Favorites list, 5 seeded CA stations | `-open-tab favorites` |
| `map-sca-timeline` | Marine conditions timeline: SCA zones painted on the map, scrubber parked mid-week | `-open-tab map -sca-step 3` |
| `zone-glance` | At-a-glance marine zone summary popover | `-open-tab map -select-zone PZZ650` |
| `buoy-detail` | Buoy detail sheet: water-temp hero + sparkline, swell rose, wind, pressure | `-open-tab map -select-buoy 46053` |
| `settings` | Customization: units, chart themes, refresh, notifications | `-open-tab settings` |
| `calendars` | Printable tide calendars | `-open-tab calendars` |

Add a scene = add a line to `scenes.conf`. Settle seconds are the wait for live
NOAA/NWS/NDBC data to render (data is live; only location, favorites, and Pro are seeded).

## App-side hooks (in the app repo)

`-screenshot-mode` (existing) seeds 5 CA favorites, pins location to Santa Barbara,
unlocks Pro, forces dark appearance. This tooling added, gated behind it:

- `ContentView.swift` — `-open-tab <name>` selects a tab (iPhone) / sidebar item (iPad).
- `StationMapView.swift` — `-sca-step <n>`, `-select-zone <id>`, `-select-buoy <id>`.

Zone/buoy IDs that photograph well: `PZZ650` (East Santa Barbara Channel zone),
`46053` (East Santa Barbara Channel buoy), `46054` (West SB Channel).

## Conventions

- Status bar is overridden to **9:41**, full wifi/battery; appearance **dark**.
- Raw captures land in `i/raw/` (gitignored); processed assets in `i/app-*.png`.
- Canonical devices: iPhone 17 Pro, iPad Pro 13-inch (M5), Apple Watch Series 11 (46mm).
- Image budgets and alt-text rules: `styleguide-web.md` §8.

## App Store screenshots

The App Store pipeline is separate (fastlane snapshot in the app repo:
`fastlane/Fastfile` lane `screenshots`). This tooling is for the website only.
