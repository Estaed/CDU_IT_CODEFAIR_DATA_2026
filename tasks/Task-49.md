# Task-49: Tests for map v3 and the degraded clause, written from the contract

**Status: TODO**

> **Execution:** agent `codex` (small tier) · effort `high`
> *Why:* 2026-09-21 late. Whoever writes the code does not write its test. This bee reads
> `tasks/Task-48.md` and the existing tests, never the new code. Codex pool clear.

> **Lane:** OWNS `tests/browser/test_map.py` (rewritten where the contract moved),
> `tests/browser/test_home.py` and any other test that quotes Wadeye's summary sentence or a
> removed map selector, this file · MUST NOT TOUCH `app/`, `pipeline/`, `scripts/`, `data/`,
> `dist/`, `docs/`, `CLAUDE.md` · GATE none for this bee: **do not run `gate.py`,
> `build_app.py`, `run_pipeline.py` or any browser test** (another bee is rebuilding `dist/`
> while you work). Run only `PYTHONUTF8=1 .venv/Scripts/python -m ruff check --no-cache tests`
> and `PYTHONUTF8=1 .venv/Scripts/python -m pytest --collect-only -q tests`. The main loop runs
> the gate. · DEPENDS ON none (contract only)

## Contract

Do not open `app/app.js` or `app/app.css`. Use only Playwright Python APIs that the existing
tests already use (the last wave lost a round to `to_be_closed()` and
`new_page(viewport=…)`, which do not exist): copy `_open_page`, the `PHONE` viewport and the
request blocker from the neighbouring files. A `<details>` is closed when
`el.open === false`. Compute expected counts from the inlined pack in the page
(`JSON.parse(document.getElementById("pack").textContent)`), not from literals, except where
Task-48 gives a literal.

### `tests/browser/test_map.py`

Delete the cluster tests (`test_clusters_at_zoom1_sum_to_96`, `test_zoom_8_shows_no_clusters`,
`test_click_first_cluster_zooms_in_and_splits_it`,
`test_clinic_filter_clusters_and_points_sum_to_filter_count`,
`test_selected_community_at_zoom1_is_visible_and_unclustered`,
`test_cluster_function_is_pure_and_deterministic`). Keep every other test's meaning, adapted:
filter tests now assert 96 points with `96 − len(filter.ids)` dimmed; tests that touch filter
tabs or layer chips first open `details.map-more`; the service-selector and worst-first list
tests run with `lens=service`. Add, one test each unless they share a page naturally:

1. `#/map` with no parameters: lens `fix` selected, `svg.map[data-lens=fix]`, view box
   `0 0 300 480`, 96 `g.map__community`, no `.map__cluster`, no `select`, tier counts
   10 / 20 / 66 matching `pack.priority` ranks, ten `text.map__rank` reading 1 to 10, legend
   items and counts per Task-48 §3.
2. Lens `sources`: `data-sources` on all 96 agrees with the pack by Task-48's precedence
   rule; legend counts equal the computed ones; lens `service`: the `select` is present and
   classes are the verdict classes.
3. The lens control: clicking `Sources` rewrites the hash with `lens=sources` and keeps
   `selected` and `filter`.
4. Regions: six chips, `All NT` first; clicking a region sets `region=<slug>` in the hash,
   `svg[data-region]`, a view box different from the rest view box (wait 500 ms for the
   tween), and dims exactly the points whose pack `region` differs; `Reset view` clears it.
5. One screen: at 360 × 780 on `#/map` the bottom of `div.map-legend` is ≤ 780 with
   `scrollY` 0.
6. Selection card: `Tap a community.` with nothing selected; with `selected=426` the name,
   Wadeye's exact summary sentence from Task-48 §0, `Fix first #<rank> of 96 · <word>`
   computed from the pack, four `.verdict-badge`, and `Open Wadeye` leading to
   `#/community/426`. Clicking a point selects it and keeps the lens.
7. `declutter`: reach it the same way the deleted purity test reached `cluster`. Same input
   twice gives deep-equal output; ids and order preserved; max displacement ≤ 14; at zoom 8
   positions equal the input; at zoom 1 over the real 96 the minimum pairwise distance ≥ 6.
8. `details.map-more` is closed on `#/map`, open on `#/map?filter=clinic-no-terrestrial`.
9. List: 96 `li`; lens `fix` first row is the pack's rank 1; lens `sources` starts with the
   measured ones; dim rows come last when a filter is active.
10. Zero non-`file:` requests and no page error across the lens, region and selection steps.

### Other files

`test_home.py`: Wadeye's exact sentence becomes the Task-48 §0 string, and the all-96 summary
check accepts the new degraded form (assumption present: `…not proven to work here. It
{a1 lower-first}. {a2}.`; absent: Task-45's form), built from the pack the same way.
`docs/demo-script.md` is not yours. Any other test quoting a removed selector
(`map__cluster`, the old map panel) follows the contract; say which in the report.

## Acceptance Criteria

- [ ] `ruff check --no-cache tests` prints `All checks passed!`; `pytest --collect-only`
      collects with no error.
- [ ] No file outside `tests/` and this file was touched; nothing was built or run.

## Report

Tests deleted, added and changed (file, name, one line each); every ambiguity in Task-48 and
the reading you took.
