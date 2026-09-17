# Task-00: Walking skeleton — rules, interim pack, app shell, build, gate green

Status: DONE (verify-task, 2026-09-13; gate GREEN: ruff clean, 32 unit + 1 browser test)

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* every file, function and criterion is named below and in CLAUDE.md Blueprint; the criterion is the gate's exit code. Tarik's standing instruction (2026-09-13): Claude workers, not Codex.

**Lane**
- OWNS: `pipeline/__init__.py`, `pipeline/rules.py`, `pipeline/thresholds.csv`, `pipeline/pack.py`, `app/`, `scripts/build_app.py`, `tests/`
- MUST NOT TOUCH: `spike/` (frozen; read `spike/out/capability_table.csv` and `spike/thresholds.csv` as inputs only), `design/` (read-only), `scripts/gate.py` (owned by Blueprint), `pyproject.toml` (append-only: pytest `pythonpath` if needed)
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

**Build** (`scripts/build_app.py`). `inline(template, css_parts, js, pack_json) -> str` and `main()` reading, in the order Blueprint fixes: `design/ds/design/tokens/colors.css`, `typography.css`, `spacing.css`, `design/ds/design/base.css`, `design/screens/screens.css`, `app/app.css`; then `app/app.js`; then `data/out/data_pack.json` as `<script type="application/json" id="pack">` (escape `</` as `<\/`). Writes `dist/index.html`. `APP_URL` and `TEAM_NUMBER` are read from `constants.md` by a small parser in `pack.py` (the table row for the name), never retyped.

**Tests** (`tests/`): `test_rules.py` with hand-built rows for every spike pattern (unanimous covered 1/1/1/1, unanimous not 0/0/0/0, 1/0/1/1, 0/0/1/0, 1/1/0/1, 0/0/1/1, fixed line Yirrkala, WiFi-only voice) asserting verdict word and reason; `test_pack.py` asserting 96 communities, every `population`, `publisher` line, `service.sources[*]` and `flag` carries a non-empty `source` and ISO `date`, no BushTel free-text field appears, Wadeye's four verdicts are degraded/degraded/works/works and Baniyala's telehealth is fails; `test_build.py` asserting the output contains the pack exactly once, no `http://` or `https://` outside the pack JSON, no `<link` or `<script src`, and size under the limits; `tests/browser/test_smoke.py` marked `browser`: a Playwright fixture opens `dist/index.html` with `page.route("**/*", ...)` aborting and counting every request whose URL does not start with `file:`, asserts the count is 0, `#pack` parses, the top bar has three `[role=tab]`, and the browser is closed at teardown.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root exits 0 and prints `GATE GREEN`.
- [x] `pipeline/rules.py` imports only the standard library: `grep -E "^(import|from) (pandas|geopandas|shapely|numpy)" pipeline/rules.py` prints nothing.
- [x] `tests/test_rules.py` covers the eight patterns listed above; each asserts the verdict word and the reason sentence.
- [x] `data/out/data_pack.json` has `pack_version == 1`, `count == 96`, 96 entries, and `python -c` over it finds no entry lacking `source` and `date` on population, publishers, service sources and flags.
- [x] No BushTel free text in the pack: `grep -c "Mon - Sat\|Daly River Road\|Catholic College" data/out/data_pack.json` prints 0.
- [x] `dist/index.html` contains the string `id="pack"` exactly once, no `<link`, no `<script src`, and `grep -c "http" dist/index.html` counts only occurrences inside the pack JSON (assert by stripping the pack in `test_build.py`).
- [x] Browser smoke: zero non-`file:` requests, three tabs present, pack parses, browser closed at teardown.
- [x] `constants.md` is the only place `DIC005` and the Pages address are typed: `grep -rn "DIC005" app scripts pipeline` prints nothing.

## Contract (main loop, 2026-09-13)

Written by the main loop before delegation so that the implementation bee and the test bee
work from one text. Where this section is more specific than the Execution Guide, this
section wins; where it contradicts the screens, the difference is listed at the end.

