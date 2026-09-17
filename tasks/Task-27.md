# Task-27: Transfer by camera, progress you can see and missed frames that do not cost a loop

**Status: DONE** — verified 2026-09-15 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* the frame code has an exact criterion (drop frames on purpose, still rebuild the same SHA-256); the progress UI is DOM-checkable.

**Lane**
- OWNS: `app/transfer.js`, `app/app.css` (transfer block only, tokens only), `tests/browser/test_transfer.py`, `tests/browser/test_scan.py` (only where it reads the frame format)
- MUST NOT TOUCH: `app/app.js` and `app/store.js` (Task-24), `app/scan.js` and `app/vendor/` (Task-25), `app/nearby.js`, `app/qr.js`, `pipeline/`, `scripts/gate.py`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-25

## Objective

Tarik, 2026-09-15: "the animated QR needs feedback that it was received; and what happens when
one frame is missed?" Today the sending phone has no signal at all, the receiving phone shows a
bare number, and a missed frame waits for its turn in the next loop: about 16 seconds at 128
frames, about 26 seconds once Task-25 adds jsQR. After this task the receiving phone shows clear
progress and says when it is done (and vibrates), and a missed frame is repaired by any later
frame instead of waiting for its own.

The sending phone still cannot know what the other phone saw: the light only goes one way.
The receiving screen is the feedback, and the sender's screen says so in one line.

## Execution Guide

- **Frame contract v2** (Blueprint amended 2026-09-15). Payload = gzip of the UTF-8 bytes of
  `pageHtml()`. Split into `K` source blocks of 750 bytes, the last padded with zeros. Frame text
  = `CY` + index (4 hex) + `K` (4 hex) + payload length in bytes (6 hex) + base64 of one
  750-byte block (exactly 1,000 characters). Index below `K` is source block `index`. Index `K` or
  above is a repair block: the XOR of a set of source blocks that both ends derive from the index
  alone. Seed an xorshift32 generator with `(index * 2654435761) >>> 0 || 1`, draw a degree uniformly from 6..12,
  clamped to `K` (the robust soliton with c = 0.1, delta = 0.5 was the first design, replaced after the
  2026-09-15 sweep in Status), then draw that many distinct
  block ids. The magic changes from `CX` to `CY` so a receiver from an older copy ignores the new
  frames instead of mixing them up.
- **Send order.** One pass of the `K` source frames, then only new repair frames (`K`, `K+1`, …);
  the first design alternated a cycling source frame with each repair frame and was dropped after
  the 2026-09-15 sweep. Wrap the repair index before `0xFFFF`.
- **Receive.** A peeling decoder: keep the known blocks; reduce each repair frame by XOR-ing out
  the blocks already known; when a frame has one unknown block left, that block becomes known and
  the pending frames are reduced again. Done when all `K` blocks are known; trim to the payload
  length; inflate; validate and open exactly as today (and hand the pack to Task-24's store call,
  which stays where Task-24 put it).
- **API.** `CrosscheckTransfer.encoder(html) -> Promise<{k, length, frameAt(i)}>` and
  `CrosscheckTransfer.receiver() -> {push(text) -> {complete, known, total}, bytes()}`; remove
  `frames` and `reassemble` and update their callers inside `transfer.js` and the tests.
- **Receiving screen.** A `<progress>` with `max` = `K` and `value` = known blocks, the text
  `<known> of <K> blocks`, and when done a clear line `Received. Tap Open.` with the Open button
  shown and `navigator.vibrate` called once where it exists.
