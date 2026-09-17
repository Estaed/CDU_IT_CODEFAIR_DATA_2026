# Task-37: Transfer v4 — the pack travels by light, not the app

**Status: DONE** — verified 2026-09-17 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

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

Status: implemented by the lane 2026-09-16, commit `609de81`; `verify-task` from the main loop
still owns DONE. Nothing outside the Lane's OWNS list was touched.

**What shipped.** `app/transfer.js` is v4: prefix `CP`, payload `packText()` = the currently
effective pack with `layers: []`, `JSON.stringify`d and gzipped at Show time. Everything else of
v3 is unchanged (750-byte blocks, the same header, robust soliton c 0.1 delta 0.5, one source
pass then repair, `requestAnimationFrame` with `HOLD_REFRESHES = 16`, the receiver's main-thread
`setTimeout` 100 ms loop through `CrosscheckScan`). `finish(bytes)` inflates, `JSON.parse`s,
hands the text to `CrosscheckStore.save` and prints one of three sentences. `isLite`,
`payloadBytes`, `appUrl`, `buildComplete`, `finishHtml`, the `fetch(`, `Open received app` and
`Download crosscheck.html` are gone. `app/store.js` gained `effective()` (stored pack when it is
newer than the built-in one, the same test app.js applies at startup; exported) and the layers
carry-over in `save`, which now also reports `reason: "pack_version"` on that one refusal.
`scripts/build_app.py` lost `LITE_OUT`, `LITE_PLACEHOLDER`, `LITE_CONSTANT`, `strip_jsqr`,
`strip_lite_constant`, `empty_layers`, `mark_lite`, `build_lite`, `PACK_RE`, `HTML_TAG_RE` and
the `base64`/`gzip` imports; it writes one page.

**Numbers.** `dist/index.html` **899,186 bytes**, down **98,584** from Task-36's 997,770 (85.7 %
of the 1,048,576 limit, was 95.2 %); no `dist/lite.html` is written. Payload: pack JSON with
`layers: []` **260,945 characters**, gzipped to **K 24** blocks (about 17.6 KB), against K 341
for the whole page and K 97 for the lite copy. `ruff check --no-cache .` → `All checks passed!`.
`pytest tests/test_build.py -q` → **23 passed**. `pytest -m browser -q` → **98 passed**
(`tests/browser/test_transfer.py` alone: 13). Loss tests, seed 20260915, at K 24: 10 % → **31**
pushed (cap 39), 50 % → **40** (cap 68), 70 % → **30** (cap 108); sources 0..19 never delivered
→ **32** pushed (cap 42). Part 2 greps: rule 5 prints nothing; rule 7 prints nothing; rule 8
prints exactly `app/transfer.js` and `audio: true` prints nothing.
`grep -rn "lite.html|CrosscheckLite|data-lite|fetch\(" app scripts tests` prints `app/sw.js`
twice (the host-only exception Part 2 names) and test assertion text only.

**Deviations, and why.**

1. **`CrosscheckStore.effective()` is new and exported.** Item 1 and item 4 both need "the
   currently effective pack", and app.js (MUST NOT TOUCH) does not expose which pack it is
   rendering. One definition in `store.js` beside the stored record is the honest place for it;
   duplicating the `stored.built > builtIn.built` test inside `transfer.js` would have been a
   second definition of the same rule.
2. **`save` returns `{built: null, reason: "pack_version"}`.** The receiving screen has to tell
   a version refusal from a malformed pack, and the validation lives in `store.js`. The existing
   `{built}` shape is unchanged, so `tests/browser/test_update.py`'s older assertions still hold.
3. **A refusal that is not `pack_version` reuses the parse-failure sentence.** Item 3 names only
   the two messages; a pack that validates as JSON but has the wrong community count is not a
   third case worth a third sentence, and "that did not look like Crosscheck data" is true of it.
4. **`testPayloadText` was added to the test hooks.** Without it the round-trip test would
   rebuild the payload itself and never exercise `packText()` — that is, it would not test what
   Show actually plays. Same shape as the existing `testPushFrame` and `testReceiveComplete`.
5. **`mount(container)` ignores its second argument.** `app.js` still passes `pageHtml` and is
   not this task's to change; Show no longer plays the page, so the parameter is dropped from
   the signature and the call keeps working.
6. **The `CZ`/`CY` ignore test is one parametrised test, not two.** Item "Tests" asks for both
   prefixes; one body with `["CY", "CZ"]` is the same coverage in half the lines.
7. **`tests/browser/test_transfer.py` no longer lists `fetch(` among its forbidden tokens.**
   `tests/test_build.py::test_no_fetch_anywhere_in_the_app` asserts zero across all of `app/`,
   which subsumes it, and keeping it here would have left a second `fetch(` in the repo grep for
   no extra coverage.
8. **`blocking_page` was removed from `tests/browser/conftest.py`.** It existed only for
   Task-36's lite-page test and had no other caller; the Lane allows dropping it if unused.

**Open, for the main loop.** `.github/workflows/pages.yml` lines 41-43 still name
`dist/lite.html` in a comment and a step name. The step only runs `scripts/build_app.py`, so the
deploy is correct, but the text is now wrong. That file is outside this Lane's OWNS list, so it
was left alone.

**Out of the gate, unchanged:** the S24 run from the share screen and the Android-to-iPhone case
(no phone here can test it). The full gate cannot run here: `data/raw/` is gitignored and lives
only in the main tree, so `pytest -m "not browser"` errors on the pipeline snapshots. The four
steps this task can affect were run on their own and are green.

- Main loop, 2026-09-17: the first gate run on main was red only because a stale `dist/lite.html` from the Task-36 build was still on disk (dist/ is gitignored); removed, gate green (150 unit, 98 browser). The DONE tick and the push had already gone out before that rerun; recorded here rather than hidden.
