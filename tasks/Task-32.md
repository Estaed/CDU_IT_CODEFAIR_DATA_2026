# Task-32: Remove nearby chat and the Wi-Fi join QR

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* 2026-09-16. Mechanical removal against a complete list; the gate is the criterion.
> Sonnet-tier is enough. Codex is at 100 % until 2026-09-19.

> **Lane:** OWNS `app/nearby.js` (delete), `app/app.js` (only `renderNearby`, the `nearby`
> route, the Nearby button on the share card, `NEARBY_STATUS_LINE`, `wifiText`,
> `escapeWifiField`, `nearbyCard`, `nearbyQr` and whatever those alone made unused),
> `app/app.css` (the `.nearby__*` rules only), `scripts/build_app.py` (the JS order list and
> its comment), `tests/browser/test_nearby.py` (delete), `tests/test_build.py` (the two nearby
> tests), `tests/browser/test_scan.py` and `tests/browser/test_update.py` (nearby mentions
> only), `.github/workflows/pages.yml` (the comment), `BACKLOG.md` (the two nearby lines,
> marked closed), this file · MUST NOT TOUCH `app/transfer.js`, `app/scan.js`, `app/store.js`,
> `pipeline/`, `design/`, `docs/`, `CLAUDE.md` · GATE `PYTHONUTF8=1 .venv/Scripts/python
> scripts/gate.py` · DEPENDS ON none

## Why

PRD §4.2 third batch, 2026-09-16: transfer by camera already carries the app between two
phones with no network; a room-range chat is the one feature a judge could call a gimmick,
and it carried the only WebRTC surface in the app. Report here (Task-35) takes its place.

## Contract

1. `app/nearby.js` and `tests/browser/test_nearby.py` no longer exist.
2. `#/nearby` renders the community screen's default route like any unknown hash (whatever
   `app.js` does today for an unknown route; do not add a redirect).
3. The share card has no `Nearby chat` button; its button row holds Share and Save file.
4. `grep -rn "nearby\|Nearby\|WIFI:\|RTCPeerConnection\|wifiText" app scripts tests` prints
   nothing.
5. `scripts/build_app.py` inlines, in order, `vendor/jsQR.js`, `qr.js`, `scan.js`,
   `transfer.js`, `store.js`, `app.js` (Task-35 inserts `report.js` before `app.js` later).
6. `tests/test_build.py`: `test_nearby_js_no_stun_turn_and_empty_ice_servers` is removed;
   `test_get_user_media_only_in_transfer_and_nearby` becomes
   `test_get_user_media_only_in_transfer` asserting the list is exactly `["transfer.js"]`; a
   new `test_no_rtc_peer_connection_in_app` asserts no file under `app/` contains
   `RTCPeerConnection`.
7. `pages.yml`'s head comment names transfer by camera only.
8. `BACKLOG.md`: the 2026-09-15 Task-18/19 line loses its "and the nearby scan" clause; the
   2026-09-16 Task-19 line is prefixed `Closed 2026-09-16 (nearby chat removed, Task-32):`.
9. Everything that the removal alone made unused is removed (helpers, CSS, imports); nothing
   else is touched.

## Definition of done

Gate green; contract items 1 to 9 each checked by the command or the file named. `dist/index.html`
is smaller than before by at least the size of `nearby.js` (10,371 bytes); say the numbers.

## Status

Status: TODO
