<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Source: CLAUDE.md. Make changes there, then run:
       python .claude/scripts/sync_agents_md.py <this-directory>
     Codex reads AGENTS.md rather than CLAUDE.md; this file is generated
     from it so the content remains identical. -->

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
- **`.gitattributes`** ships with the template and is not project-specific: it forces LF
  on shell scripts and CRLF on Windows launchers regardless of which OS commits, because a
  wrong-ending `.sh` fails its shebang and a wrong-ending `.cmd` can fail under cmd.exe.
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
- **Read the task file's `Execution` and `Lane` blocks first.** `Execution` names the agent,
  the effort and whether Plan mode opens; `Lane` carries the delegation contract (OWNS,
  MUST NOT TOUCH, GATE, DEPENDS ON). Both were written by `generate-tasks` with the PRD and
  Part 2 in view — a session reading the task cold does not have that context and must not
  re-litigate it.
- Native Plan mode — **only when the `Execution` block says so.** Map the file changes, wait
  for approval, then implement.
- `verify-task` — the goal-oriented fix loop, and **the gate**: nothing else marks a task
  DONE. **Run from the main loop, never by the lane that wrote the code** — the agent that
  produced the work must not be the one that relaxes its test.

**Unattended, when you want to leave the desk**
- `otopilot` — runs the tasks routed to `codex` with Plan mode closed, in parallel worktree
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

### 0. Three tiers of instruction — know which one you are using

A prompt, a rule and a protocol are not the same strength, and reaching for the
weak one where the strong one is needed is why the same mistake keeps returning.

1. **Prompt** — said once, in one turn. Gone next session. Fine for "use a table
   here", useless for anything that must hold every time.
2. **Rule** — written into this file or `Kurallar.md`. Survives sessions and is
   loaded into context, but it is still something the agent has to *remember to
   obey* while doing something else.
3. **Protocol** — structural. Not remembered, enforced. The work cannot proceed
   without it: `verify-task` is the only thing that marks DONE; `AGENTS.md` is
   generated from `CLAUDE.md` so the two cannot drift; a commit gate that refuses
   until the benchmark moves.

Escalate when a rule has failed twice. Repeating it louder a third time is how a
rule file grows into noise nobody reads. Ask instead: what would make this
impossible to get wrong?

Not everything deserves a protocol — they cost something to build and they bite
when the work legitimately needs an exception. Reserve them for the places where
a silent miss is expensive.

### 0. Vault / Brain Integration (Session Management)
**Projects are temporary, the Brain is permanent.**
Whenever a meaningful session ends (a task is completed, a major architectural decision is
made, or a difficult bug is resolved), you MUST NOT close the session without leaving a
trace in the vault.

- Summarize the core lessons learned, technical shifts, or completed milestones.
- **Never write to `D:\TarikOS\daily\<YYYY-MM-DD>.md` by hand.** `daily/` is owned by
  the SessionEnd flush worker; it records the conversation and the compiler later turns
  that machine log into `knowledge/`.
- Leave the relational handoff in `D:\TarikOS\850-Companion 🔮\`: PREPEND a new
  `## Session:` block at the TOP of `Last-Session.md`, update the specific active story
  in `Threads.md` rather than bulk-appending, and append a short entry to `Journal.md`
  when the session materially changes the shared story. The Last-Session archiver keeps
  only the newest three blocks live.
- Name the model in hand-written Last-Session and Journal entries.

### 1. Ask, don't assume
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- If something is unclear, ask **before writing a single line**. Never make silent assumptions about intent, architecture, or requirements.
- State your assumptions explicitly, out loud, even the ones you're confident in.
- If multiple interpretations exist, present them — don't pick one silently.
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
Suggest better ways of doing things, especially ideas with lasting impact over tactical fixes. Suggest, then wait for a decision; don't unilaterally act on your own suggestion.

### 7. The repository is English-only, no matter what language we're speaking
Everything written to disk in this repo is English: identifiers (classes, methods,
variables, files, folders), comments, commit messages, test descriptions — and also
`CLAUDE.md`, `docs/`, `design/` and every `tasks/Task-XX.md`. Only the **conversation**
follows whatever language we are speaking.

