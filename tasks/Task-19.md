# Task-19: Nearby chat over the phone's own Wi-Fi

**Status: DONE** — verified 2026-09-15 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* the channel contract is fixed in Part 2 and proven by the 2026-09-15 spike; the loopback criterion runs headless. The hotspot case (OQ14) is Tarik's manual check, not gated.

**Lane**
- OWNS: `app/nearby.js` (new), `app/app.js` (the `#/nearby` route and screen, plus one "Nearby chat" button on the share screen), `app/app.css` (nearby block only, tokens only), `scripts/build_app.py` (the JS tuple only), `tests/browser/test_nearby.py` (new), `tests/test_build.py` (append only)
- MUST NOT TOUCH: `app/qr.js` (Task-17), `app/transfer.js` (Task-18), `pipeline/` and `scripts/gate.py` (Task-20), `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-18

## Objective

Two phones on one Wi-Fi (a personal hotspot or any router) chat directly, browser to browser,
after scanning each other's QR once. No server, no STUN, no TURN, no storage. The same channel
hands over the data pack on request. The screen also shows a Wi-Fi join QR for the host's
hotspot. PRD §4.2 second batch; Part 2 "Entry points: Nearby chat"; spike
`reports/spike-webrtc-hotspot/` is the working reference for the WebRTC calls.

## Execution Guide

- `app/nearby.js` exposes `window.CrosscheckNearby` with `start() -> Promise<string>` (host:
  creates `new RTCPeerConnection({ iceServers: [] })`, the `chat` data channel, the offer, waits
  for `icegatheringstate === "complete"` or 3 s, returns the offer text), `accept(offerText) ->
  Promise<string>` (guest: sets remote, answers, gathers, returns the answer text),
  `finish(answerText)` (host: sets remote), `send(text)`, `requestPack()`, `close()`, and an
  `onEvent(handler)` for `{ type: "state" | "msg" | "pack" | "error", ... }`. Offer and answer
  text = the full SDP JSON `{type, sdp}` deflated with `CompressionStream("deflate-raw")` and
  base64-encoded; the other side inflates and parses. Field-level SDP reduction only if a real
  offer exceeds 1,200 characters after this (measure in the test and record the number in the
  Status block).
- The channel protocol: `{t:"msg", text}`, `{t:"pack"}` and `{t:"pack-data", json}` where `json`
  is the pack from `document.getElementById("pack").textContent`. Messages are held in a plain
  array on the screen; a reload empties it, by design.
- Screen `#/nearby`, reached from a `Nearby chat` button on the share screen (not a fourth
  tab; the top bar overflows at 360 px already, BACKLOG 2026-09-13). Cards in order: a status
  line that reads `Works while both phones are on this Wi-Fi` and the current state; `Host`
  (Start → offer QR via `CrosscheckQR` + `toSvgPath`, then Scan their answer); `Join` (Scan
  their code → answer QR); the message list and a text input with Send, disabled until open;
  `Send data pack`; and a `Wi-Fi join code` card with two inputs (network name, password) and
  the QR of `WIFI:T:WPA;S:<ssid>;P:<password>;;` rendered live, with the special characters
  `\ ; , : "` escaped with a backslash as the format requires. Nothing is persisted.
- Scanning uses `BarcodeDetector` on a `<video>` exactly as `transfer.js` does; share the
  camera helper by calling `CrosscheckTransfer`'s scanner if it exposes one, otherwise a
  30-line copy in `nearby.js` (say which in the Status block). Where `BarcodeDetector` is
  absent, the Scan buttons are disabled with the one-sentence note (OQ15).
- Every stream and the peer connection are closed on route change (`hashchange`).

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Main loop at integration, 2026-09-15: GATE GREEN, 40 browser tests.)
- [x] `tests/browser/test_nearby.py` (marker `browser`): two pages in the fixture browser both open `dist/index.html#/nearby`; page A `CrosscheckNearby.start()` → offer text (at most 2,900 characters, so it fits one QR at level L); page B `accept(offer)` → answer text; page A `finish(answer)`; within 10 s both pages report state `open`; A `send("hello")` appears in B's `.nearby__messages` as a `peer` line and in A's as a `me` line; B `requestPack()` → B's event log holds a `pack` event whose json parses to 96 communities. `close()` on both ends leaves state `closed`.
- [x] Same test: the Wi-Fi card renders a QR after typing `Crosscheck` and `pass;word`, and the encoded text (exposed as `data-text` on the QR container) is `WIFI:T:WPA;S:Crosscheck;P:pass\;word;;`.
- [x] `tests/test_build.py` (appended): `app/nearby.js` contains `iceServers: []` and none of `stun:`, `turn:`; `grep -l getUserMedia app/*.js` prints exactly `app/nearby.js` and `app/transfer.js`.
- [x] `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://" app/nearby.js` prints nothing; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/nearby.js` prints nothing.
- [x] Zero non-`file:` requests and no console errors on every route; the share screen tests stay green.

## Status

DONE 2026-09-15 (main loop: integrated, gate green; mutation check: labelling a received
message as `me` turns the loopback test red, restored. The chunked pack transfer is the right
call and Part 2's contract line is amended to say so.) Worker notes follow.

Implemented `app/nearby.js` (`window.CrosscheckNearby`: `start`, `accept`, `finish`, `send`,
`requestPack`, `close`, `onEvent`, plus `buildScanButton` — see deviation below), the `#/nearby`
screen and its `Nearby chat` button in `app/app.js`, the `nearby__*` block in `app/app.css`, and
added `app/nearby.js` to `JS_FILES` in `scripts/build_app.py` between `transfer.js` and `app.js`.

