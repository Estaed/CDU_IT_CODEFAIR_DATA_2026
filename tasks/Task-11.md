# Task-11: Reproduction README, submission packaging, spike retirement

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* the organiser's file rules are transcribed in `docs/report-requirements.md`; the criterion is a zip whose listing and file names match them, checked by a test.

**Lane**
- OWNS: `README.md` (append a "Reproduce" section; the competition text above it stays), `scripts/package_submission.py`, `tests/test_package.py`, deletion of `spike/`
- MUST NOT TOUCH: `pipeline/`, `app/`, `design/`, `docs/`, `tests/fixtures/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-09, Task-10

## Objective

The Python-based solution deliverable (PRD §4.3 / README "What must be handed in" item 4) and
the zip that goes to `itcodefair@cdu.edu.au`: reproduction instructions, the packaging script,
and the removal of the spike now that the pipeline reproduces its table from the fixture.

## Execution Guide

- `README.md` "Reproduce" section: prerequisites (Python 3.13, uv), `uv sync`, the fetch
  scripts and which snapshots are committed vs re-fetched, `scripts/run_pipeline.py`,
  `scripts/build_app.py`, `scripts/gate.py`, where each output lands, and the offline claim with
  the command that verifies it (the browser smoke test). Every command copied from Part 2, run
  once while writing.
- `scripts/package_submission.py`: builds `dist/DataChallenge_Team DIC005_Submission.zip`
  (team number read from `constants.md`) containing `dist/index.html`, `README.md`,
  `pyproject.toml`, `uv.lock`, `pipeline/`, `scripts/`, `tests/`, `data/out/`, the committed
  small raw files under `data/raw/`, and, when present at `submission/`, the report PDF named
  `DataChallenge_Team DIC005_Report.pdf` and the slide deck. If the PDF or deck is missing the
  script prints a warning naming the expected path and still builds the zip (the team adds them
  by hand); the zip never contains `.venv/`, `dist/*.zip`, `spike/` or files over 50 MB.
- Delete `spike/` after confirming `tests/test_merge.py` reads only `tests/fixtures/`. Update
  `.gitignore` (remove the `spike/raw/` line) and `docs/PRD.md` is **not** edited; the PRD's
  references to the spike stay as history.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/test_package.py`: running the packager produces a zip whose name matches `DataChallenge_Team DIC005_*.zip`, that contains `index.html`, `README.md`, `pipeline/rules.py`, `data/out/data_pack.json`, `data/out/capability_table.csv`, and no entry under `.venv/` or `spike/`; total size under 100 MB.
- [ ] `README.md` "Reproduce" section lists every command in Part 2's Entry points and the gate, and `grep -c "spike" README.md` counts only the historical mention in the scaffolding paragraph.
- [ ] `spike/` no longer exists; `grep -rn "spike/" pipeline scripts tests app --include=*.py --include=*.js` prints nothing.
- [ ] `grep -rn "DIC005" scripts/package_submission.py` prints nothing (read from `constants.md`).
