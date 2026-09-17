# Task-33: Map, third pass — one shape in four fill states, layers off, service selector, worst-first list

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* 2026-09-16. SVG geometry and a sort against a written contract; the gate checks
> counts and classes, the main loop looks at it in the emulator after DONE. Codex is at 100 %.

> **Lane:** OWNS in `app/app.js` the map functions only (`renderPoint`, `clusterRingArcs`,
> `renderClusterMarker`, `renderFilterTabs`, `renderLegend`, `renderMapPanel`,
> `renderLayerGroup`, `renderLayerChips`, the map SVG builder and `renderMap`), `app/app.css`
> (map rules), `tests/browser/test_map.py`, `design/screens/README.md` (one departure entry),
> this file · MUST NOT TOUCH the community render functions (Task-34's), `renderCompare*`,
> `pipeline/`, `design/ds/`, `data/` · GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py`
> · DEPENDS ON Task-34 (the `VERDICTS` glyph table and the badge class it changes)

## Why

Tarik, 2026-09-16: "harita baya çirkin", and "üçgen kare falan sevmedim". Seven marks compete
at once (triangles, squares, dashes, count rings, blue coverage blobs, region borders, tabs
that overflow). The map should show 96 communities and one question at a time. Heat map
rejected (PRD §4.2): 96 points do not make a surface.

## Contract

1. **Point geometry.** `renderPoint` draws every community as one `g.map__pt-group` at its
   projected point holding: for Works, `circle.map__pt.map__pt--works` filled; for Degraded,
   `circle.map__pt.map__pt--degraded` with the ring stroke and a `path.map__pt-half` filling
   the left half-disc; for Fails, `circle.map__pt.map__pt--fails` stroked, no fill; for No
   data, `circle.map__pt.map__pt--nodata` stroked with a dash pattern, no fill. Radius stays
   the pack's `size.map-point` figure as today; stroke width is a token. Fill and stroke
   colours are the verdict text tokens through `app.css` (`design/screens/screens.css`'s
   `.map__pt--*` rules are overridden there, not edited). No `polygon`, no `rect` remains
   among the points.
2. **Cluster ring arcs** keep their verdict colours; the count text stays.
3. **Service selector.** `select.map-service` above the filter tabs with the four services in
   pack order, telehealth video selected by default. Changing it recolours every point and
   cluster arc by that service's verdict, and the legend counts follow. The choice is kept in
   the hash as `&service=<id>` (default omitted) so a link reproduces it. The selected
   community and the filter tabs are unaffected.
4. **Layers off by default.** `details.map-layers` (`summary` `Layers`) holds the existing
   area-layer chips and one new chip for the SA3 region layer; every `area` layer group and the
   region group start `hidden` and a chip shows them. Town dots and labels stay visible. The
   `?layers=` query of Task-21 still forces a layer on. The legend row shows the verdict
   glyphs from `VERDICTS` (now `● ◐ ○ ◌`) with counts as today.
5. **Worst-first list.** `ol.map-list` under the legend: every community the current filter
   shows, sorted Fails, Degraded, No data, Works by the selected service, then by name; each
   `li` holds a `button.map-list__row` with the glyph, the name and the verdict word, opening
   `#/community/<id>`. Its length equals the "Showing n of 96" count.
6. **Nothing else moves.** Zoom, pan, reset, labels at zoom, clusters (Task-29) and the
   selected-community ring behave as before; `test_map.py` keeps every existing test, adapted
   only where a selector above renames what it looks at.

## Test changes

`tests/browser/test_map.py`: `test_all_filter_renders_96` counts `.map__pt-group`;
`test_licensed_no_map_verdicts` and `test_selected_baniyala` use the new classes; new
`test_area_layers_start_hidden`, `test_service_selector_recolours_and_recounts` (switch to
voice and SMS: the legend counts equal the pack's counts for that service, and the point
classes change accordingly), `test_map_list_sorted_worst_first` (length equals the shown
count; verdict order non-increasing in the sequence Fails, Degraded, No data, Works),
`test_no_polygon_points`.

## Departure entry

One bullet in `design/screens/README.md`, dated 2026-09-16: point geometry (fill states for
DESIGN.md's four shapes), layers hidden by default, the service selector, the list.

## Out of the gate

Whether the map now "reads" (main loop, emulator, advisory). The clutter of labels at zoom.

## Status

Status: DONE 2026-09-16 (worker: claude-worker; not run by the lane that wrote the code per
CLAUDE.md's `verify-task` rule -- this is the implementation report, not the gate sign-off).

**Commands run from this worktree's root, using the main tree's `.venv` interpreter:**

```
PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" -m ruff check --no-cache .
  -> All checks passed!
PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" -m pytest tests/test_build.py -q
  -> 19 passed
PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" scripts/build_app.py
  -> dist\index.html: 867887 bytes (limit 1,048,576)
PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" -m pytest -m browser -q
  -> all green
PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" -m pytest tests/test_build.py tests/browser -q
  -> 107 passed in 38.52s
grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js
  -> no output (clean)
```

`data/out/data_pack.json` is untouched (445,751 bytes, unchanged; MUST NOT TOUCH `data/`,
`pipeline/`). `scripts/gate.py` itself was **not** run: this worktree carries no `data/raw/`
(same substitute-command situation every prior worker in this repo has hit); the main loop's
`verify-task` is expected to run the real gate.

**Files touched, all within Lane OWNS:** `app/app.js` (the named map functions plus
`serviceVerdict`, generalised from `telehealthVerdict`, which only those functions called),
`app/app.css` (map rules only), `tests/browser/test_map.py`, `design/screens/README.md` (one
bullet), this file.

**What changed, against the contract:**

1. **Point geometry.** `renderPoint` now draws one `circle.map__pt.map__pt--<verdict>` per
   point (Works filled by `screens.css`'s own untouched rule; Degraded/Fails/No data overridden
   in `app.css` to `fill: none` + a token stroke width, coloured by the verdict text token) plus,
   for Degraded only, a `path.map__pt-half` (a left half-disc, `M...A r,r 0 0 0...Z`, geometry
   derived from the existing `size` constant, not a token) and, for No data, a
   `stroke-dasharray` on the circle itself, same derivation. No `polygon`, no `rect` remains
   among the points (`test_no_polygon_points`). Both shapes for a point are wrapped in one
   `g.map__pt-shape` so the existing zoom counter-scale transform (`transform-box: fill-box;
   transform-origin: center`) anchors on the *circle's* bounding box rather than the half-path's
   own off-centre one -- see Deviation 1.
2. **Cluster ring arcs**: untouched, as instructed.
3. **Service selector.** `select.map-service`, options in the pack's own service order (read
   from `pack.communities[0].services`, never a hardcoded list), telehealth video the default,
   kept in the hash as `&service=<id>` with the default omitted. Changing it re-derives every
   point's and cluster's verdict (`serviceVerdict`, generalised from the old
   `telehealthVerdict`) and the legend's tally (`legendCounts`, a count over `pack.communities`
   for the chosen service -- not a verdict, the same allowance the cluster ring's own per-verdict
   tally already uses). The active filter and selected community pass through unchanged.
4. **Layers off by default.** `details.map-layers` (`summary` "Layers") wraps the chip row;
   `isToggleLayer` now covers both `area` and `line` kind layers (today only `regions-sa3` is
   `line`), all starting hidden; `renderMap`'s default `visibleSlugs` is now an empty `Set`
   instead of "every area layer"; the chip-click hash encoding flipped to match (`null` when
   nothing is shown, not when everything is). Town markers (`kind: "point"`) are never in the
   toggle list and stay visible. `?layers=` still forces the named layers on, unchanged.
5. **Worst-first list.** `ol.actions.map-list` under the legend, one `li.service-row` >
   `button.service-row__button.map-list__row` per shown community, sorted by
   `["fails","degraded","nodata","works"].indexOf(verdict)` then `name.localeCompare`; reuses
   `.service-row`/`.service-row__button`/`.service-row__top`/`.service-row__label`/
   `.service-row__glyph--*` from `screens.css` (Task-34's community-screen rows) rather than
   inventing new row CSS -- zero new CSS beyond `.map-list { margin-top: ... }`. Its length is
   `shown.length` by construction, so it always equals "Showing n of 96".
6. **Nothing else moves.** Zoom, pan, reset, labels at zoom, clusters and the selected-community
   ring are untouched; every pre-existing test in `test_map.py` still passes.

**Deviations, surfaced per Part 1 rule 3:**

1. **A new `g.map__pt-shape` wrapper, not named in the contract.** The counter-scale rule
   (Task-21/29) scales each element around its own fill-box centre. A lone `path.map__pt-half`'s
   own bounding box is only the left square of the circle's footprint, so scaling it around its
   *own* centre would drift it away from the circle at any zoom but 1. Wrapping the circle and
   the half-path together makes their shared bounding box the full circle again (the half-path's
   box is a subset of the circle's), so "centre" resolves to the circle's actual centre. The
   counter-scale class list in `app.css` now reads `.map__pt-shape` where it read `.map__pt`.
   Verified by eye at zoom 4 with a Degraded point: the half-disc stays aligned with its ring
   through the zoom range instead of sliding left.
2. **A module-level `layersFoldOpen` flag, not named in the contract.** `renderMap` rebuilds the
   entire panel -- including a fresh `<details>` with no `open` attribute -- on every hash
   change, and a layer chip click *is* a hash change (it still routes through `mapHash` so the
   `?layers=` state survives). Without persisting the fold's own open/closed state outside the
   hash, the first chip click would re-close the fold and a second click on the same chip would
   hit an invisible (closed-`details`) element. Caught by the adapted
   `test_area_chip_toggles_hidden_on_its_group` itself failing on its *second* `chip.click()`
   with a Playwright "element is not visible" timeout before this fix. Not part of the hash
   contract (Task-33 names only `&service=` as new hash state), so a plain `let`, read on render
   and written on the native `toggle` event, the same pattern `let pack` already uses for the
   one other piece of state that survives a re-render.
3. **`test_area_chip_toggles_hidden_on_its_group` rewritten, not just adapted for a renamed
   selector.** The Test changes section names four new tests and two selector adaptations; this
   fifth, pre-existing test asserted the *old* "visible by default" behaviour, which contract
   item 4 inverts on purpose. Rewrote its body (open the fold first via `summary.click()`, since
   `details` defaults to closed and chips inside a closed one are not Playwright-actionable;
   assert hidden by default; two clicks toggle visible then hidden again) rather than leaving it
   red. Kept the test name and its target layer (the first area layer).
4. **Toggle scope is `kind === "area" || kind === "line"`, not "area layers plus the id
   `regions-sa3` by name.** The contract's literal wording ("the existing area-layer chips and
   one new chip for the SA3 region layer") names one specific layer; today `regions-sa3` is the
   only `line`-kind layer in the pack, so both readings produce an identical chip list. Chose the
   kind-based rule instead of an id check because "line" already means "region border" in
   `renderLayerGroup`'s existing kind switch, and a hardcoded id inside app.js would be exactly
   the kind of per-layer special-case Blueprint's "the app draws any layer it is given" seam is
   meant to avoid. Flagging in case a future line-kind layer (e.g. a highways layer, named in
   Task-21's own Objective prose but never built) is meant to default *visible* rather than
   hidden -- nothing in Task-33 says either way for a layer that does not exist yet.
5. **Legend subject line now names the selected service** ("Voice and SMS · all 96 communities"
   instead of a permanently hardcoded "Telehealth video · ..."). Not required by any acceptance
   criterion or named test, but leaving the old literal in place while the counts underneath it
   changed with the selector would have been actively misleading on the one screen a judge
   might read closely. `pack.legend`'s own on-disk telehealth-only counts are unused now (the
   legend always reads a fresh `legendCounts(serviceId)` tally, which reproduces
   `pack.legend` exactly when `serviceId` is the default -- checked by
   `test_service_selector_recolours_and_recounts`'s companion existing tests, e.g.
   `test_filter_routes`, still asserting `["1","58","11","26"]`).
6. **Stroke width token reused, not added.** The contract says "stroke width is a token" but
   names none; `--size-focus-ring` (2px) was already the stroke width for `.map__ring` and the
   Task-29 cluster ring arcs, so the Degraded/Fails/No-data point outlines reuse it rather than
   adding a new custom property to `app/layers.css` (that file's own scope is map *layers*, not
   point markers, so a new property there would also have been the wrong file). No token was
   added anywhere.
7. **Dash pattern and half-disc arc are plain JS geometry, not tokens.** `stroke-dasharray`
   (`"5 2.5"`, derived from `size`) and the half-disc's path `d` are computed the same way the
   pre-existing rect width/height and the Task-29 `CLUSTER_RADIUS` constant already are:
   SVG geometry in user units, which `design/screens/README.md`'s own "SVG geometry" departure
   entry already treats as data, not a CSS size (layer rule 5). Only the *stroke width* is
   called out by the contract as needing to be a token; these are not.

**Not run here, per the run instructions:** `scripts/gate.py` proper and `tests/test_pack.py`
(both need `data/raw/`, absent in this worktree, same as every prior task's Status in this repo).
