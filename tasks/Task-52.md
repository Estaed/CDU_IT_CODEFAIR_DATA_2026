# Task-52: Tests for the audit fixes, written from the contract

**Status: TODO**

> **Execution:** agent `codex` (small tier) · effort `medium`
> *Why:* 2026-09-22. The producer does not write its own measurement. Runs after Task-51, so it may run the browser suite.

**Lane**
- OWNS: `tests/browser/` (new `test_audit_fixes.py`; string updates in the existing files), this file
- MUST NOT TOUCH: `app/` (Task-51), `pipeline/`, `scripts/`, `data/`, `docs/`, `CLAUDE.md`
- GATE: from the project root, `PYTHONUTF8=1 .venv/Scripts/python -m pytest -m browser -q tests/browser --basetemp=.pytest_tmp` (delete `.pytest_tmp` afterwards) and `PYTHONUTF8=1 .venv/Scripts/python -m ruff check --no-cache tests`
- DEPENDS ON: Task-51

## Objective

Assert Task-51's table from the DOM, without reading how `app/` did it, and update existing
tests whose expected strings moved.

## Execution Guide

Use only Playwright Python APIs the neighbouring tests already use. One test per row of
Task-51's table where the state is reachable headlessly:

- F5: type `zzzz` in the search. F7: all 96 points carry `role=link`, `tabindex=0` and the
  `aria-label` computed from the pack; pressing Enter on a focused point selects it. F8: one
  `h1` per screen with the fixed text. F12, F13, F15: exact texts. F14: inside an opened
  row; the copied statement still says `Best available path`. F18: absent on `#/map`,
  present with `region=top-end`. F20: load the page with `pack_version` rewritten to 99 the
  way the existing older-pack test does it.
- F1, F2, F3, F4, F19 by stubbing before load with `page.add_init_script`:
  `CrosscheckStore.saveReport` rejecting (or `indexedDB.open` throwing),
  `navigator.clipboard.writeText` rejecting together with `document.execCommand` returning
  false, `navigator.mediaDevices.getUserMedia` rejecting with a `NotAllowedError`,
  `navigator.geolocation.getCurrentPosition` calling its error callback. If a state cannot
  be reached headlessly after an honest try, skip that one with a reason in the report;
  never assert on source text instead.
- F9: two `fieldset > legend` with the fixed texts in the report form. F10: every `.chip`,
  `.map-lens__option` and the visible `Reset view` has a rendered height of at least 44 px.
- F11: extend the existing label test to viewports 412 × 915 and 768 × 1024 and add: no two
  visible label boxes intersect.

If a test is red because the APP departs from Task-51, do not bend it: report selector,
expected, actual.

## Acceptance Criteria

- [ ] `pytest -m browser` fully green, or red only with an app departure reported as above.
- [ ] `ruff check --no-cache tests` prints `All checks passed!`.
- [ ] No file outside `tests/` and this file touched.
