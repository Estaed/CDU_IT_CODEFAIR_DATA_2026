# Task-06: NT outline, projected points, filters and actions in the pack

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* geometry and pack additions with numeric criteria (byte budget, 96 points inside the view box, filter counts fixed by the spike); no eye needed.

**Lane**
- OWNS: `pipeline/outline.py`, `pipeline/fetch/abs_boundary.py`, `pipeline/pack.py` (additive: `outline`, `points`, `filters`, `actions`), `tests/test_outline.py`, `tests/test_pack.py` (additive)
- MUST NOT TOUCH: `pipeline/sources/*`, `pipeline/merge.py`, `pipeline/rules.py`, `app/`, `scripts/build_app.py`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-05

## Objective

Everything the map screen needs, computed once: the real NT boundary simplified to one SVG path
under a byte budget, the 96 points projected into the mirror's 300×480 view box, the three
analyst filters as membership lists with their counts, and the "who does what" sentences per
disagreement pattern. Also the pack size check that the gate enforces.

## Execution Guide

- `pipeline/fetch/abs_boundary.py`: downloads the ABS ASGS Edition 3 (2021) State and
  Territory boundary GeoPackage (CC BY 4.0) to `data/raw/abs_ste_2021.gpkg` (gitignored if over
  10 MB). Record URL and licence in `provenance.SOURCES` (append one entry).
- `pipeline/outline.py`: `outline_path(gpkg, tolerance_deg) -> str` selects the NT feature,
  keeps the mainland, Tiwi and Groote polygons (the three the mirror draws), simplifies with
  `shapely.simplify(preserve_topology=True)`, projects with the mirror's constants
  (`K = 30, X0 = 128.5, Y0 = -10.5`, `x = (lon - X0) * K`, `y = (Y0 - lat) * K`, one decimal),
  and returns the `M…L…Z` path string. Choose the tolerance that lands under 8,000 bytes and
  record it in the docstring with the byte size measured.
- `pipeline/pack.py` additions: `outline` (the path string), per community `x`, `y` (projected,
  one decimal), `filters`: `[{"id": "all", "label": "All", "ids": [...]}, {"id": "clinic-no-terrestrial", "label": "Clinic, no terrestrial path", "ids": [...]}, {"id": "carrier-yes-list-no", "label": "Carrier says covered, list does not", ...}, {"id": "licensed-no-map", "label": "Licensed mast, no coverage map", ...}]` with the definitions in `design/screens/README.md`; `legend`: telehealth counts over 96; `actions` per community from the disagreement pattern (the "who does what" table in `reports/2026-09-12-spike-20.md` and PRD §4.3): the two Wadeye sentences on `design/screens/community.html` for the 1/1/1/1 pattern with satellite path, "DCDD: verify the licensed site on the ground" for 0/0/1/0, "DCDD: refresh the 2022 list for this community" for 1/0/1/1, and so on for each of the six patterns. Sentence text is data in one dict `ACTIONS_BY_PATTERN`.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0 (this includes `data/out/data_pack.json` ≤ 307,200 bytes).
- [ ] `tests/test_outline.py`: the path string is under 8,000 bytes, starts with `M`, ends with `Z`, contains exactly three closed sub-paths, and every one of the 96 projected points lies inside the 300×480 view box.
- [ ] `tests/test_pack.py`: filter counts are all 96, clinic-no-terrestrial 12, carrier-yes-list-no 14, licensed-no-map 11; legend is works 1, degraded 58, fails 11, nodata 26; every community has at least one action with `who` in `{"Carrier", "DCDD", "Community"}`; Wadeye's actions equal the two sentences on `design/screens/community.html`.
- [ ] `grep -c "abs_ste_2021" pipeline/provenance.py` prints 1.
