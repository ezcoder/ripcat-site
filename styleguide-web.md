# RipCat Web Style Guide

**`styleguide-web.md` · v1.0 · 2026-07-07**

The specification for ripcat.dev. Derived from three sources, in priority order:

1. **The shipping app UI** — `Sources/RipCatApp/BrandColors.swift`, `Sources/RipCatApp/MarineDesignSystem.swift`, `Sources/RipCatCore/ChartTheme.swift`, and pixel-sampled App Store screenshots.
2. **Apple Human Interface Guidelines (iOS)** — type scale, spacing rhythm, touch targets, dark-mode elevation, materials, motion.
3. **`branding/BRAND.md`** in ripcat-marketing — story, mascot, tone.

The goal is "Apple polish": the site should feel like the app's marketing brochure was designed by the same hand that designed the app. When the app and this guide disagree, **the app wins** — update this file.

---

## 1. Design principles

1. **Data is the hero.** The most beautiful thing on any screen is a number you can act on. Charts, numerals, and timelines get the visual budget; decoration defers.
2. **Dark-first marine.** The app's marine surfaces are dark-mode-first (`MarineDesignSystem`). The web's product sections inherit that: deep, calm, low-chroma surfaces with one saturated accent doing the pointing.
3. **Hairlines, not shadows.** In dark UI the app carries elevation with background contrast + 1px hairline borders, never drop shadows. The web does the same in dark sections. Shadows are permitted only on light backgrounds, and soft.
4. **One accent per surface.** Each surface gets a single saturated "look here" color (`--marine-accent` in dark, teal in light). High/low/coral/gold are *data semantics*, not decoration.
5. **Calm motion.** Things settle; they don't bounce. Every animation must survive `prefers-reduced-motion`.

---

## 2. Color

### 2.1 Brand core (from `BrandColors.swift` — authoritative)

| Token | Hex | RGB | Use |
|---|---|---|---|
| `--ocean-teal` | `#2EC4B6` | 46 196 182 | Primary accent, links on dark, brand marks |
| `--navy` | `#1C1A2E` | 28 26 46 | Brand dark surface |
| `--deep-navy` | `#0F0E20` | 15 14 32 | Deepest brand surface, page bg (dark) |
| `--sandy` | `#FAF5EB` | 250 245 235 | Warm light surface |
| `--coral` | `#E65A40` | 230 90 64 | High-tide semantic, warnings, warm CTA |
| `--gold` | `#F2C040` | 242 192 64 | Highlights, advisory-moderate, Yater accent |
| `--sea-green` | `#33CC73` | 51 204 115 | Low-tide semantic, positive/rising |

> Note: `branding/BRAND.md` lists Ocean Teal as `#008C8C`; the shipping app uses `#2EC4B6`. **The web uses the app's `#2EC4B6`.**

### 2.2 Accessible text variants (WCAG, from `BrandColors.swift:17-23`)

The saturated brand colors are **decorative-only on light backgrounds**. For text on light, use the app's contrast-safe variants:

| Decorative | Text (AA, ≥4.5:1) | AAA (≥7:1) |
|---|---|---|
| teal `#2EC4B6` | `#007878` | `#006464` |
| coral `#E65A40` | `#B4321E` | `#962819` |
| sea green `#33CC73` | `#14823C` | `#0F642D` |
| gold `#F2C040` | `#A07800` | — |

On dark backgrounds use the app's dark-mode variants for small text/glyphs: teal `#50DCD2`, coral `#FF785A`, green `#50E68C`.

### 2.3 Marine dark surface system (from `MarineDesignSystem.swift:41-50`)

This is the palette for all dark product/feature sections on the web:

| Token | Hex | Role |
|---|---|---|
| `--marine-base` | `#0A0E14` | Page/section background |
| `--marine-card` | `#121822` | Card background |
| `--marine-card-elevated` | `#1A2230` | Elevated card / hover / active |
| `--marine-text-primary` | `#F2F5F8` | Primary text |
| `--marine-text-secondary` | `#9BA8B8` | Secondary text, body |
| `--marine-text-tertiary` | `#5C6B7A` | Captions, disabled |
| `--marine-accent` | `#3DD2E8` | THE saturated accent: "now", selection, live |
| `--marine-hairline` | `rgba(255,255,255,.08)` | 1px borders, dividers |

Light-mode marine equivalents (app tokens): base `#F4F6F8`, card `#FFFFFF`, text `#0C1116` / `#5C6B7A` / `#9BA8B8`.

### 2.4 App-light surfaces (pixel-sampled from shipping screenshots)

For light sections that echo the iOS app: page `#FEFCF9`, tinted state cards — falling/positive `#EDF9EE`, high-tide `#FCF5F1` with a 4px `#E65A40` leading accent bar, info `#F2F9F5`.