Not a style preference. A codebase mixing languages in its identifiers is genuinely
harder to read later, and English is what every library and error message it will ever
consult is already written in. The documents share the constraint for a different reason:
they are read by delegate lanes, by reviewers and by whoever inherits this repo, none of
whom are in this conversation. Turkish lives in `D:\TarikOS` — the brain — and nowhere else.

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
| qrcode | 8.2 | build-time QR; compared module for module with the mirror's `qr.js` on 2026-09-12, 0 differences, so the build needs no Node |
| pytest | 9.1.1 (dev) | unit and browser tests |
| ruff | 0.16.7 (dev) | lint; config in `pyproject.toml`, excludes `spike/` and `design/` |
| playwright | 1.62.0 (dev) | headless Chromium opens `dist/index.html` from `file://`; verified 2026-09-13. Browser build in `~/AppData/Local/ms-playwright/` |

Rejected, one line each:
- **Preact or React with the mirror's `.jsx` components**: a second toolchain, and the components carry literal sizes the screens deliberately do not copy.
- **esbuild/Vite for a vanilla app**: minification saves nothing that matters at ~30 KB of JS.
- **Flutter, Streamlit, any server**: a tool that needs a connection to explain where there is none (notes.md, 2026-09-12).
- **pydeck/folium/Leaflet**: tile and CDN requests at runtime; the map is inline SVG.
- **duckdb**: in the spike venv, imported nowhere; dropped by `uv sync`.
- **Decimen Optical Transfer, qwbp, txqr as dependencies** (2026-09-15): AGPL-3.0 from v0.4.0 (Decimen) or code we do not need; the QR encoder, the frame loop and the SDP-in-QR handshake are our own, ~500 lines, no licence to carry.
- **STUN or TURN servers** for nearby chat: a server, and the internet; `iceServers` is `[]` and the range is the Wi-Fi.
- **ESP32 captive portal, Meshtastic nodes** (2026-09-15): cost money; report recommendations only.
- **Web fonts, icon fonts, images**: DESIGN.md forbids them and the byte budget agrees.
- **`venv` as the environment name**: uv and VS Code default to `.venv`; decided 2026-09-13.

### Architecture

**Where the code lives** (folders not yet present are created by the task that first needs them):

