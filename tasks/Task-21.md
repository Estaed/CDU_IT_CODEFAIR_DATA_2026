# Task-21: Map second pass in the app (layers, zoom, pan, labels)

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* rendering pack data with DOM-checkable criteria; whether the result "reads" is the advisory eye review after DONE (PRD §6), not a gate.

**Lane**
- OWNS: `app/app.js` (the map section: `renderMap`, `renderPoint`, `renderFilterTabs`, `renderMapPanel`, and the pack-version check), `app/layers.css` (new), `app/app.css` (map controls only, tokens only), `scripts/build_app.py` (the CSS tuple only), `pipeline/pack.py` (`PACK_VERSION` to 2 only), `tests/test_pack.py` (the version assertion only), `tests/browser/test_map.py` (append only)
- MUST NOT TOUCH: `pipeline/layers.py` (Task-20), `app/qr.js`, `app/transfer.js`, `app/nearby.js`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-19, Task-20

## Objective

Screen 2 stops being 96 dots in a blank outline: coverage shading per carrier with toggles,
region borders, highways, the five towns with labels, pinch-zoom and pan, and community names
once zoomed in. The pack becomes version 2 and the app accepts version 2 only. PRD §4.2 second
batch ("Map, second pass"); Part 2 "Map layer" seam, layer rule 5 (the `layers.css` exception)
and "Pack header".

## Execution Guide

- Draw order inside the existing `svg[viewBox="0 0 300 480"]`, each layer in its own
  `<g data-layer="<id>">`: `area` layers first (coverage, `fill` from `--layer-<id>` with the
  fill opacity token in `layers.css`), then `regions-sa3` (stroke only), then the four highways
  (stroke, wider), then `towns` (a small marker plus a `<text>` label), then the NT outline as
  today, then the 96 `.map__community` points last so they stay tappable. `app/layers.css`
  holds only custom properties: one colour per layer id, one fill opacity, one stroke width
  scale, all values derived from the design tokens where a token exists (carrier colours are
  the deliberate exception, PRD decision 2026-09-15).
- Toggles: one chip per `area` layer (`Telstra`, `Optus`, `TPG`, and MOCN if present) above
  the map beside the filter tabs, toggling the `hidden` attribute on that group; all on by
  default; state kept in the hash query (`&layers=telstra,optus`) so a link reproduces it.
- Zoom and pan by changing the `viewBox` attribute: pointer events on the svg (`touch-action:
  none` on it, set as a class in `app/app.css`); one pointer drags, two pointers pinch (scale
  by the distance ratio, centred between them), `wheel` zooms on desktop; zoom clamped to 1–8;
  a `Reset view` button restores `0 0 300 480`. Point radius and stroke widths use
  `vector-effect="non-scaling-stroke"` or divide by the zoom so they do not grow.
- Community labels: a `<text>` per point with class `map__label`, shown only when zoom is at
  least 3 (`data-zoom` attribute on the svg drives it in CSS); at zoom 8 all 96 read without
  overlap in the dense Top End clusters is *not* required, first come first drawn.
- Pack version: `pipeline/pack.py` `PACK_VERSION = 2`; `app.js` line that refuses unknown
  versions accepts 2 only; `tests/test_pack.py` asserts 2.
- The two filter behaviours and the panel (Task-08 tests) stay as they are.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_map.py` (appended): on `#/map` there is one `g[data-layer]` per layer in the pack (the test reads the ids from `data/out/data_pack.json`); each `area` layer has a chip whose click sets and clears `hidden` on its group; `#/map?layers=telstra` shows only the Telstra area group; five `.map__town` markers with the five names as text; 96 `.map__community` still present and the Task-08 filter counts unchanged.
- [ ] Same test: dispatching a `wheel` event with negative `deltaY` on the svg changes its `viewBox` to a smaller width and sets `data-zoom` above 1; after zoom 3 or more the `.map__label` elements are visible (computed `display` not `none`); `Reset view` restores `0 0 300 480` and `data-zoom="1"`.
- [ ] `tests/test_pack.py`: `pack_version == 2`; the app on a hand-edited version-1 pack shows the refusal message (existing test pattern from Task-07).
- [ ] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing; `app/layers.css` contains only lines matching `^\s*--[a-z0-9-]+:` inside one `:root {}` block and comments.
- [ ] Zero non-`file:` requests and no console errors; `dist/index.html` stays under 1,048,576 bytes.

## Status

Not started.
