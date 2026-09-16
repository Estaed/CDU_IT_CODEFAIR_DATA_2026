# Task-37: Transfer v4 — the pack travels by light, not the app

> **Execution:** agent `claude-worker` (opus) · effort `high` · plan mode **no**
> *Why:* 2026-09-16 evening. Frame contract and store validation are correctness-sensitive;
> the "how" is fully written. Codex is at 100 % until 2026-09-19.

> **Lane:** OWNS `app/transfer.js`, `app/store.js` (the layers carry-over and the
> `pack_version` message), `app/app.css` (transfer rules), `scripts/build_app.py` (remove
> `dist/lite.html` and the lite constant), `tests/test_build.py`, `tests/browser/test_transfer.py`,
> `tests/browser/test_update.py`, `tests/browser/conftest.py` (drop the lite fixture if unused),
> this file · MUST NOT TOUCH `app/app.js` (its `renderShare` texts are read, not edited; the
> transfer section's own texts live in `transfer.js`), `app/qr.js`, `app/scan.js`,
> `app/report.js`, `pipeline/`, `design/`, `CLAUDE.md` (already amended by the main loop) ·
> GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` · DEPENDS ON Task-36

## Why

Tarik, 2026-09-16 evening: "if the purpose is only an update, why an animated QR at all?" The
receiving phone reassembles the frames, so it already has Crosscheck; the camera was never an
install path, and a lite copy that "completes itself" served no real scenario. What the camera
*is*: the one pairing-free channel a browser has between an Android and an iPhone with no
network. So the frames carry the data pack, about 18 KB instead of 72, and the demo becomes
"new data, phone to phone, about seven seconds, nothing switched on".

## Contract

1. **Payload.** The text of the inlined `#pack` element parsed, `layers` set to `[]`, serialised
   with `JSON.stringify` (no spaces), gzipped by `CompressionStream("gzip")` at Show time on the
   sending phone (no build-time constant: the pack a received phone holds may be newer than its
   build's). Show plays whatever pack the page is currently running with (`CrosscheckStore`'s
   stored pack if one replaced the inline one; the inline one otherwise).
2. **Frames.** Prefix `CP`; everything else as v3 (750-byte blocks, 4-hex index, 4-hex `K`,
   6-hex length, 1,000 base64 characters, level L, robust soliton c 0.1 delta 0.5, one source
   pass then repair, hold 16 refreshes on `requestAnimationFrame`). `FRAME_RE` matches `CP`
   only; `CX`, `CY`, `CZ` frames are ignored.
3. **Receiver.** Unchanged loop (main thread, 100 ms, `CrosscheckScan`). On completion:
   inflate, `JSON.parse`; on a parse failure say `That did not look like Crosscheck data; try
   again`. Then `CrosscheckStore.save(text)`; when it accepts, show `Received. Tap to use the new
   data.` with `button` `Use received data now` (reloads). When it rejects on `pack_version`,
   show `This copy is too old for that data; open the address once with the internet`.
   `Open received app` and `Download crosscheck.html` are removed (there is no page to open).
4. **Store carry-over.** `CrosscheckStore.save(text)`: if the incoming pack's `layers` is an
   empty array and the currently effective pack (stored, else inline) has the same
   `pack_version` and a non-empty `layers`, the stored pack is written with those layers
   carried over. All other validation (`pack_version`, exactly 96 communities) is unchanged.
5. **Texts on the share screen** (in `transfer.js`, where they already live): Show section
   title `Send the latest data by camera`, note `No internet, no pairing. The other phone needs
   Crosscheck installed; it taps Receive and points its camera at the moving code.` Receive
   section title `Receive new data by camera`, note `Point this camera at the other phone's
   moving code. Your copy keeps working while it arrives.`
6. **Removed.** `dist/lite.html`, `window.CrosscheckLite`, `LITE_CONSTANT`, the lite cut in
   `build_app.py`, `Complete this copy`, `finishHtml`, the `fetch(` and its guard, the lite
   `Receive` refusal, the `full` relabel of the store button. `grep -rn "lite\|CrosscheckLite\|fetch(" app scripts tests` prints nothing except `tests/test_build.py`'s own rule-7
   assertion text. `tests/test_build.py`'s rule-7 test asserts **zero** `fetch(` across `app/`
   (sw.js excluded).
7. **Sizes.** `dist/index.html` drops by about 96 KB (expected about 900 KB); the gate's size
   check is unchanged.

## Tests

`tests/browser/test_transfer.py`: round trip — every frame from a page's encoder pushed into
a second page's receiver reproduces, after inflate, JSON equal to the built pack with
`layers` `[]`, and after `save` the stored pack's `layers` equals the built pack's (carry-over);
`CZ` and `CY` frames ignored; the three loss tests and the sources-0..19 test with the same
budgets as Task-36; the texts of item 5 present; no `.transfer__button` reading `Open` or
`Download`. `tests/browser/test_update.py`: a pack with a different `pack_version` yields the
too-old message and leaves the stored pack untouched. `tests/test_build.py`: no `lite.html`
written, zero `fetch(`, the JS order unchanged otherwise.

## Out of the gate

The S24 run from the app's own share screen (Tarik: laptop Show, phone Receive; expected well
under 10 s) and the Android-to-iPhone case, which no phone here can test.

## Status

Status: TODO
