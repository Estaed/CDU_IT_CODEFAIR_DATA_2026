# CLAUDE.md — Crosscheck — CDU IT Code Fair 2026, Data Innovation Challenge (Python 3.13 pipeline + single-file vanilla JS app; pinned in Blueprint)

> **Competition context lives in this repo, not in your memory.** Read `README.md`
> at the root of this folder before doing anything, and the files under `docs/` that it
> points to: the official brief, the deliverables, the deadlines and the judging criteria
> are all transcribed there from the organiser's website. They are the constraints this
> project is graded against — treat them the way Blueprint treats the architecture.

---
# TarikOS (Second Brain) link — Eko identity

You are Eko, Tarik's assistant and second brain, working in the **CDU IT Code Fair 2026 — Data Innovation Challenge** project.
Not a fresh agent. The brain is `D:\TarikOS` (`$TARIKOS_HOME` if set); read it for anything
outside this project.

Two things bind here and are **never copied into this repo**:
- **Kurallar.md** (house rules, Turkish, bind everywhere) — injected at session start by
  `.claude/hooks/brain-rules.sh` (Claude) and the user-level `~/.codex/hooks.json`
  (Codex). The hook says so loudly if it cannot reach the brain; a session without that
  banner runs without the rules.
- **Principles** (`D:\TarikOS\Principles.md`, engineering principles, English) — arrives from
  the user level: `~/.claude/CLAUDE.md` imports it (Claude), `~/.codex/AGENTS.md` carries a
  generated copy (Codex). `python D:/TarikOS/.brain/scripts/mount_skills.py --check` audits both.

Where a rule here contradicts Kurallar.md, the project rule wins in this directory only.

Skills live in `D:\TarikOS\.claude\skills\` and are junctioned globally; do not copy them
here (`.claude/commands/` only invokes them). The skill sequence (PRD → architecture → tasks
→ verify → otopilot) is `WORKFLOW.md`, read when a phase starts.

Generated project file, regenerate after editing this one:

    python .claude/scripts/sync_agents_md.py .             # AGENTS.md (Codex reads this)
    python .claude/scripts/sync_agents_md.py . --check     # audit only

Codex hooks are user-level. `python D:/TarikOS/.brain/scripts/render_codex_hooks.py --project .`
only removes obsolete project hook entries; it does not generate them.

---

## Blueprint

Written 2026-09-13 with `create-architecture` from `docs/PRD.md`, the 20-community spike
(`reports/2026-09-12-spike-20.md`) and the design files in `design/`. Three calls were put to
Tarik and decided that day: vanilla JS with a Python build (not Preact over the mirror's JSX),
GitHub Pages as the host the QR points at, and `.venv` as the environment name.
Amended 2026-09-16 (PRD §4.2 third batch, Tarik's decisions): nearby chat removed, Report here
added, transfer v3 to be measured before it is built, one-shape verdict glyphs. Every amended
line carries that date.

### Stack

**Python 3.13.5** through **uv 0.12.13**, environment `.venv/` at the project root, verified
installed 2026-09-13. `pyproject.toml` lists the dependencies; `uv.lock` is the resolved graph and
the only place a version is read from. Every command in this file runs **from the project root**
with `PYTHONUTF8=1` (Windows OEM code page mangles UTF-8 otherwise). Node 26.7.0 is on the machine
but is used only by `design/screens/assets/build.mjs`, a design-time tool; nothing in the gate or
the pipeline needs Node.

The app is **vanilla ES2020 JavaScript in one HTML file**, no framework, no library, no bundler.
The pipeline is Python; the build that produces the HTML is Python. One toolchain.

| Package | Version (uv.lock, 2026-09-13) | Why it is here |
|---|---|---|
| geopandas | 1.1.4 | point-in-footprint and distance-to-polygon for NBN, ACCC and ACMA layers |
| shapely | 2.1.2 | geometry predicates; simplifies the NT outline to a byte budget |
| pyogrio | 0.13.0 | geopandas 1.x default IO engine; reads the NBN shapefiles and the ACCC KML |
| pyproj | 3.8.0 | metre distances in GDA2020 MGA zones |
| pandas | 3.0.5 | the capability table; **pandas 3**: copy-on-write is the default, so chained assignment never writes back; do not carry pandas-2 idioms over from the spike |
| openpyxl | 3.1.5 | NT Government xlsx in; capability table xlsx out |
| lxml | 6.1.3 | ACCC KML parsing, kept from the spike |
| requests | 2.34.2 | `pipeline/fetch/` only; nothing else in the repo may import it |
| matplotlib | 3.11.2 | the two static PNG maps for the report's Findings |
| pillow | 12.3.0 (through matplotlib) | the three home-screen icons drawn at build (Task-28); not a direct dependency, read from `uv.lock` |
| qrcode | 8.2 | build-time QR; compared module for module with the mirror's `qr.js` on 2026-09-12, 0 differences, so the build needs no Node |
| pytest | 9.1.1 (dev) | unit and browser tests |
| ruff | 0.16.7 (dev) | lint; config in `pyproject.toml`, excludes `spike/`, `design/` and `reports/` (throwaway spike code, 2026-09-15) |
| playwright | 1.62.0 (dev) | headless Chromium opens `dist/index.html` from `file://`; verified 2026-09-13. Browser build in `~/AppData/Local/ms-playwright/` |
| scikit-learn | pinned by `uv add` in Task-39, version read from `uv.lock` (2026-09-17) | the map-claim reliability model, trained once in `pipeline/reliability.py` on the Audit's measured tiles; imported nowhere else (layer rule 9); its output enters the pack as a word, a probability and two feature names |