**Row.** Every rule takes `row: dict[str, str]`, one `csv.DictReader` row of
`spike/out/capability_table.csv` (all values strings, empty string for missing). Keys used:
`nbn_technology`, `in_fixed_line`, `in_fixed_wireless`, `carriers_4g_count`,
`telstra_4g_2025`, `optus_4g_2025`, `tpg_4g_2025`, `dist_km_telstra_4g`, `dist_km_optus_4g`,
`dist_km_tpg_4g`, `ntg2022_listed`, `ntg2022_macro`, `ntg2022_small`, `ntg2022_proximity`,
`ntg2022_provider`, `ntg2019_backhaul`, `any_within_5km`, `nearest_site_km`,
`nearest_site_carrier`, `nearest_site_name`, `svc_mobile_phone`, `svc_health_centre`,
`svc_school`, `svc_store`, `svc_police`, `svc_library`, `svc_council_centre`,
`svc_employment`, `svc_wifi`, `svc_stand`, `svc_aerodrome`, `road_seasonal_cut`,
`profile_last_updated`, `bushtel_id`, `name`, `aliases`, `community_type`, `nt_region`,
`population_abs2021`, `lat`, `lon`.

**Thresholds.** `rules.load_thresholds(path) -> dict[str, dict]`, key `f"{kind}.{service}.{metric}"`,
value `{"value": float | None, "unit", "direction", "source", "source_url", "checked", "note"}`
(`value` is `None` when the CSV cell is empty). Keys the rules read:
`requirement.telehealth_video.latency`, `capability.nbn_satellite.latency`,
`requirement.school_video_meeting.bandwidth_up`, `capability.nbn_satellite.bandwidth_up_max`,
`requirement.mygov_banking.bandwidth_down`.

**Figures in text.** `rules.fig(value: float, unit: str) -> str` renders `` `5,000 kbps` ``,
`` `664.9 ms` ``, `` `100 ms` ``: thousands separator, no trailing `.0`, one space, wrapped in
backticks. Every number inside a reason, detail or note string goes through it.

**Module constants in `rules.py`:** `RULE_NAME = "best-path rule"` (was `"spike rule"` until 2026-09-13: the name is shown in the app as the path source, and the spike is not a citable source), `RULE_DATE = "2026-09-12"`,
`LICENSED_RADIUS_KM = 5` (PRD decision 2026-09-12; a rule parameter, not a requirement figure).
Verdict words: `works`, `degraded`, `fails`, `nodata` (spike GREEN/AMBER/RED/n-a/no-data).

**Carrier names.** `rules.carriers_4g(row) -> list[str]` from `telstra_4g_2025`,
`optus_4g_2025`, `tpg_4g_2025` == `"1"`, in that order, names `Telstra`, `Optus`, `TPG`.
`rules.join_names(names) -> str`: `"Telstra"`, `"Telstra and Optus"`, `"Telstra, Optus and TPG"`;
empty list renders `"A carrier"`. Verb: `is` for one name (or the empty list), `are` for several.

**`best_path(row) -> str`.** `in_fixed_line == "1"` -> `fixed_line`; else
`in_fixed_wireless == "1"` -> `fixed_wireless`; else `carriers_4g_count` >= 1 and
`any_within_5km == "1"` -> `terrestrial_mobile`; else `satellite`. (PRD section 5.)

**`agreement(publishers) -> tuple[int, int]`.** `(covered, available)`; `available` counts
lines with `says_covered != "not-recorded"`, `covered` counts `says_covered == "covered"`.
Note text (pack, not rules): `"Sources agree"` when `covered in (0, available)`, else
`"Sources disagree"`.

