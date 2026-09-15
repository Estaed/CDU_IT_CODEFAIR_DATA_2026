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

**v1 additions, decided 2026-09-15 (Tarik, after the Task-08..10 wave).** Five features, each a
pack field plus a render, no new library, no computation of a verdict in the browser:

- *Send as SMS* and *Copy statement* on Screen 1: a short and a long plain-language text
  assembled from the pack's verdict words, reason sentences and source names, sent through the
  phone's own `sms:` handler or the clipboard. Works where only voice and SMS work.
- *Freshness line* on Screen 1: the oldest source the community's row rests on, with its date.
- *Changes since the previous snapshot* on Screen 3: the pipeline keeps every capability table
  it produces under `data/out/history/` and lists what changed between the two newest.
- *Compare two communities* at `#/compare/<id>/<id>`: the four verdicts and the agreement count
  side by side.
- *Sunlight mode*: one toggle that swaps to a higher-contrast token set exported from the design
  project; blocked until that export exists.

**v1 additions, second batch, decided 2026-09-15 (Tarik, after the research in
`reports/2026-09-15-research-offline-distribution.md` and the hotspot spike in
`reports/spike-webrtc-hotspot/`).** The direction for the last two weeks is "the app arrives
and works without the internet", not "a bigger app". Five features; none computes a verdict,
none makes a network request while running. Source of truth for each is this section until a
screen file exists; the existing three screens stay the reference for everything they already
show.

- *Transfer by camera* on Screen 3: "Show" plays the whole app (gzip, about 32 KB) as a loop of
  QR frames on this phone's screen; "Receive" on the other phone reads the frames with its
  camera, reassembles and decompresses them in the browser, opens the result and offers to
  save it. The existing URL QR stays as it is. Receiving uses the browser's own barcode reader
  where it exists (Chrome on Android); the iPhone receive route is Tarik's (OQ15).
- *Nearby chat* at `#/nearby`: two phones on the same Wi-Fi (one phone's personal hotspot, or
  any router) open a direct browser-to-browser channel by scanning each other's QR once; the
  channel stays open while both are in range and carries plain messages both ways, and the
  data pack on request. No server, no internet, no storage: nothing survives the page. Range
  is the Wi-Fi's. Proven on a home router with a Samsung S24 and a Xiaomi Mi 6 on 2026-09-15;
  the hotspot case is OQ14.
- *Wi-Fi join QR* on the same screen: the hotspot's name and password, typed once by the host,
  shown as a `WIFI:` QR the other phone's camera joins in one tap. The page cannot turn a
  hotspot on or join one itself; it can only show the code.
- *Map, second pass* on Screen 2, because the first pass is "not very understandable" (Tarik):
  pinch-zoom and pan; geographic context so the 96 points are not floating in a blank outline
  (the towns Darwin, Katherine, Tennant Creek, Alice Springs, Nhulunbuy; the Stuart, Barkly,
  Victoria and Arnhem highways; ABS region boundaries); community names as labels once zoomed
  in; the ACCC predicted-coverage polygons as a shaded layer, one toggle per carrier. All of
  it embedded as simplified vectors in the pack, no tiles, no requests. A relief base image is
  allowed only if the vectors alone still read as empty (Tarik decides after seeing them).
  Every new layer names its source and licence in the provenance file.
- *Mesh-size statement* on Screen 1: a third text beside the SMS and the statement, at most
  200 bytes, so a community's verdict fits one Meshtastic packet. The app does not talk to a
  radio; the text is pasted into the mesh app by hand. It exists to make the report's mesh
  recommendation a checked claim, not a hope.

