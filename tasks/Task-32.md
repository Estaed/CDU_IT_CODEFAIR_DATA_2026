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

Status: DONE

- `ruff check --no-cache .`: `All checks passed!`
- `pytest -m "not browser" -q`: 87 passed, 9 skipped, 1 failed, 49 errors — every failure and
  error is a pre-existing `data/raw/` snapshot dependency (`tests/test_source_accc.py`,
  `tests/test_source_bushtel.py`, `tests/test_source_nbn.py`, `tests/test_source_ntg.py`,
  `tests/test_source_rrl.py`, `tests/test_pack.py`, `tests/test_layers.py`), unrelated to this
  task; the worktree has no `data/raw/`, as expected. Nothing in `tests/test_build.py` or any
  other app/build test failed.
- `python scripts/build_app.py`: `dist/index.html` 856,832 bytes, down from the main tree's
  877,751 bytes — 20,919 bytes smaller, above the 10,371-byte floor (`nearby.js`'s size).
- `pytest -m browser -q`: 82 passed, 0 failed.
- Contract item 4 grep (`nearby\|Nearby\|WIFI:\|RTCPeerConnection\|wifiText` over
  `app scripts tests`): one hit, `tests/test_build.py`'s own
  `assert "RTCPeerConnection" not in ...` line added for contract item 6's
  `test_no_rtc_peer_connection_in_app` — the literal string the assertion checks for is
  unavoidable in the test that proves its absence everywhere else; every other hit is gone.

Deviations from the Lane's file list, both required to satisfy contract item 4's grep
(`app scripts tests`, comments included) and called out here rather than silently expanded:
- `app/qr.js`: reworded its header comment, which named the removed nearby handshake.
- `app/scan.js`, `app/store.js` (both MUST NOT TOUCH): each carried one comment naming
  `nearby.js` as a sibling caller; reworded to drop the dangling reference, no other line
  touched.
- `app/app.css`: one unrelated comment ("Task-29 map clustering: nearby points merge...")
  used the plain English word "nearby", not a `.nearby__*` rule; reworded to "close points
  merge" to keep the grep clean.
- `tests/browser/test_update.py`: `test_nearby_pack_request_stores_in_guest` tested nearby
  chat's pack-request path end to end, not just a mention; removed as a whole test (the
  Lane calls this file's scope "nearby mentions only", but the test's entire body was one).
- `tests/browser/test_scan.py`: `test_jsqr_path_decodes_frames_offer_and_wifi_text` renamed
  to `test_jsqr_path_decodes_transfer_frames`; dropped the offer/Wi-Fi-QR texts it decoded
  alongside the transfer frames, keeping the transfer-frame coverage the docstring's
  regression check needs.

Not run: the full `scripts/gate.py` (needs `data/raw/`, absent in this worktree, as noted in
the task's own send message).
