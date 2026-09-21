# Task-47: `headline()` reads the health-centre label from a named constant

**Status: DONE** — verified 2026-09-22 (main loop: gate green; `grep PRESENT_SERVICES\[0\]` prints nothing; pack byte size unchanged at 506,433.)

> **Execution:** agent `codex` (small tier) · effort `low`
> *Why:* 2026-09-21. A three-line mechanical change with a byte-identical output as the
> criterion. Codex pool clear (23 % / 35 %).

> **Lane:** OWNS `pipeline/pack.py` (the constant and its two uses), this file · MUST NOT
> TOUCH `tests/`, `app/`, `data/`, `dist/`, `docs/`, `CLAUDE.md` · GATE for this bee: only
> `PYTHONUTF8=1 .venv/Scripts/python -m ruff check --no-cache .` and
> `PYTHONUTF8=1 .venv/Scripts/python -m pytest -m "not browser" -q`. **Do not run
> `run_pipeline.py`, `build_app.py` or `gate.py`**: another bee is building `dist/` right now;
> the main loop runs the pipeline and the gate afterwards. · DEPENDS ON Task-44

## Contract

`pipeline/pack.py`: `headline()` takes the label as `PRESENT_SERVICES[0][1]`, an index that
silently changes meaning if the tuple is reordered. Introduce `HEALTH_CENTRE_LABEL = "Health
centre"` above `PRESENT_SERVICES`, use it inside the tuple's health-centre row and in
`headline()`. No other change; the pack the pipeline writes must be byte-identical apart
from `built`.

## Acceptance Criteria

- [ ] `grep -n "PRESENT_SERVICES\[0\]" pipeline/pack.py` prints nothing.
- [ ] ruff clean; unit tests pass.
