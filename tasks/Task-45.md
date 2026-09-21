# Task-45: Home screen, rows as questions, the summary sentence, inside words folded

**Status: DONE** — verified 2026-09-21 (main loop: gate green, 211 unit + 97 browser, HTML 968,648 bytes; layer-rule greps 5 and 7 print nothing; mutation: `is not proven to work here` changed to `is sure to work here` turns `test_community_summary_matches_every_pack_community` red, restored; eye review at 360 x 780 in `reports/shots/2026-09-21-*`: home and Wadeye both fit unscrolled. Not yet done: the emulator check and the ten-second hand-over test with people, which is the batch's real goal.)

> **Execution:** agent `codex` (`gpt-5.6-luna`) · effort `high`
> *Why:* 2026-09-21. Render-only changes in `app.js` against an exact DOM and text contract;
> the criterion is the gate plus Task-46's tests, which another bee writes from this same
> contract. The eye review afterwards is the main loop's. Codex pool clear (11 % / 33 %).

> **Lane:** OWNS `app/app.js`, `app/index.html`, `app/app.css` (tokens only),
> `design/screens/README.md` (one dated entry), this file · MUST NOT TOUCH `tests/` (Task-46
> owns every test change; a test that goes red because a string moved is expected and is
> reported, not fixed), `pipeline/`, `data/`, `app/transfer.js`, `app/report.js`,
> `app/store.js`, `app/qr.js`, `app/scan.js`, `app/vendor/`, `design/ds/`, `CLAUDE.md`,
> `docs/` · GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` · DEPENDS ON Task-44

## Why

PRD §4.2 fifth batch (2026-09-21). Non-technical teammates could not say what the app is
for. Nothing here adds a feature or a verdict: it changes what is read first, and in which
words. Every string below is exact; Task-46's tests assert them character for character.

## Contract

Rules that already bind (CLAUDE.md Blueprint): no `innerHTML` with pack strings (use `h()`),
no colour/size literal in `app.css` or `app.js` (layer rule 5: tokens only), no request
(rule 7), the app computes no verdict (rule 4): mapping a pack verdict id to a phrase is a
label, as `VERDICTS` already is.

### 1. Home, route `#/`

- `DEFAULT_HASH` becomes `"#/"`. An empty hash routes to `#/`. `DEFAULT_ID` stays `426`.
- `#/` renders into `main`:

  ```
  section.home
    h1.home__question      "Coverage maps say there is signal. Can the clinic run a video call?"
    p.home__lead           "Crosscheck puts every public source about 96 remote NT communities side by side: what the connection there allows, where the sources disagree, and what to fix first. It works with no network."
    ul.home__figures       (only when pack.headline exists)
      li.home__figure      "96 communities"
      li.home__figure      "1 of 70 clinics where a video call is known to work"
      li.home__figure      "33 where the sources disagree"
    nav.home__actions
      a.button.button--primary    href="#/community/426"  "Find a community"
      a.button.button--secondary  href="#/priority"       "What to fix first"
      a.button.button--secondary  href="#/map"            "See the map"
    p.home__note           "A diagnosis, not a fix: every figure is from a published source, and the app measures nothing."
  ```

  The numbers come from `pack.headline` (`communities`, `telehealth_works`, `with_clinic`,
  `sources_disagree`), each wrapped in `span.fig` like every other figure; the `96` in the
  lead comes from `pack.headline.communities` when present, else `pack.count`. With no
  `pack.headline` (an older received pack) the `ul` is not rendered and nothing throws.
- On `#/` no tab has `aria-selected="true"`. `screenOf` must not fall back to the community
  tab for `#/`.
- `app/index.html`: `span.top-bar__title` becomes `a.top-bar__title` with `href="#/"`, same
  text, looking the same (no underline, inherited colour; tokens only).
- The home screen fits 360 × 780 with no scrolling: the last button's bottom edge is inside
  the viewport.

### 2. Community screen

- New `p.community-summary`, after the header and before `.services`. Text = coverage clause
  + one space + telehealth clause, built from `community.agreement`, the `telehealth_video`
  service's `verdict` and `reason` (rendered with `figures()` so backticked numbers become
  `span.fig`; `textContent` then has no backticks):
  - coverage clause, `{c}` = `agreement.covered`, `{a}` = `agreement.available`, `{n}` = name:
    - `a === 0`: `No source makes a coverage claim about {n}.`
    - `c === a`: `All {a} sources say {n} has mobile coverage.`
    - `c === 0`: `None of {a} sources says {n} has mobile coverage.`
    - else: `{c} of {a} sources say {n} has mobile coverage; they disagree.`
  - telehealth clause:
    - `works`: `A video call with a doctor should work here.`
    - `degraded`: `A video call with a doctor is not proven to work here: {reason}.`
    - `fails`: `A video call with a doctor will not work here: {reason}.`
    - `nodata`: `No health centre is recorded here, so a doctor's video call is not assessed.`
    (`{reason}` as the pack gives it; add the final full stop only if the reason does not
    end with one.)
  Wadeye (426) therefore reads: `All 4 sources say Wadeye has mobile coverage. A video call
  with a doctor is not proven to work here: Latency 664.9 ms on satellite vs 100 ms required.`
