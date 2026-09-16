# Task-14: Changes since the previous snapshot on the Share screen

> **Execution:** agent `claude-worker` · effort `medium`
> *Why:* one list rendered from `pack.changes`; criteria are DOM assertions.

**Lane**
- OWNS: `app/app.js` (changes section), `tests/browser/test_changes_screen.py`
- MUST NOT TOUCH: `pipeline/`, `scripts/`, `design/`, `app/app.css`, other files under `tests/browser/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-12, Task-13

## Objective

The project's thesis shown live: between two pipeline runs the published sources moved. A
dated list under the share card: "Milingimbi: public Wi-Fi no longer listed (BushTel,
2026-09-15)". PRD §4.2 additions, 2026-09-15.

## Execution Guide

- `renderChanges(pack)` after the `.share-card`: a section titled `Changes <from> -> <to>`
  using the screens' section vocabulary (`.section`, `.section__title`, `.source-line`); one
  row per `pack.changes.items` with the community name as a `.text-link` to
  `#/community/<id>`, the sentence, and the date. When `items` is empty: one line
  `No changes between <from> and <to>`; when the pack has no `changes`: render nothing.
- No sorting or filtering in the browser: the pipeline orders the list.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/browser/test_changes_screen.py` (marker `browser`): `#/share` shows the section title with both dates, at least one row naming Milingimbi, and its link navigates to `#/community/531`; with `changes.items` emptied in the page before render, the "No changes" line shows.
- [x] Zero non-`file:` requests and no console errors; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing.

## Status

DONE 2026-09-15 (otopilot, lane gate and main gate green at `d054316`; 2 browser tests). Bee note: the empty-items case is tested by patching `JSON.parse` through `page.add_init_script` before the app reads the pack. review-visual pending.
