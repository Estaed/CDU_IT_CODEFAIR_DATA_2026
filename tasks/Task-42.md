# Task-42: Cuts — changes since the previous snapshot, the mesh text, compare

**Status: DONE** — verified 2026-09-17

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

Status: IMPLEMENTED (2026-09-17, claude-worker sonnet) — awaiting verify-task

**What landed**

1. **Changes.** `pipeline/changes.py` deleted. `pipeline/pack.py`: removed the `changes`
   import, `HISTORY_DIR`, `_refreshed` (a helper used only by `changes_header`, so it went
   too — rule 3), `changes_header`, the `history_dir` parameter of `build_pack`, and the
   `"changes"` key in the pack header. `scripts/run_pipeline.py`: removed `HISTORY`,
   `FIXTURE_SEED`, `_write_history_snapshot`, its call in `main()`, and the now-unused
   `from datetime import date` import. `data/out/history/` deleted (`capability_table_2026-
   09-12.csv`, `capability_table_2026-09-15.csv`, both tracked, removed with `git rm`).
   `tests/fixtures/capability_table_2026-09-12.csv` left in place per the contract.
   `app/app.js`: removed `renderChanges` and its call site in `renderShare` (the `changes`
   const and its slot in the share screen's markup). `app/app.css`: removed the
   `.link-row--changes` block (Task-26's Changes-row wrap rule). `tests/test_changes.py`
   deleted. `tests/browser/test_changes_screen.py` deleted. `tests/test_pack.py`: removed
   `test_changes_names_milingimbi_wifi` and `test_changes_excludes_5g_columns`.
2. **Mesh.** `app/app.js`: removed `MESH_MAX_BYTES`, `byteLength` (unused once
   `statementMesh` was gone), `statementMesh`, and the mesh button/caption/timer block in
   `renderStatementButtons` (now returns just the SMS link and Copy statement button); the
   `mesh` key dropped from `window.__statement`. `short` and `long` untouched.
   `report.js` was not touched (MUST NOT TOUCH); its comment mentioning `MESH_MAX_BYTES`
   stays, as the Tests section allows. `tests/browser/test_statement.py`: removed the mesh
   helper block (`MESH_MAX_BYTES`, `MESH_SMS_LABEL`, `_mesh_word`, `_expected_mesh_text`,
   used only by the two mesh tests) and the two tests `test_mesh_statement_under_limit_for_
   all` and `test_copy_mesh_text`; `test_short_statement_has_no_middle_dot`, which sat
   between them, is untouched.
3. **Compare.** `app/app.js`: removed `renderCompareColumn`, `renderCompare`, the
   `#/compare` route branch in `route()` (an old `#/compare/...` hash now falls through to
   the final `else`, matching no `#/community/(\d+)` pattern, so it renders the default
   community — "like any unknown hash", per the contract), the Compare button block in
   `renderSearch`'s result rows, and the now-dead `openSearch` variable and its use in
   `renderCommunity` (it existed only to focus the search box on the compare fallback's
   unmatched-id case, which no longer exists). `app/app.css`: removed the `.compare` /
   `.compare__column` / `.compare .community-header__name .text-link` / `.compare__service`
   block, and `.result-row__compare` (split out of the shared `.locate-button,
   .result-row__compare` rule, keeping `.locate-button` alone). `tests/browser/
   test_compare.py` deleted. `tests/browser/test_clarity.py::
   test_one_search_bar_with_compare_buttons` rewritten per contract item 4: it now asserts
   no `.result-row__compare` button renders on any result row, and that clicking a result's
   row opens that community (`#/community/<id>`) instead of hashing to `#/compare/...`; the
   module docstring's "per-row Compare" phrase was updated to match.
4. **Nothing else moved.** No other selector, route or render function touched.
5. **README.** Checked: the "Run the pipeline" and "Build the app" paragraphs (and the rest
   of the file) already named neither `history` nor the changes list — nothing to edit.

**Numbers**

- `ruff check --no-cache .`: `All checks passed!`
- Unit tests (`pytest -m "not browser"`): 138 passed (before: 150 — 10 in `test_changes.py`
  + 2 in `test_pack.py`, both removed).
- Browser tests (`pytest -m browser`): 85 passed (before: 97 — 3 in
  `test_changes_screen.py` + 7 in `test_compare.py` + 2 mesh tests in `test_statement.py`,
  all removed).
- `dist/index.html`: 892,413 bytes before edit vs. after — before 899,186 bytes (measured by
  stashing the changes, rebuilding, then restoring), after 892,413 bytes (limit 1,048,576).
- `data/out/data_pack.json`: 445,751 bytes before (committed HEAD) → 445,601 bytes after,
  regenerated with `pack.main()` (limit 512,000).
- Gate: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` → exit 0, `GATE GREEN`.

**Tests-section grep**

`grep -rn "changes_header\|statementMesh\|renderCompare\|history" pipeline scripts app tests`
→ one hit: `scripts/build_app.py:10: gzipped in the browser at Show time. CLAUDE.md Part 2
keeps that history.` — pre-existing prose about Task-36/37's withdrawn lite-copy history,
unrelated to the deleted snapshot-history feature; `scripts/build_app.py` is outside this
task's OWNS and was not touched.

**Deviations**

- `pipeline/pack.py`'s `_refreshed` helper is not named in the Lane block, but it existed
  only to serve `changes_header` (its own docstring says so); deleting `changes_header`
  left it unused, so it was removed under "remove what your changes made unused" rather than
  left as dead code.
- `scripts/run_pipeline.py`'s `from datetime import date` import and `FIXTURE_SEED`
  constant became unused once `_write_history_snapshot` was removed and were deleted for
  the same reason; both are inside this task's named OWNS entry for that file
  (`_write_history_snapshot` and `HISTORY`).
- No edit was needed in `README.md`: contract item 5 anticipated a sentence that, on
  inspection, was not there to begin with (checked, not assumed).
