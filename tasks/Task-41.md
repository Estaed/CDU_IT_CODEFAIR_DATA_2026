# Task-41: Priority tab, the reliability line, the analyst's sixty seconds; pack version 3

**Status: DONE** — verified 2026-09-17 (main loop: gate green, 200 unit + 89 browser, HTML 961,585 bytes, pack 506,343 bytes, version 3; mutation: reversing the priority list order turns `test_sixty_seconds` red, restored; eye review at 360 × 780 in `reports/shots/`: Priority tab, chip filter with the Why fold, Nauiyu's community screen; one fix from it, human-readable driver labels.)

> **Execution:** agent `claude-worker` (opus) · effort `high`
> *Why:* 2026-09-17. A fourth tab in `app.js`, a version bump that every transfer and store
> test keys on, and the browser test that defines the product for the pitch. Codex is at
> 100 % until 2026-09-19.

> **Lane:** OWNS `app/app.js` (a new `renderPriority` and its chips, the `#/priority` route,
> the tab order, the reliability and priority lines inside `renderCommunity`, the
> `pack_version` check, the evidence header's two new lines), `app/index.html` (the tab),
> `app/app.css` (priority rules, tokens only), `app/store.js` (the accepted version only),
> `pipeline/pack.py` (`PACK_VERSION = 3` only), `tests/browser/test_priority.py` (new),
> `tests/test_pack.py`, `tests/browser/test_map.py`, `tests/browser/test_update.py`,
> `tests/browser/test_transfer.py`, `tests/browser/test_clarity.py`, `tests/browser/test_report.py`
> (the version literal and the fold list only), `design/screens/README.md` (one dated entry
> for the fourth tab), this file · MUST NOT TOUCH `pipeline/prioritise.py`,
> `pipeline/reliability.py`, `pipeline/rules.py`, `transfer.js`, `report.js` beyond the
> evidence lines it is handed, `qr.js`, `scan.js`, `design/ds/`, `CLAUDE.md` · GATE
> `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` · DEPENDS ON Task-40, Task-42

## Why

PRD §2, "the analyst's sixty seconds", is the product's functional definition since
2026-09-17: open the app with no network, see the ranked list, open one community, read why
it ranks there, which publisher says what, whether the claim is reliable, copy the evidence.
Tasks 38 to 40 put every number in the pack; this task is the render, and the browser test
that proves the sixty seconds work is the one test the pitch is checked against.

## Contract

1. **Tab.** `app/index.html` gains `<a class="tab" role="tab" href="#/priority">Priority</a>`
   between Community and Map; `SCREENS` and `screenOf` know it; the selected tab is scrolled
   into view on load as today.
2. **Screen.** `#/priority?intervention=<word>` renders `section.priority`: one line of intro
   from the pack (`<n> communities ranked by <weights count> weighted components; weights and
   sensitivity in the report`, assembled from pack numbers), a chip row of the six
   interventions plus `All` (`chip` component; the active one `aria-pressed`), then
   `ol.priority-list` with one `li.priority-row` per shown community in pack order: the rank,
   the name, the telehealth glyph and word (`renderBadge`), the intervention, and the `why`
   sentence folded under a `details`. A row is a link to `#/community/<id>`. No sorting or
   scoring in the browser: the list is `pack.priority` filtered by the chip.
3. **Community lines.** Under the sources fold, before the reports line: `p.priority-line`
   reading `Priority #<rank> of 96 · <intervention> · <addressee>`, linking to the tab with
   that intervention's chip active; and `p.reliability-line` reading `Map claim reliability:
   <word>` followed, when the word is not `none`, by ` · <drivers[0]>, <drivers[1]>` and a
   source tap like every other line; for `none`, ` · no carrier claims coverage here` or
   ` · model not shipped` from the pack's note. The five publisher lines render through the
   existing publisher code with no change (the fifth arrived in Task-38).
4. **Evidence.** `evidenceHeader` adds the priority line and the reliability line after the
   service lines; `report.js` is untouched.
5. **Version.** `PACK_VERSION = 3`; `app.js` and `store.js` accept 3 only; the transfer and
   update tests that carry the literal move to 3; the downgrade test in `test_map.py` uses
   3 → 2.
6. **Fit.** The community screen's actions row still sits inside the first 780 px at 360 wide
   (Task-34's test): the two new lines live under the fold, not above the row.
7. **Layer rules.** Rule 5 (no literals) over `app.css` and `app.js`; rule 9's greps print
   nothing beyond the display reads named there.

## Tests (`tests/browser/test_priority.py`, marker `browser`)

`test_sixty_seconds` (the analyst's path, one test, in order: open `#/priority`, 96
`.priority-row` in pack rank order; click the `low-latency backhaul` chip, the row count equals
that word's count in the pack; click the first row, the URL is that community's, the screen
shows `Priority #<rank> of 96` with the pack's rank, a `.reliability-line` whose word is in
the four, exactly five publisher lines; `Copy evidence` through the clipboard stub yields a
block containing both lines; the abort-counting fixture saw zero non-`file:` requests);
`test_all_chip_restores_96`; `test_tab_order_and_selected` (four tabs in order, Priority
selected on that route); `test_version_3_only` (a pack with version 2 is refused with the
existing wording). `tests/test_pack.py`: version 3.

## Out of the gate

Whether the list "reads" at 360 px (advisory eye review); the report's Recommendations text.

## Status

Status: IMPLEMENTED (2026-09-17, claude-worker opus) — awaiting verify-task

**What landed.**

1. *Tab* — `app/index.html` gains the Priority tab between Community and Map; `SCREENS` is
   `["#/community", "#/priority", "#/map", "#/share"]`, so `screenOf`, the selected-tab marking
   and the scroll-into-view on load all pick it up with no other change.
2. *Screen* — `renderPriority(word)` in `app/app.js`, after `renderMap`: the intro line
   (`96 communities ranked by 9 weighted components; weights and sensitivity in the report`,
   both figures read from `pack.priority.length` and `pack.priority_components.length`), a
   `.chips.priority-chips` row of `All` plus the eight `pack.priority_interventions` words in
   header order (`chip` component, `aria-pressed` on the active one), then `ol.priority-list`
   with one `li.priority-row` per row of `pack.priority` **in pack order** — `#rank`, the name,
   the telehealth badge through the existing `renderBadge`, the intervention word, and the `why`
   sentence folded under a `details`. The row's `a.priority-row__link` opens
   `#/community/<id>`; the `details` is a sibling of that link, not a child, because a `details`
   inside an `<a>` is not valid markup. No sort and no arithmetic in the browser: the list is
   `pack.priority` filtered on the index each row already carries.
3. *Community lines* — `p.priority-line` (the whole sentence is one link to
   `#/priority?intervention=<word>`, the word URL-encoded) and `p.reliability-line`
   (`Map claim reliability: <word>` in a `.reliability-line__word` span, then the drivers or,
   for `none`, `no carrier claims coverage here`, then the usual `sourceLine`). The drivers are
   printed through `DRIVER_LABEL`, a map beside `SERVICE_LABEL` covering the five feature names
   `pipeline/reliability.py` emits (`site_km`, `depth_km`, `sites_10km`, `sites_20km`,
   `carriers_claiming`), so the line reads `licensed sites within 20 km, carriers claiming
   coverage` rather than the pipeline's own column names (fix-loop item from the 360 px eye
   review, 2026-09-17); an unknown name falls back to the raw name, so a new feature reads raw
   rather than disappearing. Both sit under
   the sources fold and **below** the actions row, beside the reports block, so Task-34's fold
   budget is untouched. The five publisher lines render through the existing publisher code,
   unchanged.
