# Task-16: Sunlight mode

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* a token-set swap and one toggle; criteria are computed-style assertions.

⛔ **Blocking question (Tarik, 2026-09-15):** the high-contrast token set must come from the
claude.ai design project as `design/ds/design/tokens/sunlight.css` (a byte-exact mirror, like
the other three). Part 2 forbids writing a colour under `app/`, and `design/ds/` is never edited
here. Export it there first, re-mirror, then remove this marker. Until then this task is not a
lane.

**Lane**
- OWNS: `app/app.js` (toggle, `data-theme` attribute, remembered in `localStorage`), `app/app.css` (the `[data-theme="sunlight"]` use only), `scripts/build_app.py` (additive: inline `sunlight.css` after `spacing.css`), `tests/browser/test_sunlight.py`, `tests/test_build.py` (additive)
- MUST NOT TOUCH: `pipeline/`, `design/`, other files under `tests/browser/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-15

## Objective

DESIGN.md's known gap closed on the device: a `Sunlight` toggle beside the Offline chip that
swaps the verdict and text colours to a higher-contrast set, remembered across opens. PRD
§4.2 additions, 2026-09-15.

## Execution Guide

- `design/ds/design/tokens/sunlight.css` defines the same custom-property names under
  `[data-theme="sunlight"]`; the build inlines it; `app/app.css` adds nothing but the selector
  if the tokens file does not scope itself.
- Toggle: a `.chip` button `Sunlight` / `Normal` next to the Offline chip; sets
  `document.documentElement.dataset.theme` and `localStorage.crosscheckTheme`. Applied before
  first render so there is no flash.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/browser/test_sunlight.py` (marker `browser`): clicking the toggle changes the computed `color` of a `.verdict-badge--fails` and sets `data-theme="sunlight"`; reloading keeps it; every verdict badge's text against its own background is at or above 4.5:1 in both themes (computed from the two computed colours in the test).
- [ ] `tests/test_build.py` (additive): `dist/index.html` contains the sunlight token block once.
- [ ] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing.
