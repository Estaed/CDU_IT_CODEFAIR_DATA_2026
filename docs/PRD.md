# Crosscheck — PRD

CDU IT Code Fair 2026, Data Innovation Challenge (theme: Remote Connectivity). Written
2026-09-12 from `notes.md`, the idea-arena verdict (`reports/2026-09-12-arena-verdict.md`), the
20-community spike (`reports/2026-09-12-spike-20.md`) and the official brief (`README.md`,
`docs/`). Says *what* and *why*; *how* is `CLAUDE.md` Part 2, written next.

Team [number pending]: Tarik (pipeline, app, README, report-ready figures), Emma, Thanh, Will
(report, slides, pitch). Submission 30 September 2026; Challenge Day 7 October 2026.

## 1. Purpose

Nobody can say, community by community, what the connectivity in a remote NT community lets
people do. The sources that exist disagree with each other (carrier predictions, the NT
Government's 2022 list, ACMA's licence register, the government's own BushTel portal), and none
of them says whether a nurse can run a telehealth call. The brief names this directly:
connectivity gaps are "not clearly understood or consistently represented".

Crosscheck puts the published sources side by side for each of the 96 BushTel Major and Minor
communities, computes the best connection path each community can get, tests that path against
what each service present in the community requires, and shows where the sources disagree. It
ships as an offline-first web app, a Python pipeline with frozen source snapshots, an 8-page
report and a pitch.

Measured on 2026-09-12 (spike, all 96): the four mobile publishers agree on 65 communities and
disagree on 31; 95 of 96 sit outside every NBN terrestrial footprint; 11 communities have a
carrier-licensed mast inside the community that no coverage map shows. That is the product:
the disagreement, with the evidence attached.

## 2. Users

| User | Situation | What they get |
|---|---|---|
| NTG DCDD analyst, carrier planner | Online, in Darwin; three of four judges are this person | The comparison table for 96 communities, the six disagreement patterns, the "verify on the ground" list, and recommendations addressed to them by name |
| Clinic nurse, school, council office | In the community; "we have internet but the call freezes" | Why the service fails (the number that fails and its source), what the alternatives in the community are (public WiFi and its hours, the licensed mast), and who to ask |
| Community member, visiting worker, judge on Challenge Day | No signal, or flight mode | The same app, loaded earlier or received phone-to-phone, working with zero connectivity |

The app is not a signal test. A speed test reports a symptom; Crosscheck reports the diagnosis
with citations. The measurement button that would let a resident add "what I saw here" is v1.1
(deferred decision D2).

## 3. Scope

- **Universe (decided 2026-09-12):** the 96 BushTel Major/Minor communities, ids and coordinates
  from the BushTel snapshot. NTG 2022's additional community rows are v1.1 (D3).
- **Geography:** Northern Territory only.
- **Real data only.** Every number traces to a published dataset with a URL, a date and a
  licence. No synthetic rows, no invented names. Where a licence is unclear, the request is on
  file (`docs/licence-requests.md`) and the Methodology says so.
- **Sources in v1:** ACCC Mobile Infrastructure Report 2025 (carrier 4G/3G/5G outdoor
  polygons), ACMA Register of Radiocommunications Licences (cellular-band transmit sites),
  NT Government coverage lists 2019/2021/2022 and small-cell list, NBN fixed-line and
  fixed-wireless footprints (2024-03-26), BushTel community profiles, ABS 2021 SA1 population
  via BushTel, healthdirect and Microsoft Teams requirement pages, ACCC Measuring Broadband
  Australia satellite latency. ADII by LGA if NT remote LGAs turn out to be published (OQ5).
- **Sources that are optional flags, gated on licence answers:** BoM cyclone tracks (OQ3),
  National Audit non-alignment tiles (OQ2).
- **No AI in the product.** The pipeline is deterministic; every verdict is a rule over sourced
  numbers. AI used in building the entry (Claude, Codex) is declared in the report appendix as
  the brief requires.

## 4. What is built

### 4.1 Pipeline

Python, run once, offline after the raw snapshots are frozen in the repo. Produces:

1. **The capability table**, one row per community (see §5), as CSV and XLSX.
2. **The app data pack**, the same table reduced to what the app shows, in the smallest
   form that still carries every source citation.
3. **Report-ready outputs for the Findings section** (decided 2026-09-12): the capability
   table as CSV + XLSX; two static NT maps as PNG, one coloured by service verdict and one by
   agreement count; the disagreement pattern table with counts and the "verify on the ground"
   list with the licensed-site evidence per community; verdict counts per service with
   population affected.
4. **A provenance file** listing every raw source with URL, fetch date, size, licence and the
   attribution line it requires.

### 4.2 App

A single installable web page that works with no connectivity once opened. Three screens.
**Source of truth for every screen is this PRD, §4.2, until `design/` holds the design
system and the screen files.** The design step runs after this PRD and before tasks are
generated: `design/brief.md` is the instruction given to Claude Design, `design/DESIGN_CAL.md`
is the public design analysis it starts from; its outputs (`design/DESIGN.md`, tokens, CSS,
then the three screens) supersede the prose below once on disk, and task files are written
against them.

**Screen 1 — Community.** Search or pick a community by name or alias. Shows: name, region,
population and its source; the services present (from BushTel, degradable per OQ1); for each
service a verdict (green / amber / red) with the one-line reason that names the failing number
and the required number ("latency 665 ms vs 100 ms required, source: ACCC MBA 2024-12-05");
the best available path and how it was chosen; the four publishers' claims side by side with
their dates; the fragility flags present (wet-season road note, 2019 backhaul type); the
"who does what" line. Tapping any value shows its source and date.

**Screen 2 — Map.** The NT outline with 96 points, coloured by one of: number of services
failing, agreement count, best available path. Filters that answer the analyst's questions:
"has a clinic and no terrestrial path", "carrier says covered but government list does not",
"licensed mast but no coverage map". Tapping a point opens Screen 1. No map tiles: the outline
and points are embedded.

**Screen 3 — Share.** Shows the data pack's date and size; offers the whole app to another
phone by QR code, system share sheet or file, so the receiving phone opens the same map with
no network. Says plainly what the app does and does not claim (it does not measure signal).

### 4.3 Report, slides, pitch

Owned by Emma, Thanh and Will, built from §4.1 item 3. Structure and file rules are in
`docs/report-requirements.md`. The Discussion section is the ethics section (§7). The
Recommendations name who does what: DCDD (refresh the 2022 list from these 31 communities;
verify the 11 licensed-but-unmapped masts), carriers (extend the three town footprints by the
measured distance; publish standardised maps), community (public WiFi hours, mesh as a
recommendation not a build), and the zero-rating of government services on remote networks.

## 5. The capability row, in plain terms

What the app shows for one community; not a schema.

- **Identity:** BushTel id, name, aliases, type, NT region, coordinates, SA1 code, ABS 2021
  population.
- **Services present:** health centre, school, community store, police, library, council
  service centre, employment services, public WiFi (with hours), STAND site, aerodrome, road
  access (with the seasonal note). Each Y / N / unknown, from BushTel, with the profile date.
- **Publishers (data, not code).** One line per source that makes a coverage claim about this
  community: `publisher, kind, says_covered, detail, source, date`. `kind` is one of
  *predicted* (ACCC carrier polygon), *licensed* (ACMA site within 5 km), *listed* (NTG 2022
  list; basis macro / small cell / proximity), *portal* (BushTel "Mobile phone" row, which
  restates Telstra's map and is labelled as such). A future *modelled* kind (D1) is a new line,
  not a new screen. The **agreement count** is the number of lines saying covered, out of the
  number available.
- **Fixed access:** NBN technology by footprint (fixed line / fixed wireless / satellite
  residual) with distance to the nearest terrestrial footprint.
- **Best available path (decided 2026-09-12):** terrestrial mobile if at least one *predicted*
  line and one *licensed* line agree; satellite otherwise; fixed line/wireless where the
  footprint contains the point. The rule and its version are printed with the verdict.
- **Service verdicts:** for each service present, green / amber / red against the requirement
  table (`spike/thresholds.csv` is the seed), with the reason sentence and the sources. The
  amber rule (decided 2026-09-12): satellite-only community inside a carrier 4G polygon is
  amber, with the assumption printed: "could work over 4G if latency is under 100 ms; no
  measurement exists here".
- **Fragility:** wet-season road note (BushTel), backhaul type 2019 (NTG), optional cyclone
  count (OQ3), optional Audit tiles within 5 km (OQ2).
- **Who does what:** one sentence per addressee derived from the pattern the community falls in.

## 6. Quality bars and how each is verified

| Bar | How it is settled |
|---|---|
| Every number in the app and the report traces to a source with URL, date and licence | The provenance file lists every source; a check fails the build if a table column has no source entry |
| The table reproduces from the frozen snapshots with no network | Pipeline runs from a clean clone with networking disabled and produces byte-identical outputs |
| The app works with zero connectivity | Tarik opens the installed app in flight mode on his own phone before each demo and on Challenge Day; a named checklist per screen |
| Size (decided 2026-09-12): app HTML ≤ 1 MB, data pack ≤ 300 KB | Measured by the gate on every build; over-size fails |
| Phone-to-phone transfer works | Tarik sends the app from one phone to a second phone by QR and by share sheet, opens it there in flight mode; recorded in the demo checklist |
| Verdict rules are correct as written | Unit tests on the rule functions with hand-built rows for every pattern in the spike (unanimous yes, unanimous no, the six disagreement patterns, fixed line) |
| The 96-row table matches the spike where inputs are unchanged | Regression test against `spike/out/capability_table.csv` columns that the pipeline keeps |
| Visual fidelity to `design/` | Advisory review by eye after `design/` exists; not a gate (recorded in Part 2) |
| Report format | Emma/Thanh/Will against `docs/report-requirements.md`; not in the software gate |

## 7. Ethics, culture, community (the Discussion section's raw material)

- The data is about First Nations communities. Indigenous Data Sovereignty (CARE principles)
  is addressed explicitly: the app shows what governments and carriers publish about a
  community, attributed to them, and does not add population-level inferences of its own.
- **Framing.** A community is not shown as a deficit. The unit of failure is the service
  and the path, with the responsible party named; the community row shows what exists there
  (WiFi hours, a licensed mast, a visiting service) before what fails.
- Real community names are used because the product is the real map; no invented names.
- Predicted is not measured: every *predicted* line is labelled as a carrier prediction, and
  the amber assumption is printed rather than hidden.
- Sparse populations: population shown as the ABS SA1 figure with its caveat text from
  BushTel; no per-capita rates on communities under 100 people.
- Licences: requested where unstated (`docs/licence-requests.md`); BushTel prose is dropped
  from the app if permission is refused (OQ1), presence flags stay with attribution.

## 8. Out of scope (v1)

- Any measurement of signal or speed by the app; crowdsourced data (D2).
- Real-time outage feeds, road-report live data, Telstra outage pages.
- Bluetooth mesh or any peer networking beyond sharing the app file (recommendation only).
- Communities outside the 96 (D3); Australia outside the NT.
- A native app, a server, a database, user accounts, analytics.
- Trend 2018→2025 from ACCC polygons (methodology breaks documented by ACCC; dropped in the verdict).
- Our own propagation model (D1).
- Machine learning or LLM output anywhere in the product.

## 9. Open questions (numbered; never renumber — task files reference these)

1. **BushTel terms of reuse.** Email drafted; until answered, the app ships presence flags
   with attribution and no BushTel free text. Decision needed if refused: keep flags under
   fair dealing with a stated notice, or replace the services layer with open lists.
2. **National Audit non-alignment CSV licence.** Optional column; drop if unanswered by 26 Sep.
3. **BoM cyclone CSV licence and whether a derived per-community count may ship.** Optional
   flag; drop if unanswered by 26 Sep.
4. **ACARA School Location licence vs the NT school list (CC-BY)** — only matters if BushTel's
   school flag is lost (OQ1).
5. **Whether NT remote LGAs are published or suppressed in ADII 2025.** Decides whether an
   inclusion column exists.
6. **ACMA 2026 Standard thresholds verbatim; whether standardised maps are downloadable** as a
   further *predicted* publisher.
7. **Ookla CC BY-NC-SA** — acceptable for this entry; ShareAlike reach. Only if a measured
   column is added.
8. **Requirement thresholds beyond healthdirect and Teams** (RACGP, ADHA, NT Education, myGov).
   Teams latency figure is still TBD.
9. **ACCC vs ACMA NT site-count reconciliation** (247 vs 333 Telstra sites) — Methodology text.
10. **What link does the clinic actually use?** NBN satellite residual describes consumer
    premises; NT health and education sites may sit on government WAN links (30 of 96
    communities have fibre backhaul in the 2019 list). Ask DCDD whether a per-community WAN
    technology list exists. Until answered, verdicts are computed on the best *public* path and
    the report says so.
11. **A sourced latency figure for 4G and for NBN fixed wireless.** Needed to turn the amber
    assumption into a rule; ACCC MBA reports are the likely source.
12. **Team number** — ANSWERED 2026-09-12: **DIC005**. Held in `constants.md`; header, footer
    and file name read it from there. (The sibling AI Challenge entry is AIC014, not this one.)

## 10. Deferred decisions (later phases; unanswered on purpose, block nothing today)

D1. **v1.1 — our own coverage model.** Terrain-aware propagation from ACMA site parameters
    (EIRP, azimuth, height, frequency) and open elevation data, added as a *modelled* publisher
    line. Started only after v1 passes its gate. Decide the model and its validation then.
D2. **v1.1 — "report signal here".** A measurement recorded offline, synced later, shown as a
    sixth line beside the published claims. Decide storage and consent then.
D3. **v1.1 — widen the universe** to NTG 2022's community rows and BushTel Town Camps.
D4. **Road-note extraction with an LLM, human-verified**, replacing the regex seasonal flag.
    Declared in the appendix if done. Not in v1.
D5. **National scope** — only if the NT is finished early; the brief allows it.

## 11. Decision log

| Date | Decision | Where it came from |
|---|---|---|
| 2026-09-12 | D + A combination: service-gap table as spine, agreement count as a column | arena verdict |
| 2026-09-12 | Name: Crosscheck | Tarik |
| 2026-09-12 | Team number DIC005; entrant Tarik Bulut, tarik.bulut@cdu.edu.au | Tarik |
| 2026-09-12 | Capability is "best available path", not NBN technology | spike: 95/96 satellite residual |
| 2026-09-12 | Publishers are data with a `kind`, so a modelled publisher is additive | Tarik, on the upgrade path |
| 2026-09-12 | ACMA "licensed" publisher defined at 5 km, not 40 km | spike: 40 km is true for 96/96 |
| 2026-09-12 | Universe = 96 BushTel Major/Minor | Tarik |
| 2026-09-12 | Size bar ≤ 1 MB HTML, ≤ 300 KB data pack; Tarik checks flight mode on his phone | Tarik |
| 2026-09-12 | Amber with the printed assumption, not grey, not green | Tarik |
| 2026-09-12 | No AI in the product; declared in the process | Tarik |
| 2026-09-12 | PWA, single HTML, no tiles, no server; Python pipeline; NT only | notes.md "Calls already made" |
