# Task-07: Community screen in the app

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* the reference markup exists (`design/screens/community.html`) and every criterion is a Playwright assertion; visual comparison is advisory (`review-visual`, run by the main loop after DONE).

**Lane**
- OWNS: `app/app.js` (community renderer, search), `app/app.css`, `app/index.html`, `tests/browser/test_community.py`
- MUST NOT TOUCH: `pipeline/`, `scripts/`, `design/`, `tests/browser/test_smoke.py` (Task-00)
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-06

## Objective

Screen 1 for all 96 communities, rendered from the pack with the exact markup and class
vocabulary of `design/screens/community.html`: search by name or alias, header, what exists
here, what the sources say, what the connection allows with expandable sources and assumption
notes, who does what, footer.

## Execution Guide

- Render functions in `app/app.js` that produce the same DOM as the reference file, class for
  class: `renderSearch`, `renderHeader`, `renderPresent`, `renderPublishers`, `renderServices`,
  `renderActions`, `renderFooter`. Build DOM with `document.createElement` or a small `h()`
  helper; never `innerHTML` with pack strings (community names and details are data).
- Figures: the pack's reason sentences carry figures in backticks; a `figures(text, size)`
  helper splits on backticks and wraps odd parts in `<span class="fig fig--<size>">`, mirroring
  `design/ds/components/core/Figures.jsx`.
- Search: an `<input class="search-input">` filtering `communities` by case-insensitive prefix
  or substring over `name` and `aliases`; results as `.result-row` buttons (markup per DESIGN.md
  "result-row": name, alias if matched, region, population); selecting sets
  `location.hash = "#/community/<id>"`.
- Service rows: `<button aria-expanded>` toggles the `.service-row__sources` panel; degraded
  rows render the `.assumption-note` from `service.assumption`.
- Footer lines come from the pack's provenance list (Task-05 registry exported into the pack as
  `attributions`), team line from `app_url`/`team` fields, closing statement text fixed.
- No colour, size or radius literal in `app.css` or `app.js` (layer rule 5); no text that is not
  from the pack or from the reference screen.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_community.py` (marker `browser`): opening `dist/index.html#/community/426` renders `h1.community-header__name` = `Wadeye`, four `.service-row` with badges whose text is `▲Degraded`, `▲Degraded`, `●Works`, `●Works` in order, two `.assumption-note`, an `.agreement__headline` containing `4` and `4`, four `.publisher-row`, and a footer with the `DIC005` team line.
- [ ] Typing `Port Keats` into `.search-input` yields exactly one `.result-row` containing `Wadeye`; clicking it changes the hash to `#/community/426`.
- [ ] Clicking the first `.service-row__button` toggles `aria-expanded` and the presence of `.service-row__sources` with three `.source-line`.
- [ ] Every one of the 96 routes `#/community/<id>` renders without a console error (`page.on("console")` collects `error` messages; assert empty) and with at least one `.service-row`.
- [ ] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing.
- [ ] Zero non-`file:` requests on the community route (reuse the Task-00 fixture).