Considered and dropped on 2026-09-15: a static "app inside one QR" (2,953 bytes per code
against 32 KB); an ESP32 captive-portal hotspot (works on both platforms, but costs money and
Tarik ruled out spending); NFC (888 bytes, Android only); a Meshtastic node pair (hardware,
money, shipping before Challenge Day); a room-range chat sold as community messaging (the
range is the honest limit and is printed in the app).

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
| Size (decided 2026-09-12; pack cap under review 2026-09-15): app HTML ≤ 1 MB, data pack ≤ 300 KB until OQ13 sets the new cap from the measured map layers | Measured by the gate on every build; over-size fails |
| Phone-to-phone transfer works | Tarik sends the app from one phone to a second phone by QR and by share sheet, opens it there in flight mode; recorded in the demo checklist. Known since 2026-09-15: an `.html` received as a file does not run on an iPhone (Quick Look has no JavaScript); the iPhone gets the app from the URL before the day |
| Transfer by camera works | Tarik plays the frames on one phone and receives on the other (Android receive; iPhone per OQ15), the received page opens and shows Wadeye's four verdicts; in the demo checklist. A unit test proves the frame set reassembles to the exact bytes of `dist/index.html` |
| Nearby chat works with no internet | Tarik: two phones on one hotspot, both in flight mode except Wi-Fi, scan, send a message each way, then switch the hotspot off and confirm the channel drops with a plain message; in the demo checklist (OQ14) |
| The map reads without explanation | Advisory eye review at 360 px against the layer list in §4.2, plus Tarik's own verdict on his phone; not a gate |
| Mesh-size statement fits one packet | Unit test: every community's text is ≤ 200 bytes in UTF-8 |
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
- ~~Bluetooth mesh or any peer networking beyond sharing the app file (recommendation only).~~
  Struck 2026-09-15: the phone's own Wi-Fi hotspot plus a browser-to-browser channel turned
  out to be free, serverless and buildable (spike 2026-09-15), so nearby chat is in v1 (§4.2).
  Still out: Bluetooth (the browser cannot form a link between two pages), LoRa or any radio
  hardware, message storage or relay of any kind, and any claim of range beyond the Wi-Fi.
- Map tiles, base maps fetched at runtime, or any request at all while the app runs.
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
13. **Pack cap after the map layers** — ANSWERED 2026-09-15 from
    `reports/2026-09-15-map-bytes.md`: tolerance 0.02 degrees for every layer (0.01 and 0.02
    are indistinguishable at phone scale); Telstra 4G, Optus 4G, MOCN 4G (shown as TPG), SA3
    regions and five towns add about 184 KB to the 260 KB pack; **cap 512,000 bytes**.
    Highways could not be downloaded by script (Geoscience Australia file is 775 MB with no
    licence stated; NT Government roads host returns 403 to scripts, CC BY on the page) and
    wait for a browser download by Tarik (Task-23).
14. **Does a phone hotspot let two clients talk to each other?** Tarik's test with
    `reports/spike-webrtc-hotspot/` on the S24 as host: CONNECTED and messages after the
    laptop server is killed means yes. If no on both phones as host, nearby chat ships with
    "works on a shared Wi-Fi router" as its stated range and the hotspot line is removed.
15. **iPhone camera receive route** — ANSWERED 2026-09-15 (Tarik): vendor jsQR 1.4.0
    (Apache-2.0, pure JavaScript, 256,885 bytes, 56,970 gzipped, last release 2021-04-24) behind
    one scan adapter that prefers the browser's own reader (Task-25). The one library exception
    in the app, named in Part 2. Rejected: zxing-wasm (maintained, MIT, but a 3.7 MB package whose
    `.wasm` would have to be inlined), qr-scanner (MIT, last release 2022, needs a separate worker
    file).
