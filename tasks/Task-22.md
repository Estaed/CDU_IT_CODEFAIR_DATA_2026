# Task-22: Mesh-size statement (200 bytes)

> **Execution:** agent `claude-worker` · effort `medium`
> *Why:* one string builder beside the two existing ones, with a byte-count criterion over all 96 communities.

**Lane**
- OWNS: `app/app.js` (the statement section: `statementShort`, `statementLong`, `renderStatementButtons` and a new `statementMesh`), `tests/browser/test_statement.py` (append only)
- MUST NOT TOUCH: `app/qr.js` and `scripts/build_app.py` (Task-17, same wave), `pipeline/`, `app/app.css`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: none

## Objective

A third text on Screen 1, at most 200 bytes, so one community's verdict fits a single
Meshtastic packet. It turns the report's mesh recommendation into a checked claim. The app does
not talk to a radio; the text is copied and pasted into the mesh app by hand. PRD §4.2 second
batch; PRD §6 "Mesh-size statement fits one packet".

## Execution Guide

- `statementMesh(community)`: ASCII only, `-` separators (GSM-7 friendly, BACKLOG 2026-09-15),
  in this order and dropping from the end until it fits: community name; the four services as
  `Tele OK`, `School LIMITED`, `myGov OK`, `Voice NOT RECORDED` using `SMS_LABEL` and
  `statementWord`; `agree a/b` from the agreement count; the pack's `built` date as `YYYY-MM-DD`;
  `crosscheck`. Assert in code (`throw`) if the result exceeds 200 bytes after every drop, so
  the browser test surfaces it.
- A third button `Copy mesh text` in `renderStatementButtons`, same clipboard path as `Copy
  statement`, with the text also on the button as `data-text` so a test can read it without
  the clipboard. A one-line caption under it: `Fits one LoRa mesh packet (200 bytes)`.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Run by the main loop at integration, 2026-09-15: GATE GREEN.)
- [x] `tests/browser/test_statement.py` (appended): for every community id in `data/out/data_pack.json`, navigating to `#/community/<id>` yields a `button[data-text]` labelled `Copy mesh text` whose `data-text` is at most 200 bytes UTF-8, contains only printable ASCII, starts with the community name and contains `crosscheck`; Wadeye's text is asserted verbatim in the test once the builder is written (the bee writes the expected string into the test from the pack strings, not by hand).
- [x] The existing SMS and statement assertions in the same file stay green.
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.js` prints nothing; zero non-`file:` requests and no console errors.

## Status

DONE 2026-09-15 (main loop: integrated from the worker's worktree, gate green; mutation check:
`MESH_MAX_BYTES` 200 to 100 turns `test_copy_mesh_text` red, restored). Worker notes follow.

Ran (worktree interpreter from the main `.venv`, not `gate.py`): `ruff check --no-cache .` →
`All checks passed!`; `scripts/build_app.py` → `dist\index.html: 320688 bytes`; `pytest
tests/browser/test_statement.py tests/browser/test_community.py tests/browser/test_smoke.py -q`
→ 13 passed, zero non-`file:` requests, zero console errors. Wadeye's mesh text: `Wadeye -
Telehealth video DEGRADED - School video DEGRADED - myGov WORKS - Voice/SMS WORKS - agree 4/4 -
2026-09-15 - crosscheck` (128 bytes UTF-8); no drop was needed for any of the 96 communities —
the longest is Hodgson River Station at 151 bytes, all under the 200-byte limit. `grep -nE
"#[0-9a-fA-F]{3}|[0-9]px" app/app.js` printed nothing.
