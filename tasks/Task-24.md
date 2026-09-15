# Task-24: Received pack updates the app in place

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
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
second batch (transfer by camera, nearby chat); Part 2 "Pack header" seam.

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

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_update.py` (marker `browser`): with no stored pack the header shows no update chip; after `CrosscheckStore.save(json)` of the built-in pack with `built` moved one day later and one community's name changed, a reload renders the changed name on `#/community/<id>` and the chip `Pack updated <date>`; `Use built-in pack` clears the store and the original name returns; `save` of a pack with a different `pack_version` or 95 communities rejects and leaves the store empty.
- [ ] Same test: in two pages, a nearby handshake followed by `requestPack()` on the guest leaves the guest's store holding the host's pack (`load()` returns its `built`); feeding the transfer round-trip frames to `reassemble` and calling the receive completion path stores the pack too.
- [ ] `tests/test_build.py` (appended): `dist/index.html` contains `window.CrosscheckStore = ` exactly once, placed before `app/app.js`; `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://" app/store.js` prints nothing.
- [ ] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/store.js app/transfer.js app/nearby.js` prints nothing; zero non-`file:` requests and no console errors on every route; all existing browser tests stay green.

## Status

Not started.
