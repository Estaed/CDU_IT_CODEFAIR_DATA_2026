# Task-19: Nearby chat over the phone's own Wi-Fi

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
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

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_nearby.py` (marker `browser`): two pages in the fixture browser both open `dist/index.html#/nearby`; page A `CrosscheckNearby.start()` → offer text (at most 2,900 characters, so it fits one QR at level L); page B `accept(offer)` → answer text; page A `finish(answer)`; within 10 s both pages report state `open`; A `send("hello")` appears in B's `.nearby__messages` as a `peer` line and in A's as a `me` line; B `requestPack()` → B's event log holds a `pack` event whose json parses to 96 communities. `close()` on both ends leaves state `closed`.
- [ ] Same test: the Wi-Fi card renders a QR after typing `Crosscheck` and `pass;word`, and the encoded text (exposed as `data-text` on the QR container) is `WIFI:T:WPA;S:Crosscheck;P:pass\;word;;`.
- [ ] `tests/test_build.py` (appended): `app/nearby.js` contains `iceServers: []` and none of `stun:`, `turn:`; `grep -l getUserMedia app/*.js` prints exactly `app/nearby.js` and `app/transfer.js`.
- [ ] `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://" app/nearby.js` prints nothing; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/nearby.js` prints nothing.
- [ ] Zero non-`file:` requests and no console errors on every route; the share screen tests stay green.

## Status

Not started.