```
pipeline/            Python package, offline after data/raw/ is frozen
  fetch/             one script per source; the ONLY place the network is touched; writes data/raw/<source>_<date>.*
  sources/           one module per publisher or layer (nbn, accc, rrl, ntg, bushtel); each emits a 96-row frame keyed on bushtel_id
  rules.py           best-available-path rule and the service verdict rules: pure functions over plain dicts
  thresholds.csv     requirement figures with source URL and date (promoted from spike/thresholds.csv)
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
                     camera receive), nearby.js (WebRTC data channel, QR handshake, Wi-Fi join QR), layers.css
                     (map-layer custom properties only). app/vendor/ exists only if OQ15 picks a WASM QR reader
                     for iPhone, with its licence file beside it and a line here first.
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
4. `app/` computes no verdict. The pack carries the verdict word, the reason sentence and the sources per service; `thresholds.csv` is not in the pack and no file under `app/` compares a figure against a requirement. The app renders, routes and shares; since 2026-09-15 it also encodes QR, plays and reads frames, gzips its own bytes and opens a WebRTC channel, none of which is a verdict.
5. Colours, sizes, radii and fonts exist only as the custom properties in `design/ds/design/tokens/*.css`, plus the map-layer colours in `app/layers.css` (custom property definitions only, nothing else in that file; decision 2026-09-15, DESIGN.md's colour rule broken on purpose for carrier layers). `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js app/qr.js app/transfer.js app/nearby.js` prints nothing; SVG geometry inside the pack is data, not CSS.
6. Nothing in the repo imports from `spike/` or `design/ds/components/`.
7. The app makes no request while running, checked in the code, not only in the browser test: `grep -nE "fetch\(|XMLHttpRequest|WebSocket|EventSource|stun:|turn:|https?://" app/app.js app/qr.js app/transfer.js app/nearby.js` prints nothing (`sw.js` is the host-only exception and is never needed for first render). `nearby.js` constructs `RTCPeerConnection({ iceServers: [] })` and nothing else.
8. The camera and the microphone are touched only in `transfer.js` (receive) and `nearby.js` (scan): `grep -l getUserMedia app/*.js` prints exactly those two files. Every stream is stopped on route change.

**Pushed down, out of the browser.** Everything deterministic runs once in the pipeline or the build, never on the phone: the path rule and all verdicts, the agreement count, the reason sentences, the "who does what" lines, the projected SVG coordinates of the 96 points, the simplified NT outline, the URL QR modules, the two PNG maps, and since 2026-09-15 the simplified map layers (towns, highways, SA3 regions, ACCC coverage per carrier). The browser does five things: pick a community, show its pack row, share the file, play or receive the app as QR frames, and hold a nearby chat. What stays in the browser is only what depends on runtime bytes or the other phone: encoding this build's own bytes as QR frames (gzip via `CompressionStream`, encoder in `qr.js`), the WebRTC handshake, and the mesh-size and SMS texts assembled from pack strings. Nothing is left with a model: the product contains no model (PRD §3).

**The seams**, only those a PRD phase names, with what sits behind each today:
- **Publisher line** `{publisher, kind, says_covered, detail, source, date}` in `pipeline/sources/*` and the pack. Today: `accc` (predicted), `ntg2022` (listed), `rrl` (licensed, 5 km), `bushtel` (portal). D1's modelled publisher is a new module emitting `kind: "modelled"`; the app renders any kind it is given.
- **Flag** `{name, value, source, date}` per community. Today: `road_seasonal_cut` (BushTel), `backhaul_2019` (NTG). OQ2 audit tiles and OQ3 cyclone count are new flag emitters, no app change.
- **Requirement row** in `pipeline/thresholds.csv`. OQ8 and OQ11 add rows; `rules.py` reads the table and never embeds a figure.
- **Pack header** `{pack_version, built, app_url, communities: 96}`; the app refuses a pack whose `pack_version` it does not know. Version 1 until the map's second pass is drawn: Task-20 adds the `layers` key additively (the app ignores it), Task-21 draws it, bumps the version to **2** and makes the app accept 2 only.
- **Map layer** `{id, label, kind: "line" | "area" | "point", src, paths: [...]}` in the pack's `layers` list, one per town set, highway, region set and carrier; the app draws any layer it is given with the colour token named by its `id` in `app/layers.css`, and toggles `area` layers. New layers are new pipeline emitters, no app change.
No seam exists for D2 (measurements), D3 (more communities) or D5 (national): they are v1.1 and get their seams when they are planned.

**Entry points**
- `PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py` from the root: reads `data/raw/`, writes `data/out/`. No network; `pipeline/fetch/*.py` are run by hand and their results committed or logged in `PROVENANCE.md`.
- `PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py` from the root: inlines, in this order, `design/ds/design/tokens/colors.css`, `typography.css`, `spacing.css`, `design/ds/design/base.css`, `design/screens/screens.css`, `app/app.css`, `app/layers.css`, then `app/qr.js`, `app/transfer.js`, `app/nearby.js`, `app/app.js` (in that order, each a plain script; the three helpers expose one object each on `window` and `app.js` is the only file that touches the DOM at load), then `data/out/data_pack.json` as `<script type="application/json" id="pack">`, into `app/index.html` → `dist/index.html`. Also copies `sw.js` and `manifest.webmanifest` to `dist/` for the host; the HTML never depends on them.
- The app routes by hash: `#/community/<bushtel_id>`, `#/map?filter=<id>`, `#/share`, `#/compare/<id>/<id>`, and since 2026-09-15 `#/nearby`. The three screens are the reference: `design/screens/community.html`, `map.html`, `share.html`. The nearby screen, the transfer controls on the share screen and the map's second pass have no screen file: PRD §4.2 (second batch) is their source of truth and they reuse the existing components (`card`, `button`, `chip`, `list`) with no new CSS beyond `app/app.css`. On load the selected tab is scrolled into view (decision 2026-09-13, PRD §11).
- Transfer by camera, the contract both ends share: payload = gzip of the exact bytes of the running page (`pageHtml()`, the same bytes save-as-file writes); the payload is base64 text because `BarcodeDetector.rawValue` is a string, not bytes; frames = `CX` + index (4 hex) + count (4 hex) + up to 1,000 base64 characters, QR byte mode, error correction L, looped at about 8 frames per second until the user stops; the receiver keeps a set keyed by index, shows `received / total`, and when complete verifies length, inflates with `DecompressionStream`, and opens the result from a `blob:` URL with a save button. Reader: `BarcodeDetector` where present; where absent the screen says so and points at the URL QR (OQ15).
- Nearby chat, the contract: host taps Start, gets an offer with ICE gathering complete (3 s cap), shows it as one QR (the SDP JSON deflated with `CompressionStream("deflate-raw")` and base64-encoded; field-level reduction only if a real offer still exceeds 1,200 characters); guest scans, shows the answer QR; host scans; the `chat` data channel carries `{t: "msg", text}` and `{t: "pack"}` / `{t: "pack-data", json}`. No storage: a reload empties the screen. The status line prints the range honestly: "Works while both phones are on this Wi-Fi". The Wi-Fi join QR is `WIFI:T:WPA;S:<ssid>;P:<password>;;` from two inputs; nothing is persisted.
- Hosting: GitHub Pages from `dist/` of `github.com/Estaed/CDU_IT_CODEFAIR_DATA_2026`. The repo is private; the account is GitHub Pro, so Pages serves from a private repo once it is enabled (Tarik, later). `APP_URL` in `constants.md` is that Pages address and the QR encodes it.
- Team number, `APP_URL`, dates: read from `constants.md`, never retyped.

**Spikes** that settled a call:
- *Does the capability table vary across 96 communities, or is the map one colour?* Spike 2026-09-12, all 96: NBN is satellite for 95 of 96, but publishers disagree on 31 and telehealth splits 1/58/11/26. **Result:** the capability column is "best available path", not NBN technology (PRD §5).
- *Is 40 km or 5 km the right radius for "licensed site nearby"?* 40 km is true for 96 of 96 and carries no information; 5 km (NTG's own small-cell radius) splits the set. **5 km.**
- *Can the build generate the QR without Node?* `qrcode` 8.2 vs the mirror's `qr.js`, version 3 level M mask 0: 444 dark modules in both, 0 differences (2026-09-12). **Python build.**
- *Do the 96 real coordinates fit the mirror's projection?* Lat −25.58…−11.15, lon 129.08…137.85 project inside the 300×480 view box (2026-09-12, `design/screens/assets/build.mjs`). **Projection reused; outline replaced by ABS in the pipeline.**
- *Can Playwright open a local file on this machine?* Chromium 1234 opened `design/screens/share.html` from `file://` and read its title (2026-09-13). **Browser smoke test is feasible.**
- *Can two browsers on one Wi-Fi open a WebRTC data channel with no STUN, no TURN and no server after the handshake?* `reports/spike-webrtc-hotspot/`, 2026-09-15: two headless Chromium contexts on the laptop, then a Samsung S24 and a Xiaomi Mi 6 on the home router, both CONNECTED with messages both ways. **Nearby chat is buildable; the phone-hotspot case is OQ14.**
- *Is the app small enough to travel by light?* `dist/index.html` 318,741 bytes, 32,099 gzipped (2026-09-15); one QR holds 2,953 bytes. **About 33 frames of 1,000 bytes; a loop, not a single code.**

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
1,048,576 bytes and `data/out/data_pack.json` ≤ 307,200 bytes), then `pytest -m browser`. The
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
   Rules E, F, W, I, B, UP; line length 100; `spike/` and `design/` excluded.
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
   once the layers land.
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
   (e) nearby loopback: two pages in the one browser exchange offer and answer through test
   glue (`page.evaluate`), a message sent from one appears on the other, and the pack request
   returns 96 communities; (f) the mesh-size text is at most 200 bytes UTF-8 for all 96
   communities, evaluated in one call; (g) every map layer in the pack is drawn (one `g` per
   layer id) and a carrier toggle hides and shows its group.
4. **Resources**: the Playwright browser is opened and closed by one pytest fixture; every file
   in the pipeline is opened in a `with` block; nothing starts a server, a thread or a
   subprocess except `gate.py` itself. The browser test asserts the browser object is closed at
   teardown. The nearby loopback test opens its two pages in the same fixture browser and
   never a signalling server; the spike server under `reports/` is not imported by any test.
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
  permitted exception is a QR *reader* for iPhone if OQ15 chooses one: permissive licence,
  under `app/vendor/` with its licence file, named in this section before it is added.
- Nearby chat uses `iceServers: []`, no STUN, no TURN, no signalling server; the handshake is
  two QR scans and nothing is stored. Transfer by camera carries the page's own bytes, never a
  URL that needs the internet.
- The product must not contain a model of any kind, LLM or ML. AI used in building it is declared
  in the report appendix.
- Never hardcode: the team number or `APP_URL` (`constants.md`), a colour, size or radius (tokens),
  a requirement figure (`pipeline/thresholds.csv`), a source URL, date or licence (the provenance
  registry in `pipeline/provenance.py`).
- No synthetic rows, no invented community names, exactly the 96 BushTel Major/Minor communities.
  Empty is `Not recorded`, unverified is `Unverified`, never blank.
- No BushTel free text in the pack until OQ1 is answered; presence flags with attribution only.
- Hard limits, measured by the gate: `dist/index.html` ≤ 1,048,576 bytes; `data/out/data_pack.json`
  ≤ 307,200 bytes **until OQ13** sets the new pack cap from `reports/2026-09-15-map-bytes.md`;
  the task that raises it changes the one figure in `scripts/gate.py` and this line, dated.
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
