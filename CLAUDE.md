# CLAUDE.md — Crosscheck — CDU IT Code Fair 2026, Data Innovation Challenge (Python 3.13 pipeline + single-file vanilla JS app; pinned in Part 2)

> **Competition context lives in this repo, not in your memory.** Read `README.md`
> at the root of this folder before doing anything, and the files under `docs/` that it
> points to: the official brief, the deliverables, the deadlines and the judging criteria
> are all transcribed there from the organiser's website. They are the constraints this
> project is graded against — treat them the way Part 2 treats the architecture.

---
# TarikOS (Second Brain) link — Eko identity

You are Eko, Tarik's primary AI assistant and second brain. You are currently in the
working directory of the **CDU IT Code Fair 2026 — Data Innovation Challenge** project.

1. Your real brain — your rules and general memory — lives in `D:\TarikOS`.
2. The TarikOS house rules (`Kurallar.md`) are **injected into every session here** by
   `.claude/hooks/brain-rules.sh`, registered in `.claude/settings.json`. They are not
   copied into this repo: one source of truth, and a copy drifts silently. They bind
   everywhere. Where a project rule in Part 1 / Part 2 contradicts one, the project rule
   wins **in this directory only**.
3. For anything else unrelated to this project (general knowledge, an Avenox transcript,
   a past decision), read `D:\TarikOS` directly.
4. You are not a fresh agent created for this project. You are **Eko**, working on this project.

The brain's path is resolved at runtime: `$TARIKOS_HOME` if set, else `D:\TarikOS`. If the
hook cannot find it, it says so loudly at session start rather than letting you work without
the rules and never know it. That failure mode is not hypothetical: this template hardcoded
`C:\TarikOS` until the vault moved to `D:`, and every clone silently pointed at a directory
that no longer existed.

**Codex gets the same injection.** `.codex/hooks.json` registers a `SessionStart` hook
pointing at `.claude/hooks/codex-brain-rules.cmd`, which runs the *same*
`brain-rules.sh` — one script, two CLIs, no second copy of the rule logic. The `.cmd`
shim is required, not stylistic: Codex runs hook commands **without a shell**, so a bare
`bash.exe script.sh` entry fails.

**`.codex/hooks.json` does not ship in this template, on purpose.** It is generated per
project and never hand-edited, because the command path has to be **absolute** — Codex
defines neither `CODEX_PROJECT_DIR` nor `CLAUDE_PROJECT_DIR` and runs the command without
a shell, so there is nothing to expand at runtime. A file shipped in the template would
carry the template's own path into every clone. The generator refuses to run while
`CLAUDE.md` still carries the unfilled project-name placeholder, so it cannot be
regenerated here by accident.

**Two setup steps, in this order, in the clone — after filling in the placeholders:**

    python D:/TarikOS/.claude/scripts/sync_agents_md.py .          # AGENTS.md <- CLAUDE.md
    python D:/TarikOS/.claude/scripts/render_codex_hooks.py --project .

    python D:/TarikOS/.claude/scripts/sync_agents_md.py . --check  # audit
    python D:/TarikOS/.claude/scripts/render_codex_hooks.py --project . --check

**`sync_agents_md.py` is not optional and it is easy to forget**, because forgetting it
produces no error: Codex never reads `CLAUDE.md`, so an `AGENTS.md` still carrying
the unfilled placeholder — or any later CLAUDE.md edit that was not synced — gives Codex a
different set of rules from Claude, quietly. Run the `--check` form whenever CLAUDE.md
changes.

`render_codex_hooks.py --project` also **writes the `.cmd` shim if it is missing**, so a
clone made before the shim existed repairs itself. `--check` reports `EKSIK` in a fresh
clone; that is the correct signal, not a fault — it means the setup step has not been run
yet. `--check` never repairs anything: a check that silently fixes what it finds is not a
check.

**One manual step remains per clone:** Codex asks for trust the first time it sees this
hook file, and an **unapproved hook is skipped silently** — the screen still says
`Completed`. So "no error" does not mean "the rules arrived". Approve it once in an
interactive `codex` session, or confirm the rules text actually appears in context.

