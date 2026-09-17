# Task-29: Map points cluster by zoom

**Status: DONE** — verified 2026-09-15 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* a deterministic grouping of 96 points by the live zoom, with DOM-countable criteria (cluster counts add up, tapping zooms in, nothing selected is hidden).

**Lane**
- OWNS: `app/app.js` (the map section only: `renderMap`, `renderPoint`, `attachMapView`, the label code, and a new cluster renderer), `app/app.css` (the map block only, tokens only), `tests/browser/test_map.py` (append only)
- MUST NOT TOUCH: `app/transfer.js`, `app/nearby.js`, `app/scan.js`, `app/vendor/`, `scripts/build_app.py`, `tests/test_build.py` (Task-25 and Task-27), `app/store.js`, `app/layers.css`, `pipeline/`, `scripts/gate.py`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-21

## Objective

Tarik, 2026-09-15, after looking at the AI Challenge app's map: "cluster by zoom". Today the
Top End (Nhulunbuy, the Tiwi Islands, the Darwin rural area) shows overlapping markers at zoom 1
that cannot be told apart or tapped. After this task, nearby points merge into one bubble with a
count while zoomed out, split as the user zooms in, and every bubble still shows how its
communities' verdicts break down, so the map's story survives at every zoom.

## Execution Guide

- **Where it runs.** In the browser, because it depends on the live zoom; it is layout, not a
  verdict (Part 2 "Pushed down" names it as a browser job since 2026-09-15). No pack change.
- **Which points.** The points currently visible under the active filter (with `All` that is all
  96). The selected community is never clustered: it is always drawn as its own point.
- **Algorithm (deterministic).** Radius in view-box units `r = CLUSTER_RADIUS / zoom` with
  `CLUSTER_RADIUS = 12` (a plain number constant) and no clustering at zoom 5 or more. Walk the
  candidate points in ascending `y`, then `x`, then id; each unassigned point takes every other
  unassigned point within `r` (Euclidean in view-box units) into its group; a group of two or more
  becomes a cluster at the members' centroid; a group of one stays a point. Recompute on every
  zoom change, at most once per animation frame (`requestAnimationFrame`), never on pan alone.
- **Cluster marker.** A `<g class="map__cluster" role="button" tabindex="0"
  aria-label="<n> communities">` holding a filled circle, the count as text, and a ring split into
  arcs by the members' telehealth verdict counts (works, degraded, fails, not recorded) using
  `stroke-dasharray` on stacked circles, coloured with the same verdict tokens the points use.
  The marker keeps a constant screen size at any zoom the same way the points already do (the
  `--map-zoom` scale). Member points and their labels are not drawn while clustered.
- **Tap or Enter on a cluster.** Set the `viewBox` to the bounding box of its members with 20
  percent padding, clamped to zoom 1–8 and to the map bounds, and update `data-zoom` the same way
  wheel zoom does, so clusters recompute.
- **Everything else stays.** Filters, the selected-point panel, carrier chips, `Reset view`,
  labels from zoom 3, the 96 `.map__community` groups (clustered ones stay in the DOM with
  `hidden`, so the existing count assertions keep meaning "96 communities on the map").

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Main loop at integration, 2026-09-15: GATE GREEN.)
- [x] `tests/browser/test_map.py` (appended): on `#/map` at zoom 1 there is at least one `.map__cluster`, and the sum of all cluster counts plus the visible `.map__community` points equals 96; every cluster's `aria-label` count equals the number it shows and the total of its ring arcs.
- [x] Same file: after zooming to 8 (wheel events) there are no `.map__cluster` elements and 96 `.map__community` points are visible; clicking the first cluster at zoom 1 raises `data-zoom` above 1 and leaves no cluster with the same member set.
- [x] Same file: with the `Clinic, no terrestrial path` filter at zoom 1, clusters and visible points add up to that filter's count (read from the pack); with a community selected at zoom 1, its `.map__community` point is visible and it belongs to no cluster.
- [x] Same file: running the clustering twice for the same zoom and filter yields identical cluster ids, positions and counts (expose the pure grouping function as `window.__map.cluster(points, zoom)` for the test, following the existing `window.__statement` pattern).
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing; zero non-`file:` requests and no console errors; every existing map test stays green.

