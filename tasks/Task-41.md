# Task-41: Priority tab, the reliability line, the analyst's sixty seconds; pack version 3

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

Status: TODO
