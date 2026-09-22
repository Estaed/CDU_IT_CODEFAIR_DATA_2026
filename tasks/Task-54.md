# Task-54: Map and report interaction polish

**Status: DONE** — verified 2026-09-22
> **Verified against:** c560a7fcd0 AGENTS.md 23162b58b8 CLAUDE.md 9182dfb49e app/app.css f3e40429bb app/app.js c7a3644cb4 app/index.html d57fe9c691 app/report.js 6a0fb74825 design/screens/README.md 82ad3f61af docs/PRD.md f18f69619e docs/TASKS_INDEX.md b1b0a4fedb tasks/Task-54.md 86fa15a40b tests/browser/conftest.py 362d429ac5 tests/browser/test_audit_fixes.py 2112fb24da tests/browser/test_clarity.py 863807f5dc tests/browser/test_community.py 4633d67923 tests/browser/test_home.py 06e0b429bb tests/browser/test_map.py b76538feb4 tests/browser/test_mobile_ui.py c08ca3650b tests/browser/test_priority.py 1bd3f0655a tests/browser/test_qr.py 7dadaffee7 tests/browser/test_report.py 0d1cef83de tests/browser/test_scan.py 07d94e3f34 tests/browser/test_share.py 9d1f1c923c tests/browser/test_smoke.py f21de3fa35 tests/browser/test_statement.py dc498f1a20 tests/browser/test_task54.py 56c8600f8a tests/browser/test_transfer.py 83f4408165 tests/browser/test_update.py

> **Execution:** agent `codex` (sol) · effort `high`
> *Why:* This is one tightly coupled mobile interaction pass across the app shell, map runtime,
> report flow and browser contracts. Keeping it in one lane avoids two implementations changing
> the same render and CSS surfaces.

**Lane**
- OWNS: `docs/PRD.md`, `CLAUDE.md`, `AGENTS.md`, `design/screens/README.md`, `app/index.html`, `app/app.js`, `app/app.css`, `app/report.js`, `tests/browser/`, `tasks/Task-54.md`, `docs/TASKS_INDEX.md`
- MUST NOT TOUCH: `pipeline/`, `data/`, `app/transfer.js`, `app/store.js`, `app/qr.js`, `app/scan.js`, `app/vendor/`, `design/ds/`, `design/screens/*.html`
- GATE: from the project root, `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py`
- DEPENDS ON: Task-53

## Objective

Make the map read as a modern, understandable mobile tool and remove ambiguity from Report here,
without changing the app's data, verdicts, report records, offline behaviour or routes. The map
must explain the different effects of a highlight filter and a geographic layer, while the report
flow must distinguish creating evidence on this phone from importing evidence from another.

## Execution Guide

- Add one small decorative, monochrome inline SVG mark to the Crosscheck home link and move the
  wordmark to the next existing title token. Do not load an icon font or image.
- Keep the three map lenses as equal navigation links with their current routes and
  `aria-current="page"`. Restyle them as one compact outlined segmented control with an obvious
  current segment, text-only labels and touch-size targets.
- Give the map frame a bordered, rounded soft surface and clip its contents. Keep the Services
  selector inside the frame but make it compact enough that the whole northern edge is not
  concealed. Add visible zoom-in and zoom-out buttons; expose those operations from the existing
  view controller and keep reset, drag, wheel and region zoom behaviour.
- Inside `Highlight and layers`, label two groups: `Highlight communities` and `Map layers`.
  Explain that highlights reorder matching rows first while the rest stay faded, and that layers
  change the map only. Keep the fold manually openable/closable and auto-open it for an active
  highlight filter.
- Above the community list, render `N highlighted of 96` from the same `isDimmed` predicate used
  for map/list dimming. A highlight filter reorders and dims both points and rows. Toggling any
  geographic layer changes neither list order, list dimming nor the highlighted count.
- Make Report here query-state aware. Closed: `Report here`, `aria-expanded="false"`; open:
  `Close report`, `aria-expanded="true"`. A second activation removes the report query and form.
- Present saved/imported evidence under one `Community reports` group. Name the local summary
  `Saved on this phone` and the importer `Import report lines from another phone`. Keep CR1
  parsing, IndexedDB, Copy, SMS, QR, evidence text, counts and refresh behaviour unchanged.
- Use tokens only for CSS. Add no URL, library, image, tile, request, pack field or route.
- Regenerate `AGENTS.md` from `CLAUDE.md` with the repository script.

## Acceptance Criteria

- [x] The top-left link visibly reads `Crosscheck`, uses a title token larger than Task-53, and
      contains one decorative inline SVG mark with no accessible duplicate name.
- [x] At 360 × 780 the three map lenses are one outlined, equal-width segmented navigation
      control; each target is at least 44 CSS pixels and exactly one has `aria-current="page"`.
- [x] The map is a bounded soft-surface card. Visible zoom-in and zoom-out controls change the
      SVG viewBox; reset restores the base view. Drag, wheel, region zoom and all 96 points remain.
- [x] On the Services lens the selector remains inside and over the same-height map frame but
      does not span the full frame width or consume a separate row.
- [x] `Highlight and layers` exposes separately labelled highlight and map-layer groups, can be
      opened and closed manually, and is open after following a highlight filter link.
- [x] The list heading reports the exact non-dimmed count out of 96. Highlight filters reorder
      matching rows first and dim the rest on both map and list; layer toggles do not alter that
      count, order or dimming.
- [x] Report here opens and closes the form on successive activations, with its label and
      `aria-expanded` matching the query state.
- [x] One `Community reports` group uses the phrases `Saved on this phone` and
      `Import report lines from another phone`; save, import, counts, Copy evidence, SMS and QR
      remain green with the unchanged CR1 line format.
- [x] Existing verdict, map, zero-request and first-viewport contracts remain green. `app/` adds
      no literal CSS colour/size/radius/duration, URL, icon font, external image or dependency;
      both byte caps hold.
- [x] The task gate and full project gate pass.

## Report

- The title now uses `--text-title-md` with a decorative double-check mark. The map lenses are
  an outlined segmented navigation; the map is a clipped soft-surface card with visible zoom
  buttons and a narrower Services selector.
- `Highlight and layers` now identifies `Highlight communities` and `Map layers` as separate
  groups. The list prints the non-dimmed count, keeps highlighted rows first and explicitly says
  the remainder stays faded. A browser contract proves a geographic layer changes none of the
  list ids, dimming states or count.
- Report here now toggles its query and form, label and `aria-expanded`. Saved/imported evidence
  is one visible `Community reports` section; import alone remains folded, so the analyst's
  one-click Copy evidence path remains visible.
- Built HTML: 990,746 bytes, up 5,062 bytes from Task-53's 985,684; still 57,830 bytes below the
  cap. The data pack is unchanged at 506,433 bytes.
- Full gate: ruff green; 212 unit/integration tests passed; build and both size caps green;
  124 browser tests passed; `GATE GREEN`.
- Failure trajectory: initial contract run `4 fail -> 0 fail`; full gate
  `2 browser fail -> 0 fail`. The first full gate caught one stale label assertion and one real
  regression: folding the whole reports group hid Copy evidence. The group was kept visible and
  only its importer remains folded. Red proof was the initial four-contract run against the
  Task-53 build; each failed on the exact missing Task-54 behaviour before passing after the
  implementation.