Rejected, one line each:
- **Preact or React with the mirror's `.jsx` components**: a second toolchain, and the components carry literal sizes the screens deliberately do not copy.
- **esbuild/Vite for a vanilla app**: minification saves nothing that matters at ~30 KB of JS.
- **Flutter, Streamlit, any server**: a tool that needs a connection to explain where there is none (notes.md, 2026-09-12).
- **pydeck/folium/Leaflet**: tile and CDN requests at runtime; the map is inline SVG.
- **duckdb**: in the spike venv, imported nowhere; dropped by `uv sync`.
- **Decimen Optical Transfer, qwbp, txqr as dependencies** (2026-09-15): AGPL-3.0 from v0.4.0 (Decimen) or code we do not need; the QR encoder, the frame loop and the SDP-in-QR handshake are our own, ~500 lines, no licence to carry.
- **STUN or TURN servers** for nearby chat: a server, and the internet. Moot since 2026-09-16: nearby chat itself is removed (PRD §4.2 third batch); no file under `app/` may construct an `RTCPeerConnection`.
- **cimbar, Decimen** as the transfer method (2026-09-16): WASM with an unverified licence, and AGPL. The colour-multiplexed frame (candidate C) is our own design, measured in Task-31.
- **ESP32 captive portal, Meshtastic nodes** (2026-09-15): cost money; report recommendations only.
- **zxing-wasm, qr-scanner** as the iPhone QR reader (2026-09-15): zxing-wasm is a 3.7 MB package whose `.wasm` would have to be inlined; qr-scanner needs a separate worker file and was last released in 2022. jsQR is plain JavaScript and inlines as one script.
- **Web fonts, icon fonts, images**: DESIGN.md forbids them and the byte budget agrees. One exception since 2026-09-15 (Task-28): the home-screen icons `icon-192.png`, `icon-512.png` and `apple-touch-icon.png`, drawn at build time from the colour tokens with Pillow and served next to `dist/index.html` like `sw.js`; `dist/index.html` never loads them.
- **`venv` as the environment name**: uv and VS Code default to `.venv`; decided 2026-09-13.

### Architecture

**Where the code lives** (folders not yet present are created by the task that first needs them):

```
pipeline/            Python package, offline after data/raw/ is frozen
  fetch/             one script per source; the ONLY place the network is touched; writes data/raw/<source>_<date>.*
  sources/           one module per publisher or layer (nbn, accc, rrl, ntg, bushtel; since 2026-09-17 audit: the National
                     Audit non-alignment tiles, kind "measured"); each emits a 96-row frame keyed on bushtel_id
  rules.py           best-available-path rule and the service verdict rules: pure functions over plain dicts
  thresholds.csv     requirement figures with source URL and date (promoted from spike/thresholds.csv)
  reliability.py     2026-09-17 (Task-39): the map-claim reliability model; the ONLY module that imports scikit-learn;
                     trains on the Audit tiles and the audited roads, validates on a held-out SA3-region split, writes
                     data/out/reliability.csv (one row per community: word, probability, two features) and
                     data/out/tables/reliability_validation.csv; refuses to write the word column when AUC < 0.65
  prioritise.py      2026-09-17 (Task-40): the priority score, rank, intervention and addressee per community, plain
                     functions over dicts like rules.py; weights read from priority_weights.csv, never embedded;
                     writes data/out/priority.csv and the sensitivity table
  priority_weights.csv  2026-09-17: one row per score component (name, weight, source column, note); the one place a weight lives
  merge.py           joins the source frames into the capability table
  pack.py            capability table -> data/out/data_pack.json, the subset the app shows, every citation kept
  figures.py         the two PNG maps and the report tables
  provenance.py      data/out/PROVENANCE.md from the source registry (URL, fetch date, size, licence, attribution line)
  outline.py         NT boundary (ABS ASGS 2021 STE, CC BY 4.0) simplified to one SVG path for the pack
  layers.py          map second pass (2026-09-15): towns, highways, SA3 regions, ACCC coverage per carrier,
                     simplified in degrees and projected with outline.project, emitted as SVG path strings
                     under the pack's `layers` key; every layer registered in provenance.py
data/raw/            frozen snapshots; files over 10 MB are gitignored and re-fetched by pipeline/fetch/
data/out/            capability_table.csv/.xlsx, data_pack.json, PROVENANCE.md, figures/
app/                 index.html (template), app.js (render only), app.css (app-only rules, tokens only), sw.js, manifest.webmanifest
                     since 2026-09-15 also: qr.js (QR encoder, byte mode, own code), transfer.js (frame loop and
                     camera receive), layers.css (map-layer custom properties only), store.js (received pack
                     and, since 2026-09-16, the phone's own reports in IndexedDB), scan.js (one QR reader
                     adapter, Task-25), vendor/jsQR.js + vendor/jsQR.LICENSE (the one library exception, OQ15)
                     since 2026-09-16: report.js (Report here: the record, its 200-byte line, import by paste,
                     the evidence text; Task-35). nearby.js was removed the same day (Task-32).
reports/spike-qr/    the transfer v3 experiment pages (Task-31): built by their own build.py into dist/spike/,
                     published by pages.yml, imported by nothing, deleted once Task-36 lands
scripts/             gate.py, build_app.py, run_pipeline.py
tests/               unit tests; tests/browser/ holds the Playwright smoke test (marker "browser")
dist/                build output, gitignored; dist/index.html is the deliverable
design/              brief.md, ds/ (read-only mirror of the design project), screens/ (the three reference screens)
spike/               frozen 2026-09-12 throwaway; imported by nothing; deleted once the pipeline reproduces spike/out/capability_table.csv
docs/ reports/       PRD, competition brief, dated research and spike reports
```

