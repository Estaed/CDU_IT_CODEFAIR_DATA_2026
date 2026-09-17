# Task-24: Received pack updates the app in place

**Status: DONE** — verified 2026-09-15 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* one storage seam and one startup branch; every criterion is a DOM or storage assertion in the existing browser fixture.

**Lane**
- OWNS: `app/store.js` (new), `app/app.js` (startup pack selection, the update chip, the "use built-in pack" action, and the two receive call sites), `app/transfer.js` (call the store when a received page is complete), `app/nearby.js` (call the store when a `pack` event arrives), `app/app.css` (update chip only, tokens only), `scripts/build_app.py` (the JS tuple only), `tests/browser/test_update.py` (new), `tests/test_build.py` (append only)
- MUST NOT TOUCH: `app/qr.js`, `app/layers.css`, `pipeline/`, `scripts/gate.py`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-26

## Objective

Today a pack that arrives by light (Task-18) opens as a separate downloaded copy, and a pack that
arrives over Wi-Fi (Task-19) is only logged. Tarik's decision 2026-09-15: "update atsın". After
this task, a received pack that is newer than the built-in one is kept in the browser's storage
and used on every later start, so the installed app updates in place with no network. PRD §4.2
second batch (transfer by camera, nearby chat); Blueprint "Pack header" seam.

## Execution Guide

- `app/store.js` exposes `window.CrosscheckStore` with `save(packJson) -> Promise<{built}>`,
  `load() -> Promise<packObject|null>`, `clear() -> Promise<void>`, backed by IndexedDB
  (database `crosscheck`, store `pack`, one record keyed `"pack"` holding the JSON text and its
  `built` date). Reject a pack whose `pack_version` differs from the built-in one or whose
  `communities` count is not 96; never store anything else. Wrap every call so a browser that
  refuses IndexedDB (private mode, some `file://` cases) degrades to "no stored pack", logged
  once, never an error on screen.
- Startup in `app.js`: read the built-in pack from `#pack` as today, then `await
  CrosscheckStore.load()`; if a stored pack exists and its `built` is later than the built-in
  `built`, render from the stored pack. The header shows a chip `Pack updated <built date>` with
  a `Use built-in pack` action that calls `clear()` and reloads. Nothing else in rendering
  changes: every screen already reads from the one `pack` object.
- Receive by light (`transfer.js`): when `reassemble` completes and the page validates, parse the
  received page's `#pack` script text, `save` it, and add a `Use received pack now` button beside
  `Open received app` that reloads the current page. The download button stays.
- Nearby (`nearby.js` / the screen in `app.js`): on the `pack` event, `save` the JSON and show
  `Pack <built> received, tap to use` which reloads.
- No network call, no service worker change; `sw.js` stays untouched. Layer rules 7 and 8 keep
  holding (`store.js` contains none of the network words).

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Main loop at integration, 2026-09-15: GATE GREEN.)
- [x] `tests/browser/test_update.py` (marker `browser`): with no stored pack the header shows no update chip; after `CrosscheckStore.save(json)` of the built-in pack with `built` moved one day later and one community's name changed, a reload renders the changed name on `#/community/<id>` and the chip `Pack updated <date>`; `Use built-in pack` clears the store and the original name returns; `save` of a pack with a different `pack_version` or 95 communities rejects and leaves the store empty.
- [x] Same test: in two pages, a nearby handshake followed by `requestPack()` on the guest leaves the guest's store holding the host's pack (`load()` returns its `built`); feeding the transfer round-trip frames to `reassemble` and calling the receive completion path stores the pack too.
- [x] `tests/test_build.py` (appended): `dist/index.html` contains `window.CrosscheckStore = ` exactly once, placed before `app/app.js`; `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://" app/store.js` prints nothing.
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/store.js app/transfer.js app/nearby.js` prints nothing; zero non-`file:` requests and no console errors on every route; all existing browser tests stay green.

## Status

DONE 2026-09-15 (main loop: three-way cherry-pick onto Task-28 with no conflict, gate green; mutation check: requiring 95 communities in store.js turns the update tests red, restored) Worker notes follow.

Implementation complete; every checkable DoD item above was verified except the gate itself
(this worktree has no `data/raw/`, and the lane's instructions say not to run `gate.py`).
Verified instead, all from the worktree root with the main tree's interpreter:

- `PYTHONUTF8=1 .venv/Scripts/python -m ruff check --no-cache .` -> `All checks passed!`
- `PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py` -> `dist\index.html: 583953 bytes`
- `PYTHONUTF8=1 .venv/Scripts/python -m pytest tests/test_build.py tests/browser -q` -> `73
  passed` (all dots, no failures; includes the 6 new tests in `test_update.py` and the 2
  appended to `test_build.py`).
- `Select-String -Path app\store.js -Pattern 'fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://'`
  -> no output.
- `Select-String -Path app\app.css,app\app.js,app\store.js,app\transfer.js,app\nearby.js -Pattern
  '#[0-9a-fA-F]{3}|[0-9]px'` -> no output.

Files changed:

- `app/store.js` (new): `window.CrosscheckStore` (`save`, `load`, `clear`) backed by IndexedDB,
  database `crosscheck`, store `pack`, one record keyed `"pack"`. `save` reads the built-in pack
  fresh from `#pack` on every call and rejects a candidate whose `pack_version` differs or whose
  `communities` array is not length 96; every IndexedDB call is wrapped so a refusal degrades to
  "no stored pack" (one `console.warn`, never an error on screen).
