# Task-34: Community screen, third pass — one screen before scrolling

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* 2026-09-16. The layout is specified to the element; the gate checks the fold. The
> eye review of the result in the emulator is the main loop's, after DONE. Codex is at 100 %.

> **Lane:** OWNS in `app/app.js` the community render functions only (`renderHeader`,
> `renderServices`, `renderServiceRow`, `renderVerdictLegend` (delete), `renderAgreement`,
> `renderPublishers`, `renderPresent`, `renderActions`, `renderStatementButtons`,
> `renderFreshness`, `renderCommunity`, `renderFooter`, and the `VERDICTS` glyph table),
> `app/app.css` (community rules), `tests/browser/test_clarity.py` (items 5, 6, 7, 8 rewritten),
> `tests/browser/test_community.py` (selectors that move), `design/screens/README.md` (one
> departure entry), this file · MUST NOT TOUCH the map functions, `renderCompare*`,
> `renderSearch`, `renderLocate`, `app/transfer.js`, `app/report.js`, `pipeline/`, `design/ds/`
> · GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` · DEPENDS ON Task-32

## Why

At 360 wide the community screen is about seven screens long (measured 2026-09-16 at
360 × 780, full page 5,324 px at 2×). A first-time user asks three things: what works here,
why, and what can I do. The screen should answer the first before any scroll. Tarik: "hem
hemen anlaşılsın hem de kullanıcı için işlevli olsun".

## Contract (the test agent writes against exactly this)

1. **Glyphs.** `VERDICTS` glyphs are `●` Works, `◐` Degraded, `○` Fails, `◌` No data
   (U+25CF, U+25D0, U+25CB, U+25CC). Every `.verdict-badge` and the compare screen use them
   through this one table; nothing else changes on the compare route.
2. **Header.** `.community-header` holds, in order: `h1` name, one `.community-header__meta`
   line `"<type> · <region> · <n> people"` (`n` formatted with a thousands separator, from
   the pack, with its source and date as a `title` attribute on the line, not as visible text).
   Search and `Use my location` stay above it as Task-30 left them.
3. **The four rows.** `.services` is one `card` holding four `button.service-row`, in the
   pack's service order. Each row shows `.service-row__glyph` (the verdict glyph),
   `.service-row__name` (the service name) and `.service-row__badge` (a `.verdict-badge` with
   glyph and word). `aria-expanded` is `false` until tapped. Tapping toggles
   `.service-row__detail` beneath that row (one open at a time is not required) holding the
   reason sentence, the assumption block if any, and the service's source lines exactly as
   Task-07 rendered them. No verdict legend and no intro line exist on the screen
   (`.verdict-legend` and `.intro` are gone; Task-30 items 5 and 7 are reversed by this task).
4. **Sources, folded.** `details.sources-fold` with `summary` reading `"<available> of <total>
   sources agree"` (or `"Sources disagree: <n> of <m> say covered"` when they do not, the
   wording `renderAgreement` produces today), closed by default; open, it holds the publisher
   list `renderPublishers` renders today, unchanged.
5. **Actions.** `.actions` directly under the sources fold: `button.report-button` reading
   `Report here` (a stub in this task: it sets `location.hash` to `#/community/<id>?report`
   and does nothing else; Task-35 owns the behaviour), and `details.share-fold` whose
   `summary` reads `Share` and whose body holds the three existing buttons `Send as SMS`,
   `Copy statement`, `Copy mesh text` and the freshness line, unchanged in behaviour and
   selectors.
6. **Folded sections.** `details.present-fold` (`summary` `What exists here`) holding
   `.present-list` as today; `details.actions-fold` (`summary` `Who to ask`) holding the
   lines `renderActions` renders today under the old title `Who does what`. Both closed by
   default. `.section__title` no longer exists on the community screen.
7. **The fold.** At 360 × 780, on `#/community/<Wadeye id>` freshly loaded, the bottom of
   `.actions`'s bounding box is at most 780 px from the top of the page with `scrollY` 0.
   Also true for the community with the longest name and for one whose four rows include an
   assumption (the rows are closed, so the assumption does not count).
8. **Footer.** `renderFooter` gains the sentence `Crosscheck does not measure signal.` if it
   is not already there (it is, since Task-30: keep exactly one occurrence on the page).
9. **Compare and search unchanged.** `test_compare.py` and the search tests pass untouched
   except for the glyph characters.

## Test changes

`tests/browser/test_clarity.py`: `test_intro_line` and `test_verdict_legend_in_first_section`
are deleted; `test_section_order_plainest_first` becomes `test_folds_in_order` asserting the
`details` summaries read, in order, the agreement line, `Share`, `What exists here`,
`Who to ask`; `test_what_exists_here_is_text` asserts `.present-list` inside
`details.present-fold`. New in the same file: `test_four_rows_with_new_glyphs`
(Wadeye: four `.service-row`, glyphs from the set above, badge words as the pack says),
`test_row_toggle_opens_detail`, `test_first_screen_holds_actions_at_360x780` (item 7, three
communities). `test_community.py::test_service_row_toggle` is updated to the new selectors.

## Departure entry

One bullet under "Where the screens depart from a literal reading" in
`design/screens/README.md`, dated 2026-09-16: the glyph set (`● ◐ ○ ◌` for DESIGN.md's
`● ▲ ■ –`), the folded sections and the two-action row, with PRD §4.2 third batch as the
reason.

