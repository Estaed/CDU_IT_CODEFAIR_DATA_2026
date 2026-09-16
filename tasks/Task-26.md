# Task-26: Small fixes before outside testers, and the page that never updates

> **Execution:** agent `claude-worker` · effort `medium`
> *Why:* five render fixes already described in BACKLOG plus a service worker bug; each has a DOM or static criterion.

**Lane**
- OWNS: `app/app.js` (the header chip, `statementShort`, `renderChanges`), `app/app.css` (link-button underline, changes row, transfer layout only; tokens only), `app/transfer.js` (visibility of the receive result buttons and of the Show frame area only), `app/sw.js`, `scripts/build_app.py` (the `sw.js` copy step only), `tests/browser/test_statement.py`, `tests/browser/test_changes_screen.py`, `tests/browser/test_transfer.py`, `tests/browser/test_smoke.py` (append only), `tests/test_build.py` (append only), `BACKLOG.md` (remove the five entries this task fixes)
- MUST NOT TOUCH: `app/nearby.js` (Task-19), `app/qr.js` (Task-17), `app/layers.css` (Task-21), `pipeline/`, `scripts/gate.py`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-21

## Objective

Tarik wants other people to try the app once the task list is done, so the rough edges they
would hit first are fixed now. The most serious one: a phone that opened the Pages address once
keeps showing that first version forever, because `app/sw.js` serves the page cache-first from a
cache whose name never changes. Tarik saw exactly this on 2026-09-15 ("Pages is still old")
while the server already had the new build.

## Execution Guide

1. **Service worker (the update bug).** `app/sw.js` keeps its role (host-only, never needed for
   first render) and changes three things:
   - Cache name `crosscheck-__BUILD__`; `scripts/build_app.py` writes `dist/sw.js` with
     `__BUILD__` replaced by the first 12 hex characters of the SHA-256 of the final
     `dist/index.html` bytes, so every build installs a new cache.
   - `install` calls `self.skipWaiting()`; `activate` deletes every other cache and calls
     `self.clients.claim()`.
   - `fetch`: requests with `mode === "navigate"` (and `./`, `./index.html`) go **network first**,
     put the fresh response in the cache, and fall back to the cache when the network fails;
     other GET requests stay cache-first as today.
2. **"Send as SMS" is underlined.** The design base rule `a{text-decoration:underline}` wins over
   the button styling on `<a class="button">`. Add `a.button { text-decoration: none; }` beside
   the existing button rules in `app/app.css`.
3. **Changes row on the Share screen.** No trailing `·` after the last item; lay out name,
   sentence and date so a 360 px screen wraps them cleanly (name and sentence wrap together, the
   date on its own line or right-aligned under them, tokens only).
4. **Header chip.** `Offline-ready` while `navigator.onLine` is true, `Offline` when it is false;
   keep updating on the `online` and `offline` events. The app works offline either way, so the
   old word `Online` misled testers.
5. **SMS text.** In `statementShort` only, join services with `" - "` instead of `" · "`, so an
   SMS stays in the GSM-7 alphabet and uses fewer segments. The `·` elsewhere in the UI stays.
6. **Share screen, transfer block.** `Open received app` and `Download crosscheck.html` stay
   hidden until a receive completes; the Show frame area takes no space until Show is tapped.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Main loop at integration, 2026-09-15: GATE GREEN.)