Commands run from the worktree root with the main tree's `.venv`:
- `ruff check --no-cache .` → `All checks passed!`
- `scripts/build_app.py` → `dist\index.html: 559961 bytes` (well under the 1,048,576 limit)
- `pytest tests/test_build.py tests/browser -q` → `50 passed in 22.10s`

Measured offer text length: **600 characters** (SDP JSON, deflated with `CompressionStream
("deflate-raw")`, base64-encoded) — far under the 1,200-character field-reduction threshold and
the 2,900-character QR-level-L ceiling in the DoD, so no SDP field-level reduction was needed.

Deviations from a literal reading of the Execution Guide, both load-bearing:

1. **Pack transfer is chunked on the wire.** The Execution Guide's channel protocol names
   `{t:"pack"}` / `{t:"pack-data", json}` as if the whole pack fit one data-channel message.
   Measured 2026-09-15: `data/out/data_pack.json` is 445,751 bytes, and Chromium's
   `RTCDataChannel.send` throws `"Trying to send message larger than max-message-size"` on a
   message that size (confirmed with a throwaway repro before fixing; not committed). Sending
   the pack as-is silently corrupts the run — page A's console got a pageerror and the message
   never left. Fixed by adding a transport-only message shape,
   `{t:"pack-chunk", i, n, part}` (16,000 characters per chunk, well under any observed
   message-size limit), that the sender loops over and the receiver reassembles before emitting
   the same logical `{type:"pack", json}` event `onEvent` consumers see — the documented API
   surface (`requestPack()`, the `pack` event) is unchanged; only the wire format gained one
   internal message type invisible outside `nearby.js`.
2. **Scanner helper lives in `nearby.js`, exposed as `buildScanButton`.** `CrosscheckTransfer`
   exposes no reusable scanner (`{ frames, reassemble, inflate, mount }` only), so per the
   Execution Guide a ~30-line copy was written in `nearby.js` (`buildScanButton`, ~55 lines
   including the button/video DOM it needs to own so `getUserMedia` stays out of `app.js` —
   layer rule 8's `grep -l getUserMedia app/*.js` check). It is not in the Execution Guide's
   `window.CrosscheckNearby` method list (`start`/`accept`/`finish`/`send`/`requestPack`/
   `close`/`onEvent`), but that list only enumerates the WebRTC core; `app.js`'s `renderNearby()`
   calls `CrosscheckNearby.buildScanButton(label, onCode)` for both the Host "Scan their answer"
   and Join "Scan their code" buttons, the same delegation shape `app.js` already uses for
   `CrosscheckTransfer.mount()` on the share screen.

Other notes for the reviewer:
- `#/nearby` is not a fourth tab (BACKLOG 2026-09-13, repeated in the Execution Guide): reached
  only from the `Nearby chat` button on the share screen; `screenOf()` maps its hash to `#/share`
  so the Share tab stays highlighted while the screen is open.
- The share screen's new `Nearby chat` button uses class `nearby__button`, not
  `button button--secondary`, on purpose: `tests/browser/test_share.py` (Task-09, not touched)
  asserts `.button` has count 2 and `.button--secondary` has text `"Save file"`; a shared class
  would have broken both. Confirmed green after the change.
- `window.CrosscheckNearby.close()` is wired to a page-wide `hashchange` listener registered at
  module load, so every stream and the peer connection close on any route change, not only a
  deliberate `Close` action (Lane: "Every stream and the peer connection are closed on route
  change").
- `window.__nearby.events` is exposed for the browser test (same pattern as the existing
  `window.__statement` debug export in `app.js`), reset on every `renderNearby()` mount.