Skills are not stored in this repo. They live in `D:\TarikOS\.claude\skills\` and are
junctioned into `~/.claude/skills/` and `~/.codex/skills/`, so the same version loads here.
See `.claude/skills-README.md`.

The text below defines this project's local rules and architecture (adapted from the
original CLAUDE.md for Codex).
---

## Part 1: Operational Principles & Workflow (IMMUTABLE)

**Core Workflow (Skill Routing).** Grouped by *when they run*, not numbered — only the
first group is a sequence. Nothing here is a ladder to climb once and leave behind.

**Once per project, in this order**
- **Scaffolding files**, created with the folder and grown from there: `notes.md` (raw
  dump), `reports/` (unattended research output), `BACKLOG.md` (what was deferred and
  why), `constants.md` (values that must not be retyped), `MODELS.md` (which model runs
  which lane here). Each carries its own instructions; delete the instructions, not the
  file. `constants.md` and `MODELS.md` may be deleted outright if this project genuinely
  has no such values or lanes — say so in Part 2 rather than leaving them empty.
- `notes.md` — before any skill runs, dump what the thing has to do while looking at it.
  Features, data sources, and the calls already being made ("not in v1", "their third
  party, our own build"). Two minutes of this is what `create-prd` needs as input; see
  the file's own instructions.
- `create-prd` — the spec, from `notes.md`, the user's inputs, or designs.
- `create-architecture` — turns the PRD into Part 2 below: the stack, the layer rule, the
  seams, the verification rules. Part 2 ships as a placeholder in this template, so this
  step is **required** before any task is written. Once Part 2 exists, amending it stays a
  decision to raise with the user rather than an edit made in passing.
- `generate-tasks` — breaks the PRD into atomic `tasks/Task-XX.md`. Refuses to run before
  Part 2 exists.

**Per task, in a loop**
- **Read the task file's `Execution` and `Lane` blocks first.** `Execution` names the agent
  and the effort; `Lane` carries the delegation contract (OWNS,
  MUST NOT TOUCH, GATE, DEPENDS ON). Both were written by `generate-tasks` with the PRD and
  Part 2 in view — a session reading the task cold does not have that context and must not
  re-litigate it.
- **No Plan mode on tasks.** A task runs directly from its file. The task file is the
  contract — `Lane` (OWNS / GATE), the Acceptance Criteria and Part 2 are binding; the
  Execution Guide is the recommended route, not a script. Deviate from the guide when you
  have a concrete reason, stay inside OWNS, and say what you changed and why in the report.
  An open "how" is a ⛔ question to the operator, closed before the task runs — never a
  planning session at run time.
- `verify-task` — the goal-oriented fix loop, and **the gate**: nothing else marks a task
  DONE. **Run from the main loop, never by the lane that wrote the code** — the agent that
  produced the work must not be the one that relaxes its test.

**Unattended, when you want to leave the desk**
- `otopilot` — runs the tasks routed to `codex` that carry no ⛔ stop marker, in parallel worktree
  lanes, and runs each lane's `GATE` command itself. You approve one wave plan; everything
  after that is unattended, and you come back to a report. It refuses to start on a dirty
  tree, a red baseline, a missing `Lane` block, or any unanswered blocking question — clear
  those before you walk away, not after.

**Per group of tasks, once they are green — not per task**
- `/code-review` over the accumulated diff — **not** a persona subagent: it is built to
  review a diff and takes an effort level, where a cold subagent reports every provisional
  value and deliberate omission Part 2 records as a defect. Feed it the task file and
  Part 2, and treat its findings as candidates, not verdicts.
- `review-visual` — only when the task produced something anyone looks at. Compares the
  built output against the source of truth Part 2 names, because `verify-task` cannot see a
  screen and reading the code to describe what it *would* render is the same guess that
  wrote it. Advisory like `/code-review` — never a gate.

**Any time, on their own — these are not stages and carry no place in the order**
- `idea-arena` — when the approach is genuinely open and more than one mechanism fits.
  Expensive; skip it whenever the approach is already decided or the call is cheap to
  reverse. Before the PRD its verdict is what the PRD describes; later it answers a question
  the PRD left open, and nothing about running it again means starting over.
- `research` — for a claim that can be checked: is this package maintained, does this API
  still exist, what is the current version, what is the known trap. It reports dated sources
  and hands the decision back; it never edits `docs/PRD.md`, Part 2 or a task file.
- `derin-akil` — for a problem that is stuck rather than open: a bug that survives the
  obvious fixes, a performance cliff, an architecture that will not close. It packages the
  relevant code, asks one non-agentic deep model, and then **verifies every finding against
  live code** before anything is applied. That verification half is the skill; a report from
  a model that cannot run the code is a hypothesis.
- `claude-chef` — the delegation policy itself: which tier of the stack a piece of work
  goes to. Read it before spawning subagents or Codex lanes, not after. Its mirror
  `codex-chef` applies when Codex is the main loop instead.
- `codex-swarm` — runs `codex exec` lanes directly, and generates image assets. Unlike
  `otopilot` it is not gated and not unattended: you are still at the desk. Its mirror
  `claude-swarm` spawns `claude -p` lanes from a Codex main loop.

  The prefix names **what gets spawned**, not who reads the file, and no CLI is shown the
  swarm that spawns its own kind — a Codex session reading `codex-swarm` would be reading
  "respawn yourself".

**Where the project currently stands** — which tasks are DONE, which is next — is
`docs/TASKS_INDEX.md`, never this file. Status written here goes stale within a week and
is then loaded into every session as a fact.

### 1. Ask, don't assume
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State assumptions out loud; if several readings exist, present them.
- **Precedence:** a task file is the answer to "what do you want" — run it. Ask only when an
  ambiguity changes the contract (Lane, Acceptance Criteria, Part 2); otherwise take the
  simplest reading consistent with Part 2 and say so in the report.
- If a simpler approach exists, say so. Push back when warranted.

### 2. Simplicity first
**Simplest solution for simple problems, better solutions for harder problems. Minimum code that solves the problem.**
- No features beyond what was asked. MVP strictly.
- No abstractions for single-use code.
- If you write 200 lines and it could be 50, rewrite it.
- **The documents obey this too** — this file, the PRD, task files, skills. A paragraph that
  steers no decision gets cut; one that steers a decision in half the words gets rewritten.

### 3. Surgical changes
**Touch only what you must. Clean up only your own mess.**
- Don't "improve" adjacent code, comments, or formatting. Don't refactor things that aren't broken.
- Remove imports/variables/functions that **your** changes made unused.
- Report bad code or spec contradictions as a separate issue; do not silently fix or ignore them.
- **New files go where the existing structure already puts them.** Check what folders exist
  before creating one; a task file naming a folder that does not match reality loses to
  reality. Create a folder for 3+ related files, never for one or two that fit elsewhere,
  and say which existing folder you chose when the task named a different one.

### 4. Goal-driven execution
**Define success criteria. Loop until verified.**
- Transform tasks into verifiable goals (e.g., "Add Login validation" → "Write tests for invalid inputs, then make them pass").
- For multi-step tasks, state a brief plan up front.
- Strong success criteria let you loop independently. Implementation is not complete until `verify-task` confirms zero errors.

### 5. Flag uncertainty explicitly
If you're unsure about something, run a small, localized, low-risk experiment and bring the hypothesis *and* the results to discuss. Confidence without certainty causes damage. Say "I don't know" plainly.

### 6. Better ideas are welcome
Suggest better ways of doing things, especially ideas with lasting impact over tactical
fixes. Suggest, then wait for a decision on product and architecture. Delegation, model
choice and vault hygiene follow `Kurallar.md`, which decides without asking.

### 7. The repository is English-only
Everything written to disk in this repo is English: identifiers, comments, commit messages,
`CLAUDE.md`, `docs/`, `design/`, `tasks/`. Only the conversation follows the language we
speak. Turkish lives in the brain (`D:\TarikOS`) and nowhere else.

### 8. Part 2 is binding until it is changed on purpose
Part 2 below is not advice; every task was written against it. When the code contradicts
it — a seam that does not fit, a pinned version that breaks, a layer rule that cannot hold
— stop and say so. Do not silently deviate, and do not edit Part 2 to match what you just
wrote: that makes the deviation invisible to every session afterwards. Changing it is the
user's call, and `create-architecture` is what amends it.

---

## Part 2: Technical Architecture

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

**Pushed down, out of the browser.** Everything deterministic runs once in the pipeline or the build, never on the phone: the path rule and all verdicts, the agreement count, the reason sentences, the "who does what" lines, the projected SVG coordinates of the 96 points, the simplified NT outline, the URL QR modules, the two PNG maps, and since 2026-09-15 the simplified map layers (towns, highways, SA3 regions, ACCC coverage per carrier). The browser does five things: pick a community, show its pack row, share the file, play or receive the app as QR frames, and (since 2026-09-16, replacing nearby chat) keep and count the phone's own reports. Since 2026-09-16 (Task-30, decided by Eko on Tarik's delegation) picking a community may also use the phone's own GPS: `navigator.geolocation` once, nearest of the 96 by great-circle distance, nothing stored or sent; and `scan.js` tunes the stream the two camera files open (resolution, continuous and tap focus, zoom) without opening one itself. What stays in the browser is only what depends on runtime bytes or the other phone: encoding this build's own bytes as QR frames (gzip via `CompressionStream`, encoder in `qr.js`), the mesh-size, SMS and (2026-09-16) evidence texts assembled from pack strings and the phone's reports, since 2026-09-15 grouping the visible map points into zoom clusters (it depends on the live zoom; layout, not a verdict; Task-29), and since 2026-09-16 sorting the shown communities worst first under the map (a sort over pack verdicts, not a verdict). Since 2026-09-17 (fourth batch) the pack also carries, per community, the map-claim reliability word and the priority rank, score, intervention and addressee, all computed in the pipeline; the Priority tab is a render of `pack.priority` in pack order and a chip filter over its `intervention` field, nothing more. The mesh text and the compare render are gone the same day (Task-42). Nothing runs a model at runtime: the one model (`pipeline/reliability.py`) trains once in the pipeline and ships as numbers (PRD §3, §4.2 fourth batch).

**The seams**, only those a PRD phase names, with what sits behind each today:
- **Publisher line** `{publisher, kind, says_covered, detail, source, date}` in `pipeline/sources/*` and the pack. Today: `accc` (predicted), `ntg2022` (listed), `rrl` (licensed, 5 km), `bushtel` (portal), and since 2026-09-17 `audit` (measured: `not-covered` when a non-alignment tile lies within 5 km, `not-recorded` when no audited road does; Task-38). D1's modelled publisher is a new module emitting `kind: "modelled"`; the app renders any kind it is given. `mobile_says` keeps its four keys (the action table, the filters, the figures and the disagreement patterns all match on that string); the audit line comes from two new table columns, `audit5` (`1`, `0` or empty for not recorded) and `audit_nearest_km`, and `pack.publisher_lines` appends it as the fifth line. The agreement count's `available` still counts only lines that make a claim.
- **Reliability line** (2026-09-17, Task-39) `claim_reliability: {word: high|medium|low|none, p_wrong, drivers: [name, name], src}` per community in the pack; `none` with `p_wrong: null` when the model did not ship (kill criterion) or the community has no carrier claim to test. The app prints one line from it and never recomputes it.
- **Priority row** (2026-09-17, Task-40) `{id, rank, score, components: [{name, value, weight, contribution}], intervention, addressee, why}` in the pack's `priority` list, 96 rows, rank order. `intervention` is one of the six words in `pipeline/prioritise.py`'s table; a new intervention is a new rule row there and a new chip in the app, no other change. Weights live only in `pipeline/priority_weights.csv`; a component whose source is licence-gated (cyclone, ADII) carries weight 0 and `note: "awaiting OQn"` until it lands.
- **Flag** `{name, value, source, date}` per community. Today: `road_seasonal_cut` (BushTel), `backhaul_2019` (NTG). OQ2 audit tiles and OQ3 cyclone count are new flag emitters, no app change.
- **Requirement row** in `pipeline/thresholds.csv`. OQ8 and OQ11 add rows; `rules.py` reads the table and never embeds a figure.
- **Pack header** `{pack_version, built, app_url, communities: 96}`; the app refuses a pack whose `pack_version` it does not know. Version 1 until the map's second pass is drawn: Task-20 adds the `layers` key additively (the app ignores it), Task-21 draws it, bumps the version to **2** and makes the app accept 2 only. 2026-09-17: Tasks 38 to 40 add `audit` lines, `claim_reliability` and `priority` additively under version 2 (the app ignores what it does not render); Task-41 renders them, bumps to **3** and makes the app accept 3 only. Task-42 removes the header's `changes` block.
- **Map layer** `{id, label, kind: "line" | "area" | "point", src, paths: [...]}` in the pack's `layers` list, one per town set, highway, region set and carrier; the app draws any layer it is given with the colour token named by its `id` in `app/layers.css`, and toggles `area` layers. New layers are new pipeline emitters, no app change.
- **Report line** (2026-09-16, Task-35), the one record the app writes itself: `CR1|<bushtel_id>|<yyyymmddhhmm UTC>|<status: works|slow|none>|<carrier: telstra|optus|tpg|other|->|<effectiveType or ->|<rtt ms or ->|<downlink Mbps or ->|<lat>,<lon> or -`, at most 200 bytes UTF-8, and nothing else. The pack does not carry reports and `pack_version` does not move for them; they live in the phone's IndexedDB (`store.js`) and travel as this line. A later version is a new prefix (`CR2`), and a reader ignores prefixes it does not know.
No seam exists for D3 (more communities) or D5 (national): they are v1.1 and get their seams when they are planned (D2 became Report here on 2026-09-16, the Report line above).

**Entry points**
- `PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py` from the root: reads `data/raw/`, writes `data/out/`. No network; `pipeline/fetch/*.py` are run by hand and their results committed or logged in `PROVENANCE.md`.
- `PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py` from the root: inlines, in this order, `design/ds/design/tokens/colors.css`, `typography.css`, `spacing.css`, `design/ds/design/base.css`, `design/screens/screens.css`, `app/app.css`, `app/layers.css`, then `app/vendor/jsQR.js`, `app/qr.js`, `app/scan.js`, `app/transfer.js`, `app/store.js`, `app/report.js`, `app/app.js` (in that order since 2026-09-16, each a plain script; the helpers expose one object each on `window` and `app.js` is the only file that touches the DOM at load), then `data/out/data_pack.json` as `<script type="application/json" id="pack">`, into `app/index.html` → `dist/index.html`. Also writes the host-only files to `dist/`: `sw.js` (cache named after the build hash), `manifest.webmanifest`, and the three home-screen icons drawn from the tokens (Task-28); the HTML links the manifest and icons but works without them.
- The app routes by hash: `#/community/<bushtel_id>`, `#/map?filter=<id>`, `#/share`, and since 2026-09-17 `#/priority?intervention=<word>` as the fourth tab (Task-41); `#/compare/<id>/<id>` existed from 2026-09-15 to 2026-09-17 (Task-42) and `#/nearby` from 2026-09-15 to 2026-09-16. Since 2026-09-17 the Priority tab is the first thing the analyst sees after the default community: the tab order is Community, Priority, Map, Share, and the "analyst's sixty seconds" (PRD §2) is the browser test (i) below. The three screens are the reference: `design/screens/community.html`, `map.html`, `share.html`. The transfer controls on the share screen, the map's second and third passes, the community screen's third pass and Report here have no screen file: PRD §4.2 (second and third batches) is their source of truth and they reuse the existing components (`card`, `button`, `chip`, `list`, `details`) with no new CSS beyond `app/app.css`. Since 2026-09-16 the four verdict glyphs are `●` Works, `◐` Degraded, `○` Fails, `◌` No data, in badges, legends and as map point geometry (filled disc, half disc, ring, dotted ring); DESIGN.md's `● ▲ ■ –` are departed from in `design/screens/README.md`. On load the selected tab is scrolled into view (decision 2026-09-13, PRD §11).
- Transfer by camera, the contract both ends share (**v4, Task-37, 2026-09-16 evening**; `CX`, `CY` and `CZ` are gone and are ignored). **What travels is the data pack, not the app**: the receiving phone already has Crosscheck (its camera app cannot reassemble frames), so the camera is the pairing-free, cross-platform (Android to iPhone) update channel for a phone with no network, and the app itself is installed once from `APP_URL` or by a shared file. Payload = gzip of the inlined pack JSON with `layers` replaced by `[]` (about 18 KB, K about 25 on 2026-09-16; the map layers are static geography and the receiver keeps its own). Blocks of 750 bytes; frame text = `CP` + index (4 hex) + `K` (4 hex) + payload length (6 hex) + base64 of one block (1,000 characters), QR byte mode, level L; repair blocks by xorshift32 from the index with a robust-soliton degree (c 0.1, delta 0.5); one source pass, then repair only. Sender: frame changes inside `requestAnimationFrame`, held 16 refreshes (3.75 frames a second; measured on the S24 2026-09-16, 141 codes decoded of 189 frames read). Receiver: the main-thread loop, one `CrosscheckScan.reader().detect(video)` per 100 ms, peeling decoder, `known of K`, vibration, then `CrosscheckStore.save(text)` which validates `pack_version` and the community count and, when the incoming `layers` is empty, carries the stored or inline layers over; `Use received data now` reloads. A pack the copy cannot accept (other `pack_version`) says `This copy is too old for that data; open the address once with the internet`. Browser tests: round trip byte-exact against the built pack, layers carried over, `CZ`/`CY` ignored, loss at 10 / 50 / 70 % within 1.6 / 2.8 / 4.5 × K, sources 0..19 never delivered within 1.75 × K. History, kept because it is a finding: v2 sent the whole page (K 233) and stalled near 110 on the S24; Task-31 round one (worker reader, 2 × 2 grid, RGB multiplexing) reached 15 of 233; round two's lite copy (K 97) completed in 28 s; Task-36 shipped that lite copy with a self-completing fetch for a few hours until Tarik pointed out the receiver must already have the app, so an update needs only the pack. `dist/lite.html` and `window.CrosscheckLite` no longer exist.
- Report here (2026-09-16, Task-35), the contract: on the community screen `Report here` opens a form with the status (`works`, `slow`, `none`), an optional carrier, and a consent line for a coarse position; on save `report.js` reads `navigator.connection` if present, asks `navigator.geolocation` once only if consented, rounds the position to two decimals, stores the Report line (seam above) in IndexedDB under the community id, and shows it as one text with Copy, SMS and a static QR. `Add reports` on the same screen takes pasted lines (any number, one per line), keeps the well-formed `CR1` ones and drops the rest silently. The screen shows `Reports from here: <n>` with the counts per status and the latest date; it never touches a badge. `Copy evidence` assembles, from pack strings and the stored reports, one plain-text block for one community: the four verdicts with their sources and dates, the publisher lines, then the reports. Nothing leaves the phone by itself.
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
   the changes screen, compare and the mesh text are deleted with their features (Task-42).
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

### Why this section exists

`docs/PRD.md` says *what* to build and *why*. `tasks/Task-XX.md` says *how* to build one
slice. Neither survives as ambient context; they are read on demand. `CLAUDE.md` is loaded into
**every** session, so Part 2 is the only place where the project's technical invariants are
always present. Without it, each session re-derives the stack and 30 tasks drift into 30
slightly different architectures. Part 2 is what makes task 27 look like task 3 wrote it.