**Service functions.** Each returns
`{"verdict": str, "reason": str, "sources": [{"label": str, "source": str, "date": str}, ...]}`
plus `"assumption": str` only when one applies. `source` and `date` for figures come from the
thresholds entry (`source`, `checked`); the path line is
`{"label": "Path", "source": f"{path word}, {RULE_NAME}", "date": RULE_DATE}` where the path
word is `satellite`, `fixed line`, `fixed wireless` or `terrestrial mobile` (from `best_path`).
Let `sat` be `nbn_technology == "SATELLITE_RESIDUAL"`, `fixed` be `nbn_technology in
("FIXED_LINE", "FIXED_WIRELESS")`, `accc` be `carriers_4g_count` >= 1, `ntg` be
`ntg2022_listed == "1"`, `wifi` be `svc_wifi == "Y"`, `C` = `join_names(carriers_4g(row))`,
`P` = `"Fixed line"` or `"Fixed wireless"` from `nbn_technology`.

`telehealth_video(row, thresholds)`; required = `requirement.telehealth_video.latency`,
measured = `capability.nbn_satellite.latency`:
- `svc_health_centre != "Y"` -> `nodata`, reason `No health centre recorded on BushTel`, sources `[]`.
- `nbn_technology == ""` -> `nodata`, reason `No fixed-access record for this community`, sources `[]`; required `value is None` -> `nodata`, reason `Requirement figure not published`, sources `[]`.
- `fixed` -> `works`, reason `{P} footprint contains the community; latency is under the {fig(required)} requirement on fixed access`, sources: `Required figure` (required), path; assumption `No fixed-access latency figure is sourced yet; fixed access is treated as under {fig(required)} until the ACCC figure is added.`
- `sat and accc` -> `degraded`, reason `Latency {fig(measured)} on satellite vs {fig(required)} required`, sources: `Failing figure` (measured), `Required figure` (required), path; assumption `Could work over {C} 4G if latency is under {fig(required)}. No measurement exists here.`
- `sat and not accc` -> `fails`, reason `Latency {fig(measured)} on satellite vs {fig(required)} required; no carrier 4G polygon`, same three sources, no assumption.

`school_video_meeting(row, thresholds)`; required = `requirement.school_video_meeting.bandwidth_up`,
capacity = `capability.nbn_satellite.bandwidth_up_max`:
- `svc_school != "Y"` -> `nodata`, reason `No school recorded on BushTel`, sources `[]`.
- empty technology or empty requirement -> `nodata` as above.
- `fixed` -> `works`, reason `{P} footprint contains the community; the {fig(required)} upload requirement is cleared on fixed access`, sources: `Required figure` (required), path.
- `sat` -> `degraded`, reason `Upload {fig(capacity)} on satellite vs {fig(required)} required; the latency requirement is not published`, sources: `Capacity figure` (capacity), `Required figure` (required), path; assumption `Microsoft Teams publishes no latency requirement. Treated as Degraded on satellite until one is sourced.`

`mygov_text(row, thresholds)`: empty technology -> `nodata`, reason `No fixed-access record for this community`, sources `[]`; otherwise `works`, reason `Text-first services reach any working link; no published requirement`, sources: `Required figure` from `requirement.mygov_banking.bandwidth_down` (its `source` is `none published`), path. The empty requirement value is by design here and does not produce `nodata`.

`voice_sms(row)`: always applies, takes no thresholds.
- `accc and ntg` -> `works`, reason `{C} 4G {is/are} predicted here and the community is on the 2022 list`.
- `accc and not ntg` -> `works`, reason `{C} 4G {is/are} predicted here; the community is not on the 2022 list`.
- `ntg and not accc` -> `works`, reason `The community is on the 2022 list; no carrier 4G polygon over the community`.
- neither, `wifi` -> `degraded`, reason `No carrier 4G polygon and not on the 2022 list; public WiFi only`.
- neither, no wifi -> `fails`, reason `No carrier 4G polygon and not on the 2022 list; no public WiFi recorded`.
Sources: `{"label": "Predicted", "source": "ACCC MIR 2025", "date": ""}`, `{"label": "Listed", "source": "NT Government 2022 list", "date": ""}`, and for the two WiFi cases also `{"label": "WiFi", "source": "BushTel profile", "date": ""}`; `pack.py` fills empty dates from `SOURCE_DATES` or the profile date.

