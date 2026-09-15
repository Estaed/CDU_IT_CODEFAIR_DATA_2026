# Task-26: Small fixes before outside testers, and the page that never updates

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
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

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/test_build.py` (appended): `dist/sw.js` contains `crosscheck-` followed by the first 12 hex characters of the SHA-256 of `dist/index.html`, does not contain `__BUILD__`, and contains `skipWaiting`, `clients.claim` and `navigate`.
- [ ] Browser tests: on Wadeye's community screen the `Send as SMS` link has computed `text-decoration-line` equal to `none`; `statementShort` for all 96 communities contains no `·`; the header chip reads `Offline-ready` and, after `context.set_offline(True)` and an `offline` event, `Offline`; on the Share screen the last changes item's text does not end with `·`; before any receive the `Open received app` and `Download crosscheck.html` controls are not visible, and the Show frame area is not visible until Show is clicked.
- [ ] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/transfer.js` prints nothing; zero non-`file:` requests and no console errors; every existing browser test stays green.
- [ ] The five fixed entries are removed from `BACKLOG.md` (Task-13 underline, Task-14 changes row, Task-07 chip, Task-13 separator, Task-18 buttons and empty box).

## Status

Not started.
