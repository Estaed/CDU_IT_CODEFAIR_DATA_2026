# Task-48: Map v3: three lenses, no clusters, regions that zoom, one screen; the degraded clause

**Status: DONE** — verified 2026-09-22 (main loop: gate green, 212 unit + 117 browser, HTML 982,131 bytes. Four rounds: round 1 (top bee tier) met the contract but read badly at 360 x 780; round 2 raised the height cap and marker sizes; round 3 fixed a label drawn 150 px from its own point, a factual error no test had caught; round 4 put label offsets in screen units after the new DOM-measured label test went red in region views. Eye review at 360 and 412 wide and in the `terra_nt` emulator: `reports/shots/2026-09-22-*`. Lesson: the first spec capped the map too small and gave no label rule; both were spec gaps, not bee errors.)

> **Execution:** agent `codex` (top bee tier) · effort `high`
> *Why:* 2026-09-21 late. The largest render surface in `app.js` (about 700 lines), replaced
> against an exact DOM contract; hard-precision lane. The eye review and the emulator check
> afterwards are the main loop's. Codex pool clear (23 % / 35 %).

> **Lane:** OWNS `app/app.js` (every map function from `cluster` to `renderMap`, the map part
> of `route`, and the one `degraded` branch of the community summary), `app/app.css` (map
> rules, tokens only), `design/screens/README.md` (one dated entry), this file · MUST NOT
> TOUCH `tests/` (Task-49 owns every test change; tests red because the map contract moved
> are expected and reported, not fixed), `pipeline/`, `data/`, `app/index.html`,
> `app/transfer.js`, `app/report.js`, `app/store.js`, `app/qr.js`, `app/scan.js`,
> `app/layers.css`, `app/vendor/`, `design/ds/`, `CLAUDE.md`, `docs/` · GATE
> `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` (you are the only bee allowed to build)
> · DEPENDS ON Task-45

## Why

PRD §4.2 sixth batch. At 360 × 780 the map was unreadable: numbered clusters hid the points,
town names sat under markers, the default colouring made 58 of 96 points identical, and the
legend was below the fold. Tarik gave a free hand; the earlier map rules (zoom clusters,
filters that remove points) are superseded by this contract. Rules that still bind: tokens
only (layer rule 5: no hex, no `px` literal in `app.css`/`app.js`; `vh`, `em`, `%` and the
spacing tokens are fine), no request, no verdict computed in the app (reading `priority.rank`,
a verdict id or a publisher line and choosing a class from it is a render), no `innerHTML`
with pack strings.

## Contract

### 0. The degraded clause (community summary, from Task-45)

For `degraded`, when the telehealth service has an `assumption`: split it on `". "`, take
the first two parts `a1`, `a2` (backticks rendered through `figures()` as today) and write
`A video call with a doctor is not proven to work here. It {a1 with its first letter
lower-cased}. {a2}.` With no assumption, or fewer than two parts, keep Task-45's form
(`…not proven to work here: {reason}.`). Wadeye (426) now reads exactly: `All 4 sources say
Wadeye has mobile coverage. A video call with a doctor is not proven to work here. It could
work over Telstra 4G if latency is under 100 ms. No measurement exists here.` The other three
telehealth clauses do not change.

### 1. Route

`#/map?lens=<fix|service|sources>&region=<slug>&filter=<id>&selected=<id>&layers=<a,b>&service=<id>`.
Defaults (`lens=fix`, no region, `filter=all`, default service) are omitted from hashes the
app writes; unknown values fall back to the default. A region slug is the region name
lower-cased with spaces as `-` (`top-end`, `big-rivers`, `east-arnhem`, `barkly`,
`central-australia`). Every control rewrites the hash and keeps the other parameters.

### 2. DOM, top to bottom inside `main`

```
div.map-lens[role=tablist]
  a.map-lens__option[role=tab][aria-selected]   "Fix first" | "Services" | "Sources"
select (the existing service selector)           rendered ONLY when lens=service
div.map-frame
  svg.map[data-lens][data-zoom][data-region?]    viewBox "0 0 300 480" at rest, no region
  button "Reset view"                            as today; also clears the region
div.map-legend
  span.map-legend__item × n                      per lens, each with its count
section.map-card                                 see §5
nav.map-regions
  a.chip[aria-pressed]                           "All NT" + the five regions, in order of first appearance in pack.communities
details.map-more                                 summary "Highlight and layers"
  (the existing filter tabs, then the existing layer chips, markup and classes unchanged)
ol.map-list                                      see §6
```

- `details.map-more` is closed unless `filter` is not `all` or `layers` is set.
- `div.map-frame` caps the svg's height (a `vh`-based max-height, width following the
  300:480 ratio, centred) so that at 360 × 780, with nothing selected, the bottom edge of
  `div.map-legend` is inside the viewport with no scrolling.