- [x] `tests/test_build.py` (appended): `dist/sw.js` contains `crosscheck-` followed by the first 12 hex characters of the SHA-256 of `dist/index.html`, does not contain `__BUILD__`, and contains `skipWaiting`, `clients.claim` and `navigate`.
- [x] Browser tests: on Wadeye's community screen the `Send as SMS` link has computed `text-decoration-line` equal to `none`; `statementShort` for all 96 communities contains no `·`; the header chip reads `Offline-ready` and, after `context.set_offline(True)` and an `offline` event, `Offline`; on the Share screen the last changes item's text does not end with `·`; before any receive the `Open received app` and `Download crosscheck.html` controls are not visible, and the Show frame area is not visible until Show is clicked.
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/transfer.js` prints nothing; zero non-`file:` requests and no console errors; every existing browser test stays green.
- [x] The five fixed entries are removed from `BACKLOG.md` (Task-13 underline, Task-14 changes row, Task-07 chip, Task-13 separator, Task-18 buttons and empty box).

## Status

DONE 2026-09-15 (main loop: integrated, gate green; mutation check: the chip text back to `Online` turns the smoke test red, restored; `dist/sw.js` carries the build hash. Accepted deviation: `test_host_files_copied` now compares only the manifest, because `sw.js` is no longer a plain copy by design.) Worker notes follow.

Commands run from the worktree root with the main tree's `.venv`:
- `PYTHONUTF8=1 python -m ruff check --no-cache .` → `All checks passed!`
- `PYTHONUTF8=1 python scripts/build_app.py` → `dist\index.html: 574152 bytes`
- `PYTHONUTF8=1 python -m pytest tests/test_build.py tests/browser -q` → 67 passed, exit code 0.
- `gate.py` itself was not run (no `data/raw/` in this worktree, per the lane instructions); the
  three commands above cover lint, build and the two test suites the task touches. The gate's
  own `pytest -m "not browser"` step and the size check were not separately re-run, but nothing
  in this task touches `pipeline/` and the build's printed size (574,152 bytes) is well under
  the 1,048,576-byte limit.

**What actually caused the "Send as SMS" underline**: not what the task file's own hint
described. `.button` in `design/screens/screens.css` (line 101) sets no `text-decoration` at
all, so there was no more-specific rule "winning" over a `.button` rule that already said none —
`app/app.css` had no `.button`/`a.button` rule of any kind before this task. Measured with
Playwright before any change: `getComputedStyle(link).textDecorationLine` was `"underline"`,
coming unopposed from `design/ds/design/base.css`'s `a{text-decoration:underline}` (the only
rule touching decoration on that element). Fix: `a.button { text-decoration: none; }` added to
`app/app.css` (specificity 0,1,1, beats both `a` and `.button` regardless of source order).
`design/` is MUST NOT TOUCH, so the fix could not go where `.button` itself lives; it had to be
a more specific selector in `app/app.css`, which is what the task asked for anyway.

**What actually caused the Show-frame/receive-buttons bug (item 6)**: `transfer.js` already set
the `hidden` attribute correctly on `.transfer__stage`, the `Open received app` button and the
`Download crosscheck.html` link before any change in this task — verified with Playwright
(`getComputedStyle` reported `display: grid` / `display: flex` and `is_visible() == true` on all
three *before* any edit). The real cause: `.transfer__stage` and `.transfer__button` in
`app/app.css` each set their own `display` as normal-author CSS, which the cascade ranks above
the browser's UA-stylesheet `[hidden]{display:none}` regardless of specificity (origin is
compared before specificity) — so the `hidden` attribute had no visual effect. Fix: two
`[hidden]` override rules added beside those two class definitions in `app/app.css`. No change
was needed in `app/transfer.js` itself for this item.

**Deviation from the Lane's "append only" on `tests/test_build.py`**: `test_host_files_copied`
asserted `dist/sw.js` is byte-identical to `app/sw.js`. That assertion is now false by design
(item 1 makes `sw.js` the one host file that is *not* a plain copy) and the test failed on the
unmodified build. Left as-is it would keep the gate red, which contradicts the DoD. Fixed by
narrowing that one existing assertion to `manifest.webmanifest` only (still an exact copy) and
adding the required hash-substitution checks as a new, appended test
(`test_sw_cache_name_is_build_hash`) rather than leaving a test that asserts behaviour item 1
deliberately removes. No other existing test in any owned file was modified.

Reviewer note: `app/layers.css` and `app/nearby.js` were read but not touched (MUST NOT TOUCH).
`app/transfer.js` was read in full; no production edit was needed for item 6, only the CSS fix
above and a browser test confirming the pre-existing `hidden` logic now actually renders hidden.
