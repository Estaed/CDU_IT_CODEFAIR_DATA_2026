# Task-00: Walking skeleton — rules, interim pack, app shell, build, gate green

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* every file, function and criterion is named below and in CLAUDE.md Part 2; the criterion is the gate's exit code. Tarik's standing instruction (2026-09-13): Claude workers, not Codex.

**Lane**
- OWNS: `pipeline/__init__.py`, `pipeline/rules.py`, `pipeline/thresholds.csv`, `pipeline/pack.py`, `app/`, `scripts/build_app.py`, `tests/`
- MUST NOT TOUCH: `spike/` (frozen; read `spike/out/capability_table.csv` and `spike/thresholds.csv` as inputs only), `design/` (read-only), `scripts/gate.py` (owned by Part 2), `pyproject.toml` (append-only: pytest `pythonpath` if needed)
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: none

## Objective

Turn the red gate green with a thin slice through every layer: the verdict rules as pure
functions with tests, a first data pack built from the spike's capability table (interim input,
replaced in Task-05), the single-file app shell, the build that inlines everything into
`dist/index.html`, and the Playwright smoke test that proves the file opens offline. After this
task every later task starts from a green gate and adds one thing.

## Execution Guide

**Rules** (`pipeline/rules.py`, stdlib only, layer rule 1). Promote the rules from the
`spike/merge.py` docstring and `spike/merge.py` lines 95–120 into pure functions over plain dicts:

- `best_path(row) -> "fixed_line" | "fixed_wireless" | "terrestrial_mobile" | "satellite"` per PRD §5: fixed where `in_fixed_line`/`in_fixed_wireless` is truthy; terrestrial mobile where a *predicted* line and a *licensed* line both say covered; satellite otherwise.
- `agreement(publishers) -> (covered, available)` counting `says_covered == "covered"` over lines whose `says_covered != "not-recorded"`.
- `telehealth_video(row, thresholds)`, `school_video_meeting(row, thresholds)`, `mygov_text(row)`, `voice_sms(row)` each returning `{"verdict": "works|degraded|fails|nodata", "reason": str, "sources": [...]}`. Reason sentences are the ones on `design/screens/community.html` and `map.html` with figures in backticks (`Latency \`664.9 ms\` on satellite vs \`100 ms\` required`), so the app can wrap them in `.fig` spans. `nodata` when the service is absent (`svc_health_centre`/`svc_school` not `Y`) or the requirement figure is empty.
- Thresholds come from `pipeline/thresholds.csv` (copy of `spike/thresholds.csv`, same columns); `load_thresholds(path) -> dict` in `rules.py` uses `csv`. Requirement figures are never embedded in code.

**Interim pack** (`pipeline/pack.py`). `build_pack(rows, thresholds, app_url, built) -> dict` and a `main()` that reads `INTERIM_TABLE = ROOT / "spike/out/capability_table.csv"` (module constant, swapped in Task-05) and writes `data/out/data_pack.json`. Pack shape, version 1:

```
{ "pack_version": 1, "built": "YYYY-MM-DD", "app_url": <constants.md APP_URL>, "count": 96,
  "communities": [ { "id", "name", "aliases": [], "type", "region", "population": {"value", "source", "date"},
      "lat", "lon", "present": [ {"name": "Health centre"}, ... ],
      "publishers": [ {"publisher","kind","says_covered","detail","source","date"} ],
      "path": {"value", "rule", "date"},
      "services": [ {"service","verdict","reason","sources":[{"label","source","date"}], "assumption"?: str} ],
      "flags": [ {"name","value","source","date"} ],
      "actions": [ {"who","text"} ] } ] }
```

The four publishers and their kinds, details and dates are exactly those on `design/screens/community.html` (Wadeye) and `map.html` (Baniyala). BushTel free text (`wifi_comment`, `road_access_comment`, `stand_comment`) is **not** copied while PRD OQ1 is open: `present` carries names only and `flags` carries the derived `road_seasonal_cut` boolean. One module constant `BUSHTEL_TEXT_ALLOWED = False` guards the three fields so OQ1's answer is a one-line change. Dates: BushTel lines use the row's `profile_last_updated` converted from `dd/mm/yyyy` to ISO; the others are the constants on the screens (ACCC MIR `2025-11-10`, NTG 2022 `2022-07-04`, ACMA RRL `2026-09-12`, ACCC MBA `2024-12-05`, healthdirect and Teams `2026-09-12`), held in one `SOURCE_DATES` dict in `pack.py` until Task-05's provenance registry replaces it.

