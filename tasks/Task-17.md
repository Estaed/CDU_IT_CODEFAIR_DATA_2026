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

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Run by the main loop at integration, 2026-09-15: GATE GREEN, 137 unit and 35 browser tests.)
- [x] `tests/browser/test_qr.py` (marker `browser`): opens `dist/index.html`, and for each of three inputs computes the oracle in the test with Python `qrcode` (`border=0`, `fit=True`, the same level, `QRCode.add_data` with the byte string) and asserts `CrosscheckQR.encode(...)` returns the identical `version`, `size` and module array. Inputs: `"Crosscheck"` at M; the `APP_URL` from `constants.md` at M; a fixed 1,000-byte pseudo-random `Uint8Array` (seeded, generated in both the test and the page from the same integer sequence) at L.
- [x] `tests/test_build.py` (appended): `dist/index.html` contains the string `window.CrosscheckQR` exactly once and `app/qr.js` appears before `app/app.js` in the inlined script.
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/qr.js` prints nothing; `grep -nE "fetch\(|XMLHttpRequest|WebSocket|https?://" app/qr.js` prints nothing.
- [x] Zero non-`file:` requests and no console errors on load (existing smoke test stays green).

## Status

DONE 2026-09-15 (main loop: integrated from the worker's worktree, gate green; mutation check:
disabling penalty rule 2 in `qr.js` turns `test_qr.py` red, restored). Worker notes follow.

Ran `ruff check --no-cache .` (clean), `scripts/build_app.py` (`dist/index.html` built), and
`pytest tests/test_build.py tests/browser/test_qr.py tests/browser/test_smoke.py -q` (12
passed). Did not run the full `scripts/gate.py` or the full suite per the Lane instructions —
the worktree has no `data/raw/`, so pipeline/source tests fail there for reasons unrelated to
this task; confirmed this out of caution and it is exactly the pre-existing gap the caller
described, not a regression from this change.

The oracle test forces `code.add_data(data, optimize=0)` on the Python side so the oracle
always builds a single byte-mode `QRData`, matching `qr.js`'s byte-mode-only encoder (default
`optimize=20` can otherwise split alphanumeric/numeric runs into separate segments). The
1,000-byte input is a seeded 32-bit LCG (`state = (1103515245*state+12345) & 0xFFFFFFFF`,
byte = `(state>>16)&0xFF`); the test computes it in Python for the oracle and the page
regenerates the identical sequence itself in JS from the same seed and constants
(`Math.imul` for the 32-bit multiply), so no byte array crosses the Python/JS boundary for
that input.

One real bug found and fixed during verification: `mapData`'s zigzag column loop mutated the
JS `for` loop's own counter (`if (col <= 6) col -= 1`) inside the body, which then fed into
the loop's own `col -= 2` step — unlike Python's `for col in range(...)`, where mutating `col`
inside the body never affects the next value `range` yields. This desynced every column after
the timing strip and dropped column 0 entirely. Fixed by deriving `col` from a separate,
un-mutated `colBase` counter. Found by a temporary debug harness (built, run, and deleted
during this task; not part of the diff) that dumped per-mask-pattern lost-point scores and
candidate matrices from both sides and diffed them cell by cell.