4. *Evidence* — `evidenceHeader` emits the priority line and the reliability line (with the
   `(source, date)` citation) after the four service lines and before the publisher lines.
   Both the screen and the evidence text share one `reliabilityTail`, so the readable driver
   labels reach the copied block by the same route. `report.js` is untouched.
5. *Version* — `PACK_VERSION = 3` in `pipeline/pack.py`, `app.js` accepts 3 only, the pack was
   regenerated. `app/store.js` needed no edit: it already compares an incoming pack against the
   built-in one's `pack_version` rather than a literal, so it accepts 3 only by construction.
6. *Fit* — `test_first_screen_holds_actions_at_360x780` passes unchanged.
7. *Layer rules* — rule 5's grep over `app.css` and `app.js` prints nothing; rule 7's grep
   prints nothing; rule 9's `grep -nE "weight|score" app/app.js` prints exactly one line, the
   intro sentence the contract's own wording requires (`"weighted components; weights and
   sensitivity in the report"`). `score` is never read: the row shows the rank, not the number.

**Numbers.**

- `dist/index.html` **961,585 bytes** (was 953,155; limit 1,048,576; 960,904 before the
  driver labels, +681 for them).
- `data/out/data_pack.json` 506,343 bytes (limit 512,000), unchanged but for the version field.
- Tests: browser **85 → 89** (`tests/browser/test_priority.py`: `test_sixty_seconds`,
  `test_all_chip_restores_96`, `test_tab_order_and_selected`, `test_version_3_only`); unit
  **200 → 200** (version literals only).
- Rows per chip: `All` 96 · low-latency backhaul 12 · mobile site (MBSP nomination) 4 ·
  verify and publish the licensed site 5 · refresh the coverage list 14 · backup power 15 ·
  verify on the ground 3 · measure the link here 31 · monitor 12.

**Gate.** `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` → `GATE GREEN`, exit 0, run
in full twice (before and after the driver labels). Lint `All checks passed!`; 200 unit
passed; build 961,585 bytes; both size checks ok; 89 browser passed.

**Deviations.**

- *Three tests outside the Lane's OWNS list changed, each a direct consequence of the fourth
  tab or the version bump*: `tests/browser/test_smoke.py` and `tests/browser/test_clarity.py`
  (`test_top_bar_tabs_fit_360`) counted three tabs and now count four — the four still fit at
  360 with no horizontal scroll; `tests/browser/test_map.py`'s downgrade test is renamed
  `test_older_version_pack_is_refused` and downgrades 3 → 2.
- *That map test and `test_version_3_only` now check the same thing.* Both are named by the
  contract (item 5 and the Tests section), so both are kept; if `verify-task` prefers one, the
  map copy is the one to drop, since the version now belongs with the Priority tab.
- *The honesty note on source `s52`* (the reliability model's "extrapolation from the nearest
  audited conditions, not a measurement here") is carried as the `title` of the reliability
  line's source span, the same way the header already carries the population's citation.
  Nothing rendered `sources[*].note` before this task, so without it the note would ship in the
  pack and appear nowhere.
- *The contract says "click the first row"*; the test clicks `.priority-row__link`, that row's
  own anchor, because the row also holds the `Why` fold and a click at the row's centre is not
  deterministic between them.