- `.services`: the `Best available path` note leaves the top of the card. The card's first
  child is `div.services__question` with the text `Can people here…` (U+2026). The path note,
  unchanged in content, becomes the last child of **every** service row's detail, class
  `service-row__path` (hidden until the row is opened).
- Row labels (`.service-row__name`) come from a new `SERVICE_QUESTION` map:
  `telehealth_video` → `see a doctor by video`, `school_video_meeting` → `join a school
  lesson by video`, `mygov_text` → `use myGov and banking`, `voice_sms` → `call and text`
  (fall through to `SERVICE_LABEL`, then the id). `SERVICE_LABEL` and `SMS_LABEL` stay and
  keep feeding the SMS, the statement, the evidence text, the map's service selector and
  the legend. Badges, glyphs and verdict words do not change.
- Sources fold summary: `Do the sources agree? Yes, {a} of {a}` when `note` is `Sources
  agree`, else `Do the sources agree? No: {c} of {a} say covered`.
- `.kind-chip` text comes from a `KIND_LABEL` map with fall-through to the raw kind:
  `predicted` → `carrier's prediction`, `listed` → `government list`, `licensed` → `licence
  register`, `portal` → `community portal`, `measured` → `drive test`.
- The reliability line becomes `details.reliability-line` (closed): `summary` = `How far to
  trust the coverage map here: ` + `span.reliability-line__word` with the pack word; the body
  holds what the line's tail says today (drivers or the no-model text) and its source line.
  The evidence text (`Map claim reliability: …`) does not change.
- The actions row still sits inside the first 780 px at 360 wide (browser test (h)).

### 3. Tab label

`app/index.html`: the second tab's text is `Fix first`; its `href` stays `#/priority`. The
Priority screen itself is unchanged.

### 4. Share screen

Everything that sends or receives the pack by camera (the play/receive controls and their
status) moves, unchanged, inside one `details.transfer-fold` whose `summary` is `Update
another phone by camera`. Closed by default; opened by the code whenever a transfer is
running or the route asks for one. The URL QR, `Share this app` and `Save file` stay outside
and first.

### 5. `design/screens/README.md`

One entry dated 2026-09-21 under "Where the screens depart": the home screen has no screen
file (PRD §4.2 fifth batch is its source of truth; it reuses `button`, `fig` and the type
scale), the tab label, the question-form rows.

## Acceptance Criteria

- [ ] Every selector and string in the contract exists exactly as written.
- [ ] Layer-rule greps 4, 5, 7, 8 and 9 in CLAUDE.md still print what they printed before.
- [ ] `ruff`, the unit tests, the build and both size checks pass. Browser tests that fail
      **only** because a string or the default route moved are listed in the report with
      the old and new string; any other browser failure is yours to fix.
- [ ] Nothing in `tests/` was edited.

## Report

Files changed, the list of browser tests red for string/route reasons, `dist/index.html`
bytes, anything in the contract you could not do as written and why.
