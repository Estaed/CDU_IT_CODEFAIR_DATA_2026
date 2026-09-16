# Spike: transfer v3 — four frame geometries, measured on two phones

Task-31, 2026-09-16. Tarik's phone test that day: the v2 receiver climbs to about 110 blocks
and then crawls. The v2 repair degree (uniform 6..12) was tuned against 10 % frame loss; a real
phone loses half or more, and at that loss a repair frame almost never reduces to one unknown
block. Rather than pick a fix on paper, four candidates are built here as standalone pages and
measured. The winner is built into `app/transfer.js` by Task-36, and this folder is deleted then.

Nothing under `app/` imports anything here. The pages read `app/vendor/jsQR.js`, `app/qr.js`
and `app/scan.js` at build time and copy none of them; the fountain code and the peeling
receiver are copied into `spike.js` on purpose, so a change here can never reach the app by
accident.

## Build and run

```
PYTHONUTF8=1 .venv/Scripts/python reports/spike-qr/build.py
```

writes `dist/spike/send.html` and `dist/spike/receive.html` — one file each, no `src=`, no
`href=`, no request at runtime. `.github/workflows/pages.yml` runs the same command, so after a
push to `main` the pages are at `<APP_URL>spike/send.html` and `<APP_URL>spike/receive.html`.
Use the Pages address on the phones: Chrome on Android refuses the camera on a `file://` page.

## What the candidates are

Every candidate carries one 750-byte block per code, in a `CZ` frame:
`CZ` + candidate letter + index (4 hex) + `K` (4 hex) + payload length (6 hex) + base64 of one
block (1,000 characters). The payload is 174,725 bytes generated in-page from xorshift32 seeded
`0x5EED` — the gzipped size of the app on 2026-09-16, so `K` is 233, the real thing's size. Both
pages show the first 8 hex characters of SHA-256 over the payload; a completed run must show the
sender's hash.

| Letter | Codes per frame | How |
|---|---|---|
| A | 1 | one code, today's geometry |
| B | 4 | a 2 × 2 grid of codes |
| C | 3 | three codes multiplexed into the R, G and B channels of one code-sized picture |
| D | 12 | the 2 × 2 grid of colour composites |

The fountain code is common to all four and is v2's with one change: the repair degree comes
from the robust soliton distribution (`c = 0.1`, `delta = 0.5`) instead of v2's uniform 6..12.
Send order is unchanged — one pass of the `K` sources, then repair frames only.

The sender changes the frame inside `requestAnimationFrame` and holds it for a chosen number of
display refreshes (4, 6 or 8 — at 60 Hz, 15, 10 and 7.5 frames a second), never from a timer.
The receiver reads on `requestVideoFrameCallback` where it exists, one frame in flight at a
time; jsQR runs in a Web Worker built from a Blob of its own inlined source, and the native
`BarcodeDetector` path stays on the main thread as in the app.

## Measurement protocol (Tarik, on the phones)

Sender: the laptop's browser fullscreen on `send.html`, the same window size for every run, or
the second phone. Receiver: the S24, then the Mi 6, on `receive.html` from the Pages address.

1. For each candidate at hold 6: five runs per phone. Hold the receiver by hand about 20 cm
   from the screen. Start on the receiver first.
2. Then candidate A at hold 4 and at hold 8, five runs each, on the S24 only.
3. Set the receive page's Candidate, Hold and Phone fields before each run — they are what the
   log line records.
4. Copy the `<pre>` block with the Copy button after each phone and paste it below.

Each completed run appends one line:
`candidate,hold,phone,reader,seconds,frames_seen,codes_decoded`. `seconds` is measured from the
first decoded code, not from Start, so a slow aim does not count against a candidate. Loss
cannot be computed across two phones — the receiver never learns how many frames the sender has
shown — so the page shows decoded-per-second and new-blocks-per-second over the last 5 seconds
instead.

## Decision rule (fixed in advance, PRD §4.2)

Among the candidates that complete 5 of 5 runs on both phones at hold 6, the shortest median
seconds wins; ties go to the simpler candidate (A before B before C before D). If no candidate
completes 5 of 5 on both phones, the one with the most completions wins and Task-36 records the
gap.

## Results

Pasted from the receive page. Filled by the main loop from Tarik's runs.

```
candidate,hold,phone,reader,seconds,frames_seen,codes_decoded
```

| Candidate | Hold | Phone | Completions / 5 | Median seconds | Notes |
|---|---|---|---|---|---|
| A | 6 | S24 | | | |
| A | 6 | Mi 6 | | | |
| B | 6 | S24 | | | |
| B | 6 | Mi 6 | | | |
| C | 6 | S24 | | | |
| C | 6 | Mi 6 | | | |
| D | 6 | S24 | | | |
| D | 6 | Mi 6 | | | |
| A | 4 | S24 | | | |
| A | 8 | S24 | | | |

**Verdict:** _(main loop, after the runs)_

## Measured before the phones, on the laptop (2026-09-16)

No camera: the frame texts and the drawn pictures are fed straight back through the receiver's
own code in headless Chromium.

- Candidate A, every frame pushed in order: complete at **233 pushed = exactly K**, payload
  hash `ab4eb170` on both ends.
- Candidate A, every third frame pushed (67 % loss): complete at **290 pushed** out of 868
  shown — 1.24 × K pushed, 3.73 × K shown — same hash. For comparison, v2's uniform 6..12
  degree needed 1.75 × K pushed to survive only 10 % loss.
- Candidate C: the composite drawn by the sender's own `drawFrame`, read back and split by the
  receiver's own `splitChannels`, decodes **3 of 3** codes with jsQR (version 23, 109 modules,
  468 px picture).
- Candidate B through the Blob worker: 4 of 4 quadrants decoded.
- Sender frame rate at hold 6 in headless Chromium (nominal 10 fps): A 10.7, B 9.3, C 10.7,
  D 5.7 frames a second. **D is encoder-bound** — twelve version-23 codes per frame is more QR
  encoding than one phone frame budget holds, so a D run on a phone is likely to play slower
  than its hold setting asks. That is part of what the measurement is for.

Not measured here, and the reason this spike exists: what a camera makes of a colour composite
(crosstalk between channels, white balance, rolling shutter) and of four small codes at once.