**Expected verdicts on the spike table** (test oracle, all 96 rows): `telehealth_video`
works 1 / degraded 58 / fails 11 / nodata 26; `school_video_meeting` works 1 / degraded 69 /
nodata 26; `mygov_text` works 96; `voice_sms` works 74 / degraded 5 / fails 17 (counted
from the spike verdict columns 2026-09-13; the first draft of this paragraph was wrong). Wadeye (426):
degraded, degraded, works, works. Baniyala (458): fails, degraded, works, fails. Yirrkala (576):
works x4, path `fixed_line`.

**Eight hand-built test rows** (`mobile_says` order accc/ntg2022/rrl5/bushtel; every row has
`svc_health_centre = svc_school = "Y"` and `nbn_technology = "SATELLITE_RESIDUAL"` unless said;
accc=1 means `carriers_4g_count = "1"` and `telstra_4g_2025 = "1"`; rrl5=1 means
`any_within_5km = "1"`; bushtel=1 means `svc_mobile_phone = "Y"`, bushtel=0 means `""`):
1/1/1/1 (Wadeye shape: telehealth degraded, voice works, path terrestrial_mobile);
0/0/0/0 (telehealth fails, voice fails, path satellite);
1/0/1/1 (voice works with "the community is not on the 2022 list");
0/0/1/0 (Baniyala shape: telehealth fails, voice fails, agreement 1 of 3 with bushtel not-recorded);
1/1/0/1 (path satellite because no licensed site; telehealth degraded);
0/0/1/1 (voice fails, agreement 2 of 4);
Yirrkala fixed line (`in_fixed_line = "1"`, `nbn_technology = "FIXED_LINE"`, 1/1/1/1: telehealth
works with assumption, school works, path fixed_line);
WiFi-only voice (0/0/0/0 with `svc_wifi = "Y"`: voice degraded).
Each test asserts the verdict word and the full reason string.

**Publisher lines** built in `pack.py` (`publisher_lines(row, profile_date) -> list[dict]`), order fixed:
1. `{"publisher": "ACCC Mobile Infrastructure Report 2025", "kind": "predicted"}`; covered when `accc`; detail `{C} 4G outdoor polygon, carrier prediction`; not covered: `No carrier 4G polygon over the community, carrier prediction; nearest {carrier} 4G polygon {fig(km, "km")}` using the smallest of the three `dist_km_*_4g` (skip empty); `source` `ACCC MIR 2025`.
2. `{"publisher": "NT Government 2022 coverage list", "kind": "listed"}`; covered when `ntg`; detail `{Macro cell|Small cell|Proximity}, {Provider}` with the first of `ntg2022_macro`, `ntg2022_small`, `ntg2022_proximity` equal to `"1"` and the provider title-cased per `/`-separated part (`OPTUS/TELSTRA` -> `Optus/Telstra`); not covered: `Not on the list`; `source` `NT Government 2022 list`.
3. `{"publisher": "ACMA licence register", "kind": "licensed"}`; covered when `any_within_5km == "1"`; detail `{nearest_site_carrier} site at {fig(nearest_site_km, "km")}, {site}` where `site` is `nearest_site_name` with a trailing run of upper-case words removed (`74 Perdjert Street WADEYE` -> `74 Perdjert Street`; `19 m Mast, Baniyala Community EAST ARNHEM` -> `19 m Mast, Baniyala Community`); not covered: `No carrier cellular site licensed within {fig(LICENSED_RADIUS_KM, "km")}; nearest {carrier} site at {fig(km, "km")}`; `source` `ACMA RRL`.
4. `{"publisher": "BushTel", "kind": "portal"}`; `svc_mobile_phone` `Y` -> covered, detail `Mobile phone row: yes, links to Telstra's coverage map`; `N` -> `not-covered`, `Mobile phone row: no`; else `not-recorded`, `Mobile phone row not recorded`; `source` `BushTel profile`, `date` = profile date.
`says_covered` values: `covered`, `not-covered`, `not-recorded`. Dates for lines 1-3 from `SOURCE_DATES`.

