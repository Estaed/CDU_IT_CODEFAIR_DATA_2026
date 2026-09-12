# idea-arena — research briefs, 2026-09-12

Four independent research lanes, one per candidate mechanism. Each lane sees only its own
brief. Output: notes with dated sources, **no conclusion, no recommendation**. The main loop
builds the cases and adjudicates.

Model for every lane: `opus` (context gathering with a loose brief). Agent type:
`general-purpose` (needs WebSearch, WebFetch, Write). Written to
`reports/2026-09-12-arena-<lane>.md`.

## Common preamble (prepended to every brief)

You are a research lane inside a design contest for a student data-science competition
entry. Read this brief only. Do not look for other lanes' files in `reports/`.

**Problem (do not propose a solution to it; research the mechanism you are given).**
People in the remote communities of Australia's Northern Territory, the NT Government
department that serves them (DCDD), and the mobile carriers do not reliably know how
connected each community actually is. What exists today: carriers' predicted coverage maps,
an NT Government community coverage list last updated 2022, ACMA radio licence records,
the ADII inclusion index, and anecdote. These disagree with each other and none of them
show what fails in a cyclone or the wet season. The cost: investment is ordered on guesses,
a community cannot prove its own situation, a provider can say "there is coverage there".

**Context.** CDU IT Code Fair 2026, Data Innovation Challenge, theme Remote Connectivity.
Deliverables: 8-page report, 10-minute pitch, an interactive prototype that must work
offline, Python source. Deadline 30 Sep 2026. Judges: three NT Government DCDD staff, one
CDU lecturer. Judging criteria: datasets, originality, technical sophistication,
contextual relevance/practicality, ethics, presentation. Hard constraint from the team:
**real data only** — every number must trace to a published source; no synthetic data.
Scope: NT only. The organisers' sanctioned dataset list: NT Remote Areas Mobile Coverage,
ADII dashboard, NBN dataset, ACCC Mobile Infrastructure Report data release, tropical
cyclone reports, First Nations Connectivity Mapping Tool, ACMA Site Location Map, ABS
TableBuilder, plus any other public dataset.

**Sourcing rules.** Primary sources first (the data portal, the agency, the standard). Two
independent sources for anything load-bearing. Date every finding with the day you checked
it. Where a page cannot be retrieved or a figure is not published, write
**"TBD — needs validation"** and say what would settle it; never fill the gap with a guess.
Actually try to download or at least HEAD the data files: file size, format, licence, last
updated. Record exact URLs.

**Output.** Write `reports/2026-09-12-arena-<lane>.md` in English. Structure: one section
per question below, each with numbered findings, each finding with source URL and date.
Then a section "Other facts found" and a section "TBD". **No verdict, no ranking, no
"therefore this approach is good/bad".** Stop when the questions are answered or when
you have spent the equivalent of about 40 web fetches.

---

## Lane A — `reconcile`

**Mechanism to research.** For each remote NT community, compute how many independent
published sources say it is covered: the three carriers' predicted coverage polygons
(ACCC data release, 2018–2025), the NT Government coverage lists (2019/2021/2022), and the
presence of a licensed mobile base station within N km (ACMA RRL). Disagreement between
sources is treated as a finding. Also the 2018→2025 trend per community. Hard constraint of
this lane: **only already-published official datasets; no new measurement, no user input.**

Questions:
1. ACCC Mobile Infrastructure Report data release (data.gov.au dataset
   `accc-mobile-infrastructure-report-data-release`): list the resources. For the coverage
   maps: format (KML/KMZ/other), one file per carrier per technology per year? File sizes?
   Licence? Is the geometry polygon coverage at a resolution that supports point-in-polygon
   tests for a community location, or is it coarse/rasterised? Can the NT subset be clipped
   with geopandas/shapely on a laptop? The page may return 403 to automated fetch; try
   data.gov.au API (`/api/3/action/package_show?id=...`), researchdata.edu.au mirror, and
   the ACCC's own page.
2. ACCC "mobile sites" spreadsheet(s): do they carry lat/lon per site, carrier, technology,
   and year? How many NT sites?
3. ACMA Register of Radiocommunications Licences: can mobile carrier base stations be
   isolated (licence type, client name, service category) with coordinates, from the daily
   `spectra_rrl.zip` or the RRL API? Size of the extract, licence terms, does the API need
   a key?
4. NT Government open data: the 2019 (coverage + backhaul), 2021 (3G/4G) and 2022 (remote
   areas coverage) datasets — columns, row counts, coordinates present, licence. Do the
   three share a community identifier or only names?
5. **Prior art.** Does the First Nations Connectivity Mapping Tool
   (spatial.infrastructure.gov.au) already overlay carrier coverage per community? What
   layers does it show, and does it expose an ArcGIS feature service or download? Is there
   any other published multi-source reconciled coverage view for the NT or Australia
   (ACCAN, RTIRC 2024 review, state governments, academic)?
6. Known critiques of predicted coverage maps in Australia (ACCC, ACMA, RTIRC, ACCAN,
   academic): quotes with sources on the gap between predicted and experienced coverage.

## Lane B — `measured`

**Mechanism to research.** Compare *measured* connectivity (real user speed tests, observed
cell towers, crowd-collected signal data) against *predicted* carrier coverage per NT
community, so the "lived experience vs the map" gap becomes visible. The prototype may
also collect new measurements from a phone. Hard constraint of this lane: **the approach
must bring in data that carriers and governments do not publish — measurements from the
field.**