**App shell** (`app/index.html`, `app/app.css`, `app/app.js`). `index.html` is the template with three placeholders `<!-- CSS -->`, `<!-- PACK -->`, `<!-- JS -->` and the markup of the top bar from `design/screens/share.html` (title, three tabs, offline chip) plus an empty `<main class="content">`. `app.js` (ES2020, no imports from anywhere) reads the pack from `#pack`, routes on `location.hash` (`#/community/<id>`, `#/map`, `#/share`, default `#/community/426`), marks the selected tab `aria-selected`, calls `scrollIntoView({inline: "nearest"})` on it, sets the offline chip from `navigator.onLine`, and for now renders one line per screen: `"<n> communities"` on community, `"Map"` on map, `"Share"` on share. `app.css` holds only rules the three screen files did not need (for example `main { min-height: ... }` using tokens) and may be empty.

**Build** (`scripts/build_app.py`). `inline(template, css_parts, js, pack_json) -> str` and `main()` reading, in the order Part 2 fixes: `design/ds/design/tokens/colors.css`, `typography.css`, `spacing.css`, `design/ds/design/base.css`, `design/screens/screens.css`, `app/app.css`; then `app/app.js`; then `data/out/data_pack.json` as `<script type="application/json" id="pack">` (escape `</` as `<\/`). Writes `dist/index.html`. `APP_URL` and `TEAM_NUMBER` are read from `constants.md` by a small parser in `pack.py` (the table row for the name), never retyped.

**Tests** (`tests/`): `test_rules.py` with hand-built rows for every spike pattern (unanimous covered 1/1/1/1, unanimous not 0/0/0/0, 1/0/1/1, 0/0/1/0, 1/1/0/1, 0/0/1/1, fixed line Yirrkala, WiFi-only voice) asserting verdict word and reason; `test_pack.py` asserting 96 communities, every `population`, `publisher` line, `service.sources[*]` and `flag` carries a non-empty `source` and ISO `date`, no BushTel free-text field appears, Wadeye's four verdicts are degraded/degraded/works/works and Baniyala's telehealth is fails; `test_build.py` asserting the output contains the pack exactly once, no `http://` or `https://` outside the pack JSON, no `<link` or `<script src`, and size under the limits; `tests/browser/test_smoke.py` marked `browser`: a Playwright fixture opens `dist/index.html` with `page.route("**/*", ...)` aborting and counting every request whose URL does not start with `file:`, asserts the count is 0, `#pack` parses, the top bar has three `[role=tab]`, and the browser is closed at teardown.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root exits 0 and prints `GATE GREEN`.
- [ ] `pipeline/rules.py` imports only the standard library: `grep -E "^(import|from) (pandas|geopandas|shapely|numpy)" pipeline/rules.py` prints nothing.
- [ ] `tests/test_rules.py` covers the eight patterns listed above; each asserts the verdict word and the reason sentence.
- [ ] `data/out/data_pack.json` has `pack_version == 1`, `count == 96`, 96 entries, and `python -c` over it finds no entry lacking `source` and `date` on population, publishers, service sources and flags.
- [ ] No BushTel free text in the pack: `grep -c "Mon - Sat\|Daly River\|Catholic College" data/out/data_pack.json` prints 0.
- [ ] `dist/index.html` contains the string `id="pack"` exactly once, no `<link`, no `<script src`, and `grep -c "http" dist/index.html` counts only occurrences inside the pack JSON (assert by stripping the pack in `test_build.py`).
- [ ] Browser smoke: zero non-`file:` requests, three tabs present, pack parses, browser closed at teardown.
- [ ] `constants.md` is the only place `DIC005` and the Pages address are typed: `grep -rn "DIC005" app scripts pipeline` prints nothing.
