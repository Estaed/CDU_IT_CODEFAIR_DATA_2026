# Task-33: Map, third pass — one shape in four fill states, layers off, service selector, worst-first list

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
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

Status: TODO
