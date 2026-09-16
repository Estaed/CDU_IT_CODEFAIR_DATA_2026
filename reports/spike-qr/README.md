# Spike: transfer v3 — round two, the lite payload at 5 fps

Task-31, 2026-09-16. Tarik's phone test that day: the shipped v2 receiver climbs to about 110 of
233 blocks and then crawls. Round two is measured on two phones and decides whether camera
transfer ships at all; the winner is built into `app/transfer.js` by Task-36, and this folder is
deleted then.

Nothing under `app/` imports anything here. The pages read `app/vendor/jsQR.js`, `app/qr.js`,
`app/scan.js` and `dist/index.html` at build time and copy none of them into this folder; the
fountain code, the send loop and the peeling receiver are copied into `spike.js` on purpose, so
a change here can never reach the app by accident.

## Round one, kept as the record

Four frame geometries — A one version-23 code, B a 2 × 2 grid, C three codes in the R, G and B
channels, D both — played by a refresh-synchronised sender and read by a
`requestVideoFrameCallback` loop with jsQR in a Web Worker, against a 174,725-byte pseudorandom
payload (K 233). **None completed on either phone; the best run reached 15 of 233 blocks,
against the shipped v2 loop's 110 the day before** — so the wall is the phone's decode rate on
version-23 codes, and round one's reader path was slower than the one the app already ships. B
and C are shelved: both make each code smaller or harder to read, which is the wrong direction
when the decoder is the bottleneck. Round one's code and its loopback numbers are in git history
at commit `788a7de`.

## Round two: one candidate

Fewer blocks and fewer frames a second, and the payload is the product's own, not a proxy's.

**The lite payload.** `build.py` derives it from `dist/index.html` (run `scripts/build_app.py`
first): the inlined `vendor/jsQR.js` is dropped, the pack's `layers` value becomes `[]`, and
`<html>` gets `data-lite="1"`. Gzipped at level 6 that is **69,554 bytes, K 93** (2026-09-16)
against v2's 233 blocks. The gzipped bytes and their SHA-256 are inlined into both pages, so a
completed run proves the received bytes are the sent bytes.

**Fountain code.** As round one: 750-byte blocks, one pass of the `K` sources then repair frames
only, robust soliton `c = 0.1`, `delta = 0.5`, xorshift32 seeded from the frame index, the
peeling receiver copied from `transfer.js`. Frame text is `CZ` + index (4 hex) + `K` (4 hex) +
payload length (6 hex) + 1,000 base64 characters, QR byte mode, level L. `CZ` means a v2 (`CY`)
receiver and this one can never mix frames.

**Sender.** One code per frame, drawn as an SVG path exactly as the app draws it, changed inside
`requestAnimationFrame` and held for `hold` display refreshes. The selector offers 12 (5 fps at
60 Hz, the default), 8 and 16. Fullscreen button, wake lock, and a counter of frames and seconds.

**Receiver.** The v2 app's loop, copied not redesigned: `getUserMedia` with the app's
`constraints()`, `tune()` from `scan.js` for focus and zoom, then `setTimeout(scan, 100)` calling
`CrosscheckScan.reader().detect(video)` on the main thread. No worker, no
`requestVideoFrameCallback`. On DONE it vibrates, records the run, and offers `Open lite copy`
so the received page can be opened and seen to run.

## Build and run

```
PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py
PYTHONUTF8=1 .venv/Scripts/python reports/spike-qr/build.py
```

writes `dist/spike/send.html` and `dist/spike/receive.html` — one file each, no `src=`, no
`href=`, no `fetch(`, no request at runtime. `.github/workflows/pages.yml` runs the same
commands, so after a push to `main` the pages are at `<APP_URL>spike/send.html` and
`<APP_URL>spike/receive.html`. Use the Pages address on the phones: Chrome on Android refuses
the camera on a `file://` page.

## Measurement protocol (Tarik, on the phones)

Laptop browser fullscreen on `send.html` at hold 12. The S24 then the Mi 6 on `receive.html`
from the Pages address, held about 20 cm from the screen, five runs each, `Start` on the phone
first. A run that passes four minutes is stopped and noted as `not complete <known>`. Then hold
8 and hold 16, three runs each, on the S24 only. Set Hold and Phone on the receive page before
each run — they are what the log line records. Use `Copy runs` and paste the lines below.

Each completed run appends one line:
`hold,phone,reader,seconds,frames_read,codes_decoded`. `seconds` is measured from the first
decoded code, not from Start, so a slow aim does not count against the candidate. Loss cannot be
computed across two phones — the receiver never learns how many frames the sender has shown — so
the page shows decoded-codes-per-second over the last 5 seconds instead.

## Decision rule (fixed in advance)

5 of 5 completed on both phones at hold 12 → Task-36 builds it, with the loss budgets set from
the worst measured run. Fewer → camera transfer is retired to the report as a measured negative
result; the share sheet is the offline handoff, and `Complete this copy` still ships for a lite
copy that travelled by Quick Share.

## Results

Pasted from the receive page. Filled by the main loop from Tarik's runs.

```
hold,phone,reader,seconds,frames_read,codes_decoded
```

| Hold | Phone | Completions / runs | Median seconds | Notes |
|---|---|---|---|---|
| 12 | S24 | / 5 | | |
| 12 | Mi 6 | / 5 | | |
| 8 | S24 | / 3 | | |
| 16 | S24 | / 3 | | |

**Verdict:** _(main loop, after the runs)_

## Measured before the phones, on the laptop (2026-09-16)

No camera: the frame texts are fed straight back through the receive page's own receiver in
headless Chromium.

- Payload: lite copy 451,623 bytes, gzipped **69,554 bytes**, **K 93**, SHA-256 `c39ed0d5…`.
- Every frame pushed in order: complete at **93 pushed = exactly K**, and the reassembled bytes
  equal the sender's payload byte for byte.
- Every third frame pushed (67 % loss): complete at **120 pushed** out of 360 shown —
  1.29 × K pushed, 3.87 × K shown — same bytes.
- The inflated payload parses as HTML with `data-lite="1"`, carries no vendored jsQR, and its
  pack has `layers` empty, 96 communities, `pack_version` 2.
- Sender at hold 12 in headless Chromium: 8 version-23 codes (109 modules) in 1.4 s.
- Neither page makes a non-`file:` request.

Not measured here, and the reason this spike exists: what a phone's camera and decoder make of a
version-23 code held for 12 refreshes, at the distance and the light a real handoff has.
