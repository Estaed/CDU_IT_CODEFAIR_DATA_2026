# Task-25: QR reading on every browser (jsQR fallback for iPhone)

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* one vendored file behind one small adapter; the criterion decodes QR codes the app itself draws, in headless Chromium with `BarcodeDetector` forced absent, so no camera or iPhone is needed to gate it.

**Lane**
- OWNS: `app/vendor/jsQR.js` (new), `app/vendor/jsQR.LICENSE` (new), `app/scan.js` (new), `app/transfer.js` (replace direct `BarcodeDetector` use with the adapter; drop the "cannot scan" branch), `app/nearby.js` (same), `scripts/build_app.py` (the JS tuple and one licence header comment only), `tests/browser/test_scan.py` (new), `tests/test_build.py` (append only)
- MUST NOT TOUCH: `app/app.js` and `app/store.js` (Task-24), `app/qr.js` (Task-17), `app/layers.css` (Task-21), `pipeline/`, `scripts/gate.py`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-24

## Objective

Safari on iPhone has no `BarcodeDetector` (broken since iOS 18), so today an iPhone can show QR
codes but cannot read them: no Receive by light, no scanning in nearby chat. After this task every
scan in the app goes through one adapter that uses the browser's reader where it exists and the
vendored jsQR decoder where it does not. Tarik's decision 2026-09-15 (OQ15 answered). This is the
one library exception Part 2 allows.

## Execution Guide

- **Vendor, measured 2026-09-15:** `jsqr` 1.4.0 from npm (Apache-2.0, repository
  `github.com/cozmo/jsQR`, last release 2021-04-24), file `dist/jsQR.js`, 256,885 bytes, 56,970
  bytes gzipped, a webpack UMD that sets `self.jsQR`. Get it at development time with `npm pack
  jsqr@1.4.0` in a temporary folder outside the repo (the runtime never fetches it). Copy
  `package/dist/jsQR.js` to `app/vendor/jsQR.js` and make exactly one edit: remove the URL
  `http://en.wikipedia.org/wiki/Bresenham` from its comment on line 9758 (the build test forbids
  URLs outside pack citations and layer rule 7 greps for them). Record in `app/vendor/jsQR.LICENSE`:
  the package name and version, the SHA-256 of the npm tarball and of the unmodified `jsQR.js`,
  the one edit made (Apache-2.0 section 4(b) asks for a notice of changes), then the full Apache
  2.0 licence text copied from `package/LICENSE`.
- `scripts/build_app.py`: `JS_FILES` gains `app/vendor/jsQR.js` first and `app/scan.js` after
  `app/qr.js`; final order `vendor/jsQR.js, qr.js, scan.js, transfer.js, nearby.js, store.js,
  app.js`. Prefix the vendored block inside the script with one comment line that carries no URL:
  `/*! jsQR 1.4.0, Apache-2.0, (c) Cosmo Wolfe; one comment URL removed; licence text in
  app/vendor/jsQR.LICENSE of the source repository */`.
- `app/scan.js` exposes `window.CrosscheckScan` with:
  - `reader()` returning an object with `detect(video) -> Promise<string[]>`: if
    `"BarcodeDetector" in window`, `new BarcodeDetector({ formats: ["qr_code"] })` and map
    `rawValue`; otherwise draw the current video frame onto one reusable offscreen `<canvas>`
    scaled so its longer side is at most 720 (a plain number constant, not CSS), read
    `getImageData`, call `jsQR(data, width, height, { inversionAttempts: "dontInvert" })`, return
    `[code.data]` or `[]`.
  - `decodeImageData(imageData) -> string|null`, the jsQR path alone, for tests.
  - `kind()` returning `"native"` or `"jsqr"`, shown in small text under Receive and Scan so a
    phone test says which reader ran.
- `app/transfer.js` and `app/nearby.js`: replace every `new BarcodeDetector` / `detect(video)`
  with `CrosscheckScan.reader().detect(video)`; delete the "This browser cannot scan QR codes"
  branches. Keep a one-sentence message only when `navigator.mediaDevices` is absent. Polling
  rate stays as it is; jsQR on a 720-pixel frame is slower, so skip a tick while the previous
  decode is still running.
- Layer rule 8 still holds: `scan.js` never calls `getUserMedia`; it receives the video element.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_scan.py` (marker `browser`): with an init script that removes `window.BarcodeDetector`, `CrosscheckScan.kind()` is `"jsqr"`; for each of (a) the first, the last and every 16th transfer frame from `CrosscheckTransfer.frames` on `dist/index.html`, (b) a nearby offer text from `CrosscheckNearby.start()`, (c) `WIFI:T:WPA;S:Crosscheck;P:pass\;word;;`, the page draws `CrosscheckQR.encode(text, level)` onto a canvas with `fillRect` at 4 units per module and a 4-module quiet zone, and `CrosscheckScan.decodeImageData(ctx.getImageData(...))` returns exactly `text`.
- [ ] Same test: with `BarcodeDetector` present (a stub class defined by the init script), `kind()` is `"native"` and `reader().detect` calls the stub.
- [ ] `tests/test_build.py` (appended): `dist/index.html` contains the jsQR licence header comment exactly once, before `window.CrosscheckScan = `, which appears once and before `window.CrosscheckTransfer`; the sha256 of `app/vendor/jsQR.js` equals the value recorded in `app/vendor/jsQR.LICENSE` for the edited file; `dist/index.html` is at most 1,048,576 bytes; `BarcodeDetector` appears in `app/scan.js` and in no other file under `app/`.
- [ ] `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://" app/scan.js app/vendor/jsQR.js app/transfer.js app/nearby.js` prints nothing; `grep -l getUserMedia app/*.js` prints exactly `app/nearby.js` and `app/transfer.js`; zero non-`file:` requests and no console errors; all existing browser tests stay green.

## Status

Not started. Expected cost, written down so nobody is surprised: `dist/index.html` grows by about
257 KB, and a transfer by light grows by about 57 KB gzipped, which is about 76 more frames
(roughly 10 more seconds per loop at 8 frames a second). Record the measured figures here.