**The layer rule**, each line checkable:
1. `pipeline/rules.py` imports only the standard library. `grep -E "^(import|from) (pandas|geopandas|shapely|numpy)" pipeline/rules.py` prints nothing. Rules take and return plain dicts so they are unit-tested with hand-built rows.
2. Modules in `pipeline/sources/` never import each other; they meet only in `merge.py` on `bushtel_id`. `grep -E "from pipeline.sources" pipeline/sources/*.py` prints nothing.
3. `requests` appears only under `pipeline/fetch/`. `grep -rl "import requests" pipeline app scripts tests | grep -v pipeline/fetch/` prints nothing.
4. `app/` computes no verdict. The pack carries the verdict word, the reason sentence and the sources per service; `thresholds.csv` is not in the pack and no file under `app/` compares a figure against a requirement. The app renders, routes and shares; since 2026-09-15 it also encodes QR, plays and reads frames and gzips its own bytes; since 2026-09-16 it records what a person says about their own phone (Report here) and counts such records, none of which is a verdict. A report never changes a badge: `grep -n "verdict" app/report.js` prints nothing.
5. Colours, sizes, radii and fonts exist only as the custom properties in `design/ds/design/tokens/*.css`, plus the map-layer colours in `app/layers.css` (custom property definitions only, nothing else in that file; decision 2026-09-15, DESIGN.md's colour rule broken on purpose for carrier layers). `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/qr.js app/transfer.js app/nearby.js` prints nothing; SVG geometry inside the pack is data, not CSS.
6. Nothing in the repo imports from `spike/` or `design/ds/components/`.
7. The app makes no request while running, checked in the code, not only in the browser test: `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|RTCPeerConnection|stun:|turn:|https?://" app/app.js app/qr.js app/scan.js app/store.js app/transfer.js app/report.js app/vendor/jsQR.js` prints nothing (`sw.js` is the host-only exception and is never needed for first render). Since 2026-09-16 `report.js` may read `navigator.connection` (a property, not a request) and `navigator.geolocation` once on a tap. (A one-tap `fetch(` exception for a lite copy existed for a few hours on 2026-09-16, Task-36, and was withdrawn the same evening by Task-37: the camera never was a first-install path, so nothing needs completing. The grep prints nothing again.)
8. The camera is touched only in `transfer.js` (receive): `grep -l getUserMedia app/*.js` prints exactly that file (2026-09-16, nearby.js removed). Every stream is stopped on route change. The microphone is never touched: `grep -n "audio: true" app/*.js` prints nothing.
9. (2026-09-17) The one model lives in one file: `grep -rlE "^(import|from) sklearn" pipeline scripts tests app | grep -v pipeline/reliability.py` prints nothing, and `grep -n "sklearn\|reliability" app/*.js` prints nothing except the render of the pack's `claim_reliability` word in `app.js`. The priority score is computed in `pipeline/prioritise.py` only: `grep -nE "weight|score" app/app.js` prints nothing beyond reading `priority.score` from the pack for display. `pipeline/prioritise.py` imports only the standard library, like `rules.py`.

**Pushed down, out of the browser.** Everything deterministic runs once in the pipeline or the build, never on the phone: the path rule and all verdicts, the agreement count, the reason sentences, the "who does what" lines, the projected SVG coordinates of the 96 points, the simplified NT outline, the URL QR modules, the two PNG maps, and since 2026-09-15 the simplified map layers (towns, highways, SA3 regions, ACCC coverage per carrier). The browser does five things: pick a community, show its pack row, share the file, play or receive the app as QR frames, and (since 2026-09-16, replacing nearby chat) keep and count the phone's own reports. Since 2026-09-16 (Task-30, decided by Eko on Tarik's delegation) picking a community may also use the phone's own GPS: `navigator.geolocation` once, nearest of the 96 by great-circle distance, nothing stored or sent; and `scan.js` tunes the stream the two camera files open (resolution, continuous and tap focus, zoom) without opening one itself. What stays in the browser is only what depends on runtime bytes or the other phone: encoding this build's own bytes as QR frames (gzip via `CompressionStream`, encoder in `qr.js`), the mesh-size, SMS and (2026-09-16) evidence texts assembled from pack strings and the phone's reports, since 2026-09-15 grouping the visible map points into zoom clusters (it depends on the live zoom; layout, not a verdict; Task-29; replaced 2026-09-21 by Task-48's `declutter(points, zoom)`, the same kind of pure layout function: all 96 points are always drawn, nudged apart at rest and back in their true place by zoom 8, and choosing a point's size from `priority.rank` or its class from a publisher line is a render, not a score), and since 2026-09-16 sorting the shown communities worst first under the map (a sort over pack verdicts, not a verdict). Since 2026-09-21 (PRD §4.2 fifth batch) also the one summary sentence per community, assembled from the pack's agreement counts, the telehealth verdict id and its reason string the way the SMS text is (a verdict id mapped to a phrase is a label, as the badge word is; 96 sentences would not fit under the pack cap); the home screen's three counts are pushed down into `pack.headline`. Since 2026-09-17 (fourth batch) the pack also carries, per community, the map-claim reliability word and the priority rank, score, intervention and addressee, all computed in the pipeline; the Priority tab is a render of `pack.priority` in pack order and a chip filter over its `intervention` field, nothing more. The mesh text and the compare render are gone the same day (Task-42). Nothing runs a model at runtime: the one model (`pipeline/reliability.py`) trains once in the pipeline and ships as numbers (PRD §3, §4.2 fourth batch).

