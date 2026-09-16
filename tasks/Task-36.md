# Task-36: Transfer v3 in the app, from the Task-31 winner

> **Execution:** agent `claude-worker` (opus) · effort `high` · plan mode **no**
> *Why:* 2026-09-16. The frame contract is correctness-sensitive and the loss tests are the
> criterion; Opus. The "how" is fixed by Task-31's measured verdict, filled into "The winner"
> below by the main loop before this task starts. Codex is at 100 % until 2026-09-19.

> **Lane:** OWNS `app/transfer.js`, `app/scan.js` (only if the winner needs channel or
> quadrant reading), `app/app.css` (transfer rules), `tests/browser/test_transfer.py`,
> `tests/browser/test_scan.py` (only if `scan.js` changes), `reports/spike-qr/` (delete) and
> `.github/workflows/pages.yml` (remove the spike step and path), `CLAUDE.md` Part 2 (only the
> transfer contract paragraph, dated), this file · MUST NOT TOUCH `app/app.js`, `app/qr.js`,
> `app/store.js`, `app/report.js`, `pipeline/`, `design/` · GATE `PYTHONUTF8=1
> .venv/Scripts/python scripts/gate.py` · DEPENDS ON Task-31 (measured), Task-32

## Why

Tarik's phone test stalls near 110 blocks; the cause and the candidates are in Task-31 and
PRD §11 (2026-09-16). This task builds the measured winner into the app and removes v2.

## Fixed regardless of the winner

1. Frame prefix `CZ`, block 750 bytes, header `CZ` + index (4 hex) + `K` (4 hex) + length
   (6 hex) as today; `CY` frames are ignored by the receiver (`FRAME_RE` matches `CZ` only).
2. Repair degree from the robust soliton distribution, `c = 0.1`, `delta = 0.5`, drawn from the
   index-seeded xorshift32 as Task-31 specifies; send order one source pass then repair only.
3. Sender frames change inside `requestAnimationFrame`, held for a fixed number of refreshes
   (the hold Task-31 measured best); receiver reads with `requestVideoFrameCallback` where it
   exists, else `requestAnimationFrame`, with no fixed wait; jsQR runs in a Worker built from
   a `Blob` of its own source text (no file, no request; `test_build.py`'s grep still prints
   nothing).
4. Progress UI as today (`known of K`, vibration, Received, Open, Download, Use received pack).
5. `tests/browser/test_transfer.py`: the round trip (d) against `dist/index.html`; the loss
   tests become three, at 10 %, 50 % and 70 % of the send order dropped by seed, each asserting
   completion within the budget the Task-31 measurement sets (written here by the main loop as
   multiples of `K`); the sources-0..19-never-delivered test stays; a `CY` frame pushed to the
   receiver is ignored (`known` unchanged).
6. `reports/spike-qr/` is deleted and the workflow's spike step and path removed.
7. Part 2's transfer paragraph is rewritten by the main loop to the v3 contract with the
   measured numbers, dated; the worker does not edit it.

## The winner (filled by the main loop after Task-31)

⛔ Not yet written. Candidate: — . Hold: — . Median seconds S24 / Mi 6: — / — . Loss budgets:
10 % — × K, 50 % — × K, 70 % — × K. If B or C: the frame layout and the reader change carried
over from `reports/spike-qr/spike.js`, and for C the layer rule 5 exception line for Part 2.

## Out of the gate

Real-phone completion (Tarik, 5 of 5 on both phones, PRD §6).

## Status

Status: TODO (blocked until "The winner" is filled)