## Status

DONE 2026-09-15 (main loop: three-way cherry-pick with no conflict, gate green; mutation check: cluster radius 0 turns the cluster tests red, restored; eye review of the zoom 1 and zoom 3 screenshots: the Top End reads, but radius 12 also pairs points in the sparse south that did not overlap, a candidate to tune after outside feedback) Worker notes follow.

Commands run from this worktree's root, using the main tree's `.venv` interpreter:

- `PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" -m ruff check --no-cache .`
  → `All checks passed!`
- `PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" scripts/build_app.py`
  → `dist\index.html: 593548 bytes`
- `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` → no output (clean).
- `PYTHONUTF8=1 "<PYTHON_ROOT>/.venv/Scripts/python" -m pytest tests/test_build.py tests/browser -q`
  → `........................................................................ [ 90%]` then
    `........                                                                 [100%]`,
    exit code 0, 80 of 80 tests passed (20 in `tests/browser/test_map.py`, 14 pre-existing +
    6 new for this task), 0 failures.

`scripts/gate.py` was **not** run: this worktree carries no `data/raw/`, and the Execution
block for this task explicitly named the substitute command list above instead. `verify-task`
from the main loop, which does have `data/raw/`, is expected to run the real gate.

**Cluster count at zoom 1 with `All` (96 communities):** 24 clusters (52 communities clustered)
plus 44 individual `.map__community` points visible = 96, matching the pack's total. Verified
both by a scratch Playwright script (`clusters: 24 visible points: 44 total points: 96`) and by
`tests/browser/test_map.py::test_clusters_at_zoom1_sum_to_96`.

**What a reviewer should know:**
- The pure grouping function is `window.__map.cluster(points, zoom)` in `app/app.js`, right
  after `telehealthVerdict`. `CLUSTER_RADIUS = 12` and `CLUSTER_MAX_ZOOM = 5` are the two plain
  constants named in the Execution Guide.
- `attachMapView` now takes a fourth argument, `pointGroupsById` (a `Map` from community id to
  its `.map__community` group element), built in `renderMap` so clustered members can be hidden
  and shown again without rebuilding the point markup on every zoom change.
- Clustering recompute is rAF-throttled and triggered only from `zoomAt` (wheel, pinch); pan
  (`pointers.size === 1` in `pointermove`) never calls it. `reset()` and the cluster
  tap-to-zoom handler (`zoomToCluster`) call `updateClustering()` directly since each is a
  single discrete change, not a rapid stream — this keeps `test_reset_view_restores_default_viewbox`
  and the new click-to-split test deterministic without depending on an `requestAnimationFrame`
  firing before the test's next assertion.
- The cluster marker reuses the existing `.map__hit` class (screens.css) for its invisible tap
  target instead of a new one, and joins the existing counter-scale rule in `app.css` (`.map__pt,
  .map__ring, .map__label, .map__town-dot, .map__town-label` now also lists
  `.map__cluster-fill, .map__cluster-arc, .map__cluster-count`) so it holds a constant screen
  size at any zoom, matching the points.
- `test_click_first_cluster_zooms_in_and_splits_it` uses `dispatch_event("click")` rather than
  Playwright's `.click()`: neighbouring cluster hit circles (r 16, same as point hit circles)
  can geometrically overlap on screen at zoom 1, the same reason the pre-existing
  `test_click_point_selects_it` needs an isolated community. Dispatching targets the element
  directly instead of relying on pointer hit-testing.
- Two screenshots for the main loop's eye review are at `reports/spike-map-bytes/map-clusters-zoom1.png`
  (zoom 1, showing clusters with counts and verdict-coloured rings, e.g. a 3-member cluster near
  Nhulunbuy split red/orange) and `reports/spike-map-bytes/map-clusters-zoom3.png` (after
  wheel-zooming toward the Top End to `data-zoom="3"`, where most of that area's clusters have
  already split into individual labelled points; one small cluster remains).
- No deviations from the Execution Guide otherwise: radius formula, walk order, centroid,
  per-verdict ring, hidden members/labels, 20% padded bounding-box zoom-to-cluster, and the
  zoom-5 cutoff are all implemented as specified.
