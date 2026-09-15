# Task-20: Map layers in the pipeline (towns, highways, regions, coverage)

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* geometry work with byte-count criteria; the tolerances and the cap come from `reports/2026-09-15-map-bytes.md` (OQ13). ⛔ Only if the highway source in that report has no licence line (OQ16): ship towns, regions and coverage, leave `highways` out, and say so in Status. Owner of OQ16: Eko, via `research`.

**Lane**
- OWNS: `pipeline/layers.py` (new), `pipeline/fetch/abs_sa3.py` (new), `pipeline/fetch/roads.py` (new), `pipeline/provenance.py` (append registry entries), `pipeline/pack.py` (the `layers` key only), `scripts/gate.py` (the pack cap figure only), `tests/test_layers.py` (new), `tests/test_pack.py` and `tests/test_build.py` (append only; the cap figure where they read it), `data/out/` (regenerated)
- MUST NOT TOUCH: `app/` (Tasks 17–19, 21), `pipeline/rules.py`, `pipeline/sources/`, `design/`, `CLAUDE.md` (the cap line there is the main loop's)
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: none (reads `reports/2026-09-15-map-bytes.md`, produced outside the task list)

## Objective

The pack carries the geography the map's second pass draws: five towns, four highways, ABS
SA3 regions inside the NT and the ACCC 2025 predicted 4G coverage per carrier, each as
simplified SVG path strings in the pack's projected space, each with a provenance entry.
`pack_version` stays 1 in this task (the key is additive and the app ignores it until
Task-21). PRD §4.2 second batch, OQ13, OQ16; Part 2 "Map layer" seam and `layers.py`.

## Execution Guide

- Read `reports/2026-09-15-map-bytes.md` first: it gives bytes per layer per tolerance and the
  source URLs and licences. Pick the tolerance per layer that the report marks as still
  readable and record the choice as constants at the top of `layers.py` with the report's
  numbers in the comment. The new pack cap is the measured total plus 10 percent headroom,
  rounded up to the next 50 KB; it replaces the one figure in `scripts/gate.py` and wherever
  the tests read it (grep `307200` / `307_200`). Write the chosen figure in the Status block so
  the main loop can copy it into Part 2.
- `pipeline/layers.py`: `towns() -> dict`, `highways(roads_path) -> dict`, `regions(sa3_zip)
  -> dict`, `coverage(carrier, kml_path, boundary) -> dict`, and `build_layers(raw_dir,
  boundary_path) -> list[dict]`. Each layer is `{id, label, kind, src, paths}` per the Part 2
  seam: `kind` is `point` (towns: `paths` = `[{x, y, label}]`), `line` (highways, region
  borders) or `area` (coverage). Geometry via geopandas/shapely as in `pipeline/outline.py`;
  project with `outline.project`; round to 1 decimal; drop rings under 4 projected square
  units; simplify in degrees with `preserve_topology=True`. Layer ids: `towns`, `hwy-stuart`,
  `hwy-barkly`, `hwy-victoria`, `hwy-arnhem`, `regions-sa3`, `cov-telstra`, `cov-optus`,
  `cov-tpg` (add `cov-mocn` only if the report shows it adds information over the three).
- Town coordinates from the source the report names (ABS UCL 2021 centroids or the roads
  dataset's place names); never typed by hand. Five towns: Darwin, Katherine, Tennant Creek,
  Alice Springs, Nhulunbuy.
- `pipeline/fetch/abs_sa3.py` and `pipeline/fetch/roads.py` follow `pipeline/fetch/abs_boundary.py`
  (use `_download.py`, write `data/raw/<source>_<date>.*`); they are run by hand once and the
  files logged in `PROVENANCE.md`. Reuse the ACCC cache the pipeline already writes under
  `data/out/cache/` rather than re-parsing the KMLs.
- `pipeline/provenance.py`: one registry entry per new source (URL, fetch date, size, licence,
  attribution line); every layer's `src` is a key into the pack's `sources` table exactly as
  publisher lines do.
- `pipeline/pack.py`: `"layers": layers.build_layers(...)` in `build_pack`; nothing else moves.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0 with the new cap in `scripts/gate.py`.
- [ ] `tests/test_layers.py`: a hand-built square polygon in lat/lon becomes one path string with the expected projected, rounded coordinates; a ring under 4 square units is dropped; `build_layers` on the frozen `data/raw/` returns the ids listed above (highways may be absent only under the ⛔ case), every layer has `kind` in `{point, line, area}`, non-empty `paths`, and a `src` present in `provenance` with a URL, a date and a licence; the summed UTF-8 bytes of all path strings is at most the figure chosen from the report (assert the number).
- [ ] `tests/test_pack.py` (appended): the pack has a `layers` list whose every `src` is a key of the pack's `sources` table; `pack_version` is still 1; exactly 96 communities still.
- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py` from the root regenerates `data/out/data_pack.json` under the new cap and `data/out/PROVENANCE.md` lists the new sources with licence lines.
- [ ] Layer rule 2 and 3 greps from Part 2 still print nothing; `ruff check --no-cache .` prints `All checks passed!`.

## Status

Not started.