**`SOURCE_DATES`** in `pack.py`: `ACCC MIR 2025` -> `2025-11-10`; `NT Government 2022 list` ->
`2022-07-04`; `ACMA RRL` -> `2026-09-12`; `ACCC Measuring Broadband Australia release 147/24` ->
`2024-12-05`; `NT Government 2019 coverage list` -> `2019`. Applied to every service source
whose `source` matches (overrides the thresholds `checked` date) and to publisher lines 1-3.

**Community object** (`pack.build_pack(rows, thresholds, app_url, built)`), keys in this order:
`id` (int), `name`, `aliases` (list, comma-split, stripped, empty list when blank), `type`
(`Major`/`Minor`), `region` (`nt_region` title-cased: `Top End`, `East Arnhem`, `Big Rivers`,
`Central Australia`, `Barkly`), `population` `{"value": int, "source": "ABS 2021 SA1 via BushTel",
"date": profile_date}`, `lat`, `lon` (floats), `present` (list of `{"name"}` for each `svc_*`
== `Y`, order and names: Health centre, School, Store, Police, Library, Council service centre,
Employment services, Public WiFi, STAND site, Aerodrome), `publishers`, `agreement`
`{"covered", "available", "note"}`, `path` `{"value", "rule": RULE_NAME, "date": RULE_DATE,
"note"}` with note `satellite (nbn satellite residual)` + `; {C} 4G {is/are} predicted here`
when `accc`; `terrestrial mobile ({C} 4G predicted, licensed site within {fig(5, "km")})`;
`fixed line (nbn fixed-line footprint)`; `fixed wireless (nbn fixed-wireless footprint)`;
`services` (list of four in order `telehealth_video`, `school_video_meeting`, `mygov_text`,
`voice_sms`, each the rule result with `"service"` prepended as the first key), `flags`
(`road_seasonal_cut` value bool from `"1"`, source `BushTel profile`, profile date;
`backhaul_2019` value `ntg2019_backhaul` or `Not recorded`, source `NT Government 2019 coverage
list`, date `2019`), `actions` `[]` (filled by Task-06). Profile date: `profile_last_updated`
`dd/mm/yyyy, hh:mm:ss AM` -> `yyyy-mm-dd`. Communities sorted by `id`.

**Pack header**: `pack_version` 1, `built` (ISO date), `app_url`, `count` 96, `communities`.
`main()` writes `data/out/data_pack.json` with `json.dumps(..., ensure_ascii=False,
separators=(",", ":"))` plus a trailing newline, UTF-8, LF. Run as
`PYTHONUTF8=1 .venv/Scripts/python -m pipeline.pack`. `pack.read_constant(name) -> str` reads the
`constants.md` table row whose first cell is `` `NAME` `` (backticks included) and returns the
second cell stripped. `BUSHTEL_TEXT_ALLOWED = False` guards `wifi_comment`,
`road_access_comment`, `stand_comment`; while False none of the three strings is read.

**ISO date in tests** means `YYYY-MM-DD` or a bare `YYYY` (the 2019 list has no day).

