# Task-31: Transfer v3 experiment — round two: the lite payload at 5 fps on two phones

> **Execution:** agent `claude-worker` (opus) · effort `high` · plan mode **no**
> *Why:* 2026-09-16, rewritten after round one. The reader loop is copied from the shipped
> app; the payload is measured, not guessed. Codex is at 100 % until 2026-09-19. Tarik runs the
> phones; the main loop rules.

> **Lane:** OWNS `reports/spike-qr/` (rewrite in place), this file · MUST NOT TOUCH `app/`,
> `tests/`, `scripts/`, `pipeline/`, `design/`, `.github/` (the workflow step from round one
> stays as it is) · GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` green plus
> `PYTHONUTF8=1 .venv/Scripts/python reports/spike-qr/build.py` writes `dist/spike/send.html`
> and `dist/spike/receive.html` · DEPENDS ON none

## Round one, kept as the record (2026-09-16)

Four candidates were built and measured by Tarik on the S24 and the Mi 6 against a laptop
screen: A (one v23 code, robust soliton, refresh-synchronised sender at holds 4, 8 and 12,
`requestVideoFrameCallback` reader, jsQR in a worker), B (2 × 2 codes), C (three codes in
the R, G, B channels), D (B+C). **None completed; the best run reached 15 of 233 blocks.**
The v2 app's plain loop (8 fps, one `BarcodeDetector.detect` per 100 ms on the main thread)
had reached 110 of 233 on the same phone the day before. So the wall is the phone's decode
rate on version-23 codes, and the round-one reader path was slower than the shipped one, not
faster. B and C are shelved: both make each code smaller or harder to read, which is the wrong
direction when the decoder is the bottleneck. The round-one code is replaced in place; the
results table in `README.md` keeps round one's outcome in one line. Round one's worker
loopback numbers (A complete at exactly K; 67 % loss complete at 1.24 × K; C 3 of 3 channels
decoded from a canvas) stay in git history at commit `788a7de`.

## Round two: one candidate

Fewer blocks and cleaner frames. The candidate is exactly what Task-36 would ship, so the
measurement is the product's, not a proxy's.

**Payload.** `build.py` derives it from the main tree's `dist/index.html` (run
`scripts/build_app.py` first): remove the inlined `vendor/jsQR.js` script (the build marks each
inlined file; find the marker for jsQR and drop that whole `<script>`), and in the inlined pack
JSON replace the `layers` value with `[]`; add `data-lite="1"` to `<html>`. Gzip the result
with Python's `gzip` at level 6, report the byte count and `K` on stdout, and write the gzipped
bytes base64-encoded into both spike pages as a constant (the pages then carry the real
payload; no pseudorandom stand-in this round). Expected: about 65 KB, K about 90.

**Fountain code.** Unchanged from round one: 750-byte blocks, source pass then repair only,
robust soliton `c = 0.1`, `delta = 0.5`, xorshift32 seeded from the index, the peeling
receiver copied from `transfer.js`. Frame text `CZ` + index (4 hex) + `K` (4 hex) + length
(6 hex) + 1,000 base64 characters; one code per frame; QR level L as today.

**Sender.** One code per frame, drawn as SVG path exactly as the app does, changed inside
`requestAnimationFrame` and held for `hold` refreshes with the selector offering 12 (5 fps,
the default), 8 and 16. Fullscreen button, wake lock, counter (frames shown, seconds).

**Receiver.** The v2 app's loop, copied not redesigned: `getUserMedia` with the app's
`constraints()`, `tune()` from the inlined `scan.js` (tap focus, zoom slider), then
`setTimeout(scan, 100)` calling `CrosscheckScan.reader().detect(video)` on the main thread
(`BarcodeDetector` where present, else jsQR on the centred 1024 crop). No worker, no
`requestVideoFrameCallback`. Counters: frames read, codes decoded, known of `K`, seconds since
the first decode, decoded per second over the last 5 s, and `DONE <seconds>` with a vibration
when the SHA-256 of the reassembled bytes equals the constant computed at build. On DONE the
page also inflates the bytes with `DecompressionStream("gzip")` and offers `Open lite copy`
(a `blob:` URL) so Tarik can see that the received page runs.

**Recording a run.** One line per completed run in a `<pre>`,
`hold,phone,reader,seconds,frames_read,codes_decoded`, and a `Copy` button that uses
`navigator.clipboard.writeText` inside the click handler (round one's copy failed on the
phone; if the clipboard call rejects, select the `<pre>` text so a long-press copy works).

## Measurement protocol (Tarik)

Laptop fullscreen `send.html`, hold 12. S24 then Mi 6 on `receive.html` from the Pages
address, about 20 cm, five runs each, `Start` on the phone first. If a run passes four
minutes, stop it and note `not complete <known>`. Then hold 8 and hold 16, three runs each on
the S24 only. Paste the `<pre>` lines.

## Decision rule (fixed in advance)

5 of 5 completed on both phones at hold 12 → Task-36 builds it, with the loss budgets set
from the worst measured run. Fewer → camera transfer is retired to the report as a measured
negative result; the share sheet is the offline handoff; `Complete this copy` still ships for
a lite copy that travelled by Quick Share.

## Definition of done

- `build.py` prints the lite payload size and `K`, writes the two pages, each single-file, no
  `src=`/`href=` outside itself, no `fetch(`.
- Loopback without a camera (worker's own Playwright script, not in `tests/`): all frames in
  order complete at exactly `K`; every third frame completes; the inflated bytes parse as HTML
  with `data-lite="1"`, no `jsQR` text, and a pack whose `layers` is empty. Numbers in Status.
- The gate stays green (the spike is outside the app).
- `README.md`: round one's outcome in one line, round two's protocol, empty results table.

## Status

Status: DONE (verify-task, main loop, 2026-09-16). Phone result, Tarik, S24 against the laptop
fullscreen: `12,phone,native,36.1,179,125` and `16,phone,native,27.6,189,141` (hold, phone,
reader, seconds, frames read, codes decoded). Both completed; hold 16 (3.75 fps) was faster
because fewer captured frames straddle a change. The Mi 6 (2017) cannot read the frames at all
and is dropped as a reference device by Tarik's decision ("o kadar eski telefonla
yapmayacağız"); the target is an S24-class phone. `Open lite copy` opened the received page,
online and offline. Verdict: Task-36 builds it at hold 16. Worker notes follow. `reports/spike-qr/` rewritten in place (`build.py`, `page.html`,
`spike.css`, `spike.js`, `README.md`); nothing outside that folder and this file was touched.

**The payload.** `build.py` prints `lite copy: 451,623 bytes, gzipped 69,554 bytes, K 93`
(2026-09-16, SHA-256 `c39ed0d5…`), against v2's 233 blocks — a 2.5x cut, close to the task's
estimate of about 65 KB and K about 90. `dist/spike/send.html` 403,566 bytes,
`dist/spike/receive.html` 403,575 bytes; neither has a `src=`, an `href=` or a `fetch(`, and
neither makes a non-`file:` request in headless Chromium.

**Loopback, no camera** (own Playwright script, run from the worktree root, not committed):

- every frame pushed in order: complete at **93 pushed = exactly K**, and the reassembled bytes
  equal the sender's payload byte for byte and hash to the build's constant;
- every third frame pushed (67 % loss): complete at **120 pushed** out of 360 shown —
  1.29 x K pushed, 3.87 x K shown — same bytes as the lossless run;
- the inflated payload parses as HTML with `data-lite="1"`, carries no vendored jsQR, and its
  pack has `layers` empty, 96 communities, `pack_version` 2;
- the send page at hold 12 drew 8 version-23 codes (109 modules) in 1.4 s in headless Chromium.

**Gate.** `ruff check --no-cache .` clean; `pytest -m browser -q` 93 passed (the app suite is
untouched); `scripts/build_app.py` and `reports/spike-qr/build.py` both run from the root.

### Deviations

1. **"Drop that whole `<script>`" is a cut, not an element.** `scripts/build_app.py` concatenates
   every JS file into **one** `<script>`, so there is no jsQR element to remove. `build.py` cuts
   the licence-comment marker plus the vendored file's own text, both read from the tree, and
   raises if that exact block is not present — so a change in `build_app.py`'s marker fails the
   spike build loudly instead of shipping a payload with jsQR still in it.
2. **"No `jsQR` text" is checked as "no vendored jsQR".** `app/scan.js` names `window.jsQR` as
   its fallback reader and is inlined in every build, so the literal string survives in the lite
   copy by design. The loopback check asserts the library itself is gone: neither its licence
   marker nor its `function jsQR(` definition appears.
3. **The frame SVG is cloned from a `<template>` in `page.html`.** `build.py` refuses a `</`
   inside an inlined script, which rules out `transfer.js`'s own namespace-derivation trick, and
   an SVG namespace URL literal would put a URL in the page. The element is written once in
   markup and cloned; the two lines that draw it (set `viewBox`, set the path's `d` from
   `CrosscheckQR.toSvgPath`) are the app's, unchanged.
4. **The payload is injected as its own small script** (`window.SpikePayload`, carrying the
   base64, the SHA-256 and the two byte counts) rather than as a placeholder inside `spike.js`,
   so `spike.js` stays a plain file with no build-time substitution in it.
5. **`data/raw/` is not in a worktree** (gitignored, it lives only in the main tree), so
   `scripts/gate.py`'s unit step errors there on missing snapshots until the folder is linked in,
   and with it linked `tests/test_regression.py` re-runs the whole pipeline from cold and takes
   far longer than it does in the main tree. The link is not committed and nothing about it is a
   code change. The three gate steps this task can affect were run on their own and are green:
   lint, `scripts/build_app.py`, and the browser suite. The full gate belongs to the main tree.
