# Task-53: Mobile shell, service cards and map composition

**Status: DONE** — verified 2026-09-22 with the full project gate and a 360 × 780 mobile render.
> **Verified against:** 7d27d88af9 AGENTS.md 6e1ff3e43d CLAUDE.md 35c4eab667 app/app.css 2aded97471 app/app.js 5917191f02 app/index.html 92f3cd43c3 design/screens/README.md 28da424f24 docs/PRD.md 85f997f886 docs/TASKS_INDEX.md 50ed9d7146 tasks/Task-53.md 86fa15a40b tests/browser/conftest.py 362d429ac5 tests/browser/test_audit_fixes.py 3fa6e0efcc tests/browser/test_clarity.py 863807f5dc tests/browser/test_community.py 4633d67923 tests/browser/test_home.py 06e0b429bb tests/browser/test_map.py b76538feb4 tests/browser/test_mobile_ui.py c08ca3650b tests/browser/test_priority.py 1bd3f0655a tests/browser/test_qr.py e8c77c59c1 tests/browser/test_report.py 0d1cef83de tests/browser/test_scan.py 07d94e3f34 tests/browser/test_share.py 9d1f1c923c tests/browser/test_smoke.py f21de3fa35 tests/browser/test_statement.py 56c8600f8a tests/browser/test_transfer.py 83f4408165 tests/browser/test_update.py

> **Execution:** agent `codex` (sol) · effort `high`
> *Why:* The change crosses the app shell, community and map runtime surfaces and needs the
> existing Playwright contracts updated together with a real mobile-width render.

**Lane**
- OWNS: `docs/PRD.md`, `CLAUDE.md`, `AGENTS.md`, `design/screens/README.md`, `app/index.html`, `app/app.js`, `app/app.css`, `tests/browser/`, `tasks/Task-53.md`, `docs/TASKS_INDEX.md`
- MUST NOT TOUCH: `pipeline/`, `data/`, `app/report.js`, `app/transfer.js`, `app/store.js`, `app/qr.js`, `app/scan.js`, `app/vendor/`, `design/ds/`, `design/screens/*.html`
- GATE: from the project root, `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py`
- DEPENDS ON: Task-51, Task-52

## Objective

Make Crosscheck read as a mobile application at compact widths without changing any route,
pack field, verdict, evidence string or offline behaviour. The community answers should scan as
four service cards, the main destinations should be reachable from a persistent bottom
navigation, and the Services map control should stop taking height away from the map.

## Execution Guide

- In `app/index.html`, keep the four existing destination links and route order. Add one small
  decorative inline SVG icon beside each visible label. Remove tab roles and selection state;
  the route owns `aria-current="page"`.
- In `app/app.js`, add a small namespace-correct SVG builder for the four service icons:
  telehealth, school, government/text service, and phone/SMS. Wrap every service button and its
  detail in one card. An expanded card spans the full two-column grid and exposes the existing
  reason, assumption, sources and path unchanged. Set and clear `aria-current` on top-level and
  map-lens links. Keep filter buttons' current tab behaviour because they switch a local view.
- In `app/app.css`, use tokens only. At compact widths (up to `40rem`) leave the title and
  offline state in the sticky top bar and place the destination links in a fixed bottom bar,
  accounting for `env(safe-area-inset-bottom)`. Keep visible icons small while every link retains
  the touch-size minimum. At wider widths retain the current top-bar placement.
- Render the service answers as a two-column grid of bordered cards. A selected/expanded card
  spans both columns. Colour continues to represent verdict only; service icons use normal ink.
- Put `.map-service` inside `.map-frame` above the SVG as an overlay and delete the shorter
  service-frame height rule. The three lens links remain immediately above the frame and use
  navigation semantics. All 96 points, region/filter/layer behaviour, legend, selection card
  and list stay as they are.
- Update browser tests that addressed the two navigation groups as tabs, and add a focused
  mobile UI test. Do not weaken any verdict, map-count, offline-request or first-viewport check.
- Regenerate `AGENTS.md` from `CLAUDE.md` with the repository script.

## Acceptance Criteria

- [x] At 360 × 780 the four top-level links form one fixed bottom navigation, each has a
      decorative SVG icon and visible label, each rendered target is at least 44 CSS pixels,
      and page content is not hidden behind the navigation.
- [x] Exactly one top-level link has `aria-current="page"` on Community, Fix first, Map and
      Share; home has none. Neither the top-level navigation nor the map lens uses tab roles or
      `aria-selected`.
- [x] The community screen renders four `.service-card` elements in two columns. Each contains
      one service icon, the existing question label and the unchanged verdict glyph/word;
      opening one card reveals its detail and makes that card span both columns.
- [x] The Services map selector is a child of `.map-frame`, visually overlays the map, and the
      Services and Fix first frames have the same rendered height at 360 × 780.
- [x] Existing map contracts remain green: 96 points, all three lenses, filter dimming, region
      view, legend counts, selection card, declutter bounds and zero non-`file:` requests.
- [x] `app/` adds no URL, icon font, external image or library; layer-rule greps 5 and 7 remain
      empty; `dist/index.html` and the pack remain under their existing byte caps.
- [x] The task gate and full project gate pass.

## Report

- Mobile captures: `before-community.png`, `before-map-service.png`,
  `after-community.png` and `after-map-service.png` in the task's visual review directory.
- Built HTML: 985,684 bytes, up 3,553 bytes from 982,131; still 62,892 bytes below the cap.
  The pack is unchanged at 506,433 bytes.
- At 360 × 780 the four services render in two rows (two columns); all four bottom-navigation
  targets are 52 CSS pixels high. Services and Fix first map frames both render at 483.59375
  CSS pixels.
- Full gate: ruff green; 212 unit tests passed; build green; both byte caps green; 120 browser
  tests passed; `GATE GREEN`.
- Failure trajectory: the first browser run exposed eight stale tab-role selectors, then the
  focused mobile set passed 11/11 after the contracts were updated. The first gate attempt hit
  25 Windows temporary-directory permission errors (not assertion failures); the same suite
  passed with its temporary directory inside the workspace. Red proof changed one decorative
  icon to `aria-hidden=false`; the navigation test failed 3/4, then passed after restoration.
