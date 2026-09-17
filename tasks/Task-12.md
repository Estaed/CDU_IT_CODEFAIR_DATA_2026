# Task-12: Freshness, history and changes in the pack

**Status: DONE** — verified 2026-09-15 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

> **Execution:** agent `claude-worker` · effort `medium`
> *Why:* pure pipeline work over the capability table; every criterion is a unit test on hand-built rows or the committed history files.

**Lane**
- OWNS: `pipeline/changes.py` (new), `pipeline/pack.py` (additive: `freshness` per community, `changes` in the header), `scripts/run_pipeline.py` (additive: history write), `data/out/history/`, `tests/test_changes.py`, `tests/test_pack.py` (additive)
- MUST NOT TOUCH: `pipeline/sources/*`, `pipeline/merge.py`, `pipeline/rules.py`, `pipeline/figures.py`, `app/`, `design/`, `tests/browser/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-10

## Objective

Three pack additions that make staleness and drift visible (PRD §4.2 additions, 2026-09-15):
the oldest source under each community, a committed history of every capability table the
pipeline produced, and the list of what changed between the two newest tables.

## Execution Guide

- `pipeline/changes.py`: `diff_tables(older: list[dict], newer: list[dict]) -> list[dict]` over
  plain dicts keyed on `bushtel_id`; compares only the columns the pack shows (verdict columns,
  `best_path`, the four `says_covered` flags, the `svc_*` presence flags) and returns
  `{bushtel_id, name, column, before, after}` rows; `sentence(row) -> str` turns one row into
  plain English ("Public Wi-Fi no longer listed", "Telehealth video: degraded -> fails").
  `newest_pair(history_dir) -> tuple[Path, Path] | None`.
- `scripts/run_pipeline.py`: after the table is written, copy it to
  `data/out/history/capability_table_<built date>.csv` (skip if a byte-identical file for that
  date exists). Seed the folder with the 2026-09-12 fixture as
  `capability_table_2026-09-12.csv` so the first diff is 12 -> 15 September.
- `pack.py`: per community `freshness: {"source": <sources key>, "date": "YYYY-MM-DD"}` = the
  oldest dated line among that community's publisher lines and flags; header
  `changes: {"from": "<date>", "to": "<date>", "items": [{"id", "name", "text", "date"}]}`, items
  in table order. Empty list when there is one history file. Pack stays under 307,200 bytes.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/test_changes.py`: hand-built rows: no change -> `[]`; one verdict flip -> one row with before/after; a community present only in the newer table -> one row `column == "bushtel_id"`; ignored columns (free text, coordinates) never produce a row.
- [x] `tests/test_pack.py` (additive): every community has `freshness` with a key present in `sources` and a date; `changes.items` for the committed history names Milingimbi's `svc_wifi` Y -> N; the pack is under 307,200 bytes.
- [x] `data/out/history/` holds `capability_table_2026-09-12.csv` (byte-equal to the fixture) and `capability_table_2026-09-15.csv`.
- [x] `grep -rn "spike" pipeline/changes.py` prints nothing.

## Status

DONE 2026-09-15 (otopilot, lane gate and main gate green at `552a1a0`; 13 new unit tests). Bee note: the 2026-09-12 history file stores verdicts in the old RAG vocabulary, so `pack.py` recomputes the verdict columns through `rules.py` before diffing; `changes.items` for 12 -> 15 September is exactly Milingimbi's public Wi-Fi.
