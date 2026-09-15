# Task-08: Map screen in the app

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* reference markup `design/screens/map.html`, geometry already in the pack (Task-06); criteria are DOM counts and hash changes under Playwright.

**Lane**
- OWNS: `app/app.js` (map renderer), `tests/browser/test_map.py`
- MUST NOT TOUCH: `pipeline/`, `scripts/`, `design/`, `tests/browser/test_smoke.py`, `tests/browser/test_community.py` (Task-07)
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-07

## Objective

Screen 2: the NT outline with 96 points shaped and coloured by the telehealth verdict, four
filter tabs with counts, the legend with the all-96 counts and the "showing n of 96" line, the
selected community's panel beneath, and tap-to-open. All from the pack; the browser computes
nothing but which points to show.

## Execution Guide

- `renderMap(filterId, selectedId)` builds the `<svg class="map" viewBox="0 0 300 480">` with
  `<g class="map__land">` (the pack `outline` path) and one `<g class="map__community">` per
  community in the active filter, using the exact point markup of
  `design/screens/assets/build.mjs` (circle r 5 / triangle / 10×10 square / 10×3 dash, hit
  circle r 16, ring r 9 and `<text class="map__label">` for the selected one). Use
  `document.createElementNS` for SVG.
- Filter tabs from `pack.filters`: `<button class="tab" role="tab">` with `.tab__count`; the
  selected tab carries `aria-selected="true"` and is scrolled into view on render (PRD decision
  2026-09-13). Route: `#/map?filter=<id>&selected=<bushtel_id>`; default filter `all`, default
  selected none.
- Legend from `pack.legend` (all 96) plus the subject line and the "Showing n of 96: <filter
  definition>" line, whose definition text is carried in `pack.filters[*].definition` (Task-06
  adds the field if absent; if it is absent, the renderer prints only "Showing n of 96" and the
  task report says so).
- Selected panel: community header block, agreement, publisher rows, the telehealth service
  row and `.link-row` → `#/community/<id>`, reusing the Task-07 render functions.
- Tapping a `.map__community` sets `selected` in the hash; tapping the `.text-link` opens the
  community route.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/browser/test_map.py` (marker `browser`): `#/map` renders 96 `.map__community`; `#/map?filter=licensed-no-map` renders 11, of which 6 carry `.map__pt--fails` and 5 `.map__pt--nodata`; `#/map?filter=clinic-no-terrestrial` renders 12; `#/map?filter=carrier-yes-list-no` renders 14.
- [x] With `selected=458`, exactly one `.map__ring` exists and the `.map__label` text is `Baniyala`; the panel shows `1` of `3` in `.agreement__headline` (was `4` from the mock; PRD decision 2026-09-13 counts only publishers that make a claim; corrected 2026-09-15 by the otopilot main loop) and a `.verdict-badge--fails`.
- [x] Clicking a `.map__community` updates the hash to include its id; clicking `.text-link` navigates to `#/community/458`.
- [x] The legend row shows counts 1, 58, 11, 26 in `.map-legend__count` regardless of the active filter.
- [x] Zero non-`file:` requests and no console errors on every filter route.
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing (SVG attributes `r="5"` etc. are user units, not px, and are allowed).

## Status

DONE 2026-09-15 (otopilot, lane gate and main gate green at `c90c3bf`; `pack.filters[*].definition` absent so the map prints only "Showing n of 96"). review-visual pending.