- `app/app.js`: `pack` is now `let`, reassigned once by `maybeApplyStoredPack()` if
  `CrosscheckStore.load()` resolves with a pack whose `built` is later than the built-in one;
  that function runs after the first synchronous render (`route()`), so the existing tests that
  wait for the first screen are unaffected. Added the update chip (`.chip.update-chip`, built and
  inserted at runtime next to the existing `.offline-chip` inside a new `.header-chips` wrapper,
  since `index.html` is not in this lane's OWNS list) with a `Use built-in pack` button that
  clears the store and reloads. The nearby screen's `pack` event handler now renders a clickable
  `Pack <built> received, tap to use` element (nearby.js already saved the pack before emitting
  the event) instead of the old static "Data pack received." text.
- `app/transfer.js`: `finish()` now extracts the received page's `#pack` script text via the
  already-computed `DOMParser` result and calls `CrosscheckStore.save`; on success a new
  `Use received pack now` button (beside `Open received app`, before `Download crosscheck.html`)
  becomes visible and reloads on click. `buildReceive()` now also returns `finish`, and `mount()`
  tracks it as `mountedReceiveFinish`; a new `testReceiveComplete(bytes)` export drives that same
  completion path from a test with no camera (Playwright/headless Chromium has neither).
- `app/nearby.js`: on `pack-chunk` reassembly completing, awaits `CrosscheckStore.save(json)`
  before emitting the `pack` event, so any listener that reacts to the event can rely on the
  store already holding it.
- `app/app.css`: `.header-chips`, `.update-chip`, `.update-chip[hidden]`, `.update-chip__button`
  (tokens only), and `.nearby__use-pack` (two UA-button-default overrides the existing
  `.nearby__msg--peer` background/border/font rules do not cover).
- `scripts/build_app.py`: `JS_FILES` now inlines `app/store.js` between `nearby.js` and
  `app.js`, matching the order CLAUDE.md Blueprint already names.
- `tests/browser/test_update.py` (new, 6 tests): no-chip-when-empty, save+reload+chip+revert,
  version/count rejection, nearby-guest-store, transfer-receive-store, and a static
  no-network-literal check on `store.js`.
- `tests/test_build.py` (appended): `store.js` inlined exactly once before `app.js`
  (`test_store_js_inlined_once_before_app_js`), and `store.js` carries no network words
  (`test_store_js_has_no_network_words`).

Deviations / judgment calls, both surgical and named here rather than made silently:

1. `index.html` is not listed under this lane's OWNS, so the update chip's DOM (the
   `.header-chips` wrapper and `.chip.update-chip` element) is built and inserted by `app.js` at
   runtime rather than added as static markup in the template. `.offline-chip` itself is untouched
   — same element, same class, just relocated one level deeper into the new wrapper — so the two
   existing offline-chip tests in `tests/browser/test_smoke.py` still pass unmodified.
2. The Execution Guide says nearby.js "or the screen in app.js" saves the pack on the `pack`
   event; I had nearby.js do the `CrosscheckStore.save` (it already owns the full JSON at
   reassembly) and await it before emitting, so app.js's screen code only has to react to the
   event for the UI (parsing `.built` for the message text and wiring the reload). Both files
   still end up doing part of "call the store when a pack event arrives", per the Lane block
   listing that phrase under both `app/nearby.js` and (implicitly, via "the two receive call
   sites") `app/app.js`.
3. `transfer.js`'s `finish()` is private to `buildReceive()`'s closure and is normally reached
   only through the camera scan loop, which headless Chromium cannot exercise (no
   `BarcodeDetector`, no camera). Added `testReceiveComplete(bytes)` to
   `window.CrosscheckTransfer`, documented in the source as test-only, so
   `test_transfer_receive_completion_stores_pack` drives the exact same completion path (parse,
   validate, `CrosscheckStore.save`, reveal the new button) the DoD asks for, the same way
   `window.__statement` and `window.__nearby` are already exposed elsewhere in this codebase for
   the same reason.
