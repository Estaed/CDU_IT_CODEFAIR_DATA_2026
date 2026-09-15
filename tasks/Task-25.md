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

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Main loop at integration, 2026-09-15: GATE GREEN.)
- [x] `tests/browser/test_scan.py` (marker `browser`): with an init script that removes `window.BarcodeDetector`, `CrosscheckScan.kind()` is `"jsqr"`; for each of (a) the first, the last and every 16th transfer frame from `CrosscheckTransfer.frames` on `dist/index.html`, (b) a nearby offer text from `CrosscheckNearby.start()`, (c) `WIFI:T:WPA;S:Crosscheck;P:pass\;word;;`, the page draws `CrosscheckQR.encode(text, level)` onto a canvas with `fillRect` at 4 units per module and a 4-module quiet zone, and `CrosscheckScan.decodeImageData(ctx.getImageData(...))` returns exactly `text`. (Was blocked by the jsQR version-23 defect below; resolved by the second recorded edit to `app/vendor/jsQR.js`, and now holds for every sampled frame, not just 1 of 15. Also added `test_all_versions_1_to_40_decode_at_byte_mode_capacity`, one text per QR version 1-40 at level L's byte-mode capacity, as the regression check for this exact defect class.)
- [x] Same test: with `BarcodeDetector` present (a stub class defined by the init script), `kind()` is `"native"` and `reader().detect` calls the stub.
- [x] `tests/test_build.py` (appended): `dist/index.html` contains the jsQR licence header comment exactly once, before `window.CrosscheckScan = `, which appears once and before `window.CrosscheckTransfer`; the sha256 of `app/vendor/jsQR.js` equals the value recorded in `app/vendor/jsQR.LICENSE` for the edited file; `dist/index.html` is at most 1,048,576 bytes; `BarcodeDetector` appears in `app/scan.js` and in no other file under `app/`.
- [x] `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://" app/scan.js app/vendor/jsQR.js app/transfer.js app/nearby.js` prints nothing; `grep -l getUserMedia app/*.js` prints exactly `app/nearby.js` and `app/transfer.js`; zero non-`file:` requests and no console errors; all existing browser tests stay green.

## Status

DONE 2026-09-15 (main loop: three-way cherry-pick with no conflict, gate green; mutation check: putting the upstream 74 back in the version 23 table turns the all-versions scan test red, restored; the version 23 defect was found by the worker and re-verified by the main loop over all 40 versions) Worker notes follow.

Implemented and tested. Not marked DONE here; that is `verify-task`'s call, from the main loop,
per Part 1.

**Commands run (from the worktree root, main tree's interpreter, PowerShell -- the Bash tool
refused the cross-tree path as expected):**
- `ruff check --no-cache .` -> `All checks passed!`
- `python scripts/build_app.py` -> `dist\index.html: 844595 bytes`
- `python -m pytest tests/test_build.py tests/browser -q` -> `80 passed in 35.12s`
- `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://" app/scan.js app/vendor/jsQR.js app/transfer.js app/nearby.js` -> nothing (clean)
- `grep -l getUserMedia app/*.js` -> `app/nearby.js`, `app/transfer.js` (exactly those two)
- `grep -rl BarcodeDetector app/*.js app/vendor/*.js` -> `app/scan.js` (exactly that one)

**Measured figures:**
- `dist/index.html`: 844,595 bytes (budget 1,048,576; about 204 KB of headroom). Grew from the
  pre-jsQR baseline mostly as expected, plus everything Task-26/28 already added since that
  baseline was measured.
- `app/vendor/jsQR.js`: 256,847 bytes (unchanged by the second edit -- `74` -> `78` is the same
  digit count).
- Transfer by light: 220 frames for this build's own bytes (up from the 128-frame, pre-jsQR
  baseline; growth matches the expected order of magnitude).
- SHA-256, npm tarball `jsqr-1.4.0.tgz`: `b5299b37917a1fe7a8cab9dd5cc6b8accf82663add80abe5bf7761a921cc6602`
- SHA-256, `package/dist/jsQR.js` unmodified: `bc40c8a15196236b2314db0856f72ca0b49980cd5413b8c852a7349f5fee0859`
- SHA-256, `app/vendor/jsQR.js` edited, both edits applied (as vendored): `fe2ce9b7b6f8b5ade1ec36623584117eab267ff438acada61ad1d09f70df61ac`
- All three (tarball, unmodified, edited) recorded in `app/vendor/jsQR.LICENSE`, alongside both
  edits made and the full Apache-2.0 text.

**jsQR version-23 defect -- resolved, second edit applied (coordinator decision, CLAUDE.md Part 2
amended in main to allow it):**
`app/vendor/jsQR.js`'s own version table (`VERSIONS[22]`, `versionNumber: 23`) read
`alignmentPatternCenters: [6, 30, 54, 74, 102]`; the ISO/IEC 18004 value for the fourth centre is
`78`, not `74`. Confirmed independently by the main loop against Python `qrcode`'s
`util.PATTERN_POSITION_TABLE` (all 40 versions compared; only version 23 differs) and by
rendering+decoding every version 1-40 at level L (the shipped file failed only version 23; a copy
with the one entry corrected decoded all 40). Corrected in `app/vendor/jsQR.js` as the one
additional line (no other byte changed -- confirmed: the file is still 256,847 bytes and the old
value no longer appears anywhere in it); the second edit, its citation and the new SHA-256 are
recorded in `app/vendor/jsQR.LICENSE`.

`tests/browser/test_scan.py` no longer pins the version-23 failure: every sampled transfer frame,
the nearby offer text and the Wi-Fi join QR now assert plain equality
(`decodeImageData(...) === text`), matching the DoD's own wording exactly. Added
`test_all_versions_1_to_40_decode_at_byte_mode_capacity`: one text per QR version 1-40, each
built at that version's exact byte-mode capacity at level L (`BYTE_CAPACITY_L`, from Python's own
`qrcode.util.BIT_LIMIT_TABLE` through the same formula `app/qr.js`'s `bestVersion` uses), so
`CrosscheckQR.encode` is forced to land on every version in turn and jsQR is asked to decode all
40 -- this is the regression check that would catch this exact defect class again if a future
jsQR upgrade reintroduces it. `tests/test_build.py`'s existing
`test_vendored_jsqr_sha256_matches_license_file` reads the recorded hash from the licence file
dynamically, so it needed no code change and now compares against the new hash automatically.
