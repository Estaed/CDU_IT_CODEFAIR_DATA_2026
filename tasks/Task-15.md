# Task-15: Compare two communities

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* a fourth route built from the Task-07 render functions; criteria are DOM assertions.

**Lane**
- OWNS: `app/app.js` (compare route and renderer), `app/app.css` (compare grid only, tokens only), `tests/browser/test_compare.py`
- MUST NOT TOUCH: `pipeline/`, `scripts/`, `design/`, other files under `tests/browser/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-14

## Objective

Two communities side by side for the "which one first" conversation: `#/compare/<id>/<id>`,
two columns, each with the header block, the agreement headline and the four verdict badges;
reached from a "Compare with..." search box on Screen 1. PRD §4.2 additions, 2026-09-15.

## Execution Guide

- Route `#/compare/<a>/<b>`; an unknown id falls back to `#/community/<a>` (or Screen 1 with
  the search open if both are unknown). Reuse `renderHeader` and the badge markup of
  `renderServices`; a two-column grid with a `.compare` class in `app/app.css` using
  `--space-*` tokens and the existing breakpoint; at 360 px the columns stack.
- On Screen 1 a second search box labelled `Compare with...` below the main one; picking a
  result navigates to the compare route. The selected tab stays "Community".
- Each column's name is a `.text-link` back to its community route.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/browser/test_compare.py` (marker `browser`): `#/compare/9/458` renders two `.community-header__name` (Amoonguna, Baniyala), eight `.verdict-badge`, two `.agreement__headline`; typing `Bani` in the compare box on `#/community/9` and picking the result changes the hash to `#/compare/9/458`; `#/compare/9/999999` lands on `#/community/9`.
- [x] Zero non-`file:` requests and no console errors; `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing.

## Status

DONE 2026-09-15 (otopilot, lane gate and main gate green at `8687e87`; 8 browser tests). Bee notes: the screens carry no media query, so the grid wraps with auto-fit/minmax (stacked at 360, two columns at 768); the compare box has its own `.compare-search__input` because two tests expect exactly one `.search-input`; both ids unknown falls back to Wadeye with the search focused. The two-column layout is the one exception to DESIGN.md's single-column rule, recorded in the PRD decision log 2026-09-15. review-visual pending.
