# Task-42: Cuts — changes since the previous snapshot, the mesh text, compare

> **Execution:** agent `claude-worker` · effort `medium`
> *Why:* 2026-09-17. Deletion with a green gate as the only criterion; the risk is leaving a
> dangling reference, which the gate catches. Codex is at 100 % until 2026-09-19.

> **Lane:** OWNS `app/app.js` (the `renderChanges`, `renderCompare`, `renderCompareColumn`,
> `statementMesh` functions, the `Compare` result button, the `#/compare` route branch and the
> mesh button and caption only), `app/app.css` (the rules those removed elements used),
> `pipeline/changes.py` (delete), `pipeline/pack.py` (the `changes` header block, `HISTORY_DIR`
> and `changes_header` only), `scripts/run_pipeline.py` (`_write_history_snapshot` and
> `HISTORY`), `data/out/history/` (delete), `tests/test_changes.py`,
> `tests/browser/test_changes_screen.py`, `tests/browser/test_compare.py` (delete all three),
> `tests/browser/test_statement.py` (the two mesh tests), `tests/browser/test_clarity.py` (the
> compare-button assertions), `tests/test_pack.py` (the two `changes` tests), `README.md` (the
> sentence naming the changes list), this file · MUST NOT TOUCH `pipeline/sources/`,
> `pipeline/merge.py`, `pack.publisher_lines`, `transfer.js`, `report.js`, `store.js`, the
> freshness line, the SMS and statement buttons, `design/`, `CLAUDE.md` · GATE `PYTHONUTF8=1
> .venv/Scripts/python scripts/gate.py` · DEPENDS ON none (wave 27, beside Task-38)

## Why

PRD §4.2 fourth batch, last bullet. Three features have no user who would press them: the
pack changes only when the pipeline is rerun, so `Changes since the previous snapshot` lists
what Tarik did; nobody in the 96 communities carries a Meshtastic radio, so the mesh text
serves a report sentence, not a person; and the Priority list (Task-41) is the comparison an
analyst actually wants. Every line removed is one line less to explain on stage.

## Contract

1. **Changes.** `pipeline/changes.py`, `data/out/history/`, `pack.changes_header`, the
   `changes` key in the pack header, `_write_history_snapshot` and the share screen's changes
   section go. `tests/fixtures/capability_table_2026-09-12.csv` stays: the regression test
   reads it.
2. **Mesh.** `statementMesh`, `MESH_MAX_BYTES`, `byteLength` if nothing else uses it, the
   `Copy mesh text` button and its caption, and `window.__statement.mesh` go. `short` and
   `long` stay. The report keeps the 200-byte sentence as prose; the Report line's own 200-byte
   cap in `report.js` is untouched (it is the report's, not the mesh's).
3. **Compare.** The `#/compare` route, both render functions, the `Compare` button in search
   results and its CSS go. An old `#/compare/...` hash falls through to the default community
   route like any unknown hash.
4. **Nothing else moves.** The freshness line, SMS, `Copy statement`, `Report here`, the map
   and the transfer render exactly as before: the browser suite minus the deleted files passes
   unchanged. `test_clarity.py::test_one_search_bar_with_compare_buttons` becomes a test that
   the search bar has no compare button and a result opens its community.
5. **README.** The "Run the pipeline" and "Build the app" paragraphs no longer mention history
   or changes.

## Tests

The gate: ruff clean (no unused imports left by the deletions), the unit suite without
`test_changes.py`, the browser suite without the two deleted files and the two mesh tests.
`grep -rn "changes_header\|statementMesh\|renderCompare\|history" pipeline scripts app tests`
prints nothing (a comment in `report.js` about the report line's cap is allowed).

## Out of the gate

Nothing.

## Status

Status: TODO
