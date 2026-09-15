# Crosscheck screens

Step 2 of `design/brief.md`: the three screens, built against `design/ds/design/DESIGN.md` and
the token files the mirror's `styles.css` imports. Written 2026-09-12.

Open any file from disk with the machine offline. Each shows the same markup twice, in a
360 × 780 frame and a 768 × 1024 frame, side by side. The markup lives once in a
`<template>`; a six-line inline script clones it into the two frames, so the two cannot
drift. Nothing changes between the frames: no media query, no breakpoint, same order.

| File | Bytes | What it is |
|---|---|---|
| `community.html` | 11 949 | Screen 1, Wadeye |
| `map.html` | 11 298 | Screen 2, filter "Licensed mast, no coverage map", Baniyala selected |
| `share.html` | 9 861 | Screen 3, QR code, data pack, two buttons, plain statement |
| `screens.css` | 12 010 | One class per DESIGN.md component, shared by the three files; tokens only |
| `harness.css` | 1 058 | The two frames; carries the brief's four viewport figures, which are not tokens |
| `assets/build.mjs` | 6 466 | Generates the two SVG fragments below from the CSV and the mirror |
| `assets/map.svg` | 3 149 | NT outline and the filtered points, inlined into `map.html` verbatim |
| `assets/qr.svg` | 6 204 | QR modules, inlined into `share.html` verbatim |

The stylesheet chain is `../ds/styles.css`, which pulls `tokens/colors.css`,
`tokens/typography.css`, `tokens/spacing.css` and `base.css` through the mirror's own imports.
Nothing under `design/ds/` was edited.

## Numbers, recomputed from `spike/out/capability_table.csv`

All 96 rows, computed by `assets/build.mjs` and cross-checked in Python on 2026-09-12. Where
the brief's step 2 carries a different count, the CSV wins and the difference is recorded here.

| On screen | Count | Definition used | Brief said |
|---|---|---|---|
| Licensed mast, no coverage map | 11 | `rrl5=1` and `accc=0` in `mobile_says`: a carrier cellular site licensed within 5 km (ACMA RRL) and no carrier 4G polygon over the point (ACCC MIR 2025). Same 11 as `any_within_5km=1` and `carriers_4g_count=0`. | 11 |
| Clinic, no terrestrial path | 12 | `svc_health_centre=Y` and the PRD §5 best-available-path rule gives satellite: not (`accc=1` and `rrl5=1`), not inside a fixed-line or fixed-wireless footprint. | 41 |
| Carrier says covered, list does not | 14 | `accc=1` and `ntg2022=0` in `mobile_says`. | 19 |
| All | 96 | every row | 96 |

No definition reproduces 41. The two candidates the task named give 69 (health centre and
`nbn_technology` starting with `SATELLITE`, which is 69 of the 70 health centres because 95 of
96 communities are satellite residual, so the filter would say almost nothing) and 11 (health
centre and no carrier 4G polygon). The screen uses the PRD's own definition of a terrestrial
path, which gives 12; the one community beyond the 11 has a carrier polygon but no licensed
site within 5 km, so the path rule does not trust the polygon. Change the label and the count
together if a different definition is preferred. Decided 2026-09-13: the PRD path rule stays; it is
now in the PRD decision log.

Telehealth video verdicts across all 96, shown in the legend: Works 1, Degraded 58, Fails 11,
No data 26. The 11 filtered communities are Orrtipa-Thurra, Manmoyi, Woodycupaldiya, Baniyala,
Birany Birany, Rorruwuy, Mapuru, Amanbidji, Nitjpurru, Rittarangu and Wurankuwu; their
telehealth verdicts are Fails 6 and No data 5, which is why the map shows only squares and
dashes. The legend counts stay at all-96 as the brief asks, with a second line saying 11 of 96
are shown.

