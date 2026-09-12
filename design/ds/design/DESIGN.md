---
version: 1.0
name: Crosscheck-design-system
description: A phone-first, sunlight-readable reference interface on a white canvas with a near-black primary action, the platform's own system fonts, hairline dividers and flat grey blocks. Colour has exactly one job, the verdict: green, ochre, red and grey, each always paired with a glyph and a word. Every figure is set in monospace and carries its source and date beneath it.
adapted-from: VoltAgent/awesome-design-md, Cal.com design analysis (MIT). Proprietary identity, display face and marketing components removed; rules kept.

colors:
  primary: "#111111"
  primary-pressed: "#242424"
  primary-disabled: "#e5e7eb"
  ink: "#111111"
  body: "#374151"
  muted: "#6b7280"
  muted-soft: "#898989"
  hairline: "#e5e7eb"
  hairline-soft: "#f3f4f6"
  canvas: "#ffffff"
  surface-soft: "#f8f9fa"
  surface-card: "#f5f5f5"
  surface-strong: "#e5e7eb"
  on-primary: "#ffffff"
  verdict-works-text: "#157a3a"
  verdict-works-fill: "#e6f4ea"
  verdict-degraded-text: "#8a5a00"
  verdict-degraded-fill: "#f6ead0"
  verdict-fails-text: "#b42318"
  verdict-fails-fill: "#fbe4e0"
  verdict-nodata-text: "#596270"
  verdict-nodata-fill: "#f3f4f6"

typography:
  sans: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  mono: 'ui-monospace, "SF Mono", Menlo, Consolas, monospace'
  title-lg: { fontFamily: "{typography.sans}", fontSize: 22px, fontWeight: 600, lineHeight: 1.3, letterSpacing: -0.3px }
  title-md: { fontFamily: "{typography.sans}", fontSize: 18px, fontWeight: 600, lineHeight: 1.4, letterSpacing: 0 }
  title-sm: { fontFamily: "{typography.sans}", fontSize: 16px, fontWeight: 600, lineHeight: 1.4, letterSpacing: 0 }
  body-md: { fontFamily: "{typography.sans}", fontSize: 16px, fontWeight: 400, lineHeight: 1.5, letterSpacing: 0 }
  body-sm: { fontFamily: "{typography.sans}", fontSize: 14px, fontWeight: 400, lineHeight: 1.5, letterSpacing: 0 }
  caption: { fontFamily: "{typography.sans}", fontSize: 13px, fontWeight: 400, lineHeight: 1.4, letterSpacing: 0 }
  label: { fontFamily: "{typography.sans}", fontSize: 13px, fontWeight: 600, lineHeight: 1.4, letterSpacing: 0 }
  button: { fontFamily: "{typography.sans}", fontSize: 14px, fontWeight: 600, lineHeight: 1, letterSpacing: 0 }
  tab: { fontFamily: "{typography.sans}", fontSize: 14px, fontWeight: 600, lineHeight: 1.4, letterSpacing: 0 }
  figure-lg: { fontFamily: "{typography.mono}", fontSize: 22px, fontWeight: 400, lineHeight: 1.3, letterSpacing: 0 }
  figure-md: { fontFamily: "{typography.mono}", fontSize: 16px, fontWeight: 400, lineHeight: 1.5, letterSpacing: 0 }
  figure-sm: { fontFamily: "{typography.mono}", fontSize: 14px, fontWeight: 400, lineHeight: 1.5, letterSpacing: 0 }
  figure-xs: { fontFamily: "{typography.mono}", fontSize: 13px, fontWeight: 400, lineHeight: 1.4, letterSpacing: 0 }

rounded:
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  pill: 9999px
  full: 9999px

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px

size:
  touch: 44px
  control: 44px
  topbar: 56px
  chip: 28px
  badge: 24px
  screen-pad: 16px
  content-max: 640px
  design-width: 360px
  viewport-min-height: 640px
  hairline: 1px
  rule: 3px
  focus-ring: 2px
  map-point: 10px
  map-point-ring: 18px
  qr: 200px

verdicts:
  works:    { word: "Works",    glyph: "●", text: "{colors.verdict-works-text}",    fill: "{colors.verdict-works-fill}" }
  degraded: { word: "Degraded", glyph: "▲", text: "{colors.verdict-degraded-text}", fill: "{colors.verdict-degraded-fill}" }
  fails:    { word: "Fails",    glyph: "■", text: "{colors.verdict-fails-text}",    fill: "{colors.verdict-fails-fill}" }
  nodata:   { word: "No data",  glyph: "–", text: "{colors.verdict-nodata-text}",   fill: "{colors.verdict-nodata-fill}" }