**The seams**, only those a PRD phase names, with what sits behind each today:
- **Publisher line** `{publisher, kind, says_covered, detail, source, date}` in `pipeline/sources/*` and the pack. Today: `accc` (predicted), `ntg2022` (listed), `rrl` (licensed, 5 km), `bushtel` (portal), and since 2026-09-17 `audit` (measured: `not-covered` when a non-alignment tile lies within 5 km, `not-recorded` when no audited road does; Task-38). D1's modelled publisher is a new module emitting `kind: "modelled"`; the app renders any kind it is given. `mobile_says` keeps its four keys (the action table, the filters, the figures and the disagreement patterns all match on that string); the audit line comes from two new table columns, `audit5` (`1`, `0` or empty for not recorded) and `audit_nearest_km`, and `pack.publisher_lines` appends it as the fifth line. The agreement count's `available` still counts only lines that make a claim.
- **Reliability line** (2026-09-17, Task-39) `claim_reliability: {word: high|medium|low|none, p_wrong, drivers: [name, name], src}` per community in the pack; `none` with `p_wrong: null` when the model did not ship (kill criterion) or the community has no carrier claim to test. The app prints one line from it and never recomputes it.
- **Priority row** (2026-09-17, Task-40; encoding amended the same evening for the pack cap: 512,119 bytes as first written, 119 over) `{id, rank, score, c: [contribution, ...], i, why}` in the pack's `priority` list, 96 rows, rank order, with two headers written once: `priority_components: [{name, weight}]` (the `c` array aligns to it) and `priority_interventions: [{word, addressee}]` (`i` indexes it; the words spelled out per row put the pack 369 bytes over the cap, so the row carries the index and the community's pointer is `priority: {rank, i}`; the addressee is a function of the intervention, so it lives here, not per row). `intervention` is one of the **eight** words in `pipeline/prioritise.py`'s table (six on 2026-09-17 morning; `verify on the ground` and `measure the link here` added the same evening, Tarik's decision, because 46 of 96 fell through to `monitor`, the measured publisher's three communities among them); a new intervention is a new rule row there, a header entry and a new chip in the app, no other change. Weights live only in `pipeline/priority_weights.csv`; a component whose source is licence-gated (cyclone, ADII) carries weight 0 and `note: "awaiting OQn"` until it lands.
- **Priority order, amended 2026-09-27 (Tarik):** the pack priority row adds `g: service|check|monitor` without changing the weights or pack version. `pipeline/prioritise.py` assigns `service` when telehealth or voice/SMS has the source-based `fails` verdict, `check` for any remaining intervention other than `monitor`, and `monitor` otherwise. Sort by that group, then the approved score and the existing tie breakers. The app prints all 96 in those three sections and never computes a group. A service verdict is inferred from published inputs, not a field measurement; the section says so. The report and map use the same global ranks.
- The Priority screen's intervention chips sit inside a collapsed `Filter by action` fold when no chip is selected (2026-09-27 Android emulator eye check); an active chip opens the fold. This keeps the first source-based service gap above the phone's fold without changing the route or filter semantics.
- **Flag** `{name, value, source, date}` per community. Today: `road_seasonal_cut` (BushTel), `backhaul_2019` (NTG). OQ2 audit tiles and OQ3 cyclone count are new flag emitters, no app change.
- **Requirement row** in `pipeline/thresholds.csv`. OQ8 and OQ11 add rows; `rules.py` reads the table and never embeds a figure.
- **Pack header** `{pack_version, built, app_url, communities: 96}`; the app refuses a pack whose `pack_version` it does not know. Version 1 until the map's second pass is drawn: Task-20 adds the `layers` key additively (the app ignores it), Task-21 draws it, bumps the version to **2** and makes the app accept 2 only. 2026-09-17: Tasks 38 to 40 add `audit` lines, `claim_reliability` and `priority` additively under version 2 (the app ignores what it does not render); Task-41 renders them, bumps to **3** and makes the app accept 3 only. Task-42 removes the header's `changes` block. 2026-09-21 (Task-44): `headline: {communities, with_clinic, telehealth_works, sources_disagree}` is added after `legend`, additively under version 3; the home screen prints it and renders without it.
- **Map layer** `{id, label, kind: "line" | "area" | "point", src, paths: [...]}` in the pack's `layers` list, one per town set, highway, region set and carrier; the app draws any layer it is given with the colour token named by its `id` in `app/layers.css`, and toggles `area` layers. New layers are new pipeline emitters, no app change.
- **Report line** (2026-09-16, Task-35), the one record the app writes itself: `CR1|<bushtel_id>|<yyyymmddhhmm UTC>|<status: works|slow|none>|<carrier: telstra|optus|tpg|other|->|<effectiveType or ->|<rtt ms or ->|<downlink Mbps or ->|<lat>,<lon> or -`, at most 200 bytes UTF-8, and nothing else. The pack does not carry reports and `pack_version` does not move for them; they live in the phone's IndexedDB (`store.js`) and travel as this line. A later version is a new prefix (`CR2`), and a reader ignores prefixes it does not know.
No seam exists for D3 (more communities) or D5 (national): they are v1.1 and get their seams when they are planned (D2 became Report here on 2026-09-16, the Report line above).

