# Task-29: Map points cluster by zoom

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
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

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_map.py` (appended): on `#/map` at zoom 1 there is at least one `.map__cluster`, and the sum of all cluster counts plus the visible `.map__community` points equals 96; every cluster's `aria-label` count equals the number it shows and the total of its ring arcs.
- [ ] Same file: after zooming to 8 (wheel events) there are no `.map__cluster` elements and 96 `.map__community` points are visible; clicking the first cluster at zoom 1 raises `data-zoom` above 1 and leaves no cluster with the same member set.
- [ ] Same file: with the `Clinic, no terrestrial path` filter at zoom 1, clusters and visible points add up to that filter's count (read from the pack); with a community selected at zoom 1, its `.map__community` point is visible and it belongs to no cluster.
- [ ] Same file: running the clustering twice for the same zoom and filter yields identical cluster ids, positions and counts (expose the pure grouping function as `window.__map.cluster(points, zoom)` for the test, following the existing `window.__statement` pattern).
- [ ] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing; zero non-`file:` requests and no console errors; every existing map test stays green.

## Status

Not started.
