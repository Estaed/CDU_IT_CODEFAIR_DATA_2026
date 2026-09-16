# Task-31: Transfer v3 experiment — A, B, C and B+C measured on two phones

> **Execution:** agent `claude-worker` (opus) · effort `high` · plan mode **no**
> *Why:* 2026-09-16. Image processing (channel split, quadrant crop) and a fountain decoder are
> correctness-sensitive, so the worker is Opus; the "how" is written below, so no plan mode.
> Codex is at 100 % until 2026-09-19. The phone runs are Tarik's; the verdict is the main loop's.

> **Lane:** OWNS `reports/spike-qr/` (new), `.github/workflows/pages.yml` (one step and one
> path), this file · MUST NOT TOUCH `app/`, `tests/`, `scripts/`, `pipeline/`, `design/` ·
> GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` (must stay green: the spike is outside
> the app and ruff excludes `reports/`) plus `PYTHONUTF8=1 .venv/Scripts/python
> reports/spike-qr/build.py` writes four files under `dist/spike/` · DEPENDS ON none

## Why

Tarik's phone test, 2026-09-16: the receiver climbs to about 110 blocks and then crawls. The
main loop reproduced it in simulation with the shipped decoder (PRD §11, 2026-09-16): the v2
repair degree (uniform 6..12) was tuned against 10 % frame loss, a real phone loses half or
more, and at that loss a repair frame almost never reduces to one unknown block. Rather than
pick a fix on paper, four candidates are built as standalone pages and measured on the S24 and
the Mi 6. The winner is built into the app by Task-36.

## What is built

`reports/spike-qr/` holds the experiment; nothing in the app imports it, and it is deleted
when Task-36 lands.

- `build.py`: inlines `app/vendor/jsQR.js`, `app/qr.js` and `app/scan.js` from the main tree
  (read-only; the spike must not copy them) plus `spike.js` and `spike.css` into
  `dist/spike/send.html` and `dist/spike/receive.html`, and copies nothing else. Two pages, not
  eight: each page carries a candidate selector.
- `spike.js`: the shared code, one `window.Spike` object. `spike.css`: plain CSS, literal
  values allowed (this is not the app; layer rule 5 does not apply under `reports/`).
- `README.md`: how to run, the decision rule, and the results table (filled by the main loop
  from Tarik's numbers).
- `pages.yml`: one added step after `Build dist/index.html` running `uv run python
  reports/spike-qr/build.py`, and `reports/spike-qr/**` added to the trigger paths. The
  pages are then at `<APP_URL>spike/send.html` and `<APP_URL>spike/receive.html`; the camera
  needs the secure origin (PRD §11, 2026-09-15).

## The contract

**Payload.** Both pages generate the same test payload in-page: 174,725 bytes from xorshift32
seeded with `0x5EED`, byte = low 8 bits of each draw. That is the gzipped size of the app on
2026-09-16, so `K` matches the real thing (233 blocks of 750). The receiver verifies completion
with SHA-256 over the reassembled bytes against the sender's, computed by `crypto.subtle` on
both pages and shown as its first 8 hex characters.

**Fountain code, common to every candidate.** Source blocks of 750 bytes as today. The repair
block set for index `i` is drawn from xorshift32 seeded `(i * 2654435761) >>> 0 || 1` as
`transfer.js` does today, but the degree comes from the robust soliton distribution with
`c = 0.1`, `delta = 0.5` (build the cumulative table once per `K`, draw one uniform from the
same generator, binary-search the table; degree 1 is allowed). Send order: one pass of sources,
then repair only, as today. The receiver is the peeling decoder of `transfer.js`, copied into
`spike.js` (the spike must not import `transfer.js`; `CY` compatibility is not wanted).

**Frame text.** `CZ` + candidate letter (`A`, `B`, `C`, `D` for B+C) + index (4 hex) + `K`
(4 hex) + payload length (6 hex) + base64 of one block (1,000 characters). One code carries
one block in every candidate; the candidates differ in how many codes a frame carries and how.

**Candidates.**

- **A — one code per frame, synchronised.** One QR per frame, exactly as today's geometry.
  Sender: the frame changes inside `requestAnimationFrame`, held for `hold` display refreshes
  (selector: 4, 6, 8; at 60 Hz that is 15, 10 and 7.5 frames a second), never from a timer.
  Receiver: `video.requestVideoFrameCallback` where it exists, else `requestAnimationFrame`;
  no fixed wait between reads. jsQR runs in a Web Worker built from a `Blob` URL of its own
  source (no separate file, no request), one frame in flight at a time, frames arriving while
  one is decoding are dropped. The native `BarcodeDetector` path stays on the main thread as
  today. The reader choice is the page's own copy of `CrosscheckScan.kind()`.
- **B — four codes per frame.** A 2 × 2 grid of four codes, each the same version as A's
  single code (the grid is larger on screen; the page is fullscreen, landscape suggested by a
  line of text). Frame `n` shows indexes `4n .. 4n+3` of the send order. Receiver, native:
  `detect()` returns every code in the picture, all are pushed. Receiver, jsQR: the centred
  square is split into four quadrants and each is decoded separately (four worker calls per
  frame, or one call per quadrant in turn). Sender timing as A.
- **C — three codes per frame in colour.** Three codes of A's geometry, one per colour
  channel, drawn on one canvas: a module is dark in channel `c` if that channel's code has a
  dark module there, so the pixel colour is `(R, G, B)` with each component `0` when dark and
  `255` when light. The finder and timing patterns are identical in all three codes (same
  version, same mask forced to mask 0 by the encoder option), so they are black in the
  composite and every reader locates them. Frame `n` shows indexes `3n .. 3n+2`. Receiver:
  the camera frame's centred square is split into three greyscale images (the R, G and B
  components each stretched to the range of that channel's own darkest and lightest 1 % of
  pixels, then written as grey RGBA), and each is decoded as an ordinary QR by the page's
  reader (`BarcodeDetector.detect(canvas)` accepts a canvas; jsQR takes the ImageData). Crosstalk
  between channels is what the experiment measures. Sender timing as A.
- **D — B and C together.** The 2 × 2 grid of colour composites: twelve blocks per frame,
  indexes `12n .. 12n+11`.

**Send page controls.** Candidate (A, B, C, D), hold (4, 6, 8 refreshes), Start / Stop, and
a counter: frames shown, elapsed seconds, the payload hash. Fullscreen button. Wake lock.

**Receive page controls.** Candidate (must match), Start / Stop, reader kind shown, and the
counters that make the measurement: camera frames seen, codes decoded, new blocks, known of
`K`, elapsed seconds since the first decoded code, and on completion `DONE <seconds> <hash>`
with a vibration. Also `loss = 1 - decoded / (frames shown so far as told by the sender)` is
not computable across two phones, so the receive page shows instead *decoded per second* and
*new blocks per second* over the last 5 seconds. Tap-to-focus and the zoom slider from
`scan.js`'s `tune()` are reused.

**Recording a run.** Every completed run appends one line to a `<pre>` on the receive page,
`candidate,hold,phone,reader,seconds,frames_seen,codes_decoded`, with a Copy button, so Tarik
copies the block once per phone into the README's results table.

## Measurement protocol (Tarik, on the phones)

Sender: the laptop's browser fullscreen on `send.html` at the same window size for every run,
or the second phone. Receiver: S24, then Mi 6, on `receive.html` from the Pages address. For
each candidate at hold 6: five runs per phone, receiver held by hand about 20 cm from the
screen, Start on the receiver first. Then A at hold 4 and hold 8, five runs each on the S24
only. Copy the `<pre>` block after each phone.

## Decision rule (fixed in advance, PRD §4.2)

Among candidates that complete 5 of 5 runs on both phones at hold 6, the shortest median
seconds wins; ties go to the simpler candidate (A before B before C before D). If no candidate
completes 5 of 5 on both phones, the one with the most completions wins and Task-36 records
the gap. The main loop writes the verdict into `README.md` and into Task-36's spec.

## Definition of done

- `build.py` runs from the root and writes `dist/spike/send.html` and `dist/spike/receive.html`,
  each a single file with no `src=` or `href=` to anything outside itself.
- Loopback check without a camera, in the worker's own browser session (not a gate test):
  pushing every frame text of candidate A in order completes at exactly `K` pushed; pushing
  every third frame (a 67 % loss) completes; the hash matches. Reported in Status with numbers.
- Candidate C's composite, drawn to a canvas and split back by the receiver's own channel
  code, decodes all three codes in the same session (screen to canvas, no camera). Reported.
- The gate stays green; the workflow file parses (`python -c "import yaml, sys;
  yaml.safe_load(open('.github/workflows/pages.yml'))"` if PyYAML is present, else by eye).
- `README.md` holds the empty results table and the protocol above.

## Out of the gate

The phone runs (Tarik), the verdict (main loop). Whether landscape helps. iPhone (none
available).

## Status

Status: BUILT 2026-09-16, awaiting the phone runs and the main loop's verdict (`verify-task` is
the gate; this section is the worker's report, not a DONE mark).

### What was built

`reports/spike-qr/`, five files, nothing under `app/`, `tests/`, `scripts/` or `pipeline/`
touched:

- `spike.js` (979 lines, one `window.Spike`): the `CZ` frame contract, the fountain encoder, the
  peeling receiver copied from `transfer.js` (not imported), the robust soliton degree table
  (`c = 0.1`, `delta = 0.5`, cumulative table per `K`, one uniform draw, binary search), the
  in-page 174,725-byte payload, the four candidate geometries as one `SHAPE` table
  (`cells × channels`: A 1×1, B 4×1, C 1×3, D 4×3), the drawing side, the reading side
  (quadrant split, channel split with the 1 % stretch), the jsQR Blob worker, and both pages.
- `spike.css`, `page.html`, `build.py`, `README.md` (protocol, empty results table, decision
  rule, and the laptop numbers below).
- `.github/workflows/pages.yml`: one step (`Build dist/spike/`, after `Build dist/index.html`)
  and one trigger path (`reports/spike-qr/**`). Nothing else in the file changed.

### Verification (from the worktree root, main tree's `.venv`, `PYTHONUTF8=1`)

- `ruff check --no-cache .` → `All checks passed!`
- `python scripts/build_app.py` → `dist\index.html: 877751 bytes`
- `python reports/spike-qr/build.py` → `dist\spike\send.html: 318277 bytes`,
  `dist\spike\receive.html: 318286 bytes`. Neither file contains a single `src="` or `href="`
  (grep over both: zero matches) nor any `http://`, `https://`, `fetch(` or `XMLHttpRequest`.
- `pytest -m browser -q` → **86 passed, exit code 0** (the app suite is untouched).
- **`scripts/gate.py` was not run**: this worktree has no `data/raw/`, so the pipeline half of
  the gate cannot run here. The three checks the gate would run that are affected by this change
  (ruff, `build_app.py`, `pytest -m browser`) are green above.
- `python -c "import yaml, ..."` → `ModuleNotFoundError: No module named 'yaml'` (PyYAML is not
  in the environment), so `pages.yml` was checked by eye as the DoD allows: one list item added
  to `on.push.paths` at the same indentation as its siblings, one step added to `jobs.build.steps`
  in the same shape as the `Build dist/index.html` step above it. Line endings stay LF.

### Loopback numbers (Definition of done), headless Chromium, `file://`, no camera

Run with a throwaway Playwright script (not added to `tests/`), driving `dist/spike/receive.html`
and calling the page's own `Spike` functions.

| Check | Result |
|---|---|
| A, every frame pushed in order | complete at **233 pushed = exactly K**; payload hash `ab4eb170`, received hash `ab4eb170` |
| A, every third frame pushed (67 % loss) | complete at **290 pushed** of **868 shown** (1.24 × K pushed, 3.73 × K shown); same hash both ends |
| C, composite drawn then split back by the receiver's own channel code | **3 of 3** codes decoded, each byte-equal to the text encoded into that channel (version 23, 109 modules, 468 px picture, jsQR) |
| B, through the Blob worker (extra, not required) | **4 of 4** quadrants decoded; reader kind `jsqr` |
| Sender smoke, all four candidates, hold 6 (extra) | no page error, no request; frames a second: A 10.7, B 9.3, C 10.7, **D 5.7** |

For contrast with v2: the shipped uniform 6..12 degree needed 1.75 × K pushed frames to survive
**10 %** loss (Task-27 Status). The soliton degree here survives **67 %** loss at 1.24 × K
pushed. That is one seed and one deterministic loss pattern, not a sweep — it is the DoD's
check, not a verdict on the degree family.

### Deviations from the spec, and why

1. **`page.html` exists, and the folder has five files rather than four.** The task listed
   `build.py`, `spike.js`, `spike.css` and `README.md`. Both pages need HTML around the inlined
   blocks; putting that markup in Python strings inside `build.py` would hide it. One template
   with a `__PAGE__` placeholder and a `data-page` attribute produces both pages, mirroring
   `app/index.html` → `scripts/build_app.py`.
2. **The Lane block says `build.py` "writes four files under `dist/spike/`"; it writes two.**
   The "What is built" section and the Definition of done both name exactly two
   (`send.html`, `receive.html`) and say "two pages, not eight", so two is what was built. The
   count in the Lane block looks like a leftover. Flagging rather than inventing two more files.
3. **Candidate C does not force mask 0.** `app/qr.js`'s `encode(text, level)` has no mask option
   and the lane must not touch `app/`. The three channel codes are therefore rendered with
   whatever mask the encoder picks for each. This is safe for the reason the task's own sentence
   gives: the finder, timing and alignment patterns are fixed by the version, not by the mask, so
   they are identical in all three codes and black in the composite, and every reader locates
   them. Only the **format-information** modules differ per channel by mask choice — and each
   channel's format bits are read from that channel's own picture after the split, never from the
   composite. The data modules differ per channel by design in any case. Measured: 3 of 3 codes
   decode from a real composite (table above). If the phone runs show C failing where this
   suggests it should not, the mask option is the first thing to add — in Task-36, in `app/qr.js`,
   by whoever owns that file.
4. **The receive page's frame counter counts sampled frames, not every camera frame.** With
   `requestVideoFrameCallback` the page only sees the frames it asks for, and it asks for the
   next one after the last decode finishes ("one frame in flight, later frames dropped", as the
   task specifies). So `frames_seen` in the log line is "frames looked at", and the drop is
   visible as the gap between that and the camera's own rate rather than as a counter.
5. **`build.py` refuses on a `</` in any inlined source instead of escaping it.** `spike.js`
   reads the jsQR script element's `textContent` back to build the worker, and the usual `<\/`
   escape would be a syntax error there. No inlined file contains the sequence (checked: zero
   occurrences in all four).

### Open questions for the main loop

- Candidate D plays at **5.7 fps against a nominal 10** on a fast laptop because twelve
  version-23 codes must be QR-encoded per frame. A phone will be slower. D may therefore be
  measuring the encoder rather than the camera. Worth deciding before the runs whether to keep D
  at hold 6 or give it its own hold.
- The protocol says "the laptop's browser fullscreen ... at the same window size for every run".
  The sender scales the codes to the largest square in the stage, so the same window gives A and
  C twice the module size B and D get. That is the honest comparison (same screen, more codes)
  but it should be stated in the report as the thing being traded.