**Entry points**
- `PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py` from the root: reads `data/raw/`, writes `data/out/`. No network; `pipeline/fetch/*.py` are run by an operator or the scheduled source-refresh automation, and their results are committed or logged in `PROVENANCE.md`.
- Since 2026-09-27 (Tarik's decision), the Codex project automation **Crosscheck source refresh** checks official publisher metadata weekly. When a source with usable terms and a compatible existing fetch module has changed, it may run that fetch module, regenerate the pack, run the full gate and publish a changed, validated result to `main`; a failed fetch, changed schema, dirty checkout or red gate leaves Pages unchanged and reports the blocker. This is an external operator run of `pipeline/fetch/`, never a request by the app or `run_pipeline.py`. BushTel OQ1, Audit OQ2 and a new ACCC/NBN year require separate review before ingestion.
- `PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py` from the root: inlines, in this order, `design/ds/design/tokens/colors.css`, `typography.css`, `spacing.css`, `design/ds/design/base.css`, `design/screens/screens.css`, `app/app.css`, `app/layers.css`, then `app/vendor/jsQR.js`, `app/qr.js`, `app/scan.js`, `app/transfer.js`, `app/store.js`, `app/report.js`, `app/app.js` (in that order since 2026-09-16, each a plain script; the helpers expose one object each on `window` and `app.js` is the only file that touches the DOM at load), then `data/out/data_pack.json` as `<script type="application/json" id="pack">`, into `app/index.html` → `dist/index.html`. Also writes the host-only files to `dist/`: `sw.js` (cache named after the build hash), `manifest.webmanifest`, and the three home-screen icons drawn from the tokens (Task-28); the HTML links the manifest and icons but works without them.
- The app routes by hash: since 2026-09-21 `#/` is the home screen and the default (one sentence, the three `pack.headline` figures, three buttons; no tab is selected there and the top-bar title links to it; Task-45), then `#/community/<bushtel_id>`, `#/map?filter=<id>` (since 2026-09-21, Task-48, PRD §4.2 sixth batch, also `lens=<fix|service|sources>` with `fix` the default, and `region=<slug>`, which tweens the view box to that region and dims the rest; a filter dims instead of removing), `#/share`, and since 2026-09-17 `#/priority?intervention=<word>` as the fourth tab (Task-41); `#/compare/<id>/<id>` existed from 2026-09-15 to 2026-09-17 (Task-42) and `#/nearby` from 2026-09-15 to 2026-09-16. Since 2026-09-17 the Priority tab is the first thing the analyst sees after the default community: the tab order is Community, Priority, Map, Share, and the "analyst's sixty seconds" (PRD §2) is the browser test (i) below. The three screens are the reference: `design/screens/community.html`, `map.html`, `share.html`. The transfer controls on the share screen, the map's second and third passes, the community screen's third pass and Report here have no screen file: PRD §4.2 (second and third batches) is their source of truth and they reuse the existing components (`card`, `button`, `chip`, `list`, `details`) with no new CSS beyond `app/app.css`. Since 2026-09-16 the four verdict glyphs are `●` Works, `◐` Degraded, `○` Fails, `◌` No data, in badges, legends and as map point geometry (filled disc, half disc, ring, dotted ring); DESIGN.md's `● ▲ ■ –` are departed from in `design/screens/README.md`. On load the selected tab is scrolled into view (decision 2026-09-13, PRD §11).
- Since 2026-09-22 (Task-53, PRD §4.2 seventh batch), compact widths use a persistent bottom navigation for the same four routes, with inline SVG icons plus visible labels and `aria-current="page"`; wider widths keep those links in the top bar. The community's four service answers are individual two-column cards whose static icons identify the service, never the verdict. The map lens links also use `aria-current`; the Services selector sits over the map and no longer shortens its frame. These are deliberate departures from the original icon-free, top-tab reference screens and are recorded in `design/screens/README.md`.
- Since 2026-09-22 (Task-54, PRD §4.2 eighth batch), the map lens links form one compact outlined segmented control; the map has a bounded soft surface and visible zoom controls; its fold separates highlight filters from map-only geographic layers; and the community list states how many rows are highlighted while keeping all 96. The Crosscheck home link has a decorative inline check mark and a larger title token. These presentation changes add no route, pack field, tile, request or runtime dependency.
- Transfer by camera, the contract both ends share (**v4, Task-37, 2026-09-16 evening**; `CX`, `CY` and `CZ` are gone and are ignored). **What travels is the data pack, not the app**: the receiving phone already has Crosscheck (its camera app cannot reassemble frames), so the camera is the pairing-free, cross-platform (Android to iPhone) update channel for a phone with no network, and the app itself is installed once from `APP_URL` or by a shared file. Payload = gzip of the inlined pack JSON with `layers` replaced by `[]` (about 18 KB, K about 25 on 2026-09-16; the map layers are static geography and the receiver keeps its own). Blocks of 750 bytes; frame text = `CP` + index (4 hex) + `K` (4 hex) + payload length (6 hex) + base64 of one block (1,000 characters), QR byte mode, level L; repair blocks by xorshift32 from the index with a robust-soliton degree (c 0.1, delta 0.5); one source pass, then repair only. Sender: frame changes inside `requestAnimationFrame`, held 16 refreshes (3.75 frames a second; measured on the S24 2026-09-16, 141 codes decoded of 189 frames read). Receiver: the main-thread loop, one `CrosscheckScan.reader().detect(video)` per 100 ms, peeling decoder, `known of K`, vibration, then `CrosscheckStore.save(text)` which validates `pack_version` and the community count and, when the incoming `layers` is empty, carries the stored or inline layers over; `Use received data now` reloads. A pack the copy cannot accept (other `pack_version`) says `This copy is too old for that data; open the address once with the internet`. Browser tests: round trip byte-exact against the built pack, layers carried over, `CZ`/`CY` ignored, and the loss budgets as a **distribution, not one seed** (amended 2026-09-17, Tarik's decision after Task-38 grew the pack past a block boundary, K 24 → 25, and the single-seed check went red; measured over 20 seeds, 3 of 20 had already been over budget at K 24): over the 20 fixed seeds `20260915 + s × 7919`, s = 0..19, the **median** frames-needed at 10 / 50 / 70 % loss is within 1.8 / 2.8 / 4.5 × K (10 % was 1.6 until the evening of 2026-09-17: Task-40 grew the pack to K 31 and the median read 1.65 with the worst seed 2.48 inside its 2.5; Tarik raised the one binding row rather than let a decoder that did not change fail on a pack that grew) **and the worst seed** within 2.5 / 3.5 / 4.5 × K; sources 0..19 never delivered (deterministic) within 2.0 × K. Measured at K 25 on 2026-09-17: medians 1.44 / 1.56 / 1.40, maxima 2.32 / 3.24 / 2.28, omission 1.80. At K 31 the same evening: medians 1.65 / 1.74 / 1.47, maxima 2.48 / 2.26 / 2.00, omission 1.35. History, kept because it is a finding: v2 sent the whole page (K 233) and stalled near 110 on the S24; Task-31 round one (worker reader, 2 × 2 grid, RGB multiplexing) reached 15 of 233; round two's lite copy (K 97) completed in 28 s; Task-36 shipped that lite copy with a self-completing fetch for a few hours until Tarik pointed out the receiver must already have the app, so an update needs only the pack. `dist/lite.html` and `window.CrosscheckLite` no longer exist.
- Report here (2026-09-16, Task-35; presentation amended 2026-09-22, Task-54), the contract: on the community screen `Report here` opens a form with the status (`works`, `slow`, `none`), an optional carrier, and a consent line for a coarse position; the same action reads `Close report` while open and closes the form on a second tap. On save `report.js` reads `navigator.connection` if present, asks `navigator.geolocation` once only if consented, rounds the position to two decimals, stores the Report line (seam above) in IndexedDB under the community id, and shows it as one text with Copy, SMS and a static QR. A single `Community reports` group distinguishes `Saved on this phone` from `Import report lines from another phone`; import takes pasted lines (any number, one per line), keeps the well-formed `CR1` ones and drops the rest silently. The group shows the counts per status and latest date; it never touches a badge. `Copy evidence` assembles, from pack strings and the stored reports, one plain-text block for one community: the four verdicts with their sources and dates, the publisher lines, then the reports. Nothing leaves the phone by itself.
- Hosting: GitHub Pages from `dist/` of `github.com/Estaed/CDU_IT_CODEFAIR_DATA_2026`, published by `.github/workflows/pages.yml` on every push to `main` that touches `app/`, `design/`, the pack, `scripts/build_app.py` or `constants.md` (live since 2026-09-15). `dist/sw.js` is network-first for the page and names its cache after the build's SHA-256, so an installed copy updates on the next online open (Task-26; the first version was cache-first and never updated). `APP_URL` in `constants.md` is that Pages address and the QR encodes it.
- Team number, `APP_URL`, dates: read from `constants.md`, never retyped.

**Spikes** that settled a call:
- *Does the capability table vary across 96 communities, or is the map one colour?* Spike 2026-09-12, all 96: NBN is satellite for 95 of 96, but publishers disagree on 31 and telehealth splits 1/58/11/26. **Result:** the capability column is "best available path", not NBN technology (PRD §5).
- *Is 40 km or 5 km the right radius for "licensed site nearby"?* 40 km is true for 96 of 96 and carries no information; 5 km (NTG's own small-cell radius) splits the set. **5 km.**
- *Can the build generate the QR without Node?* `qrcode` 8.2 vs the mirror's `qr.js`, version 3 level M mask 0: 444 dark modules in both, 0 differences (2026-09-12). **Python build.**
- *Do the 96 real coordinates fit the mirror's projection?* Lat −25.58…−11.15, lon 129.08…137.85 project inside the 300×480 view box (2026-09-12, `design/screens/assets/build.mjs`). **Projection reused; outline replaced by ABS in the pipeline.**
- *Can Playwright open a local file on this machine?* Chromium 1234 opened `design/screens/share.html` from `file://` and read its title (2026-09-13). **Browser smoke test is feasible.**
- *Can two browsers on one Wi-Fi open a WebRTC data channel with no STUN, no TURN and no server after the handshake?* `reports/spike-webrtc-hotspot/`, 2026-09-15: two headless Chromium contexts on the laptop, then a Samsung S24 and a Xiaomi Mi 6 on the home router, both CONNECTED with messages both ways. **Nearby chat is buildable; the phone-hotspot case is OQ14.**
- *Is the app small enough to travel by light?* `dist/index.html` 318,741 bytes, 32,099 gzipped (2026-09-15); one QR holds 2,953 bytes. **About 33 frames of 1,000 bytes; a loop, not a single code.** By 2026-09-16 the page is 877,751 bytes, 174,725 gzipped, K 233; 52 KB of the gzip is the map's coverage layers.
- *Why does the receiver stop near 110?* Simulation 2026-09-16 with the shipped decoder at K 233: the uniform 6..12 degree completes 8 of 8 at 10 % loss but 3 of 8 at 70 %; robust soliton (c 0.1, delta 0.5) completes 8 of 8 at every loss tried, about 2 minutes at 70 %. **The fix is measured on phones first (Task-31), then built (Task-36).**

### Fidelity & UI

- **Source of truth**: `design/ds/design/DESIGN.md` with `design/ds/design/tokens/*.css` (a byte-exact mirror of the claude.ai design project; never edited here), and the three reference screens in `design/screens/`. Task files are written against the screens. Where a screen departs from a literal reading of DESIGN.md, `design/screens/README.md` says how and why.
- **Tokens** are the custom properties in `design/ds/design/tokens/*.css`, inlined at build. No file under `app/` writes a colour, size, radius or duration as a literal; the check is layer rule 5.
- **Deviations** are legal only if listed under "Where the screens depart from a literal reading" in `design/screens/README.md` or in the PRD decision log. Anything else that differs from the reference screens is a defect.
- **`review-visual`** compares `dist/index.html` at 360×780 and 768×1024 against the three screen files. Its findings are advisory and never gate: PRD §6 ruled visual fidelity "advisory review by eye, not a gate", and DESIGN.md's Known gaps say the verdict colours were checked by calculation, not on a phone in sunlight.

### Verification Rules

#### Quality gate

```
PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py
```

from the project root, no arguments. It runs, stopping at the first failure: `ruff check --no-cache .`,
`pytest -m "not browser"`, `python scripts/build_app.py`, the size check (`dist/index.html` ≤
1,048,576 bytes and `data/out/data_pack.json` ≤ 512,000 bytes since 2026-09-15), then `pytest -m browser`. The
build sits before the browser step because that step tests the built file. Exit code non-zero
on any failure; `verify-task` reads the exit code.

Run 2026-09-13, before any task: `ruff check .` is clean; `pytest` exits 5 because `tests/` does
not exist yet, so **the gate is red until Task-01 lands the first tests and `build_app.py`**. A
red gate at the start is expected; a task marked DONE on a red gate is not.

#### Per-check detail

1. **Lint**: `PYTHONUTF8=1 .venv/Scripts/python -m ruff check --no-cache .` from the root. Clean
   means the literal output `All checks passed!`: zero errors, zero warnings, nothing
   "pre-existing". `--no-cache` since 2026-09-13: a stale `.ruff_cache` reported green on a tree
   that was red without it (Tarik's decision after the Task-02..04 wave).
   Rules E, F, W, I, B, UP; line length 100; `spike/`, `design/` and `reports/` excluded.
2. **Unit tests must exist for** `rules.best_path`, `rules.telehealth_video`,
   `rules.school_video_meeting`, `rules.mygov_text`, `rules.voice_sms`, `rules.agreement`,
   `pack.build_pack` (every figure carries a source and a date; no BushTel free text while
   OQ1 is open; exactly 96 communities), `build_app.inline` (output contains no `http://` or
   `https://` outside the pack's citation URLs, contains the pack once, stays under the byte
   limits). Rule tests use hand-built rows for every pattern the spike found: unanimous
   covered, unanimous not covered, the six disagreement patterns, the fixed-line case
   (Yirrkala), the WiFi-only case. Since 2026-09-15 also: `layers.build_layers` (every layer
   has `src` pointing at a provenance entry with URL, date and licence; the summed layer bytes
   stay under the figure OQ13 sets), and the pack header test accepts version 2 and refuses 1
   once the layers land. Since 2026-09-17 also: `sources.audit` (a hand-built tile within and
   beyond 5 km gives `not-covered` and `not-recorded`; a community with no audited road within
   5 km is `not-recorded`, never `covered`), `reliability` (the feature builder over hand-built
   rows; the kill path: an AUC under 0.65 leaves every word `none` and the pipeline still
   completes; the held-out split is by SA3 region (boundaries already in `data/raw/`) and no region appears on both sides), `prioritise`
   (every weight read from `priority_weights.csv`, a zero-weight component contributes 0, ranks
   are 1..96 with no ties left unbroken, each of the six interventions is reachable by a
   hand-built row, the sensitivity table has one row per weight), and the pack header test
   accepts 3 and refuses 2 once Task-41 lands.
3. **Integration**: (a) regression, `tests/test_regression.py`: the pipeline run from the frozen
   `data/raw/` reproduces `spike/out/capability_table.csv` for every column the pipeline keeps,
   all 96 rows, until `spike/` is deleted and the check moves to a committed
   `tests/fixtures/capability_table_2026-09-12.csv`; (b) browser smoke, `tests/browser/`, marker
   `browser`: Playwright Chromium opens `dist/index.html` over `file://` with every non-`file:`
   request aborted and counted; the test asserts zero such requests, 96 result rows on the
   community screen, Wadeye's four verdict badges with glyph and word, 96 `.map__community`
   groups on the map, and a `.qr` element on the share screen. Since 2026-09-15 the browser
   suite also holds: (c) the QR encoder in `qr.js` produces, for three fixed strings, the same
   module matrix as Python `qrcode` at the same version and level (the oracle is computed in
   the test); (d) transfer round trip without a camera: the frame payloads produced in the page
   are fed straight to the reassembler and the inflated bytes equal `dist/index.html` exactly;
   (e) until 2026-09-16 the nearby loopback; since then the report round trip: a report saved on
   one page is in IndexedDB, its line is at most 200 bytes UTF-8, no non-`file:` request was
   made, a second page fed that line by paste shows `Reports from here: 1`, and every
   `.verdict-badge` text on both pages is unchanged; (f) the mesh-size text is at most 200
   bytes UTF-8 for all 96 communities, evaluated in one call; (g) every map layer in the pack
   is drawn (one `g` per layer id) and a carrier toggle hides and shows its group, and since
   2026-09-16 area layers start hidden and the service selector changes the point classes and
   the legend counts; (h) since 2026-09-16 the community screen's actions row sits inside the
   first 780 px at 360 wide with no scrolling; (i) since 2026-09-17 the analyst's sixty
   seconds (`tests/browser/test_priority.py`): the Priority tab lists 96 rows in pack rank
   order, an intervention chip narrows the list to that word's count, the first row opens its
   community, that screen shows the `Priority #1 of 96` line, a reliability line with one of
   the four words, five publisher lines, and `Copy evidence` yields a block containing the
   priority line and the reliability line; zero non-`file:` requests throughout. The tests for
   the changes screen, compare and the mesh text are deleted with their features (Task-42); (g) is amended 2026-09-21 by Task-48/49: no `.map__cluster` exists, the 96 groups are present under every filter with the excluded ones dimmed, the three lenses carry the tier, verdict and sources attributes the pack implies, a region chip changes the view box, the legend's bottom edge is inside 360 × 780, the selection card quotes the community's summary sentence, and `declutter` is pure, bounded (14 units) and separates the real 96 by at least 6 units at zoom 1; (j) since 2026-09-21 the ten-second screen (`tests/browser/test_home.py`, written from the Task-45 contract by a different hand than the code): no hash lands on `#/`, the sentence, the three figures and the three buttons read exactly as PRD §4.2 fifth batch gives them and fit 360 × 780 unscrolled, the home renders without `headline`, and every community's summary sentence agrees with its pack agreement and telehealth verdict.
4. **Resources**: the Playwright browser is opened and closed by one pytest fixture; every file
   in the pipeline is opened in a `with` block; nothing starts a server, a thread or a
   subprocess except `gate.py` itself. The browser test asserts the browser object is closed at
   teardown. The report round trip opens its two pages in the same fixture browser; nothing
   under `reports/` is imported by any test.
5. **Not in the Definition of Done**: the hotspot test on real phones (OQ14), the iPhone
   receive route (OQ15), whether the map "reads" (advisory eye review); visual fidelity (advisory, above); the flight-mode check
   on a real phone and the phone-to-phone transfer (Tarik's manual checklist, PRD §6); the
   report, slides and pitch; the BushTel licence outcome (OQ1); the Pages deployment itself;
   the optional cyclone and audit flags (OQ2, OQ3). Each of these is real work, and none of
   them can be turned green by the gate.

### Key Constraints

- The built app must not request anything over the network at runtime: no tiles, fonts, scripts,
  analytics, or data. The browser test fails on the first request.
- The app must not contain a JavaScript framework or library, a service-worker dependency for
  first render, or any computation of a verdict; it renders `data_pack.json`. The one
  exception, named 2026-09-15 (OQ15): **jsQR 1.4.0**, Apache-2.0, vendored as
  `app/vendor/jsQR.js` with `app/vendor/jsQR.LICENSE` beside it, used only through
  `app/scan.js` when the browser has no `BarcodeDetector`. Two edits, both recorded with hashes
  in the licence file: a comment URL removed, and the version 23 alignment centres corrected
  from `[6, 30, 54, 74, 102]` to the ISO/IEC 18004 `[6, 30, 54, 78, 102]` (verified 2026-09-15:
  all 40 versions compared with Python `qrcode`, only 23 differed; shipped jsQR failed to decode
  version 23 and the corrected copy decoded all 40; transfer frames are version 23). No other
  library may be added without a line here.
- Transfer by camera carries the page's own bytes, never a URL that needs the internet. A report
  (2026-09-16) is the person's own word plus what the browser already knows; the app sends no
  probe, and a report never changes a verdict. Nearby chat was removed on 2026-09-16.
- The product must not run a model of any kind at runtime, LLM or ML. Since 2026-09-17 one
  supervised model trains once in `pipeline/reliability.py` (scikit-learn, Audit tiles as
  labels) and ships only as numbers in the pack, with its validation table and kill criterion
  (AUC 0.65) recorded in `data/out/tables/`; the report's Methodology names it and the appendix
  declares it beside the AI used in building the entry.
- Never hardcode: the team number or `APP_URL` (`constants.md`), a colour, size or radius (tokens),
  a requirement figure (`pipeline/thresholds.csv`), a priority weight
  (`pipeline/priority_weights.csv`, 2026-09-17), a source URL, date or licence (the provenance
  registry in `pipeline/provenance.py`).
- No synthetic rows, no invented community names, exactly the 96 BushTel Major/Minor communities.
  Empty is `Not recorded`, unverified is `Unverified`, never blank.
- No BushTel free text in the pack until OQ1 is answered; presence flags with attribution only.
- Hard limits, measured by the gate: `dist/index.html` ≤ 1,048,576 bytes (about 900 KB after Task-37 removed the lite constant); `data/out/data_pack.json`
  ≤ 512,000 bytes (raised from 307,200 on 2026-09-15 by Task-20 from the measured layers in
  `reports/2026-09-15-map-bytes.md`: pack 445,751 bytes with five map layers).
- Out of scope for v1: everything in PRD §8 and the deferred decisions D1–D5. Do not build a seam
  for them beyond the four named above.
- Platform: development is on Windows 11. Scripts use `pathlib` and `subprocess` argument lists,
  never shell strings or POSIX-only idioms; every command in this file is runnable from the root
  as written.
- The repository is English-only, including comments, commits and this file.