### 3. Points

- There are **always 96** `g.map__community[data-id]`, whatever the filter, region or lens.
  `.map__cluster` no longer exists anywhere; `cluster`, `clusterRingArcs` and
  `renderClusterMarker` are deleted (Principles 6: declared dead means deleted).
- `map__community--dim` on every point outside the active filter's `ids` or outside the
  active region; `map__community--selected` on the selected one. Dim points stay tappable.
- Lens `fix`: `data-tier="1"` for `priority.rank` 1–10, `"2"` for 11–30, `"3"` for the rest;
  a disc in the ink colour, three sizes; tier 1 also holds `text.map__rank` with the rank.
  Legend: `Top 10` (10), `11 to 30` (20), `The rest` (66), counts computed from the pack.
- Lens `service`: exactly today's verdict geometry and classes (`map__pt--works|degraded|
  fails|nodata`) for the selected service; legend as today (glyph, word, count).
- Lens `sources`: `data-sources="measured"` when the community's publisher line of kind
  `measured` says `not-covered`; else `"disagree"` when `agreement.note` is `Sources
  disagree`; else `"agree"`. Measured: ring in the fails colour; disagree: filled ink disc;
  agree: small muted disc. Legend: `Drive test found no signal`, `Sources disagree`,
  `Sources agree`, each with its count.
- Declutter: a pure function `declutter(points, zoom)` exposed exactly the way `cluster` is
  exposed today (same object, new name), `points` = `[{id, x, y}]` in view-box units. It
  returns the same ids in the same order with display positions; deterministic (no
  `Math.random`, no dependence on call history); no point moves more than 14 view-box units
  from its true place; at `zoom >= 8` every point is at its true place; at `zoom = 1` the
  smallest pairwise distance between display positions is at least 6 units (raise the
  iteration count until it holds on the real 96). Offsets shrink continuously as zoom grows.
  Marker sizes stay constant on screen while zooming, as they do today.
- Labels: every label (`text`) gets a halo (`paint-order: stroke`, stroke in the canvas
  colour). Town labels are drawn above the points. Community names show for the selected
  point, for tier 1 in lens `fix`, and for every point from the zoom level at which names
  appear today.

### 4. View

Wheel, pinch, drag and `Reset view` keep today's behaviour and keep writing `data-zoom`.
With `region=<slug>` the view box is the bounding box of that region's true positions
padded by 12 units on each side and widened or heightened to the 300:480 ratio, and
`svg[data-region]` carries the slug. Changing region tweens the view box with
`requestAnimationFrame` over at most 300 ms; under `prefers-reduced-motion: reduce` it jumps.
Marker size, dim state and lens changes ease through CSS `transition` on `opacity` and
`transform`; the selected point carries a slow pulsing ring (CSS keyframes); both are off
under reduced motion.

### 5. `section.map-card`

Nothing selected: `p.map-card__hint` reading `Tap a community.` Selected:
`h2.map-card__name`, the same `p.community-summary` the community screen shows (one
function, called twice), `p.map-card__fix` reading `Fix first #{rank} of {count} ·
{intervention word}` (from `pack.priority` and `pack.priority_interventions`), the four
`.verdict-badge`s in pack order each preceded by its short service name (`SMS_LABEL`), and
`a.button.button--primary` `Open {name}` to `#/community/{id}`. The card replaces
`renderMapPanel`, which is deleted.

### 6. `ol.map-list`

All 96, dim ones last. Order: lens `fix` by rank; lens `service` worst first as today; lens
`sources` measured, then disagree, then agree, then by name. Each `li` links to
`#/map?…&selected=<id>` (keeping the other parameters) and shows the name and, right-aligned,
`#{rank} · {intervention}` / the verdict word / `{covered} of {available} say covered`.

### 7. `design/screens/README.md`

One entry dated 2026-09-21 (late): the map departs from `map.html` by PRD §4.2 sixth batch
(lenses, no clusters, region zoom, dimming filters, capped height, selection card).

## Acceptance Criteria

- [ ] Every selector, attribute and string above exists exactly as written.
- [ ] `grep -n "cluster" app/app.js app/app.css` prints nothing.
- [ ] Layer-rule greps 4, 5, 7, 8, 9 print what they printed before.
- [ ] ruff, unit tests, build and both size checks pass. Browser tests red **only** because
      the map contract or the Wadeye sentence moved are listed in the report; any other
      browser failure is yours.
- [ ] Nothing under `tests/` was edited.

## Report

Files changed, lines removed against added in `app.js`, the measured minimum pairwise
distance at zoom 1, the bottom edge of `.map-legend` at 360 × 780, the red browser tests
with reason, anything you could not do as written and why.