### 2.5 Semantic rules

- **Rising / high tide → coral.** **Falling / low tide → sea green.** Never swap; never use red/green for anything else on a chart surface.
- Advisory severity: none = neutral hairline chip · moderate = gold chip, dark text · active/severe = coral chip, white text. Always pair color with a shape/label change (colorblind-safe, mirrors the app's VoiceOver-labeled severity coding).
- Gradients: `oceanGradient` (teal → navy, 135°) and `sandyGradient` (sandy fading out, vertical) are the only sanctioned decorative gradients, plus data-fill gradients under chart curves (accent at 20–28% alpha → transparent).

---

## 3. Typography

### 3.1 Families

| Role | Web stack | App equivalent |
|---|---|---|
| UI & body | `-apple-system, BlinkMacSystemFont, "SF Pro Text", Inter, sans-serif` | SF Pro |
| Display / headlines | `"Bricolage Grotesque", -apple-system, sans-serif` (weights 600–800 only) | Marketing lettering |
| Hero numerals & data | `ui-rounded, "SF Pro Rounded", -apple-system, sans-serif` + `font-variant-numeric: tabular-nums` | `.rounded` + `.monospacedDigit()` (`MarineDesignSystem.swift:113`) |
| Code / station IDs | `ui-monospace, "SF Mono", monospace` | — |

**Data numerals are sacred:** any number that represents a live reading (tide height, °F, kt, hPa, countdown) renders in the rounded stack, semibold, tabular. This is the single strongest "same hand as the app" signal.

### 3.2 Type scale (HIG-anchored, 1rem = 16px)

| Web token | Size / line-height | Weight | HIG analog |
|---|---|---|---|
| `--t-hero` | clamp(2.75rem, 5.5vw, 4.25rem) / 1.06 | 800 display | — (marketing) |
| `--t-title1` | 2rem / 1.15 | 700 display | Title 1 (28) |
| `--t-title2` | 1.375rem / 1.25 | 700 display | Title 2 (22) |
| `--t-title3` | 1.25rem / 1.3 | 600 | Title 3 (20) |
| `--t-headline` | 1.0625rem / 1.4 | 600 | Headline (17 semibold) |
| `--t-body` | 1.0625rem / 1.55 | 400 | Body (17) |
| `--t-callout` | 1rem / 1.5 | 400 | Callout (16) |
| `--t-subhead` | 0.9375rem / 1.45 | 400–500 | Subheadline (15) |
| `--t-footnote` | 0.8125rem / 1.4 | 400 | Footnote (13) |
| `--t-caption` | 0.75rem / 1.35 | 600, uppercase, tracking .05em | Caption 1 (12) |
| `--t-hero-number` | 3.25rem / 1 | 600 rounded tabular | Marine hero 52pt semibold |

### 3.3 Rules

- Letter-spacing: display ≥ Title 2 gets `-0.015em`; `--t-caption` metric labels get `+0.05em` and uppercase (mirrors app metric labels, tracking 0.5).
- Body text max measure: 34–38rem (~65ch). Never justify.
- No font weights below 400; no light/thin faces (HIG legibility).
- Marketing kickers use the `--t-caption` spec in the section's accent color.

---

## 4. Spacing & layout

**8pt grid.** All paddings, gaps, and margins are multiples of 4px, preferring 8s: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 88, 120`.

| Token | Value | Use |
|---|---|---|
| `--sp-card` | 16px | Card interior padding (app `MetricCard` = 16) |
| `--sp-card-lg` | 24px | Large/feature card padding |
| `--sp-stack` | 12px | Vertical rhythm inside a card |
| `--sp-grid` | 20–24px | Gap between cards in a grid |
| `--sp-section` | 96px desktop / 64px mobile | Between page sections |
| `--container` | 1120px max, 24px side padding | Page column |

- Touch/click targets ≥ 44×44px (HIG minimum) — includes nav links and footer links.
- Section rhythm: kicker → title → subtitle → 48px → content.
- Two-column feature layouts: 55/45 split, 64px gutter, collapse ≤ 900px.

---

## 5. Shape, elevation & materials

| Token | Value | Use |
|---|---|---|
| `--r-card` | 20px | Cards, chart panels (app `MetricCard` cornerRadius 20 continuous) |
| `--r-control` | 12px | Buttons, inputs |
| `--r-chip` | 999px | Chips, pills, day segments (app uses Capsule) |
| `--r-cta-inner` | 10px | Small inline CTAs (app zone-summary CTA) |
| `--r-device` | 44px outer / 34px screen | iPhone frame; iPad 24/18; Watch 38/30 |

**Elevation:**

- **Dark sections:** background steps (`base → card → elevated`) + 1px `--marine-hairline` border. **No box-shadows.** Hover = elevate the background one step and brighten the hairline, translateY(-2px) max.
- **Light sections:** `0 2px 14px rgba(28,26,46,.06)` resting, `0 18px 40px rgba(28,26,46,.13)` hover. Never both a strong border and a strong shadow.
- **Materials:** sticky nav = `rgba(base, .82)` + `backdrop-filter: blur(14px)` + bottom hairline (mirrors app `.ultraThinMaterial` capsule controls). Use blur materials only for chrome (nav, floating controls), never for content cards.

**Corner smoothing:** where supported, prefer `corner-shape: squircle` / large radii that read as continuous curvature; never radius > half the element height except chips.

---

## 6. Components

### 6.1 Buttons

| Variant | Spec |
|---|---|
| Primary (dark surface) | bg `--ocean-teal`, text `#0F0E20`, weight 700, radius 12, padding 14×24; hover: brighten + translateY(-2px) |
| Primary (light surface) | bg `--navy`, text white |
| App Store button | White bg, navy text, Apple glyph, two-line label ("Download on the / App Store"), radius 14 |
| Secondary/ghost | 1.5px hairline border, transparent bg; hover: accent border + 8% accent bg |
| Section-accent CTA | In cohort/feature sections the primary button may take the section accent (gold/green/teal) with `#0F0E20` text |

### 6.2 Cards

- **Metric card** (the app's signature): radius 20, padding 16, hairline border, caption-spec label on top, rounded tabular numeral below, optional trend glyph in semantic color. Web replica must match this anatomy exactly.
- **Feature card:** radius 20, padding 24, icon container 44×44 radius 12.
- **Chart panel:** radius 20, padding 24, caption footer at 60% opacity.

### 6.3 Chips & status

- Day/timeline chips: capsule, caption type; severity per §2.5.
- Live indicator: 6px accent dot + 2.4s opacity pulse (freeze under reduced motion).

### 6.4 Device frames

Real screenshots only — never mock UI that doesn't exist. Frame specs: near-black `#0B0A12` body, 1px `rgba(255,255,255,.14)` edge, screen radius per §5 table. iPhone gets a Dynamic Island pill; iPad thin uniform bezel; Watch gets side button/crown hints and pure-black canvas bleed (watch UI is `#000`-native, so the frame and screen may merge).

### 6.5 Charts (web-drawn SVG)

Follow `ChartTheme.swift` semantics: curve 3px round-cap in surface accent, gradient fill 20–28% → 0, high markers coral, low markers sea green, "now" = white/accent dot with dashed vertical hairline, labels footnote-size tabular. Grid lines at `--marine-hairline`. Perceptual ramps (thermal for water temp, etc.) — never rainbow.

---

## 7. Motion

| Pattern | Spec |
|---|---|
| Reveal on scroll | opacity 0→1 + translateY 22px→0, 600ms `cubic-bezier(.22,.61,.36,1)`, threshold 12%, once |
| Hover lift | 150–180ms ease-out, ≤ 2–5px |
| Live pulse | 2.4s ease-in-out infinite, opacity 1↔.5 |
| Scroll behavior | `scroll-behavior: smooth`, auto under reduced motion |

`prefers-reduced-motion: reduce` disables all of the above (content fully visible, static). JS-gated reveals must also render visible without JS (`.js` class pattern).

---

## 8. Imagery & screenshots

- **Real screens only**, captured via `tools/` (see `tools/README.md`) in `-screenshot-mode` (dark, Santa Barbara, seeded favorites, Pro unlocked).
- Canonical devices: iPhone 17 Pro, iPad Pro 13-inch (M5), Apple Watch Series 11 (46mm) — matches App Store set.
- Hero screenshots: PNG, 2× logical resolution, ≤ 700KB after `sips` resize; photographs/mascot art: JPEG q80.
- Every screenshot gets descriptive alt text naming the station and the reading shown.
- Mascot art (Rip): use as a *story* element on sandy/light surfaces only; never behind data.

## 9. Voice (summary — full rules in ripcat-marketing `GUARDRAILS.md`)

Chill, working-waterfront, specific. Numbers over adjectives. US-only coverage, predictions-not-guarantees, no safety/catch/wave-quality promises, comparisons dated and website-only. Sign-off: *"Made in Santa Barbara by a surfer, his daughter, and their cat, Rip."*

## 10. Theme keynote: the pocket oracle

The design's underlying narrative — **"a weatherman in your pocket"**: every surface answers *what is the water doing right now, and what will it do next*. Hero numerals = the oracle speaks. Timelines = it sees ahead. Glanceable chips/complications = it whispers from your wrist. Copy and layout should always resolve to that promise: all the data you need, in your pocket.
