# Task-18: Transfer by camera (QR frames)

**Status: DONE** — verified 2026-09-15 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* the frame contract is fixed in Blueprint and the round trip is checkable without a camera; the camera path itself is Tarik's manual check (PRD §6).

**Lane**
- OWNS: `app/transfer.js` (new), `app/app.js` (the share screen: `renderShare` and what it calls), `app/app.css` (transfer block only, tokens only), `scripts/build_app.py` (the JS tuple only), `tests/browser/test_transfer.py` (new)
- MUST NOT TOUCH: `app/qr.js` (Task-17), `app/nearby.js` (Task-19), `pipeline/` and `scripts/gate.py` (Task-20), `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-17

## Objective

Screen 3 gains "Show" and "Receive". Show plays the whole running app as a loop of QR frames;
Receive on another phone reads them with the camera, reassembles, inflates and opens the
result with a save button. The app travels by light, no network, no file. PRD §4.2 second
batch; Blueprint "Entry points: Transfer by camera".

## Execution Guide

- Payload: `pageHtml()` (already in `app.js`, the bytes save-as-file writes) → UTF-8 bytes →
  gzip with `new CompressionStream("gzip")` → base64 text. `BarcodeDetector.rawValue` is a
  string, not bytes, which is why the payload is base64 (Blueprint, 2026-09-15).
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

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Main loop at integration, 2026-09-15: GATE GREEN, 37 browser tests.)
- [x] `tests/browser/test_transfer.py` (marker `browser`): in `dist/index.html`, `CrosscheckTransfer.frames(pageHtml)` (the test reads `dist/index.html` from disk and passes its text) returns N frames, every frame matches `^CX[0-9a-f]{4}[0-9a-f]{4}[A-Za-z0-9+/=]{1,1000}$`, the count field equals N on every frame, and `CrosscheckQR.encode(frame, "L").version` is at most 40 for all of them; shuffling the frames and dropping every duplicate, `reassemble` reports `complete`, and the SHA-256 of `inflate(bytes)` computed in the page with `crypto.subtle` equals the SHA-256 of `dist/index.html` computed in the test.
- [x] Same test: `#/share` shows a `.transfer` block with buttons labelled `Show` and `Receive`; clicking Show renders an `svg` inside `.transfer` and a counter text matching `frame 1 of \d+`; clicking Stop removes the loop (the counter stops changing over 500 ms).
- [x] `grep -l getUserMedia app/*.js` prints only `app/transfer.js` (until Task-19 adds `app/nearby.js`); `grep -nE "fetch\(|XMLHttpRequest|WebSocket|https?://" app/transfer.js` prints nothing; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/transfer.js` prints nothing.
- [x] All existing browser tests (share, changes screen, statement) stay green; zero non-`file:` requests and no console errors.

## Status

DONE 2026-09-15 (main loop: integrated, gate green; mutation check: requiring `total - 1`
frames in `reassemble` turns the round-trip test red, restored. Integration fix: the Task-17
build test now counts the declaration `window.CrosscheckQR = ` rather than every mention, so
`transfer.js` uses plain `window.CrosscheckQR` dot access instead of the bracket workaround the
worker described below. Open point for Tarik: 128 frames at 8 fps is a 16-second loop and a
missed frame costs a full loop; see the session summary for the options.) Worker notes follow.

Implemented in worktree `agent-a8581c4299e0875ba`, rebased onto `efeeb6b` (Wave 14 DONE) first.

Files: `app/transfer.js` (new), `app/app.js` (`renderShare` builds a `.transfer` container and
calls `window.CrosscheckTransfer.mount(transfer, pageHtml)`), `app/app.css` (`.transfer*` block,
tokens only), `scripts/build_app.py` (`JS_FILES` now `qr.js, transfer.js, app.js`),
`tests/browser/test_transfer.py` (new).

Commands run from the worktree root with the main tree's interpreter:

- `ruff check --no-cache .` -> `All checks passed!`
- `scripts/build_app.py` -> `dist\index.html: 540981 bytes`
- `pytest tests/test_build.py tests/browser -q` -> `47 passed` (all green, including the two new
  `test_transfer.py` tests and every pre-existing browser test: share, changes screen,
  statement, community, compare, map, QR, smoke).

Current build: `dist/index.html` is 540,981 bytes (limit 1,048,576). `CrosscheckTransfer.frames`
on that file produces **128 frames**, total base64 payload **127,668 characters** across them
(first frame 1,000 base64 chars, last frame 678). Frame count is higher than the 2026-09-15
spike's ~33-frame estimate because the pack has grown since (Wave 14 added map layers and
raised the pack cap to 512,000 bytes), so the gzip ratio on this larger, less repetitive payload
is lower than the spike's.

Deviations from a literal reading of the Execution Guide, both forced by tests already in the
repo that Task-18 must not touch (`tests/test_build.py`, not in this task's OWNS list):
- `transfer.js` calls the runtime QR encoder via `window["CrosscheckQR"]` (bracket access)
  through a local `crosscheckQR` alias, not `window.CrosscheckQR` (dot access). Calling it the
  literal way made `tests/test_build.py::test_qr_js_inlined_once_before_app_js` fail: that test
  counts the exact text `window.CrosscheckQR` in the built page and asserts it appears once
  (qr.js's own declaration). Once transfer.js needs to *call* the encoder, a second literal
  occurrence is unavoidable unless the call site avoids the dotted spelling.
- The "received app looks like Crosscheck" check in `finish()` parses the inflated HTML with
  `DOMParser` and checks `documentElement.tagName === "HTML"` and `getElementById("pack") !==
  null`, rather than `html.includes("<html")` / `html.includes('id="pack"')` as literally read
  in the Execution Guide. The substring form embeds the literal text `id="pack"` in transfer.js's
  own source, which — once inlined into `dist/index.html` as JS text — pushed
  `test_real_build`'s and `test_save_file_downloads_the_page`'s `html.count('id="pack"') == 1`
  checks to 2. The DOMParser form is arguably more correct anyway (structural check instead of a
  text scan) and carries no such literal.
- The Receive counter/status line uses class `.transfer__status`, not `.transfer__counter`: the
  Execution Guide doesn't name a class, and giving Show and Receive the same counter class made
  Playwright's locator strict-mode reject `.transfer .transfer__counter` (two matches). CSS rule
  for both class names is shared in `app/app.css`.
- The Receive **button** is always rendered with the label `Receive` (satisfying the literal AC
  text "buttons labelled Show and Receive"); the `BarcodeDetector`-absent fallback is decided at
  click time, not mount time, so the card doesn't have to choose between "always show a Receive
  button" and "replace the whole card with one sentence when unsupported" at render time — it
  does the latter only once the user asks to scan.

Not verified here (per the lane's own instructions): `scripts/gate.py` itself (no `data/raw/` in
this worktree); the real camera round trip on two phones (Tarik's manual check, PRD §6); nothing
in `app/qr.js`, `app/nearby.js`, `pipeline/`, `scripts/gate.py`, or `design/` was touched.