- **Sending screen.** `frame <n>` and `pass <p>`, and one line: `Keep showing until the other
  phone says Received.`

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0. (Main loop at integration, 2026-09-15: GATE GREEN.)
- [x] `tests/browser/test_transfer.py`: every frame from `encoder(dist html)` matches `^CY[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{6}[A-Za-z0-9+/]{1000}$`; pushing frames `0..K-1` into a receiver completes and the SHA-256 of the inflated result (computed in the page) equals the SHA-256 of `dist/index.html`; with a seeded random 10 % of frames dropped from the send order, the receiver completes within `1.75 * K` pushed frames with the same SHA-256; with source frames `0..19` never delivered it completes within `1.75 * K`; a frame starting `CX` is ignored. (Bound changed from `1.5 * K` to `1.75 * K` by Tarik on 2026-09-15: a 42-variant sweep found no design that meets `1.5 * K` reliably, and `1.75` is the smallest multiplier with 50 of 50 seeds at K 224 for the adopted design; see Status.)
- [x] Same test: on `#/share`, after pushing every frame through the page's receiver hook, the `<progress>` value equals its `max`, `Received. Tap Open.` is visible and the Open button is visible; after Show, the sender shows text matching `frame \d+` and `pass \d+`.
- [x] `grep -nE "fetch\(|XMLHttpRequest|WebSocket|https?://" app/transfer.js` prints nothing; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/transfer.js` prints nothing; zero non-`file:` requests and no console errors; every existing browser test stays green.

## Status

DONE 2026-09-15 (main loop: three-way cherry-pick with no conflict, gate green; mutation check: forcing repair degree 60 turns the 10 % loss test red, restored; bound 1.75 x K approved by Tarik after the sweep) Worker notes follow.

### Adopted: repair-only send order, uniform 6..12 degree, budget = 1.75 × K (this round)

Tarik's decision after the sweep below: adopt the best measured variant
(`repair-only after first pass` + `uniform 6..12` degree) and set the completion budget from
measurement instead of the original estimate. Implemented in `app/transfer.js`:
- **Send order** (`createSequence`): after the first pass of the `K` source frames, only new
  repair frames are sent (`K, K+1, ...`, wrapping before `0xFFFF`) — no more cycling source
  resend. `pass` now counts laps of the repair-index space instead of laps of the source cycle.
- **Repair degree** (`drawDegree`): a uniform integer in `6..12`, clamped to `K`, drawn from the
  same xorshift32 stream the index seeds — replaces the robust soliton distribution
  (`solitonCache`/`solitonCumulative`, both removed; nothing else in the file used them).
  `drawDistinctIds`, `blockIdsForIndex`, the `CY` frame format, block size, `encoder`/`receiver`
  APIs, the progress UI and the `testPushFrame`/`testReceiveComplete` hooks are all unchanged.
- Also removed as dead weight once sources are only ever sent once: `buildShow`'s per-source QR
  cache (`sourceCache`/`qrFor`) — a direct consequence of the send-order change, cleaned up under
  the "remove what your own change made unused" rule rather than left as debris.

**50-seed measurement, K = 224 (the app's real size), the exact code path (same xorshift32 seed
formula, same peeling receiver, same `createSequence`), 10% of the send order dropped, seeds
1..50:**

| Budget m | cap = ⌈m × K⌉ | Successes / 50 | Worst pushed among successes |
|---|---|---|---|
| 1.5 | 336 | 45/50 | 335 (5 trials did not complete within cap) |
| 1.75 | 392 | **50/50** | 345 |
| 2.0 | 448 | 50/50 | 345 |
| 2.25 | 504 | 50/50 | 345 |
| 2.5 | 560 | 50/50 | 345 |
| 3.0 | 672 | 50/50 | 345 |

**Chosen m = 1.75** — the smallest of the six tried that reaches 50/50.

**Test seed check** (seed 20260915, the seed `test_transfer.py` already used before this round —
not switched to find an easier one): completes at **321 pushed frames** at K = 224, well inside
every multiplier tried, including 1.5 × K (336).

**Sources 0..19 never-delivered scenario** (deterministic, no drop, run once): completes at
**302 pushed frames** at K = 224 — also inside 1.5 × K, so the same `m = 1.75` budget covers it
with more margin than the drop scenario needed.

Both `tests/browser/test_transfer.py::test_seeded_ten_percent_drop_completes_within_budget` and
`::test_sources_0_to_19_never_delivered_still_completes` now assert `1.75 * K` (not the DoD's
original `1.5 * K` line, which is left untouched above for the main loop to rewrite with this
figure, per instruction). Both are green — see the commands below.

Files touched this round: `app/transfer.js` (send order + degree family, see above),
`tests/browser/test_transfer.py` (both loss-budget tests now assert `1.75 * K`; module docstring
and per-test comments updated to explain why and point at this section).
`tests/browser/test_scan.py` and `tests/browser/test_update.py` untouched this round (their
`encoder`/`createSequence`/`receiver` calls needed no change — the API surface did not move).

Commands run from the worktree root with the main tree's `.venv`, this round:
- `ruff check --no-cache .` → `All checks passed!`
- `python scripts/build_app.py` → `dist\index.html: 853548 bytes`
- `python -m pytest tests/test_build.py tests/browser -q` → **86 passed, exit code 0.**
- `scripts/gate.py` was **not** run (no `data/raw/` in this worktree, per instructions).

K for the current build: **224** source blocks (`dist/index.html` 853,548 bytes; gzipped
payload 167,442 bytes; 750-byte blocks) — effectively unchanged from the previous round's 224.

### Fix-the-code sweep (previous round, kept for history)

Per the coordinator's instruction, the DoD's `1.5 * K` was put back in the test, and the pinned
algorithm was swept for a variant that clears **both** loss scenarios ("seeded random 10% of
the send order dropped" and "source frames 0..19 never delivered, no other loss") within
`1.5 * K` pushed frames, at K = 43, 90 and 224, 20 seeded trials per scenario (the
0..19-never-delivered scenario has no randomness beyond the fixed omission, so its "20 trials"
are identical runs; reported once per variant/K, same as ticking every seed). The simulation
reused the exact pinned pieces unchanged: xorshift32 seeded from `(index * 2654435761) >>> 0 ||
1`, the same peeling decoder, the same distinct-id draw. Two send orders and seven degree
families, 14 variants x 3 K = 42 rows:

| Send order | Degree family | K | cap (1.5×K) | 10% drop: successes / 20 (max pushed among successes) | Sources 0..19 never delivered |
|---|---|---|---|---|---|
| alternate (current) | soliton c=0.03 δ=0.05 | 43 | 65 | 8/20 (64) | complete, 59 pushed |
| alternate (current) | soliton c=0.03 δ=0.05 | 90 | 135 | 4/20 (133) | not complete (135) |
| alternate (current) | soliton c=0.03 δ=0.05 | 224 | 336 | 1/20 (319) | not complete (336) |
| alternate (current) | soliton c=0.03 δ=0.5 | 43 | 65 | 7/20 (64) | not complete (65) |
| alternate (current) | soliton c=0.03 δ=0.5 | 90 | 135 | 2/20 (128) | not complete (135) |
| alternate (current) | soliton c=0.03 δ=0.5 | 224 | 336 | 1/20 (334) | not complete (336) |
| alternate (current) | soliton c=0.1 δ=0.05 | 43 | 65 | 14/20 (65) | not complete (65) |
| alternate (current) | soliton c=0.1 δ=0.05 | 90 | 135 | 2/20 (128) | not complete (135) |
| alternate (current) | soliton c=0.1 δ=0.05 | 224 | 336 | 1/20 (321) | not complete (336) |
| alternate (current, **pinned**) | soliton c=0.1 δ=0.5 (**pinned**) | 43 | 65 | 8/20 (64) | not complete (65) |
| alternate (current, **pinned**) | soliton c=0.1 δ=0.5 (**pinned**) | 90 | 135 | 2/20 (128) | not complete (135) |
| alternate (current, **pinned**) | soliton c=0.1 δ=0.5 (**pinned**) | 224 | 336 | 1/20 (319) | not complete (336) |
| alternate (current) | soliton c=0.3 δ=0.05 | 43 | 65 | 6/20 (65) | not complete (65) |
| alternate (current) | soliton c=0.3 δ=0.05 | 90 | 135 | 0/20 (—) | not complete (135) |
| alternate (current) | soliton c=0.3 δ=0.05 | 224 | 336 | 0/20 (—) | not complete (336) |
| alternate (current) | soliton c=0.3 δ=0.5 | 43 | 65 | 11/20 (65) | not complete (65) |
| alternate (current) | soliton c=0.3 δ=0.5 | 90 | 135 | 0/20 (—) | not complete (135) |
| alternate (current) | soliton c=0.3 δ=0.5 | 224 | 336 | 0/20 (—) | not complete (336) |
| alternate (current) | uniform 6..12 | 43 | 65 | 15/20 (65) | not complete (65) |
| alternate (current) | uniform 6..12 | 90 | 135 | 12/20 (133) | complete, 116 pushed |
| alternate (current) | uniform 6..12 | 224 | 336 | 12/20 (335) | not complete (336) |
| repair-only after first pass | soliton c=0.03 δ=0.05 | 43 | 65 | 14/20 (64) | complete, 51 pushed |
| repair-only after first pass | soliton c=0.03 δ=0.05 | 90 | 135 | 14/20 (134) | not complete (135) |
| repair-only after first pass | soliton c=0.03 δ=0.05 | 224 | 336 | 13/20 (335) | not complete (336) |
| repair-only after first pass | soliton c=0.03 δ=0.5 | 43 | 65 | 13/20 (64) | complete, 58 pushed |
| repair-only after first pass | soliton c=0.03 δ=0.5 | 90 | 135 | 14/20 (135) | not complete (135) |
| repair-only after first pass | soliton c=0.03 δ=0.5 | 224 | 336 | 11/20 (335) | not complete (336) |
| repair-only after first pass | soliton c=0.1 δ=0.05 | 43 | 65 | 18/20 (63) | complete, 61 pushed |
| repair-only after first pass | soliton c=0.1 δ=0.05 | 90 | 135 | 12/20 (135) | complete, 121 pushed |
| repair-only after first pass | soliton c=0.1 δ=0.05 | 224 | 336 | 15/20 (332) | complete, 301 pushed |
| repair-only after first pass | soliton c=0.1 δ=0.5 | 43 | 65 | 14/20 (64) | complete, 58 pushed |
| repair-only after first pass | soliton c=0.1 δ=0.5 | 90 | 135 | 7/20 (126) | not complete (135) |
| repair-only after first pass | soliton c=0.1 δ=0.5 | 224 | 336 | 8/20 (335) | not complete (336) |
| repair-only after first pass | soliton c=0.3 δ=0.05 | 43 | 65 | 13/20 (65) | not complete (65) |
| repair-only after first pass | soliton c=0.3 δ=0.05 | 90 | 135 | 5/20 (134) | not complete (135) |
| repair-only after first pass | soliton c=0.3 δ=0.05 | 224 | 336 | 8/20 (329) | not complete (336) |
| repair-only after first pass | soliton c=0.3 δ=0.5 | 43 | 65 | 15/20 (65) | complete, 58 pushed |
| repair-only after first pass | soliton c=0.3 δ=0.5 | 90 | 135 | 6/20 (134) | not complete (135) |
| repair-only after first pass | soliton c=0.3 δ=0.5 | 224 | 336 | 6/20 (328) | not complete (336) |
| repair-only after first pass | uniform 6..12 | 43 | 65 | **20/20** (58) | not complete (65) |
| repair-only after first pass | uniform 6..12 | 90 | 135 | 19/20 (130) | complete, 103 pushed |
| repair-only after first pass | uniform 6..12 | 224 | 336 | 17/20 (332) | complete, 302 pushed |

**No variant passes both scenarios (20/20 on the drop, complete on the never-delivered case) at
all three K.** The two closest: `repair-only + uniform 6..12` clears the drop 20/20, 19/20,
17/20 at K=43/90/224 but fails the never-delivered case at K=43 (needs a repair frame to hit a
missing block that a uniform-degree draw over the *whole* K happens not to reach fast enough in
65 frames when only 20 of 43 blocks are even missing); `repair-only + soliton(c=0.1, δ=0.05)`
clears the never-delivered case at all three K but the drop only 18/20, 12/20, 15/20. Every
other combination is worse on at least one axis. Per step 4 of the coordinator's instruction:
**no criterion changed, `app/transfer.js` is unchanged from the previous round** (still
`c = 0.1`, `δ = 0.5`, the alternating send order — the pinned row above, which itself only
clears the drop 8/1/1 out of 20 at K=43/90/224 and never clears the never-delivered case within
`1.5 * K`), and the two DoD tests are left failing.

At the time this sweep was reported, no parameter/send-order combination reached the DoD's
`1.5 * K` for both loss scenarios at K=224, and step 4 of the coordinator's instruction said to
stop and report rather than keep widening the search or relax the number. Tarik's decision on
seeing this table (recorded at the top of this Status section): adopt `repair-only + uniform
6..12` — the best performer on the drop scenario in the table above (20/20, 19/20, 17/20 at
K=43/90/224, all with a 1.5×K cap) — and set the pushed-frame budget from a fuller, 50-seed
measurement of that exact variant rather than the original `1.5 * K` estimate. That measurement,
the resulting `m = 1.75`, and the code change are above.

Not verified by this lane: the actual camera round trip on a phone (out of the Definition of
Done per Blueprint, "Not in the Definition of Done"), and `scripts/gate.py` end to end (no
`data/raw/` in this worktree).
