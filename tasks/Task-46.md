# Task-46: Tests for the fifth batch, written from the contract, not from the code

**Status: DONE** — verified 2026-09-21 (main loop: 8 new browser tests and the `headline` unit test, written from the contracts without opening the new code; six first-run failures were test defects (Playwright API misuse, backticks left in an expected string, the old default route) and went back to a test bee; the main loop re-aligned the `headline` fixture after amending Task-44's contract.)

> **Execution:** agent `codex` (`gpt-5.6-luna`) · effort `high`
> *Why:* 2026-09-21. House rule: whoever writes the code does not write its test. This bee
> reads `tasks/Task-44.md` and `tasks/Task-45.md` and the existing tests, never the new code.
> Codex pool clear (11 % / 33 %).

> **Lane:** OWNS `tests/browser/test_home.py` (new), every other file under `tests/` for the
> string and route updates listed below and the new `headline` unit test in
> `tests/test_pack.py`, this file · MUST NOT TOUCH `app/`, `pipeline/`, `scripts/`, `data/`,
> `dist/`, `docs/`, `CLAUDE.md` · GATE none for this bee: **do not run `scripts/gate.py`,
> `build_app.py` or `run_pipeline.py`** (two other bees are writing `data/out/` and `dist/`
> at the same time). Run only `PYTHONUTF8=1 .venv/Scripts/python -m ruff check --no-cache tests`
> and `PYTHONUTF8=1 .venv/Scripts/python -m pytest --collect-only -q tests`. The main loop
> runs the gate after all three tasks land. · DEPENDS ON none (contract only)

## Why

The tests are the measurement of Tasks 44 and 45. Written from the same contract by a
different hand, a misreading shows up as a red test instead of a green lie.

## Contract

Do not open `app/app.js`, `app/index.html`, `app/app.css` or `pipeline/pack.py` to see how
something was done; if the contract is ambiguous, write the test for the literal reading and
say so in the report. Reuse the helpers and fixtures already in `tests/browser/conftest.py`
and the neighbouring files (`_open_page`, the request blocker, the `PHONE` viewport).

### New: `tests/test_pack.py`

`headline()` per Task-44 §1: hand-built community dicts (only the keys the function reads:
`present`, `services`, `agreement`; a clinic is a `present` item named `Health centre`, and
`telehealth_works` counts only communities with one) covering each verdict, both agreement
notes and a `nodata` verdict in a community that has a clinic give the expected four counts; an empty list
gives four zeros; and the built pack (however the file's other tests load it) carries
`headline` equal to `{"communities": 96, "with_clinic": 70, "telehealth_works": 1,
"sources_disagree": 33}`.

### New: `tests/browser/test_home.py` (marker `browser`)

1. Opening `dist/index.html` with no hash lands on `#/`; zero non-`file:` requests; no page
   error.
2. Every selector and exact string of Task-45 §1, including the three figures' text and the
   three `href`s; no `[role=tab][aria-selected=true]` on `#/`.
3. At 360 × 780 the last `.home__actions a` ends inside the viewport without scrolling.
4. Each button goes where it says: the community screen shows Wadeye, the Fix first tab is
   selected on `#/priority`, the map has 96 `.map__community` groups.
5. `a.top-bar__title` returns to `#/` from a community.
6. With `headline` deleted from the inlined pack before load (use the pattern the update or
   transfer tests already use to alter the pack, or `page.add_init_script`/route rewriting of
   the file), the home screen renders without `ul.home__figures` and without a page error.
7. The summary sentence, by evaluating over all 96 communities in one page call: every
   `p.community-summary` text matches one of the four coverage clauses followed by one of the
   four telehealth clauses, the clause chosen agrees with that community's pack `agreement`
   and telehealth `verdict`, and the text contains no backtick. Wadeye's is the exact string
   in Task-45 §2.
8. Community screen: `.services` first child is `.services__question` reading `Can people
   here…`; the four `.service-row__name` texts are the four questions in pack order; each
   opened row's detail ends with `.service-row__path`; every `.verdict-badge` still carries
   its glyph and one of `Works`, `Degraded`, `Fails`, `No data`.
9. `.kind-chip` texts for Wadeye are, in order, `carrier's prediction`, `government list`,
   `licence register`, `community portal`, `drive test`.
10. `details.reliability-line` is closed, its summary starts `How far to trust the coverage
    map here: ` and ends with one of `high`, `medium`, `low`, `none`.
11. Share: `details.transfer-fold` exists, is closed on load, its summary reads `Update
    another phone by camera`, and the `.qr` element is outside it.

### Updates to existing tests (strings and the default route only; assertions keep their meaning)

- `test_smoke.py`, and anywhere else the default landing hash is asserted: `#/` instead of
  `#/community/426`. Tests that open `#/community/426` explicitly stay as they are.
- `test_priority.py`: tab texts `["Community", "Fix first", "Map", "Share"]`, the selected
  tab `Fix first`; the reliability assertion follows item 10; `Copy evidence` expectations do
  not change.
- `test_clarity.py`: `4 of 4 sources agree` becomes `Do the sources agree? Yes, 4 of 4`; any
  assertion on the `Best available path` note looks inside an opened row's detail; the fold
  list gains nothing unless a test enumerates every `details` on the screen, in which case
  add `reliability-line`.
- `test_transfer.py`, `test_update.py`, `test_share.py`, `test_scan.py`: before touching a
  transfer control, open `details.transfer-fold` (set `open` or click its summary).
- `test_report.py` keeps `Telehealth video`, `School video meeting`, `myGov and banking`,
  `Voice and SMS`: the evidence text keeps the formal names. If that list is asserted against
  the visible row labels rather than the evidence text, switch that one assertion to the four
  questions and say so in the report.
- Browser test (h), the actions row inside the first 780 px at 360 wide, stays as it is.

## Acceptance Criteria

- [ ] `ruff check --no-cache tests` prints `All checks passed!`.
- [ ] `pytest --collect-only -q tests` collects with no error.
- [ ] No file outside `tests/` and this file was touched; nothing was built or run.

## Report

Each test added, each existing assertion changed (file, old, new), every place the contract
was ambiguous and which reading you took.