Questions:
1. Ookla Open Data (Speedtest by Ookla Global Fixed and Mobile Network Performance Maps,
   on AWS Open Data / GitHub `teamookla/ookla-open-data`): format (Shapefile/Parquet,
   zoom-16 quadkey tiles), quarterly releases, licence (CC BY-NC 4.0?), size per quarter,
   and — critically — **how many tiles have data inside the NT outside Darwin/Alice
   Springs/Katherine**. Try to actually download one mobile quarter and count NT tiles, or
   find someone who reports NT sparsity.
2. OpenCelliD: licence, API terms, and NT density (number of cells in the NT bounding box,
   by radio type). Mozilla Location Service shut down in 2024 — confirm and note
   alternatives (Unwired Labs, beaconDB, others).
3. Other measured sources with NT data: ACMA/ACCC measurement programs (Measuring
   Broadband Australia is fixed-line; anything mobile?), nPerf, Opensignal reports for
   Australia (public? per-region?), RTIRC submissions with measurements.
4. Browser capability: can a Progressive Web App read cellular signal strength or cell id?
   (Network Information API: `effectiveType`, `downlink`, `rtt` — support on iOS Safari and
   Android Chrome as of 2026.) Can it run a lightweight speed test offline-scheduled and
   upload later? What can a native app read that a PWA cannot?
5. Prior art: apps or projects that crowdsource mobile coverage in Australia or for remote
   Indigenous communities (e.g., Telstra/Optus feedback tools, ACCAN projects, community
   mapping projects). Sources and dates.

## Lane C — `failure`

**Mechanism to research.** Model NT connectivity as a network: base stations, their
backhaul links (satellite / microwave / fibre), the communities each serves, and the
hazards that take links down (tropical cyclones, wet-season flooding, power). Then compute
which single link or site, if lost, disconnects how many people — a single-point-of-failure
and resilience analysis. Hard constraint of this lane: **the approach must model failure
and dependency, not describe current status.**

Questions:
1. Backhaul data: the NT Government 2019 dataset "Remote Communities with Mobile Coverage
   and Backhaul Transmission" — columns, does it name backhaul type per community/site, row
   count, licence, download URL. Any newer backhaul source (ACCC data release sites sheet,
   NBN, Telstra's regional fibre maps, the Regional Connectivity Program grant lists, the
   Mobile Black Spot Program site lists with coordinates and funding rounds)?
2. Tropical cyclone data: BoM Southern Hemisphere tropical cyclone database
   (`IDCKMSTM0S.csv`) — columns, licence, date range, how NT-relevant cyclones can be
   selected; also the BoM cyclone impact/report pages for Marcus (2018), Trevor (2019),
   Megan (2024) and any 2025/2026 NT cyclones.
3. Evidence that telecommunications actually fail in NT cyclones and floods, and how: ACMA
   or ACCC outage reports, Telstra/Optus statements, NT Government or ABC reports of
   communities cut off, the 2024 RTIRC final report sections on resilience, the ACMA
   telecommunications outage reporting rules (2024–2025) and whether any outage dataset is
   public.
4. Power dependency: sources on remote NT community power (Power and Water Corporation
   Indigenous Essential Services, diesel/solar), and tower battery backup durations
   (Telstra/ACMA statements, the Mobile Network Hardening Program).
5. Methods: published graph or network-resilience analyses of telecommunications
   infrastructure (academic, Australian preferred) that a student team could reproduce
   with NetworkX — cite two or three with what data they used.
6. Wet-season road closures as a proxy hazard: any historical NT road closure dataset
   (roadreport.nt.gov.au history, NT open data, BoM flood warnings history).

## Lane D — `service`

**Mechanism to research.** Measure the outcome rather than the input: for each remote NT
community, what essential digital services (telehealth video, Centrelink/myGov, school
online learning, banking) require in bandwidth and latency, versus what the community can
actually get (NBN technology available there — Sky Muster satellite, fixed wireless, fixed
line — and mobile technology). The gap per service per community is the finding. Hard
constraint of this lane: **the unit of analysis is a service a person needs, not a signal.**

Questions:
1. NBN data: which "NBN dataset" is public — nbn's rollout map API (address/locality
   lookup returning technology type), any bulk CSV of technology by locality/SA1/SA2 on
   data.gov.au or the DITRDCSA catalogue, the Sky Muster coverage footprint. Terms of use of
   the nbn address-lookup API. Can technology-by-community be obtained for ~100 NT
   communities without scraping?
2. Bandwidth and latency requirements from official or authoritative sources: telehealth
   video (RACGP, Australian Digital Health Agency, healthdirect), Services Australia/myGov,
   online learning (NT Department of Education, NT School of the Air), the ACCC's
   "Measuring Broadband Australia" definitions, Sky Muster plan speeds and data caps, the
   2024 RTIRC recommendations on service standards, the Universal Service Obligation /
   Universal Outdoor Mobile Obligation (2025–2026) definitions.
3. Service locations in the NT as open data: health clinics (NT Health, AMSANT), schools
   (NT Department of Education), Centrelink agents / Services Australia remote servicing
   points, banks/Australia Post — with coordinates.
4. ADII 2025: what geography does it publish (LGA? remoteness class?), are NT remote LGAs
   present or suppressed, is there a First Nations supplement (the 2023 "Mapping the
   Digital Gap" study with community-level data — which communities, what variables, is the
   data downloadable, licence).
5. Prior art: published service-reachability or "digital service deserts" analyses for
   remote Australia (academic, ARC Centre of Excellence for Automated Decision-Making,
   Mapping the Digital Gap, Infrastructure Australia) — what they measured and whether the
   data is reusable.