## Out of the gate

Whether it reads on a phone (main loop, emulator, advisory); glyph rendering on Android
system fonts (DESIGN.md's known gap; the main loop checks `◐` and `◌` in the emulator and
reports).

## Status

Status: DONE (2026-09-16)

Verified in the worktree (no `data/raw/`, so only the checks that do not need it):
- `ruff check --no-cache .`: `All checks passed!`
- `pytest tests/test_build.py`: 19 passed
- `python scripts/build_app.py`: `dist/index.html` 860,261 bytes (limit 1,048,576); `data_pack.json`
  untouched at 445,751 bytes (limit 512,000) -- this task adds no pack field
- `pytest -m browser`: 83 passed, 0 failed
- `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js`: prints nothing
- Not run: `pytest -m "not browser"` beyond `test_build.py` (the pipeline/source tests need
  `data/raw/`, absent in this worktree; pre-existing, unrelated to this task)

Implementation, against the contract:
1. `VERDICTS` glyphs are `● ◐ ○ ◌`; the map's own shapes are unchanged (Task-33's job).
2. `renderHeader` is now `h1` + one `.community-header__meta` line
   `"<type> · <region> · <n> people"`, population's source/date as its `title`. The old
   `.community-header__population`/`__unit` spans and the header's own `sourceLine` are gone.
3. `.services` is a card (`app.css`, full border, not `.section`'s top hairline) holding four
   `button.service-row` (kept `.service-row__button` as a second class to reuse
   `screens.css`'s existing block/padding rule for that selector rather than duplicating it).
   Each row holds `.service-row__glyph`, `.service-row__name`, `.service-row__badge`
   (`.verdict-badge` plus that class); tapping toggles the sibling `.service-row__detail`
   (reason, assumption if any, sources) via `hidden`. `renderVerdictLegend` and
   `VERDICT_MEANING` are deleted.
4. `details.sources-fold` summary reads `"<n> of <n> sources agree"` or `"Sources disagree: <a>
   of <b> say covered"`, from `community.agreement`; body is `renderPublishers` (its own
   `h2.section__title` dropped, the row list and `renderAgreement` unchanged).
5. `.actions` holds `button.report-button` ("Report here", stub: sets
   `#/community/<id>?report`, nothing else) and `details.share-fold` ("Share"; body is
   `renderStatementButtons` output, unchanged, plus `renderFreshness`, unchanged).
6. `details.present-fold` ("What exists here") and `details.actions-fold` ("Who to ask", the
   old title) both closed by default; `.section__title` no longer appears anywhere in the
   community render functions.
7. Fold budget verified for the Wadeye id (426), the longest name (Hodgson River Station, 600)
   and a third community with an assumption in its rows (id 9): `.actions`'s bottom sits at or
   under 780 px at 360 wide, `scrollY` 0.
8. Footer sentence unchanged (already exactly one occurrence since Task-30; the intro line that
   duplicated it is gone).
9. Compare and search untouched; `test_compare.py` passes with no edits (it never asserted the
   meta line's literal text, only name/badge counts, so `renderHeader`'s new meta line does not
   break it).

Deviations from a literal reading, recorded here and in
`design/screens/README.md`:
- Two functions not in the Lane's named list were added, both strictly within the community
  screen: `renderSourcesFold` and `renderReportButton`/`renderShareFold`/`renderActionsRow`.
  The contract's item 5 names no owning function for the new two-action row, and
  `renderStatementButtons`/`renderFreshness` needed a wrapper to fold behind "Share".
- The "who to ask" list is `ul.actions__list`, not `ul.actions`: the contract names `.actions`
  for both the new two-action row (item 5) and, by continuity with "today's" `renderActions`,
  the old list. Keeping both literally named `.actions` would make
  `page.locator(".actions")` ambiguous for item 7's own fold-budget test, so the list gets its
  own name and its base list-reset moves into `app.css` under that name; `.actions__item`/
  `__who` styling is unaffected since `screens.css` scopes those selectors without a parent
  class.
- Four browser tests outside this task's named files needed their selectors updated because
  content they targeted moved into closed folds: `test_community.py::test_wadeye_renders`
  (agreement headline now needs `details.sources-fold` opened first -- this file is in the
  Lane's OWNS list), and three in `tests/browser/test_statement.py` -- not in the Lane's OWNS
  list, but not fixing them would leave `pytest -m browser` red on a contract-mandated
  restructuring: `test_copy_statement` and `test_copy_mesh_text` now open `details.share-fold`
  before clicking (Playwright requires visibility to click), and `test_freshness_line`'s
  selector moved from `.community-header .source-line` to `.community-header__freshness`
  (unchanged class, new ancestor) and also opens the fold, since `inner_text()` reads rendered
  text and returns empty for a hidden element. Reported here rather than silently expanding the
  Lane.
- `.services .section__note` needed a real CSS change, not just a class rename, to hit the
  780 px budget: the first pass (`padding: var(--space-sm) var(--space-md)` plus a
  border-bottom) put Wadeye's `.actions` bottom at 786.9 px. Cut to `padding-top:
  var(--space-xs)` only (keeping `screens.css`'s own left/right/bottom padding), which was
  enough; no other section needed trimming.

Open questions: none. Task-33 (map) and Task-35 (Report here behaviour) depend on this task's
`VERDICTS` table and `.actions`/`report-button` stub respectively, both now in place.
