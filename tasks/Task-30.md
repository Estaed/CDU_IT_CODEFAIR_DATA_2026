# Task-30: A first-time user understands the app (clarity batch)

> **Execution:** agent `main-loop` · effort `high` · plan mode **no**
> *Why:* 2026-09-16, Tarik's phone feedback batch, decisions delegated ("soru sorma kendin karar
> ver"). The criterion needs an eye on the phone (emulator), so the main loop implements; a
> separate agent writes the browser tests from the contract below.

> **Lane:** OWNS `app/app.js`, `app/app.css`, `app/scan.js`, `app/transfer.js`, `app/nearby.js`,
> `app/index.html`, `design/screens/README.md` (departures), this file ·
> tests owned by the test agent: `tests/browser/test_clarity.py`, the merged-search change in
> `tests/browser/test_compare.py` · MUST NOT TOUCH `pipeline/`, `design/ds/`, the frame contract
> (block size, frame text) · GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` ·
> DEPENDS ON Task-29

## Why

Tarik on a real phone, 2026-09-16: a newcomer cannot tell what the community screen means; the
"What exists here" chips look like buttons but are not; search and compare are two bars; the
grey licence lines under every screen take a lot of room; the scrollable tabs on Chrome do not
show that they scroll; phones struggle to read the QR frames and cannot focus; no way to find
where you are.

## Contract (the test agent writes against exactly this)

1. **Top bar.** The three screen tabs sit on their own row under the title and all three are
   fully inside a 360 wide viewport (no horizontal scroll needed).
2. **Scrollable tab rows show that they scroll.** Every `.tabs` row carries `data-overflow`:
   `""` when nothing is hidden, containing `right` while content is hidden past the right edge,
   containing `left` while content is hidden past the left edge; updated on scroll and resize.
   At 360 wide on `#/map` the `.filter-tabs` row starts with `right` (when the selected tab is
   the first one); scrolled to the end it contains `left` and not `right`.
3. **One search bar.** The community screen has exactly one `.search-input` and no
   `.compare-search`. Each result is an `li` holding the `.result-row` button (opens the
   community) and, for every community other than the one on screen, a
   `button.result-row__compare` reading `Compare`, which goes to
   `#/compare/<current id>/<result id>`.
4. **Use my location.** `button.locate-button` reading `Use my location` sits with the search.
   It asks the browser for the position once (GPS works with no network), finds the nearest of
   the 96 communities by great-circle distance, opens that community, and `.locate-status` then
   reads `Nearest community: <name>, <n> km away`. Refused or unavailable: `.locate-status`
   reads `Location not available on this phone`. Nothing is stored.
5. **Intro line.** `.intro` at the top of the community screen, one sentence that includes
   `does not measure signal`.
6. **Order, plainest first.** Community screen `.section__title` texts, in order:
   `What the connection allows`, `What the sources say`, `What exists here`, `Who does what`.
7. **Verdict legend.** `.verdict-legend` inside the first section names `Works`, `Degraded`,
   `Fails` and `No data`, each with its meaning in a few words.
8. **What exists here is text, not chips.** `.present-list` holds the facilities; no `.chip`
   inside `main` on the community screen.
9. **Footer.** The attributions live in `details.footer__sources`, closed by default, whose
   `summary` includes `Sources and licences`. `.footer__team` stays visible without opening it.
10. **QR reading.** `window.CrosscheckScan.constraints()` returns getUserMedia constraints with
    `video.facingMode` `environment` and `video.width.ideal` at least 1280.
    `window.CrosscheckScan.cropRect(w, h)` returns `{sx, sy, side, outSide}`: the centred square,
    `side = min(w, h)`, `sx = floor((w - side) / 2)`, `sy = floor((h - side) / 2)`,
    `outSide = min(side, 1024)`. On a live camera: continuous focus where the track supports it,
    tap the picture to focus, a zoom slider where the track supports zoom. The QR shown for
    transfer and nearby fills the content width instead of the fixed 200 size.

## Out of the gate

Real-phone focus and read rate (manual), whether the screen now "reads" (advisory eye review in
the emulator).

## Status

Status: DONE (verify-task, 2026-09-16, main loop; tests written by a separate agent).

- Gate: `GATE GREEN` three runs, the last on the final tree: ruff clean, 146 unit passed,
  build 877,751 bytes, 86 browser passed (13 new in `test_clarity.py`). Trajectory:
  iter 1: 0 fail -> iter 2 (legend moved below the rows, scroll reset): 0 fail -> iter 3 (dead
  compare CSS removed, square camera preview): 0 fail.
- Mutations, each built and run against `test_clarity.py`, files restored byte-exact: overflow
  watcher removed, nearest turned into farthest, jsQR crop limit 1024 -> 720, footer details
  opened, Compare shown on the current community's own row. Each turned exactly its own test red.
- Emulator (Chrome 134, android-36.1, `terra_nt`, driven over CDP): all three screen tabs on
  one row; filter row fades on the right; one search bar with Compare per result; GPS fixed at
  Wadeye gave "Nearest community: Wadeye, 0 km away"; Receive opened the camera at 1080x1856
  with focus modes manual/single-shot/continuous, the hint appeared and was removed on Stop, no
  page errors. The emulator camera has no zoom, so the slider was not seen.
- Added beyond the contract, seen in the emulator: a new screen or community opens at the top
  (the old scroll offset hid the map filters and the search results); the Show and Receive
  boxes carry a title and one sentence; the showing phone holds a screen wake lock.
- Not verified: a real phone reading real transfer frames with the new focus and crop (manual).