16. **Licence of the road and town source** for the map's second pass (Geoscience Australia
    or NT Government open data, expected CC BY 4.0). Research, before the map task starts.

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
| 2026-09-13 | Map filter "Clinic, no terrestrial path" uses the §5 best-available-path rule (health centre present, path is satellite): 12 of 96. The brief's 41 reproduces from nothing; 69 and 11 rejected, recorded in `design/screens/README.md` | Eko, on Tarik's instruction to decide |
| 2026-09-13 | Screen tabs stay in the top bar per DESIGN.md; the app scrolls the selected tab (and the selected filter tab) into view on load. Own nav row is a v1.1 candidate | Eko, on Tarik's instruction to decide |
| 2026-09-13 | The map is capped at `size.viewport-min-height` and centred on wide screens; points are coloured by the telehealth video verdict, the PRD's other colour-by choices are not renderable under DESIGN.md's colour rule and are dropped from v1 | Eko, on Tarik's instruction to decide |
| 2026-09-13 | The pack follows the §5 path rule where the reference screens disagree with it: Wadeye is `terrestrial_mobile` (predicted and licensed both say covered), not the `satellite` the mock's section note typed by hand. The screen text is the mock's error, not a rule | Eko, on Tarik's instruction to decide |
| 2026-09-13 | Agreement count: `available` counts only publisher lines that make a claim (`says_covered` is `covered` or `not-covered`); a `not-recorded` line is not a source that speaks. Baniyala reads 1 of 3, not the mock's 1 of 4 | Eko, on Tarik's instruction to decide |
| 2026-09-13 | The 300 KB pack limit stays. Task-00's interim pack is 288 KB because 56 source/date pairs are repeated per line; Task-05's provenance registry becomes a `sources` table in the pack header with short keys and every `source`/`date` pair on a line becomes one `src` key (measured 2026-09-13: 288,193 -> 225,841 bytes). `pack_version` stays 1 because no screen renders the pack before Task-07 | Eko, on Tarik's instruction to decide |
| 2026-09-15 | Five v1 additions (§4.2): SMS and statement text, freshness line, changes since the previous snapshot, compare route, sunlight mode. The community-card QR and the free-Wi-Fi rollout flag were considered and dropped: the first carries only text a camera reads and cannot update, the second is a promise, not a verdict | Tarik |
| 2026-09-15 | Text for SMS and the statement is assembled in the browser from pack strings; it is rendering, not a verdict, and keeps 96 paragraphs out of the 300 KB pack | Eko, on Tarik's instruction to decide |
| 2026-09-15 | BushTel and ACMA RRL snapshots re-fetched as `_2026-09-15` after the 12 September files were lost (worktree removal followed junctions); the static sets came back byte-identical | Tarik |
| 2026-09-15 | The compare route is the one two-column layout in the app, an exception to DESIGN.md's "don't split into columns"; it stacks on a 360 px phone | Eko, on Tarik's instruction to decide |
| 2026-09-15 | Direction for the final two weeks: the app arrives and works without the internet; no growth beyond the map's second pass. Second batch of v1 additions (§4.2): transfer by camera, nearby chat over the phone's own hotspot, Wi-Fi join QR, map second pass, mesh-size statement | Tarik, after `reports/2026-09-15-research-offline-distribution.md` |
| 2026-09-15 | No money: ESP32 captive portal and Meshtastic hardware rejected for the build, kept as report recommendations | Tarik |
| 2026-09-15 | Nearby chat is a live channel, not one-shot; dropped if the hotspot test fails on both phones (OQ14). The spike page connected two real phones over the home router the same day | Tarik |
| 2026-09-15 | The map may break the pack cap, DESIGN.md's colour rule (carrier layers) and the "no images" rule (relief base, only if needed); it may not make a network request. Zero runtime requests is the one line that stays | Tarik, "break a few rules if needed" |
| 2026-09-15 | The pack cap is set after the layers are measured (OQ13), not before | Eko |
| 2026-09-15 | Camera features need a secure origin: on the Samsung S24, Chrome answers `NotAllowedError` to the camera request on a copy opened from `file://` (the browser's QR reader itself is present). So Receive and the nearby scan work from the Pages address (`APP_URL`) or the installed PWA; a copy received as a file can Show frames and chat once paired, but cannot open the camera. GitHub Pages is published by `.github/workflows/pages.yml` from the committed pack; Tarik enables Pages once if the workflow cannot | Tarik's phone test, Eko |
| 2026-09-15 | OQ13 closed: tolerance 0.02, three carrier layers (Telstra, Optus, MOCN as TPG), SA3 regions, five towns; pack cap 512,000 bytes; highways deferred to Task-23 pending a browser download of the NT Government roads file | Eko, on Tarik's instruction to decide |
| 2026-09-15 | First install stays "open the address once with the internet" or "receive the file by Bluetooth / Quick Share". A single-QR bootstrap for a phone that has nothing (a tiny receiver page inside one code) is deferred until the app is finished: camera apps do not open a `data:` page from a QR, so it would rest on pasting text into the address bar, which is not reliable on stage | Tarik |
| 2026-09-15 | Received packs update the installed app in place (Task-24) | Tarik, "update atsin" |
| 2026-09-15 | OQ15 closed: jsQR vendored as the one library exception so iPhone can read QR codes (Task-25) | Tarik |
| 2026-09-15 | The app installs as a real home-screen app, following Tarik's Calisthenics app (`estaed.github.io/Calisthenics-App`): the page links its manifest, the manifest carries 192 and 512 pixel icons and theme colours, iPhone gets the Apple home-screen tags and a touch icon (Task-28). The icons are host-only files next to `dist/index.html`, generated at build from the design tokens; the single file itself stays free of images | Tarik |
