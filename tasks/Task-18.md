# Task-18: Transfer by camera (QR frames)

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* the frame contract is fixed in Part 2 and the round trip is checkable without a camera; the camera path itself is Tarik's manual check (PRD §6).

**Lane**
- OWNS: `app/transfer.js` (new), `app/app.js` (the share screen: `renderShare` and what it calls), `app/app.css` (transfer block only, tokens only), `scripts/build_app.py` (the JS tuple only), `tests/browser/test_transfer.py` (new)
- MUST NOT TOUCH: `app/qr.js` (Task-17), `app/nearby.js` (Task-19), `pipeline/` and `scripts/gate.py` (Task-20), `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-17

## Objective

Screen 3 gains "Show" and "Receive". Show plays the whole running app as a loop of QR frames;
Receive on another phone reads them with the camera, reassembles, inflates and opens the
result with a save button. The app travels by light, no network, no file. PRD §4.2 second
batch; Part 2 "Entry points: Transfer by camera".

## Execution Guide

- Payload: `pageHtml()` (already in `app.js`, the bytes save-as-file writes) → UTF-8 bytes →
  gzip with `new CompressionStream("gzip")` → base64 text. `BarcodeDetector.rawValue` is a
  string, not bytes, which is why the payload is base64 (Part 2, 2026-09-15).
- Frame text: `"CX" + index as 4 hex digits + count as 4 hex digits + up to 1,000 base64
  characters`. Each frame is encoded with `CrosscheckQR.encode(text, "L")` and rendered with
  `toSvgPath` into one `<svg>` that is swapped in place about 8 times a second
  (`setTimeout`-driven, not `requestAnimationFrame`, so the rate is the same on every phone).
  A `received / total` style counter under the code shows `frame i of n`. A Stop button ends
  the loop. Encoding all frames once up front on Show, then looping, keeps the loop cheap.
- `app/transfer.js` exposes `window.CrosscheckTransfer` with `frames(html) -> Promise<string[]>`,
  `reassemble(frameTexts) -> {complete, received, total, bytes|null}` (order-insensitive,
  duplicates ignored, base64 decoded to a `Uint8Array` only when complete), and
  `inflate(bytes) -> Promise<string>` (`DecompressionStream("gzip")`).
- Receive: a `<video>` fed by `getUserMedia({ video: { facingMode: "environment" } })`,
  `new BarcodeDetector({ formats: ["qr_code"] })` polled about 10 times a second with
  `detect(video)`; every `rawValue` starting with `CX` goes to the reassembler; the counter
  shows `received / total`. When complete: inflate, verify the result contains
  `<html` and `id="pack"`, build a `Blob` of type `text/html`, open it with
  `window.open(URL.createObjectURL(blob))` on the user's tap (a button "Open received app")
  and offer a download link named `crosscheck.html`. Stop all tracks on Stop and on route
  change. If `BarcodeDetector` is absent (`"BarcodeDetector" in window` false) the Receive card
  says so in one sentence and points at the URL QR above it (OQ15).
- Markup reuses `card`, `button`, `chip`; new class names under a `.transfer` block in
  `app/app.css` using tokens only. The share screen's existing QR, buttons and statement stay
  exactly as the Task-09/14 tests expect.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_transfer.py` (marker `browser`): in `dist/index.html`, `CrosscheckTransfer.frames(pageHtml)` (the test reads `dist/index.html` from disk and passes its text) returns N frames, every frame matches `^CX[0-9a-f]{4}[0-9a-f]{4}[A-Za-z0-9+/=]{1,1000}$`, the count field equals N on every frame, and `CrosscheckQR.encode(frame, "L").version` is at most 40 for all of them; shuffling the frames and dropping every duplicate, `reassemble` reports `complete`, and the SHA-256 of `inflate(bytes)` computed in the page with `crypto.subtle` equals the SHA-256 of `dist/index.html` computed in the test.
- [ ] Same test: `#/share` shows a `.transfer` block with buttons labelled `Show` and `Receive`; clicking Show renders an `svg` inside `.transfer` and a counter text matching `frame 1 of \d+`; clicking Stop removes the loop (the counter stops changing over 500 ms).
- [ ] `grep -l getUserMedia app/*.js` prints only `app/transfer.js` (until Task-19 adds `app/nearby.js`); `grep -nE "fetch\(|XMLHttpRequest|WebSocket|https?://" app/transfer.js` prints nothing; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/transfer.js` prints nothing.
- [ ] All existing browser tests (share, changes screen, statement) stay green; zero non-`file:` requests and no console errors.

## Status

Not started.
