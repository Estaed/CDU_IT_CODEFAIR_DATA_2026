# Task-17: QR encoder in the app

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* a pure algorithm with an exact oracle (Python `qrcode` at the pinned version); no eye needed.

**Lane**
- OWNS: `app/qr.js` (new), `scripts/build_app.py` (the JS list only), `tests/browser/test_qr.py` (new), `tests/test_build.py` (append only)
- MUST NOT TOUCH: `app/app.js` (Task-22, same wave), `pipeline/` (Task-20), `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: none

## Objective

The app can encode a QR code at runtime, from its own bytes or from text, with no library.
Three later features need it: the transfer frames (Task-18), the nearby handshake and the
Wi-Fi join code (Task-19). Today the only QR is rendered at build time by Python `qrcode`
(`scripts/build_app.py: qr_svg`), which cannot encode anything the phone only knows at runtime.
PRD §4.2 second batch; CLAUDE.md Part 2 "Where the code lives" and layer rule 7.

## Execution Guide

- `app/qr.js`, a plain script exposing one object `window.CrosscheckQR` with:
  - `encode(data, level)` where `data` is a string (encoded as UTF-8) or a `Uint8Array`, `level`
    is `"L"` or `"M"`; returns `{ version, size, modules }` with `modules` a `Uint8Array` of
    `size * size` (1 = dark), no quiet zone.
  - `toSvgPath(result)`: the same one-path markup `qr_svg` in `scripts/build_app.py` produces
    (one `M x y h1 v1 h-1 z` per dark module or equivalent), so `app.js` can drop it into the
    existing `.qr` container unchanged.
- Byte mode only. Version auto-fit: the smallest version 1–40 whose capacity at the level fits;
  throw if none. Mask: evaluate all eight with the four standard penalty rules and keep the
  lowest score, ties to the lowest mask index. This is exactly what Python `qrcode` does
  (`qrcode/main.py: best_fit`, `qrcode/util.py: lost_point`), and the oracle test depends on
  it: read those two functions in `.venv/Lib/site-packages/qrcode/` before writing the JS.
  Reed-Solomon over GF(256) with the standard generator polynomials; interleave blocks per the
  version's block table (copy the table values from `qrcode/base.py: RS_BLOCK_TABLE`, they are
  data, not code).
- `scripts/build_app.py`: `JS` becomes an ordered tuple `(app/qr.js, app/app.js)` inlined in
  that order inside the one `<script>`; Part 2 fixes the full order `qr.js, transfer.js,
  nearby.js, app.js`, later tasks append their file to the tuple. No other change.
- Keep `qr.js` under about 450 lines; the block table is most of it.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_qr.py` (marker `browser`): opens `dist/index.html`, and for each of three inputs computes the oracle in the test with Python `qrcode` (`border=0`, `fit=True`, the same level, `QRCode.add_data` with the byte string) and asserts `CrosscheckQR.encode(...)` returns the identical `version`, `size` and module array. Inputs: `"Crosscheck"` at M; the `APP_URL` from `constants.md` at M; a fixed 1,000-byte pseudo-random `Uint8Array` (seeded, generated in both the test and the page from the same integer sequence) at L.
- [ ] `tests/test_build.py` (appended): `dist/index.html` contains the string `window.CrosscheckQR` exactly once and `app/qr.js` appears before `app/app.js` in the inlined script.
- [ ] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/qr.js` prints nothing; `grep -nE "fetch\(|XMLHttpRequest|WebSocket|https?://" app/qr.js` prints nothing.
- [ ] Zero non-`file:` requests and no console errors on load (existing smoke test stays green).

## Status

Not started.
