# Task-27: Transfer by camera, progress you can see and missed frames that do not cost a loop

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
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

- **Frame contract v2** (Part 2 amended 2026-09-15). Payload = gzip of the UTF-8 bytes of
  `pageHtml()`. Split into `K` source blocks of 750 bytes, the last padded with zeros. Frame text
  = `CY` + index (4 hex) + `K` (4 hex) + payload length in bytes (6 hex) + base64 of one
  750-byte block (exactly 1,000 characters). Index below `K` is source block `index`. Index `K` or
  above is a repair block: the XOR of a set of source blocks that both ends derive from the index
  alone. Seed an xorshift32 generator with `(index * 2654435761) >>> 0 || 1`, draw a degree from
  the robust soliton distribution for `K` (c = 0.1, delta = 0.5), then draw that many distinct
  block ids. The magic changes from `CX` to `CY` so a receiver from an older copy ignores the new
  frames instead of mixing them up.
- **Send order.** One pass of the `K` source frames, then alternate one source frame (cycling) and
  one new repair frame (`K`, `K+1`, …), so a phone that starts late still gets both kinds. Wrap the
  repair index before `0xFFFF`.
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

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_transfer.py`: every frame from `encoder(dist html)` matches `^CY[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{6}[A-Za-z0-9+/]{1000}$`; pushing frames `0..K-1` into a receiver completes and the SHA-256 of the inflated result (computed in the page) equals the SHA-256 of `dist/index.html`; with a seeded random 10 % of frames dropped from the send order, the receiver completes within `1.5 * K` pushed frames with the same SHA-256; with source frames `0..19` never delivered it still completes; a frame starting `CX` is ignored.
- [ ] Same test: on `#/share`, after pushing every frame through the page's receiver hook, the `<progress>` value equals its `max`, `Received. Tap Open.` is visible and the Open button is visible; after Show, the sender shows text matching `frame \d+` and `pass \d+`.
- [ ] `grep -nE "fetch\(|XMLHttpRequest|WebSocket|https?://" app/transfer.js` prints nothing; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/transfer.js` prints nothing; zero non-`file:` requests and no console errors; every existing browser test stays green.

## Status

Not started.