**App shell.** `app/index.html`: `<!doctype html>`, `<html lang="en">`, `<meta charset="utf-8">`,
viewport meta, `<title>Crosscheck</title>`, `<!-- CSS -->` inside `<head>`; body holds the
top bar copied from `design/screens/share.html` (`header.top-bar` > `.top-bar__inner` with
`span.top-bar__title`, `nav.tabs[role=tablist][aria-label=Screens]` holding three
`a.tab[role=tab]` whose `href`s are `#/community/426`, `#/map`, `#/share`, and
`span.offline-chip`), then `<main class="content"></main>`, then `<!-- PACK -->`, then
`<!-- JS -->`. No `<link>`, no `<script src>`, no `http`.
`app/app.js`: reads `JSON.parse(document.getElementById("pack").textContent)`; if
`pack_version !== 1` writes `Unknown data pack` into `main` and stops; `route()` runs on load
and on `hashchange`; when the hash is empty it sets `location.hash` to `#/community/426`; sets
`aria-selected` `"true"` on the tab whose `href` prefix matches the hash (`#/community`, `#/map`,
`#/share`) and `"false"` on the others, then calls `scrollIntoView({inline: "nearest", block:
"nearest"})` on the selected one; offline chip text `Offline` when `navigator.onLine` is false,
`Online` otherwise, updated on `online`/`offline` events; renders `<p>{count} communities</p>`,
`<p>Map</p>`, `<p>Share</p>` per screen into `main`. Uses `textContent`/`createElement`, not
string HTML with data in it. No literal px, no hex colour, no `http`.
`app/app.css` may be empty apart from a one-line comment.

**Build.** `scripts/build_app.py` imports nothing from `pipeline`; `inline(template, css_parts,
js, pack_json)` replaces `<!-- CSS -->` with `<style>` + `"\n".join(css_parts)` + `</style>`,
`<!-- PACK -->` with `<script type="application/json" id="pack">` + `pack_json.replace("</", "<\\/")`
+ `</script>`, `<!-- JS -->` with `<script>` + js + `</script>`; raises `ValueError` naming any
placeholder that is missing from the template. `main()` reads the files Blueprint lists in that
order (`design/ds/design/tokens/colors.css`, `typography.css`, `spacing.css`,
`design/ds/design/base.css`, `design/screens/screens.css`, `app/app.css`; `app/app.js`;
`data/out/data_pack.json`) and writes `dist/index.html` (UTF-8, LF), creating `dist/`.
`ROOT = Path(__file__).resolve().parent.parent`.

**Tests.** `pyproject.toml` carries `pythonpath = [".", "scripts"]` under
`[tool.pytest.ini_options]` (main loop edit, done) so `from pipeline import rules, pack` and
`import build_app` both work. `tests/test_rules.py`, `tests/test_pack.py`, `tests/test_build.py`
are unit tests (no marker). `tests/browser/conftest.py` holds the module-scoped Playwright
fixture: `sync_playwright().start()`, `chromium.launch()`, yield the browser, then
`browser.close()`, `assert not browser.is_connected()`, `playwright.stop()`.
`tests/browser/test_smoke.py` is marked `@pytest.mark.browser`, opens
`(ROOT / "dist/index.html").resolve().as_uri()` after `page.route("**/*", handler)` where the
handler aborts and counts any request whose URL does not start with `file:` and continues the
rest; asserts the count is 0, `#pack` parses with `count == 96`, exactly three `[role=tab]`, and
`main` contains the text `96 communities`. `test_build.py` calls `build_app.main()` (or `inline`
with the real files) and asserts on the produced string: `id="pack"` once, no `<link`, no
`<script src`, and after removing the pack `<script ...>...</script>` block no `http://` or
`https://`; sizes under `1_048_576` and `307_200`.

**Departures from the screens, to raise with Tarik:** (1) Wadeye's section note on
`community.html` says `Best available path: satellite`, but the PRD section 5 rule gives Wadeye
`terrestrial_mobile` (predicted and licensed both say covered); the pack follows the rule.
(2) Baniyala's headline on `map.html` says `1 of 4`; the Execution Guide counts available
lines as those not `not-recorded`, which gives `1 of 3`; the pack follows the Execution Guide.
(3) ACMA site details use one template rather than the hand-shaped `19 m mast` wording.
(4) Service source dates come from the thresholds `checked` column except where `SOURCE_DATES`
overrides; Task-05's provenance registry replaces both.