components:
  button-primary: { backgroundColor: "{colors.primary}", textColor: "{colors.on-primary}", typography: "{typography.button}", rounded: "{rounded.md}", padding: 0 20px, height: "{size.control}" }
  button-primary-pressed: { backgroundColor: "{colors.primary-pressed}", textColor: "{colors.on-primary}", rounded: "{rounded.md}" }
  button-primary-disabled: { backgroundColor: "{colors.primary-disabled}", textColor: "{colors.muted}", rounded: "{rounded.md}" }
  button-secondary: { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", border: "{size.hairline} {colors.hairline}", typography: "{typography.button}", rounded: "{rounded.md}", padding: 0 20px, height: "{size.control}" }
  button-secondary-pressed: { backgroundColor: "{colors.surface-card}", textColor: "{colors.ink}", border: "{size.hairline} {colors.hairline}" }
  text-link: { backgroundColor: transparent, textColor: "{colors.ink}", typography: "{typography.body-md}", textDecoration: underline }
  focus-ring: { outline: "{size.focus-ring} solid {colors.ink}", outlineOffset: 2px }
  top-bar: { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", typography: "{typography.title-sm}", height: "{size.topbar}", borderBottom: "{size.hairline} {colors.hairline}", padding: 0 {spacing.md} }
  offline-chip: { backgroundColor: "{colors.surface-card}", textColor: "{colors.body}", typography: "{typography.label}", rounded: "{rounded.pill}", padding: 0 {spacing.sm}, height: "{size.chip}" }
  search-input: { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", typography: "{typography.body-md}", rounded: "{rounded.md}", border: "{size.hairline} {colors.hairline}", padding: 0 {spacing.sm}, height: "{size.control}" }
  search-input-focused: { border: "{size.hairline} {colors.ink}", outline: "{component.focus-ring}" }
  result-row: { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", typography: "{typography.body-md}", minHeight: "{size.touch}", padding: "{spacing.sm} {spacing.md}", borderBottom: "{size.hairline} {colors.hairline-soft}" }
  result-row-pressed: { backgroundColor: "{colors.surface-card}" }
  community-header: { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", typography: "{typography.title-lg}", padding: "{spacing.md}" }
  source-line: { textColor: "{colors.muted}", typography: "{typography.caption}", figures: "{typography.figure-xs}" }
  service-row: { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", typography: "{typography.title-sm}", reason: "{typography.body-sm}", figures: "{typography.figure-sm}", minHeight: "{size.touch}", padding: "{spacing.sm} {spacing.md}", borderBottom: "{size.hairline} {colors.hairline}" }
  service-row-pressed: { backgroundColor: "{colors.surface-card}" }
  service-row-expanded: { backgroundColor: "{colors.surface-soft}", sources: "{component.source-line}" }
  verdict-badge: { typography: "{typography.label}", rounded: "{rounded.xs}", padding: 0 {spacing.xs}, height: "{size.badge}", textColor: "{verdicts.*.text}", backgroundColor: "{verdicts.*.fill}", content: "glyph + word" }
  publisher-row: { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", typography: "{typography.body-sm}", detail: "{typography.caption}", date: "{typography.figure-xs}", padding: "{spacing.sm} {spacing.md}", borderBottom: "{size.hairline} {colors.hairline-soft}" }
  kind-chip: { backgroundColor: "{colors.surface-card}", textColor: "{colors.body}", typography: "{typography.label}", rounded: "{rounded.xs}", padding: 0 {spacing.xs}, height: "{size.badge}", values: "predicted | licensed | listed | portal" }
  says-covered-badge: { typography: "{typography.label}", textColor: "{colors.ink}", content: "Covered | Not covered | Not recorded" }
  agreement-headline: { textColor: "{colors.ink}", typography: "{typography.title-md}", figures: "{typography.figure-lg}", padding: "{spacing.md}" }
  assumption-note: { backgroundColor: "{colors.surface-card}", textColor: "{colors.body}", typography: "{typography.body-sm}", borderLeft: "{size.rule} solid {colors.verdict-degraded-text}", rounded: "{rounded.xs}", padding: "{spacing.sm} {spacing.md}" }
  chip: { backgroundColor: "{colors.surface-card}", textColor: "{colors.body}", typography: "{typography.label}", rounded: "{rounded.pill}", padding: 0 {spacing.sm}, height: "{size.chip}" }
  chip-pressed: { backgroundColor: "{colors.surface-strong}" }
  filter-tab: { backgroundColor: transparent, textColor: "{colors.muted}", typography: "{typography.tab}", padding: "{spacing.sm} {spacing.md}", minHeight: "{size.touch}", borderBottom: "{size.focus-ring} solid transparent" }
  filter-tab-selected: { textColor: "{colors.ink}", borderBottom: "{size.focus-ring} solid {colors.ink}" }
  filter-tab-pressed: { backgroundColor: "{colors.surface-card}" }
  map: { backgroundColor: "{colors.canvas}", outline: "{colors.muted}", land: "{colors.surface-soft}", pointSize: "{size.map-point}", pointShapes: "circle works | triangle degraded | square fails | dash nodata", pointColors: "{verdicts.*.text}" }
  map-point-selected: { ring: "{size.map-point-ring} {size.focus-ring} solid {colors.ink}" }
  map-legend: { typography: "{typography.caption}", counts: "{typography.figure-xs}", textColor: "{colors.body}", padding: "{spacing.sm} {spacing.md}", gap: "{spacing.md}" }
  share-card: { backgroundColor: "{colors.canvas}", border: "{size.hairline} {colors.hairline}", rounded: "{rounded.lg}", padding: "{spacing.lg}", qr: "{size.qr} inline SVG, {colors.ink} on {colors.canvas}", meta: "{typography.figure-sm}", buttons: "{component.button-primary} + {component.button-secondary}" }
  footer: { backgroundColor: "{colors.canvas}", textColor: "{colors.muted}", typography: "{typography.caption}", borderTop: "{size.hairline} {colors.hairline}", padding: "{spacing.lg} {spacing.md}" }
---

## Overview

Crosscheck is a reference tool, not a marketing surface. It puts four published claims about a remote community's connectivity side by side, tests the best available path against what each service present in the community needs, and shows where the sources disagree. It is one self-contained HTML page under 1 MB that opens in flight mode and passes phone to phone by QR code. The design has to be read on a phone in sunlight by a nurse, on a laptop by an analyst, and on a phone in flight mode by a judge.

The system keeps the source rulebook's neutral palette (`{colors.canvas}` page, `{colors.ink}` text, `{colors.primary}` action), its type scale and weights, the 4px spacing scale, the radius scale, and its restraint at the action layer. It removes everything that was brand: the display face, the pastel badges, the dark surfaces, the marketing section rhythm, and every drop shadow.

**Key characteristics**
- One canvas: `{colors.canvas}`. Hierarchy comes from hairlines (`{colors.hairline}`), flat grey blocks (`{colors.surface-card}`), size and weight 600. No shadows, gradients, blur or transparency.
- One accent: `{colors.primary}` for the primary button, links, focus rings and the selected tab. There is no second accent.
- Colour has one job. Green, ochre, red and grey appear only as verdicts, and a verdict is always glyph + word + colour (`{verdicts.works}` ● Works, `{verdicts.degraded}` ▲ Degraded, `{verdicts.fails}` ■ Fails, `{verdicts.nodata}` – No data).
- Every figure is set in `{typography.mono}`: latency, distance, population, dates, counts, file sizes. Prose stays in `{typography.sans}`.
- Every value that came from somewhere shows its source and date beneath it in `{component.source-line}`.
- Phone first: designed at `{size.design-width}`, one column, content capped at `{size.content-max}` and centred on wider screens. No breakpoint changes information order.
- Touch targets are at least `{size.touch}`.

## Colors

### Neutrals
- **Canvas** (`{colors.canvas}`): the page floor and the background of every row.
- **Surface soft** (`{colors.surface-soft}`): expanded service-row source panel; map land fill.
- **Surface card** (`{colors.surface-card}`): assumption note, chips, offline chip, kind chips, pressed rows.
- **Surface strong** (`{colors.surface-strong}`): pressed chips; disabled primary button.
- **Hairline** (`{colors.hairline}`): 1px dividers between service rows, input borders, top bar and footer rules, share card outline.
- **Hairline soft** (`{colors.hairline-soft}`): dividers between result rows and publisher rows, which sit inside a section already bounded by hairlines.

### Text
- **Ink** (`{colors.ink}`): community name, service names, agreement headline, tab selected, links.
- **Body** (`{colors.body}`): reason sentences, publisher detail, note text.
- **Muted** (`{colors.muted}`): source lines, unselected tabs, footer, map outline.
- **Muted soft** (`{colors.muted-soft}`): copyright and licence lines only.
- **On primary** (`{colors.on-primary}`): text on the primary button.

### Action
- **Primary** (`{colors.primary}`): primary button, link colour, focus ring, selected-tab rule, selected-point ring. Press state `{colors.primary-pressed}`. Disabled `{colors.primary-disabled}` with `{colors.muted}` text.

### Removed from the source
Brand accent blue, the badge pastels, success/warning/error semantic colours (replaced by the verdict set below), surface-dark and surface-dark-elevated. Nothing in Crosscheck is dark-on-dark.

## Verdicts

The verdict is the only place chromatic colour appears. Each verdict is a token with four parts and all four are always shown together; colour alone is forbidden.

| Token | Word | Glyph | Text | Fill | Meaning |
|---|---|---|---|---|---|
| `{verdicts.works}` | Works | ● | `{colors.verdict-works-text}` | `{colors.verdict-works-fill}` | Every required figure is met by the best available path |
| `{verdicts.degraded}` | Degraded | ▲ | `{colors.verdict-degraded-text}` | `{colors.verdict-degraded-fill}` | A figure fails on the measured path but a stated assumption could change it; the assumption is printed |
| `{verdicts.fails}` | Fails | ■ | `{colors.verdict-fails-text}` | `{colors.verdict-fails-fill}` | A required figure is not met and no stated assumption changes it |
| `{verdicts.nodata}` | No data | – | `{colors.verdict-nodata-text}` | `{colors.verdict-nodata-fill}` | The requirement or the path figure is not published |

Rules
- Text colours are dark enough to read on `{colors.canvas}` in sunlight and on their own fill (all at or above 4.5:1). The ochre is a dark earth tone, not a yellow.
- Fills appear only behind a verdict badge or in a legend swatch. Never as a row background or a section tint.
- Glyph shapes are reused as the map point shapes: circle, triangle, square, dash. A reader with no colour perception reads the map by shape.
- Green, ochre and red may not appear anywhere that is not a verdict: no green buttons, no red headings, no amber warnings. The one exception is the `{size.rule}` left rule on `{component.assumption-note}`, which uses `{colors.verdict-degraded-text}` because the note exists only to explain a Degraded verdict.
- Every verdict badge carries the reason sentence next to it: the number that fails, the number required, and the source and date of both.

## Typography

### Font family
The app is offline and byte-budgeted, so there are no web fonts: no `@font-face`, no font link, no vendored woff2, no icon font. Two stacks:

- Sans, `{typography.sans}`: `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`. Everything that is a word.
- Mono, `{typography.mono}`: `ui-monospace, "SF Mono", Menlo, Consolas, monospace`. Every figure: latency, distance, population, dates, counts, sizes, coordinates.

**Weights are 400 and 600 only.** Those are the two weights every platform's system font ships with; 500 and 700 are synthesised or substituted inconsistently across Android, iOS and Windows. The hierarchy is built with size and weight 600, never 700.

The source's display face was licensed to its owner and is removed. No display face replaces it; the largest size in the system is `{typography.title-lg}` at 22px.

### Hierarchy

| Token | Size | Weight | Line height | Tracking | Use |
|---|---|---|---|---|---|
| `{typography.title-lg}` | 22px | 600 | 1.3 | -0.3px | Community name |
| `{typography.title-md}` | 18px | 600 | 1.4 | 0 | Agreement headline, section titles ("Services here", "What the sources say") |
| `{typography.title-sm}` | 16px | 600 | 1.4 | 0 | Service name, top bar title, publisher name |
| `{typography.body-md}` | 16px | 400 | 1.5 | 0 | Search input, result rows, plain statements |
| `{typography.body-sm}` | 14px | 400 | 1.5 | 0 | Reason sentences, publisher detail, assumption note |
| `{typography.caption}` | 13px | 400 | 1.4 | 0 | Source lines, legend, footer |
| `{typography.label}` | 13px | 600 | 1.4 | 0 | Verdict badge, chips, kind chip, says-covered badge |
| `{typography.button}` | 14px | 600 | 1 | 0 | Button labels |
| `{typography.tab}` | 14px | 600 | 1.4 | 0 | Filter tabs (selected and unselected share the weight; colour and rule mark selection) |
| `{typography.figure-lg}` | 22px | 400 | 1.3 | 0 | The count in the agreement headline ("3 of 4") |
| `{typography.figure-md}` | 16px | 400 | 1.5 | 0 | Population in the community header |
| `{typography.figure-sm}` | 14px | 400 | 1.5 | 0 | Figures inside reason sentences (665 ms, 100 ms, 0.17 km), data-pack size |
| `{typography.figure-xs}` | 13px | 400 | 1.4 | 0 | Dates in source lines, legend counts |

### Principles
- Words in sans, figures in mono, always. A reason sentence mixes them inline: "latency `665 ms` on satellite vs `100 ms` required".
- Mono stays at 400. Semibold mono is not reliable across system stacks.
- Bigger before bolder: when something needs more emphasis, step up one size before reaching for 600.
- No letter-spacing except `{typography.title-lg}`.

## Layout

### Spacing system
- **Base unit:** 4px.
- **Tokens:** `{spacing.xxs}` 4px · `{spacing.xs}` 8px · `{spacing.sm}` 12px · `{spacing.md}` 16px · `{spacing.lg}` 24px · `{spacing.xl}` 32px · `{spacing.xxl}` 48px. The source's 96px section token is removed; there are no marketing bands.
- **Screen padding:** `{size.screen-pad}` (16px) left and right at every width.
- **Row padding:** `{spacing.sm}` vertical, `{spacing.md}` horizontal.
- **Between a value and its source line:** `{spacing.xxs}`.
- **Between sections:** `{spacing.lg}`, marked by a `{colors.hairline}` rule, not by empty space alone.

### Grid and container
- Designed at `{size.design-width}` (360px), one column.
- Content max width `{size.content-max}` (640px), centred on wider screens. Rows stretch to the container; nothing becomes multi-column.
- No breakpoint changes information order. A laptop shows the same page, wider margins.

### Density
A community's verdict list (header, agreement headline, every service row collapsed) must fit a `{size.viewport-min-height}` (640px) tall viewport without scrolling. Rows are `{size.touch}` minimum and no taller than they need: service name and badge on one line, reason sentence below. Sources are revealed on tap, not shown by default.

### Order on the community screen
1. Name, region, population, with source line.
2. What exists here: services present, WiFi hours, licensed mast, road access.
3. Agreement headline and the four publisher rows.
4. Service verdicts, each with its reason; Degraded verdicts followed by their assumption note.
5. Who does what.
6. Footer.

## Elevation and depth

| Level | Treatment | Use |
|---|---|---|
| Flat | No border, no shadow | Page, rows at rest |
| Hairline | `{size.hairline}` `{colors.hairline}` | Between service rows, around inputs and the share card, under the top bar, above the footer |
| Hairline soft | `{size.hairline}` `{colors.hairline-soft}` | Between result rows and publisher rows |
| Surface change | `{colors.surface-card}` or `{colors.surface-soft}` background | Assumption note, chips, expanded sources panel, pressed rows |
| Rule | `{size.rule}` left rule | Assumption note only |

No drop shadows, no gradients, no blur, no transparency. Sunlight flattens shadows to nothing and alpha-blended type loses contrast; hairlines and surface change survive.

## Shapes

| Token | Value | Use |
|---|---|---|
| `{rounded.xs}` | 4px | Verdict badge, kind chip, assumption note |
| `{rounded.sm}` | 6px | Result-list container |
| `{rounded.md}` | 8px | Buttons, search input |
| `{rounded.lg}` | 12px | Share card |
| `{rounded.xl}` | 16px | Reserved; no current use |
| `{rounded.pill}` | 9999px | Chips, offline chip |
| `{rounded.full}` | 9999px | Map point (works) |

Map points are geometry, not rounded boxes: circle, triangle, square and dash at `{size.map-point}`.

## Components

Each component is documented with default and pressed states only. Hover is not documented.

### Top bar
**`top-bar`** — `{size.topbar}` tall, `{colors.canvas}`, `{size.hairline}` `{colors.hairline}` bottom rule, padding `0 {spacing.md}`. Title "Crosscheck" in `{typography.title-sm}` at left; the three screen names as `{component.filter-tab}` centre or right; `{component.offline-chip}` at right. Sticky at top.

**`offline-chip`** — `{size.chip}` pill, `{colors.surface-card}` fill, `{typography.label}` in `{colors.body}`. Reads "Offline" or "Online". Beneath the label there is no colour cue; the word carries the state.

### Search
**`search-input`** — `{size.control}` tall, `{colors.canvas}`, `{size.hairline}` `{colors.hairline}` border, `{rounded.md}`, padding `0 {spacing.sm}`, `{typography.body-md}`. Placeholder "Search 96 communities" in `{colors.muted}`. Focused: border `{colors.ink}` plus `{component.focus-ring}`.

**`result-row`** — `{size.touch}` minimum, padding `{spacing.sm} {spacing.md}`, `{typography.body-md}` name in `{colors.ink}`, region and population in `{typography.caption}` `{colors.muted}` with the population figure in `{typography.figure-xs}`. Aliases matched by the query are shown in `{typography.caption}` after the name. `{size.hairline}` `{colors.hairline-soft}` between rows. Pressed: `{colors.surface-card}`.

### Community header
**`community-header`** — Name in `{typography.title-lg}`, then region and type in `{typography.body-sm}` `{colors.body}`, then population as `{typography.figure-md}` with the word "people" in `{typography.body-sm}`. Beneath: `{component.source-line}` "ABS 2021 SA1 via BushTel · `2026-06-26`". Padding `{spacing.md}`, `{size.hairline}` `{colors.hairline}` below.

**`source-line`** — `{typography.caption}` in `{colors.muted}`; dates in `{typography.figure-xs}`. Format: source name, middle dot, date. Every value shown in the app has one directly beneath it or reachable by one tap.

### Service row
**`service-row`** — Line 1: service name `{typography.title-sm}` `{colors.ink}` at left, `{component.verdict-badge}` at right. Line 2: reason sentence `{typography.body-sm}` `{colors.body}` with figures inline in `{typography.figure-sm}`: "Latency `665 ms` on satellite vs `100 ms` required". Padding `{spacing.sm} {spacing.md}`, `{size.hairline}` `{colors.hairline}` below. The whole row is the tap target (`{size.touch}` minimum). Pressed: `{colors.surface-card}`.

**`service-row-expanded`** — Opens a `{colors.surface-soft}` panel beneath line 2 listing one `{component.source-line}` per figure ("Failing figure: ACCC MBA · `2024-12-05`", "Required figure: healthdirect · `2025-03-14`") and the path rule with its version. Tap again to close.

**`verdict-badge`** — `{size.badge}` tall, `{rounded.xs}`, padding `0 {spacing.xs}`, `{typography.label}`. Glyph then word: "● Works", "▲ Degraded", "■ Fails", "– No data". Text `{verdicts.*.text}` on `{verdicts.*.fill}`. Never colour alone; never glyph alone.

### Publisher row
**`publisher-row`** — Line 1: publisher name `{typography.title-sm}`, `{component.kind-chip}`, then `{component.says-covered-badge}` at right. Line 2: detail `{typography.caption}` `{colors.body}` ("Telstra 4G outdoor polygon", "Telstra site at `0.06 km`, 74 Perdjert Street"). Line 3: `{component.source-line}` with the date. Padding `{spacing.sm} {spacing.md}`, `{size.hairline}` `{colors.hairline-soft}` below.

**`kind-chip`** — `{size.badge}` tall, `{rounded.xs}`, `{colors.surface-card}`, `{typography.label}` `{colors.body}`. One of: predicted, licensed, listed, portal. A predicted chip is always followed by the words "carrier prediction" in the detail line.

**`says-covered-badge`** — `{typography.label}` `{colors.ink}`, no fill. "Covered", "Not covered" or "Not recorded". It is a claim, not a verdict, so it does not use verdict colour.

### Agreement headline
**`agreement-headline`** — "`3` of `4` sources say covered" in `{typography.title-md}` with the two counts in `{typography.figure-lg}`. Below it, `{typography.caption}` `{colors.muted}`: "Sources disagree" or "Sources agree". Padding `{spacing.md}`.

### Assumption note
**`assumption-note`** — `{colors.surface-card}` block, `{size.rule}` `{colors.verdict-degraded-text}` left rule, `{rounded.xs}`, padding `{spacing.sm} {spacing.md}`, `{typography.body-sm}` `{colors.body}`. First word "Assumption" in `{typography.label}`. Used directly beneath any service row whose verdict is Degraded: "Could work over Telstra 4G if latency is under `100 ms`. No measurement exists here."

### Chip
**`chip`** — `{size.chip}` pill, `{colors.surface-card}`, `{typography.label}` `{colors.body}`, padding `0 {spacing.sm}`. Used for services present ("Health centre", "School", "Public WiFi Mon–Sat 8am–8pm"), fragility flags and colour-by choices. Pressed: `{colors.surface-strong}`.

### Filter tabs
**`filter-tab`** — `{typography.tab}` `{colors.muted}`, padding `{spacing.sm} {spacing.md}`, `{size.touch}` minimum height, `{size.focus-ring}` transparent bottom rule. Tabs sit in a row that scrolls horizontally if it overflows; they never wrap.

**`filter-tab-selected`** — `{colors.ink}` text and a `{size.focus-ring}` `{colors.ink}` bottom rule. Pressed: `{colors.surface-card}` background.

### Map
**`map`** — Inline SVG, no tiles. NT outline stroked `{colors.muted}` at `{size.hairline}`, land `{colors.surface-soft}`, on `{colors.canvas}`. 96 points at `{size.map-point}` in the verdict text colour and the verdict glyph shape: circle Works, triangle Degraded, square Fails, dash No data. Every point is a tap target padded to `{size.touch}`.

**`map-point-selected`** — A `{size.map-point-ring}` ring, `{size.focus-ring}` `{colors.ink}` stroke, around the selected point. The selected community's name in `{typography.label}` beside it.

**`map-legend`** — A row beneath the map, `{typography.caption}` `{colors.body}`, gap `{spacing.md}`: each verdict as glyph + word + count, the count in `{typography.figure-xs}`. "● Works `1` · ▲ Degraded `58` · ■ Fails `11` · – No data `26`".

### Share card
**`share-card`** — `{colors.canvas}`, `{size.hairline}` `{colors.hairline}` border, `{rounded.lg}`, padding `{spacing.lg}`. QR code as inline SVG at `{size.qr}`, `{colors.ink}` modules on `{colors.canvas}`, centred. Beneath: "Data pack `2026-09-30` · `212 KB`" and "App `810 KB`" in `{typography.body-sm}` with figures in `{typography.figure-sm}`, each with its `{component.source-line}`. Two buttons stacked: `{component.button-primary}` "Share this app", `{component.button-secondary}` "Save file". Then the plain statement in `{typography.body-sm}`.

### Buttons
**`button-primary`** — `{colors.primary}` fill, `{colors.on-primary}` text, `{typography.button}`, `{size.control}` tall, padding `0 20px`, `{rounded.md}`. Full width on phone. Pressed: `{colors.primary-pressed}`. Disabled: `{colors.primary-disabled}` with `{colors.muted}` text.

**`button-secondary`** — `{colors.canvas}` fill, `{colors.ink}` text, `{size.hairline}` `{colors.hairline}` border, same size and radius. Pressed: `{colors.surface-card}`.

**`text-link`** — `{colors.ink}`, underlined. Links are never coloured.

**`focus-ring`** — `{size.focus-ring}` solid `{colors.ink}`, offset 2px, on every focusable element.

### Footer
**`footer`** — `{colors.canvas}`, `{size.hairline}` `{colors.hairline}` top rule, padding `{spacing.lg} {spacing.md}`, `{typography.caption}` `{colors.muted}`. One attribution line per source with its licence and date, the team line ("CDU IT Code Fair 2026 · Data Innovation Challenge · Team DIC005"), and the plain statement "Crosscheck does not measure signal." Dates in `{typography.figure-xs}`.

## Content rules

- Sentence case everywhere: headings, buttons, tabs, chips, badges.
- No emoji, no icons, no exclamation marks. The four verdict glyphs are the only non-alphabetic characters that carry meaning.
- No deficit language. Never "vulnerable", "disadvantaged", "at-risk", "underserved", "remote and disadvantaged". Describe the service and the path, not categories of people: "Telehealth video fails on satellite here", not "this community lacks access".
- Every value that came from somewhere shows its source and date beneath it. If the screen is too dense to show it inline, one tap reveals it.
- Empty reads "Not recorded". An unverified value reads "Unverified". Never blank, never "N/A", never "unknown".
- Predicted coverage is always labelled as a carrier prediction, in words, next to the kind chip.
- A community screen shows what exists there before what fails: services present, WiFi hours, a licensed mast, a visiting service come first; verdicts follow.
- Figures keep their units and their precision as published: `665 ms`, `0.06 km`, `2,259`. Dates are ISO `YYYY-MM-DD`.
- Who does what names the addressee: "Carrier: publish measured latency for this site." "DCDD: confirm the clinic's enterprise link technology."
- The app says plainly what it does not do: "It does not measure signal."
- Tone is matter-of-fact. No persuasion, no praise, no reassurance.

## Do's and don'ts

### Do
- Reserve `{colors.primary}` for the primary button, links, focus ring and selected tab. The action layer is monochrome.
- Show every verdict as glyph + word + colour. Reuse the glyph shapes on the map.
- Set every figure in `{typography.mono}` and put its source and date beneath it.
- Build hierarchy with size, weight 600, hairlines and flat grey blocks.
- Keep every tap target at `{size.touch}` or larger, including map points.
- Keep the collapsed verdict list inside a 640px tall viewport.
- Write "Not recorded" and "Unverified" rather than leaving gaps.

### Don't
- Don't use green, ochre or red anywhere that is not a verdict (the assumption-note rule is the one exception).
- Don't show a verdict by colour alone, or by glyph alone.
- Don't use weight 700 or 500, and don't add a display face.
- Don't add drop shadows, gradients, blur or transparency.
- Don't add a second accent colour or coloured links.
- Don't change information order at any breakpoint, or split into columns.
- Don't use icons, emoji, illustrations or images. The QR code and the map are the only graphics, both inline SVG.
- Don't load anything from the network: no fonts, no tiles, no scripts, no analytics.

## Responsive behaviour

### Breakpoints

| Name | Width | Key changes |
|---|---|---|
| Phone | 360–639px | Design width. Content fills width minus `{size.screen-pad}` each side. |
| Wide | 640px and above | Content capped at `{size.content-max}` and centred. Nothing else changes: same order, same one column, same row heights. |

There is no tablet or desktop layout. An analyst on a laptop sees the phone layout with wide margins; that is intentional, so a screen discussed on a phone in a community matches the one on a desk in Darwin.

### Touch targets
- Every button, tab, row, chip that acts, and map point: `{size.touch}` minimum.
- `{component.search-input}` and buttons: `{size.control}` tall.
- Map points are drawn at `{size.map-point}` but hit-tested at `{size.touch}`.

### Text behaviour
- Text wraps; nothing is truncated with an ellipsis. Long community names wrap to two lines in the header.
- Filter tabs scroll horizontally rather than wrapping or shrinking.
- Figures do not wrap mid-value: "`665 ms`" stays together.

## Iteration guide

1. Focus on one component at a time. Reference its YAML key directly (`{component.service-row}`, `{component.assumption-note}`).
2. Variants of an existing component (`-pressed`, `-selected`, `-expanded`, `-disabled`) live as separate entries in `components:`.
3. Use `{token.refs}` everywhere. Never inline hex outside the front matter.
4. Never document hover. Default and pressed states only.
5. Before adding a colour, ask whether it is a verdict. If not, it is a neutral.
6. Before adding a font, stop: the system stack is the font.
7. When in doubt about emphasis: bigger before bolder, and never past 600.
8. When a value appears on screen, add its source line in the same change.

## Known gaps

- Real coordinates for the 96 communities and the NT outline come from the pipeline's BushTel snapshot; the map component here draws a simplified outline and accepts points as `lon`/`lat` props.
- QR code content depends on how the app is finally hosted or shared (URL vs file); the share card takes the encoded modules as a prop.
- Verdict colours were checked for contrast on white and on their own fill by calculation, not on a phone in sunlight. A field check on Challenge Day hardware is advised.
- Rendering of the four glyphs (● ▲ ■ –) varies slightly between platform fonts; sizes are set so the glyph sits on the label's x-height in the common stacks, but it is worth checking on Android.
- Dark mode is not specified. The app is used in sunlight; a dark theme is out of scope for v1.

## Attribution

Adapted from the Cal.com design analysis in VoltAgent/awesome-design-md (MIT licence). Proprietary identity, typeface and marketing components removed; neutral palette, type scale, spacing, radius, elevation, responsive and touch rules, do's and don'ts and iteration guide retained and adapted.