Wadeye and Baniyala figures are copied from their CSV rows: population 2259 and 138, nearest
Telstra site 0.064 km ("74 Perdjert Street WADEYE") and 0.17 km ("19 m Mast, Baniyala
Community"), satellite latency 664.9 ms, Baniyala's nearest Telstra 4G polygon 16.367 km.

**BushTel dates.** The brief gives the BushTel portal date as 2026-06-26. The repo does not
contain that date: the snapshot was retrieved 2026-09-12 and the CSV's `profile_last_updated`
is 2026-07-03 for Wadeye and 2025-08-06 for Baniyala. The screens use the profile's own date
from the CSV. The 2019 coverage list has no day-level date in the repo, so its source line
carries the year only.

## The QR code

`assets/build.mjs` runs the mirror's `design/ds/components/share/qr.js` in Node and writes the
module path. It encodes a placeholder address on `example.org` for team DIC005 with the https
scheme, because where the app will be hosted is still open (DESIGN.md, Known gaps). The address
string itself is kept out of every file in this folder so that `grep https` stays at zero. The
29 × 29 matrix (version 3, level M, mask 0) was compared module for module with the `qrcode`
Python package on 2026-09-12: 444 dark modules in both, 0 differences.

## Elements and tokens, per screen

Token names are the CSS custom properties from `design/ds/design/tokens/*.css`; the DESIGN.md
component key is given in the first column. Every class is defined once in `screens.css`.

### Shared by all three screens

| Element (DESIGN.md key) | Class | Tokens |
|---|---|---|
| Page (`layout`) | `.screen`, `.content` | `--surface-page`, `--text-body`, `--text-body-md`, `--size-content-max` |
| Top bar (`top-bar`) | `.top-bar`, `.top-bar__inner`, `.top-bar__title` | `--surface-page`, `--size-hairline`, `--border-hairline`, `--size-topbar`, `--space-md`, `--space-sm`, `--text-title-sm`, `--text-heading` |
| Screen tabs (`filter-tab`, `filter-tab-selected`) | `.tabs`, `.tab`, `.tab[aria-selected=true]` | `--text-tab`, `--text-secondary`, `--tab-selected`, `--space-sm`, `--space-md`, `--size-touch`, `--size-focus-ring`, `--surface-block` (pressed) |
| Offline chip (`offline-chip`) | `.offline-chip` | `--size-chip`, `--space-sm`, `--radius-pill`, `--text-label`, `--text-body`, `--surface-block` |
| Figure (`typography.figure-*`) | `.fig`, `.fig--xs`, `.fig--md`, `.fig--lg` | `--text-figure-sm`, `--text-figure-xs`, `--text-figure-md`, `--text-figure-lg` |
| Source line (`source-line`) | `.source-line` | `--text-caption`, `--text-secondary`, `--space-xxs`, dates in `--text-figure-xs` |
| Section rule and title (`layout`, `typography.title-md`) | `.section`, `.section__title`, `.section__note` | `--space-sm`, `--size-hairline`, `--border-hairline`, `--space-xs`, `--space-md`, `--text-title-md`, `--text-heading`, `--text-caption`, `--text-secondary` |
| Footer (`footer`) | `.footer`, `.footer__team` | `--space-lg`, `--space-md`, `--space-xs`, `--size-hairline`, `--border-hairline`, `--text-caption`, `--text-secondary`, dates in `--text-figure-xs` |
| Focus ring (`focus-ring`) | inherited from the mirror's `base.css` | `--size-focus-ring`, `--focus-ring` |

### community.html

| Element (DESIGN.md key) | Class | Tokens |
|---|---|---|
| Search input (`search-input`) | `.search`, `.search-input` | `--size-control`, `--space-sm`, `--space-md`, `--text-body-md`, `--text-heading`, `--surface-page`, `--size-hairline`, `--border-hairline`, `--radius-md`, placeholder `--text-secondary`, focused border `--text-heading` |
| Community header (`community-header`) | `.community-header`, `__name`, `__meta`, `__population`, `__unit` | `--space-md`, `--size-hairline`, `--border-hairline`, `--text-heading`, `--text-title-lg`, `--tracking-title-lg`, `--space-xxs`, `--text-body-sm`, `--text-body`, `--space-xs`, population in `--text-figure-md` |
| Services present (`chip`) | `.chips`, `.chip` | `--space-xs`, `--space-md`, `--size-chip`, `--space-sm`, `--radius-pill`, `--text-label`, `--text-body`, `--surface-block`, pressed `--surface-pressed` |
| WiFi, STAND, mast, road, backhaul lines (`body-sm` + `source-line`) | `.fact` | `--space-xs`, `--space-md`, `--text-body-sm`, `--text-body`, figures `--text-figure-sm` |
| Agreement headline (`agreement-headline`) | `.agreement`, `__headline`, `__note` | `--space-md`, `--text-heading`, `--text-title-md`, counts `--text-figure-lg`, `--space-xxs`, `--text-caption`, `--text-secondary` |
| Publisher row (`publisher-row`) | `.publisher-row`, `__top`, `__name`, `__detail` | `--space-sm`, `--space-md`, `--size-hairline`, `--border-hairline-soft`, `--space-xs`, `--text-title-sm`, `--text-heading`, `--space-xxs`, `--text-caption`, `--text-body`, figures `--text-figure-xs` |
| Kind chip (`kind-chip`) | `.kind-chip` | `--size-badge`, `--space-xs`, `--radius-xs`, `--text-label`, `--text-body`, `--surface-block` |
| Says-covered badge (`says-covered-badge`) | `.says` | `--text-label`, `--text-heading` |
| Service row (`service-row`, `service-row-pressed`) | `.service-row`, `__button`, `__top`, `__name`, `__reason` | `--size-hairline`, `--border-hairline`, `--size-touch`, `--space-sm`, `--space-md`, `--surface-page`, pressed `--surface-block`, `--text-title-sm`, `--text-heading`, `--space-xxs`, `--text-body-sm`, `--text-body`, figures `--text-figure-sm` |
| Expanded sources (`service-row-expanded`) | `.service-row__sources` | `--space-xxs`, `--space-sm`, `--space-md`, `--surface-soft` |
| Verdict badge (`verdict-badge`) | `.verdict-badge`, `--works`, `--degraded`, `--fails`, `--nodata` | `--space-xxs`, `--size-badge`, `--space-xs`, `--radius-xs`, `--text-label`, `--verdict-*-text`, `--verdict-*-fill` |
| Assumption note (`assumption-note`) | `.assumption-note`, `__label` | `--space-md`, `--space-sm`, `--surface-block`, `--size-rule`, `--verdict-degraded-text`, `--radius-xs`, `--text-body-sm`, `--text-body`, label `--text-label`, `--text-heading` |
| Who does what (`content rules`) | `.actions`, `__item`, `__who` | `--space-sm`, `--space-md`, `--text-body-sm`, `--text-body`, `--size-hairline`, `--border-hairline-soft`, `--text-label`, `--text-heading` |

### map.html

| Element (DESIGN.md key) | Class | Tokens |
|---|---|---|
| Filter tabs (`filter-tab`, `filter-tab-selected`) | `.tabs.filter-tabs`, `.tab`, `.tab__count` | as the screen tabs, plus `--size-hairline`, `--border-hairline` under the row and counts in `--text-figure-xs` |
| Map (`map`) | `.map`, `.map__land`, `.map__community`, `.map__hit` | `--surface-page`, `--map-land`, `--map-outline`, `--size-hairline` |
| Map points (`map`, `pointShapes`) | `.map__pt--works` circle, `--degraded` triangle, `--fails` square, `--nodata` dash | `--verdict-works-text`, `--verdict-degraded-text`, `--verdict-fails-text`, `--verdict-nodata-text` |
| Selected point (`map-point-selected`) | `.map__ring`, `.map__label` | `--focus-ring`, `--size-focus-ring`, `--text-label`, `--text-heading` |
| Legend (`map-legend`) | `.map-legend`, `__row`, `__item`, `__glyph--*`, `__count`, `__subject` | `--space-sm`, `--space-md`, `--text-caption`, `--text-body`, `--space-xxs`, `--verdict-*-text`, counts `--text-figure-xs`, `--text-secondary` |
| Selected community header, agreement, publisher rows, service row, verdict badge | same classes as community.html | same tokens |
| Open link (`text-link`) | `.link-row`, `.text-link` | `--size-touch`, `--space-sm`, `--space-md`, `--text-body-md`, `--link` |

### share.html

| Element (DESIGN.md key) | Class | Tokens |
|---|---|---|
| Share card (`share-card`) | `.share`, `.share-card` | `--space-md`, `--space-lg`, `--surface-page`, `--size-hairline`, `--border-hairline`, `--radius-lg`, `--text-body` |
| QR code (`share-card.qr`) | `.share-card__qr`, `.qr`, `.qr__modules` | `--size-qr`, `--surface-page`, `--text-heading` |
| Data pack and app size (`share-card.meta`) | `.share-card__meta` | `--space-xxs`, `--text-body-sm`, figures `--text-figure-sm` |
| Primary button (`button-primary`, `-pressed`) | `.button.button--primary` | `--size-control`, `--size-touch`, `--space-md` + `--space-xxs` (see below), `--radius-md`, `--text-button`, `--action-primary`, `--text-on-primary`, pressed `--action-primary-pressed` |
| Secondary button (`button-secondary`, `-pressed`) | `.button.button--secondary` | as above with `--surface-page`, `--text-heading`, `--size-hairline`, `--border-hairline`, pressed `--surface-block` |
| Plain statement (`body-sm`) | `.share-card__statement` | `--text-body-sm` |

## Where the screens depart from a literal reading, and why

- **Button padding.** DESIGN.md gives `padding: 0 20px` and no 20px token exists. The screens
  use `calc(var(--space-md) + var(--space-xxs))`, which is 20px composed from tokens.
- **Verdict glyph size.** The mirror's `VerdictBadge.jsx` and `MapLegend.jsx` set the glyph at a
  literal 11px and 12px wide. Those literals are a known deviation in the mirror and were not
  copied: the glyph inherits `--text-label`.
- **SVG geometry.** Point radius 5, hit radius 16, ring radius 9, the outline coordinates and
  the QR path are numbers in SVG user units, taken from `NtMap.jsx` and `qr.js`. They are data,
  not CSS sizes, which is why `grep px` on the HTML stays at zero while the map still draws.
- **Frame sizes.** 360, 780, 768 and 1024 are the brief's viewport figures and live only in
  `harness.css`, outside the screen markup.
- **The map screen shows 11 points, not 96.** The brief asks for the filter tab to be selected
  and showing 11 points; hiding the other 85 is the only way to show a filter without a second
  colour or transparency, both of which DESIGN.md forbids. Run `assets/build.mjs` with the
  filter removed to get the all-96 map.
- **Map colour-by.** PRD §4.2 offers colour by services failing, agreement count or best path.
  None of those maps onto the four verdict colours, which are the only chromatic colours
  DESIGN.md allows, so the points are coloured by the telehealth video verdict and the legend
  says so. The PRD's colour-by choices are a question for the design project, not this folder.
- **Tabs at 360.** Title, three screen tabs at DESIGN.md's tab padding and the offline chip
  do not fit in 360px, and neither do the four filter tabs above the map. Both rows scroll
  horizontally, as DESIGN.md says tabs do when they overflow. In a static file nothing scrolls
  the selected tab into view, so in the phone frame the selected "Share" tab and the selected
  "Licensed mast, no coverage map" filter sit past the right edge. Decided 2026-09-13: the app
  scrolls the selected tab into view on load; DESIGN.md is unchanged. Moving the screen tabs to
  their own row is a v1.1 candidate in `BACKLOG.md`. **Superseded 2026-09-16 (Task-30):** the
  screen tabs now have their own full-width row in the app, and a tab row that still scrolls
  (the map filters) fades on the side that hides more, because Chrome on Android shows no
  scrollbar and testers did not notice the row scrolled.
- **Community screen, Task-30 (2026-09-16, Tarik's phone feedback, decisions delegated).** The
  app departs from `community.html` in six ways: one search bar (Compare sits inside each
  result instead of a second box); a "Use my location" button under it; a one-sentence intro;
  "What the connection allows" comes first, followed by a legend of the four verdict words,
  then the sources, then "What exists here", which is a sentence rather than chips (testers
  read the chips as buttons); and the footer's attribution lines are folded under "Sources and
  licences". The QR codes a camera has to read fill the content width instead of `--size-qr`.
- **Map height at 768.** The mirror's map is `width: 100%; height: auto` on a 300 × 480 view box,
  so inside the 640px content column it would be 1024px tall and the selected label would scale
  with it. Decided 2026-09-13: `screens.css` caps the map at `--size-viewport-min-height` and
  centres it. DESIGN.md sets no cap, so no rule is contradicted; the token is reused, not added.

## Rebuilding

From the project root, with the CSV or the mirror changed:

```
node design/screens/assets/build.mjs
```

Then paste `assets/map.svg` into `map.html` and `assets/qr.svg` into `share.html` in place of
the previous `<svg class="map" …>` and `<svg class="qr" …>` elements.
