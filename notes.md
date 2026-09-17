# Notes — raw dump, 2026-09-12

Data Innovation Challenge, theme Remote Connectivity. Brief, datasets and report format are
in `README.md` and `docs/`. This file is the pre-PRD dump; nothing here is binding.

## Team and split

- Team: Tarik, Emma, Thanh, Will (same four as FishNT). Team number: not yet known, arrives
  with registration confirmation.
- Tarik builds everything that runs: data pipeline, scores, the app, README. Emma/Thanh/Will
  own the report, slides and the pitch. Handover point: the pipeline must emit report-ready
  figures and tables, because Findings depends on them.
- Time is not the constraint (Tarik's call, 2026-09-12). Do it properly.

## The problem, as read from the brief

The brief's load-bearing sentence: connectivity gaps are "not clearly understood or
consistently represented". The gap is in the map of the network, not only the network.
Carrier maps are propagation predictions, the NT Government list is frozen in 2022, ACMA
licences say where transmitters physically are, ADII says whether people can afford and use
what exists. Nobody has put them side by side per community. Three of four judges are NTG
DCDD, the people who live with that inconsistency.

## Candidate concept (to be tested in idea-arena, not decided)

**A per-community connectivity scorecard for the 96 remote NT communities (BushTel Major +
Minor), delivered as an offline-first mobile web app.**

Per community:
- Source agreement: how many of {Telstra, Optus, TPG predicted coverage (ACCC KML 2018–2025),
  NT Government 2022 list, ACMA licensed site within N km} say "covered". Disagreement is
  itself a finding.
- Trend 2018→2025 from the ACCC yearly maps.
- Fragility: backhaul type (NT 2019 dataset), cyclone tracks within 100 km (BoM), wet-season
  road cut (BushTel road access text, 23 of 96 mention it).
- Fixed access: NBN technology (Sky Muster vs fixed wireless).
- Inclusion: ADII score for the LGA, ABS population and language.
- Output: NT-wide priority ranking and a "who does what" line per community, addressed to
  DCDD / carriers / community.

Second screen: NT map coloured by score, for the investment-ordering view.

### Alternatives the arena must weigh

1. The scorecard above (source reconciliation) — Tarik's/Eko's candidate.
2. Measured-signal app: phone logs signal strength offline, syncs later; "lived experience
   vs predicted". Strong on offline-first and originality, but no real data by the deadline;
   might survive as a "report signal here" button on the scorecard.
3. Single-point-of-failure analysis: which tower or backhaul link, if lost, disconnects how
   many communities. Network graph on ACMA sites + backhaul + cyclone exposure. High
   technical sophistication.
4. Service reachability: bandwidth needed for telehealth / Centrelink / school vs what the
   community has. Strong contextual relevance, weak data.

Arena criteria = the six published judging criteria (datasets, creativity/originality,
technical sophistication, contextual relevance/practicality, ethics, presentation) plus one
of ours: offline design quality (see below).

## Design principles for the offline part (Task 5)

Two references Tarik raised on 2026-09-12:
- **Bitchat** (Bluetooth mesh messaging, 2025): the data travels phone to phone, not through
  the network. Cheap version for us: the whole data pack is one file; share it by Web Share /
  QR / file and the receiving phone opens the same map with zero connectivity. Real BLE mesh
  is not doable in a PWA (no Web Bluetooth on iOS) — goes into Recommendations as
  "community mesh", not into the app.
- **0.facebook / Facebook Zero** (2010): text-first, kilobytes not megabytes, opens on 2G.
  Also a policy recommendation: zero-rate essential government services in remote
  communities. That lands on DCDD's desk.

## Calls already made

- **PWA, single self-contained HTML**, installable, service worker caches everything. Judges
  scan a QR, switch to flight mode, it still works. No Flutter (heavy, no instant judge
  access), no Streamlit (needs a server; a dashboard that needs a connection to explain
  where there is none is self-defeating).
- Offline map = no tiles. NT boundary + community points as embedded GeoJSON.
- Python pipeline does all fetching, joining and scoring; app ships the frozen output.
  Raw sources are frozen snapshots in the repo, never fetched at runtime (same rule as Fair
  Turn's `data/raw/PROVENANCE.md`).
- Scope: NT only. All of Australia only if NT is finished early.
- Reuse from `../AI Challenge 2026/`: BushTel community fetch (96 Major+Minor, coords,
  population, region, road access), `ntgov_communities_mobile_coverage_2021.xlsx` (CC-BY),
  road-report snapshot, `reports/2026-09-12-research-geography.md`. Copy the raw files and
  the fetch script; do not import the Fair Turn package.
- Design: three screens in Claude Design after the PRD, before generate-tasks — community
  scorecard, NT map, share/transfer. Output to `design/`, tokens read from there.
- No invented Aboriginal-sounding names anywhere; real community names are fine here because
  the whole point is the real map, but the Discussion must handle Indigenous Data Sovereignty
  (CARE principles) and "community shown as a deficit" explicitly.
- Not in v1: real-time outage feeds, crowdsourced measurements at scale, national scope,
  native app.

## Data sources verified 2026-09-12 (URLs, status)

| Source | Where | Status |
|---|---|---|
| NT Mobile Phone Coverage in Remote Areas 2022 | https://data.nt.gov.au/dataset/mobile-phone-coverage-in-remote-areas-of-the-nt | XLSX, CC Attribution, updated 2022-07-04; macro, small cell, near-macro |
| NT Remote Communities with 3G/4G Coverage 2021 | https://data.nt.gov.au/dataset/remote-communities-with-mobile-coverage | already in Fair Turn `data/raw/` |
| NT Remote Communities Coverage + Backhaul 2019 | https://data.nt.gov.au/dataset/list-of-remote-communities-with-mobile-coverage | backhaul type per site — the fragility input |
| NT Remote Sites Small Cell Coverage | https://data.nt.gov.au/dataset/groups/remote-sites-with-mobile-phone-small-cell-coverage | not fetched |
| ACCC Mobile Infrastructure Report data release | https://data.gov.au/data/dataset/accc-mobile-infrastructure-report-data-release | sites XLSX 2025 + coverage KML per carrier/tech/year 2018–2025. Page 403s to automated fetch; download in a browser. Size unknown |
| ADII 2025 | https://digitalinclusionindex.org.au/interactive-data-dashboards/ | XLSX tables, LGA level; check whether NT remote LGAs are published or suppressed |
| BoM Southern Hemisphere cyclone tracks | http://www.bom.gov.au/clim_data/IDCKMSTM0S.csv | CSV, 1907–present |
| ACMA RRL | https://www.acma.gov.au/radiocomms-licence-data | daily spectra_rrl.zip; filter NT + mobile carrier licences |
| First Nations Connectivity Mapping Tool | https://spatial.infrastructure.gov.au/portal/apps/webappviewer/index.html?id=cebfe7afe0894bd9bda06edbd65b9d17 | ArcGIS web app; check for an exposed feature service |
| NBN dataset | ? | organiser names it without a link; which product is meant is unknown |
| ABS TableBuilder / ILOC 2021 boundaries | ABS ASGS Ed. 3 | CC BY 4.0 GeoPackage |
| BushTel API | https://bushtel.nt.gov.au/api/Community | undocumented, licence TBD (attribute, do not claim CC) |

## Open questions

- Licence of BushTel and road-report data (© NTG, no licence stated). Ask opendata@nt.gov.au.
- Which "NBN dataset" the organisers mean.
- Does the First Nations Mapping Tool expose downloadable data, or only a viewer.
- ACCC KML sizes and whether NT clipping is feasible in pure Python (shapely/geopandas).
- Team number, for the report header and file name.

## Deliverables to build for (union of both official lists)

Report PDF (8 pages, Discussion = ethics, AI usage declaration in appendix), 10-min slide
deck with a 5-min cut, interactive prototype, Python source with remarks, README with
reproduction steps. Zip, email to itcodefair@cdu.edu.au, deadline 30 Sep 2026, Challenge
Day 7 Oct 2026.

## Where we are — 2026-09-12 (afternoon: spike done)

**Decision (Tarik, 2026-09-12): build the D + A combination** from
`reports/2026-09-12-arena-verdict.md` — per-community service-gap table (D, spine) with the
mobile source-agreement count (A) as one input column. Candidate concept above is superseded.

Done this session: notes dump, idea-arena (4 Opus research lanes, verdict written), and the
**20-community spike** (`reports/2026-09-12-spike-20.md`, code and table in `spike/`, three
Sonnet lanes + main loop). Kill criterion passed: publishers disagree on 31 of 96 communities.
But the fixed-access column is one colour (95/96 NBN satellite residual), so the PRD must
define capability as "best available path" (terrestrial mobile where a publisher and a licensed
site agree, satellite otherwise), not "NBN technology". Six disagreement patterns, 11
licensed-site-but-no-map communities, three town-fringe communities, and the "what link does the
clinic actually use" question are the PRD's raw material.

Also done 2026-09-12 (evening): name **Crosscheck** (Tarik); `docs/PRD.md` written (12 open
questions, 5 deferred decisions, decision log); licence email drafts in
`docs/licence-requests.md` (not sent).

Next, in order:
1. Claude Design, three screens (Community, Map, Share) per PRD §4.2, into `design/`.
2. `create-architecture` (Blueprint), then `generate-tasks`. Blueprint inherits the spike's data facts
   (ACCC Optus 4G = 1.1 M placemarks, clip once; NBN FW is Darwin-only; RRL join recipe) and the
   PRD's size bar (HTML ≤ 1 MB, data pack ≤ 300 KB).

Licence emails to send early (they gate what ships offline): Bushtel@nt.gov.au (terms),
DITRDCSA (Audit non-alignment CSV licence), BoM webreg@bom.gov.au (cyclone CSV, only if the
fragility flag is kept). The spike confirms BushTel, ACCC, ACMA, NTG and NBN all ship in the
app; BushTel is the only one without a licence.

Quota note: Codex weekly at 99 % until ~2026-09-15; Claude live quota unreadable (429). Code
bees this week are Claude-side (Opus/Sonnet), not Codex.

Reminders Eko owes Tarik (asked 2026-09-12): (1) say explicitly when it is time to open Claude
Design — after the PRD, before generate-tasks; (2) draft the three licence emails (BushTel,
DITRDCSA, BoM) as files for Tarik to send from his CDU address — the spike has now shown which
sources ship, so this is due.
