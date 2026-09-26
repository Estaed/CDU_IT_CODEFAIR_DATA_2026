# Crosscheck — PRD

CDU IT Code Fair 2026, Data Innovation Challenge (theme: Remote Connectivity). Written
2026-09-12 from `notes.md`, the idea-arena verdict (`reports/2026-09-12-arena-verdict.md`), the
20-community spike (`reports/2026-09-12-spike-20.md`) and the official brief (`README.md`,
`docs/`). Says *what* and *why*; *how* is `CLAUDE.md` Blueprint, written next.

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

**Primary target, decided 2026-09-17 (Tarik, after Eko's function-by-function review).** The
first row is the product's user: the **NTG DCDD analyst** who decides where connectivity money
and verification effort go next. Three of the four judges are that person, and the brief's
stated pain is that gaps are "not consistently represented, making it difficult ... to
prioritise action and investment". Everything the app shows is judged by one test, the
**analyst's sixty seconds**: open the app with no network, see the ranked list of communities
to act on first, open one, read why it ranks there, which publisher says what, whether the
coverage claim is reliable, and copy the evidence. The nurse and the community member are the
second and third rows: they get the same row, in plain words, plus Report here. A feature that
serves none of the three rows is cut (§4.2, fourth batch).

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

- *Transfer by camera* on Screen 3: "Show" plays the whole app (gzip, about 32 KB on
  2026-09-15; 181 KB by 2026-09-16 with the map layers and jsQR, which is why the third batch
  sends a 70 KB lite copy instead) as a loop of
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

**v1 changes, third batch, decided 2026-09-16 (Tarik, after Eko's review of the phone test:
transfer stalls near 110 blocks, the map is cluttered, the community screen is seven screens
long, and the product's originality sits in "what works here and who disagrees", not in
chat).** Source of truth for each is this section; the reference screens stay the reference
for what they still show, and every departure is listed in `design/screens/README.md`.

- *Nearby chat and the Wi-Fi join QR are removed* (Task-32). `#/nearby`, `nearby.js`, the
  WebRTC channel, the pack-over-channel request and the `WIFI:` code all go; OQ14 closes as
  moot. Transfer by camera already carries the app between two phones with no network, and a
  room-range chat was the one feature a judge could call a gimmick. The 2026-09-15 spike stays
  in `reports/` as a record.
- *Report here* on Screen 1 (Task-35), the deferred D2 pulled into v1 with no network and no
  measurement: a person in the community records, on their own phone, what their phone's
  internet is doing right now (`works`, `slow`, `none`), which carrier if they know, the
  Android browser's own connection estimate where it exists (`navigator.connection`:
  `effectiveType`, `rtt`, `downlink`; absent on iPhone, then simply not recorded), the time, and
  a coarse position (two decimals, about 1 km) if they allow it. The record stays on the phone
  (IndexedDB). It leaves only when the person chooses: as one text line of at most 200 bytes,
  the same channels the mesh text already uses (copy, SMS, one static QR). Any copy of the app
  can take such lines in (paste or scan) and shows them under the published claims as a count,
  never as a verdict: "Reports from here: 3, 2 say no connection, latest 20 Sep". One tap
  copies an evidence text, the published claims and the reports for one community, addressed
  to the Mobile Black Spot Program noticeboard or a carrier. The app makes no request; the
  community's own evidence is the sixth line beside the five publishers, and the community
  decides when it travels. This is the answer to §1's "a community cannot prove its own
  situation".
- *Community screen, third pass* (Task-34): one screen at 360 × 780 before any scrolling.
  Name, type and population; the four service rows as one compact block, each a glyph, the
  service name and the verdict word; tapping a row opens its reason, assumption and sources;
  "N of M sources agree" folded to one line that opens the publisher list; two actions,
  `Report here` and `Share` (the SMS, statement and mesh texts move under Share); "What exists
  here" and "Who to ask" (the renamed "Who does what") folded. The verdict legend and the intro
  sentence of Task-30 go: the glyph and word on each row are the legend, and "does not measure
  signal" moves to the footer line.
- *Map, third pass* (Task-33): the point shapes change from circle, triangle, square and dash
  to one shape in four fill states, `●` Works (filled), `◐` Degraded (half), `○` Fails (ring),
  `◌` No data (dotted ring); the same four glyphs replace `● ▲ ■ –` in every badge and legend,
  so the map and the badges speak one language. Tarik: "üçgen kare falan sevmedim". A reader
  with no colour perception still reads fill state. A service selector above the map chooses
  which of the four verdicts colours the points (telehealth video by default); the legend
  counts follow. The carrier coverage and SA3 region layers are off by default behind one
  `Layers` control, so the default view is the outline, the five towns and the 96 points.
  Below the map, a list of the shown communities worst first (Fails, then Degraded, then No
  data, then Works), each row opening the community. Clusters stay (Task-29), restyled to the
  new shapes.
- *Transfer by camera, third version* (Task-31 experiment, Task-36 build). The v2 contract was
  tuned against 10 % frame loss; a real phone loses half or more (the reader waits 100 ms
  between reads and jsQR is slow), and at that loss the uniform 6..12 repair degree stalls
  near half of K, which is the "110" Tarik saw. Four candidates are measured on the S24 and
  the Mi 6 before anything is built: **A** the same frame with a robust-soliton degree, a
  refresh-synchronised sender and a worker-side reader; **B** four codes per frame in a 2 × 2
  grid; **C** three codes per frame multiplexed into the red, green and blue channels, our own
  design; **B+C** together. Decision rule fixed in advance: among candidates that complete 5 of
  5 runs on both phones, the shortest median time wins; ties go to the simpler one. The winner
  becomes frame prefix `CZ`, pack-independent, and the browser test's loss scenarios grow to 10,
  50 and 70 % with budgets set from the measurement. C breaks DESIGN.md's colour rule for the
  frame only: the three colours are data, not style, like the carrier layers.

Considered and dropped on 2026-09-16: a heat map (96 points on 1.35 million km² interpolate
into a surface that claims signal where nobody lives; if a surface is ever wanted it is SA3
regions coloured by the share of communities whose telehealth fails, which is honest); a ping
from the app (the community has no address to ping, the phone sits behind carrier NAT, the
browser cannot send ICMP, and a request from the app would break the one line that stays,
zero runtime requests); cimbar (needs WASM, licence unverified) and Decimen (AGPL) as transfer
libraries.

**v1 changes, fourth batch, decided 2026-09-17 (Tarik, on Eko's proposal, after the review
that found the app answers "what is here" but never "where first", that 95 of 96 verdicts rest
on one 664.9 ms figure, and that three features have no user who would press them).** Source of
truth for each is this section. Nothing here computes in the browser: every model and every
score runs in the pipeline and reaches the app as pack numbers with sources. The camera
transfer is untouched by this batch and is revisited after it (Tarik: "önce işlevli yapalım,
QR olayını sonra update ederiz").

- *Measured publisher* (Task-38): the National Audit of Mobile Coverage non-alignment tiles
  (drive tests where the government found no signal inside a carrier's claimed coverage;
  237 NT tiles, CSV of 27 May 2026) become the **fifth publisher line**, `kind: "measured"`,
  `says_covered: not-covered` where a tile lies within 5 km of the community, `not-recorded`
  where no audited road passes within that distance (the Audit drove roads, not communities;
  the line says so). The agreement count keeps counting only lines that make a claim. Licence
  unstated (OQ2): the line ships with the attribution the page carries and the report says the
  request is on file; if refused before 26 September the line is dropped from the pack and
  kept in the report as a table.
- *Map-claim reliability* (Task-39): a small supervised model, trained in the pipeline on the
  audited NT roads (positives: non-alignment tiles; negatives: audited road samples inside a
  carrier polygon with no non-alignment), with features the pack already has per community
  (distance to the nearest licensed site of the claiming carrier, depth inside the polygon,
  sites within 10 and 20 km, carriers claiming) and, if a coarse open DEM is fetched in time,
  terrain relief. Validation is a held-out split by ABS SA3 region (boundaries already in the repo), fixed before training. The output per
  community is one word, `high`, `medium` or `low`, with the probability and the two features
  that drove it, as `claim_reliability` in the pack; the app prints it as one line under the
  publishers. **Kill criterion fixed in advance:** held-out AUC under 0.65 and the model does
  not ship; the line then rests on the measured publisher alone ("drive test found no signal
  N km away"). Either way the app is complete. This is the D1 idea done with measurement rather
  than propagation; D1 stays deferred. The model runs once in the pipeline, never on the
  phone; the product still contains no model at runtime, and the report's appendix declares
  scikit-learn as the library and the Audit as the training data.
- *Priority list* (Task-40 pipeline, Task-41 app): a transparent score per community from
  weights in `pipeline/priority_weights.csv` (population, services present with the clinic
  counted twice, the telehealth and voice verdicts, claim reliability, a non-alignment tile
  within 5 km, an MBSP-funded base station within 5 km counted against, and, when the licence
  answers arrive, cyclone exposure (OQ3) and the LGA's ADII score (OQ5); an absent component
  scores zero and the table says so). Each community also gets one **intervention** from a
  rule over its pattern (`low-latency backhaul`, `verify and publish the licensed site`,
  `refresh the coverage list`, `mobile site (MBSP nomination)`, `backup power`, and since the
  evening of 2026-09-17 `verify on the ground` for a measured non-alignment within 5 km and
  `measure the link here` for a clinic whose telehealth verdict rests on the unmeasured 4G
  assumption, then `monitor`) and the addressee it goes to. A sensitivity table perturbs every weight by ±50 % and reports how
  much of the top 10 survives; the report prints it. The app gains a **fourth tab, Priority**:
  the 96 ranked worst first, each row the rank, the name, the telehealth glyph, the
  intervention; chips filter by intervention; a row opens the community, whose screen shows
  `Priority #n of 96 · <intervention>` under the sources fold. `pack_version` becomes 3 and the
  app accepts 3 only. The Recommendations section of the report is this list's top 10 with the
  evidence per row.

  **2026-09-27 decision:** the single score-first order did not answer "what to fix first":
  Nauiyu, whose voice/SMS verdict works, outranked Nitjpurru, whose voice/SMS and telehealth
  verdicts both fail. Keep the approved weights, but order by action group before score:
  `service` when either source-based service verdict is `fails`, `check` when an intervention
  other than `monitor` remains, then `monitor`. Score orders rows only within each group;
  ties retain the Task-40 rules. The pack's priority row carries `g` and the app shows three
  labelled sections with all 96 rows; the intervention chips sit in a closed `Filter by action`
  fold at compact widths' first view. "Service gap" is a source-based verdict, not a field
  measurement. The rank, report top ten and map's rank labels all follow the new order.
- *One honest sentence about LEO* (Task-40): every satellite-path telehealth verdict carries
  the assumption that a low-earth-orbit service, where a clinic has installed one, is in no
  public record (OQ10, OQ17); when a sourced LEO latency figure exists it enters
  `thresholds.csv` as a capability row and the sentence quotes it. No verdict changes until a
  per-community record exists.
- *Cuts* (Task-42): `Changes since the previous snapshot` (the pack changes only when the
  pipeline is rerun; nobody in the field presses it), the mesh-size text (no one has a
  Meshtastic radio; the report keeps the 200-byte claim as one sentence), and `Compare two
  communities` (the Priority list is the comparison an analyst wants). The freshness line,
  SMS, the statement, Report here and the transfer stay. The myGov row (96 of 96 works) stays
  in the app as a row because the table, the map selector and the evidence text carry four
  services; the pitch says plainly that "text-first services work wherever any link works" is
  the finding, not filler.

**v1 changes, fifth batch, decided 2026-09-21 (Tarik, after showing the app to non-technical
teammates: they liked the idea and could not say what the app was for, and Tarik had trouble
explaining it himself).** The goal is one test: hand the phone over with no words, ask after
ten seconds "what is this for", and three of three people answer in the sense of "the map says
there is signal; this shows whether a doctor's video call works there, and what to fix first".
Nothing here adds a feature or a verdict; it changes what is read first and in which words.
Crosscheck is a diagnosis, not a fix, and says so.

- *Home* (Task-44, Task-45): the app opens on `#/`, not on a community. One sentence
  (`Coverage maps say there is signal. Can the clinic run a video call?`), one lead line
  naming the 96 communities and the offline promise, three figures from the pack's new
  `headline` block (communities; clinics where a video call is known to work, of those with a
  clinic; communities where the sources disagree), and three buttons that are the story in
  order: `Find a community`, `What to fix first`, `See the map`. The top-bar title links here.
  No fifth tab.
- *Rows as questions* (Task-45): the service card is headed `Can people here…` and the four row
  labels are tasks (`see a doctor by video`, `join a school lesson by video`, `use myGov and
  banking`, `call and text`). The four verdict words, glyphs and colours do not change; the
  SMS, statement and evidence texts keep the formal service names.
- *One summary sentence per community* (Task-45), above the rows, assembled in the app from
  pack strings like the SMS text is: how many sources say covered, then the telehealth verdict
  in plain words with the pack's own reason. It takes the place of the `Best available path`
  note, which moves inside each row's detail, so the actions row stays inside the first
  780 px. The pack is 5 KB under its cap; 96 new sentences would not fit, and need not.
- *Inside words out of first sight* (Task-45): the tab reads `Fix first` (route unchanged);
  the sources fold reads `Do the sources agree? …`; publisher kinds read as what they are
  (`carrier's prediction`, `government list`, `licence register`, `community portal`, `drive
  test`); the reliability line reads `How far to trust the coverage map here: <word>` with the
  drivers behind it; on Share, the camera transfer sits under a closed `Update another phone
  by camera` fold.
- *The thirty-second demo* is a script in `docs/demo-script.md`, written by Eko: what stops
  when the link stops, the one sentence, three taps on Wadeye. The report and the slides use
  the same sentence.

**v1 changes, sixth batch, decided 2026-09-21 late (Tarik: "harita güzel değil, daha okunabilir
dinamik bir şey yap, önceki harita kurallarını umursamadan, tamamen özgürsün"; design by Eko).**
What was wrong, seen at 360 × 780: numbered clusters hid the points, town names sat under
markers, 58 of 96 points were the same amber half disc so the default view said nothing, and
the map ran past the screen with its legend out of sight. The map's earlier rules (zoom
clusters, filters that remove points, one colouring) are replaced by this section.

- *Three lenses* (Task-48), one segmented control, `#/map?lens=`: **Fix first** (default; point
  size by priority rank, the top ten numbered and named), **Services** (the four verdict glyphs
  for the chosen service, as before), **Sources** (agree, disagree, and the three places where a
  drive test found no signal inside claimed coverage). The map answers the same three
  questions as the home screen's three buttons.
- *No clusters.* All 96 points are always drawn. Points that overlap at rest are nudged apart
  by a pure, deterministic relaxation (layout, as clustering was) and return to their true
  place as the zoom grows.
- *Regions zoom.* Chips for `All NT` and the five regions; a tap tweens the view box to that
  region and dims the rest. *Filters highlight*: a filter dims what it excludes instead of
  removing it. Filters and coverage layers share one closed fold, `Highlight and layers`.
- *One screen.* The map's height is capped so the legend is visible under it at 360 × 780
  without scrolling; a selection card under the legend carries the community's summary
  sentence, its fix-first line, the four badges and `Open <name>`; the list below follows
  the lens. Labels carry a halo; motion respects `prefers-reduced-motion`.
- *Two fixes from the fifth batch* (Task-47, Task-48): the `degraded` summary clause now says
  why it is unproven in the pack's own words (`It could work over Telstra 4G if latency is
  under 100 ms. No measurement exists here.`) instead of quoting the satellite figure beside
  "all sources say covered"; `headline()` reads the health-centre label from a named constant.

Considered and dropped on 2026-09-21 (late): a screen that answers "can these two communities talk to each other" (Tarik's scenario). A mobile call is decided by the weaker end, which the two community screens already show; a video call between two satellite ends is a new rule (the latency adds up), and 96 × 96 pairs do not fit the pack. The scenario's one real finding goes to `docs/FINDINGS.md` instead (Task-50): 17 communities are outside everyone's mobile reach.

Considered and dropped on 2026-09-21: bringing back `Changes since the previous snapshot` as a
before/after button (no real second snapshot exists to show, and inventing one is synthetic
data; the pitch says in one sentence that a rerun after a publisher's update flips the row);
pinging named services from the app (rejected 2026-09-16, still stands); a per-service Report
here (`CR2`; the idea-arena test run of 2026-09-21 reached it independently as "task-based
capture"; it is the right next step and is written into the report's future work, not built);
renaming the verdict words to Yes / Barely / No (they are the report's and FINDINGS.md's
vocabulary, and `Degraded` here means "not proven", which the summary sentence now says).

**v1 changes, seventh batch, decided 2026-09-22 (Tarik, after reviewing current mobile app
patterns and three Crosscheck mock directions).** The app should feel like a phone tool rather
than a document while preserving the same data, routes and verdicts. The chosen direction is
the service-card treatment from direction A and the map composition from direction C.

- *Mobile shell* (Task-53): at compact widths the title and offline state stay in the top bar,
  while the four top-level destinations become a persistent bottom navigation. Each destination
  has one small monochrome inline SVG icon and its visible label: Community, Fix first, Map,
  Share. The current destination uses `aria-current="page"`; home has none selected. At wider
  widths the same links remain in the top bar. Every target remains at least the touch token.
- *Service cards* (Task-53): the four community service answers form a two-column grid of
  individual cards. Each card contains a service icon, the existing task label, and the existing
  verdict glyph and word. The icon identifies the service only; colour and the verdict glyph
  continue to carry the result. Opening a card reveals the unchanged reason, assumption,
  sources and best-path evidence across the full grid width.
- *Map composition* (Task-53): the three map lenses are navigation links with
  `aria-current="page"`. On the Services lens, its selector overlays the top of the map rather
  than consuming a separate bar and reducing the map. The service lens uses the same map height
  as the other lenses. Region chips, highlight/layer controls, the 96 points, legend, selection
  card and list keep their existing behaviour.
- Icons are authored once as small inline vector paths, need no font, image, library or request,
  and stay decorative (`aria-hidden`) beside visible text. The build and pack byte caps do not
  move.

**v1 changes, eighth batch, decided 2026-09-22 (Tarik, after testing Task-53 on the live
phone-sized app and reviewing current mobile map patterns).** This is a presentation and
interaction pass over the existing map and Report here flows; no data, verdict, route or report
line changes.

- *Brand cue* (Task-54): the top-left Crosscheck link gains a small monochrome inline check mark
  and uses the next title token so it reads as the app identity, not document body text. The
  visible word remains `Crosscheck`; the mark is decorative and introduces no image request.
- *Map controls* (Task-54): the three lenses remain equal navigation links but become one compact
  outlined segmented control with a clear selected segment. The map sits in a bounded, soft
  surface with visible zoom-in and zoom-out controls. The Services selector stays over the map
  without taking height from it, but must not span across and conceal the whole northern edge.
  All controls keep the touch-size minimum and the map remains an inline SVG with no tiles.
- *Highlight, layers and list* (Task-54): the fold names its two jobs explicitly: filters
  highlight communities and reorder the matching rows first; geographic layers change the map
  only. A list heading reports the highlighted count out of 96 and states that the rest remain
  faded. A layer toggle must not change the list count or dimming. The fold remains manually
  openable and closable, and opens when a highlight filter is active.
- *Report here* (Task-54): the action is a real toggle. A second tap closes the form and its label
  changes between `Report here` and `Close report`, with `aria-expanded` matching. Saved and
  imported evidence appears under one `Community reports` group. Copy says `Saved on this phone`
  and `Import report lines from another phone`, so creating a local report cannot be confused
  with importing one. The CR1 record, storage, evidence, SMS and QR contracts stay unchanged.
- The redesign uses only existing tokens, inline SVG geometry and the current vanilla JavaScript.
  It adds no library, map tile, request, pack field, verdict colour or new navigation route.

Considered and dropped on 2026-09-17: a restart on a different idea (13 days to submission, one
builder, the report not started; the pipeline already holds most of the inputs the priority
score needs); dropping the myGov row (touches the table, the selector, the evidence text and
the tests for one line of clarity the pitch can carry); a propagation model from ACMA site
parameters (D1; the Audit gives measured labels, which a propagation model does not).

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
| ~~Nearby chat works with no internet~~ | Struck 2026-09-16: nearby chat removed (§4.2, third batch) |
| A report stays on the phone and travels only by the person's choice | Browser test: after `Report here`, the record is in IndexedDB, no request left the page, and the exported line is at most 200 bytes UTF-8; a second page fed that line shows "Reports from here: 1" and no verdict changes (Task-35) |
| Transfer completes on a real phone | Tarik: the winner of the Task-31 sweep completes 5 of 5 runs on the S24 and the Mi 6; the browser test holds the 10, 50 and 70 % loss budgets set from that measurement (Task-36) |
| The file reaches a second phone with no network | DONE 2026-09-16, Tarik: Share on the S24 → Bluetooth → the Mi 6 received `crosscheck.html` and opened it in Chrome. Quick Share was not available on the Mi 6; Bluetooth was. The demo's guaranteed offline handoff |
| The map reads without explanation | Advisory eye review at 360 px against the layer list in §4.2, plus Tarik's own verdict on his phone; not a gate |
| Mesh-size statement fits one packet | Unit test: every community's text is ≤ 200 bytes in UTF-8 |
| Verdict rules are correct as written | Unit tests on the rule functions with hand-built rows for every pattern in the spike (unanimous yes, unanimous no, the six disagreement patterns, fixed line) |
| The 96-row table matches the spike where inputs are unchanged | Regression test against `spike/out/capability_table.csv` columns that the pipeline keeps |
| Visual fidelity to `design/` | Advisory review by eye after `design/` exists; not a gate (recorded in Blueprint) |
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

- Any measurement of signal or speed by the app. Since 2026-09-16 the app *records what the
  person says and what the Android browser already estimates* (§4.2 Report here, D2 pulled in);
  it still sends no probe, makes no request and computes no verdict from a report.
- Real-time outage feeds, road-report live data, Telstra outage pages.
- Bluetooth mesh or any peer networking beyond sharing the app file. Nearby chat was in v1
  from 2026-09-15 to 2026-09-16 and is removed (§4.2, third batch); Bluetooth, LoRa or any
  radio hardware, message storage or relay of any kind stay out.
- Map tiles, base maps fetched at runtime, or any request at all while the app runs.
- Communities outside the 96 (D3); Australia outside the NT.
- A native app, a server, a database, user accounts, analytics.
- Trend 2018→2025 from ACCC polygons (methodology breaks documented by ACCC; dropped in the verdict).
- Our own propagation model (D1). Since 2026-09-17 the pipeline trains one supervised model on
  the Audit's measured tiles (§4.2, fourth batch); propagation from site parameters stays out.
- Machine learning or LLM output computed anywhere in the product at runtime. Since 2026-09-17
  a model runs once in the pipeline and its output enters the pack as a sourced number with a
  fixed kill criterion; the app still computes nothing and ships no model.

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
14. **Does a phone hotspot let two clients talk to each other?** — CLOSED 2026-09-16 as moot:
    nearby chat removed (§4.2, third batch). The spike stays in `reports/spike-webrtc-hotspot/`.
15. **iPhone camera receive route** — ANSWERED 2026-09-15 (Tarik): vendor jsQR 1.4.0
    (Apache-2.0, pure JavaScript, 256,885 bytes, 56,970 gzipped, last release 2021-04-24) behind
    one scan adapter that prefers the browser's own reader (Task-25). The one library exception
    in the app, named in Blueprint. Rejected: zxing-wasm (maintained, MIT, but a 3.7 MB package whose
    `.wasm` would have to be inlined), qr-scanner (MIT, last release 2022, needs a separate worker
    file).
16. **Licence of the road and town source** for the map's second pass (Geoscience Australia
    or NT Government open data, expected CC BY 4.0). Research, before the map task starts.
17. **A sourced latency figure for a LEO satellite service in remote Australia** — ANSWERED
    2026-09-17 (Eko, `research`): the same ACCC Measuring Broadband Australia release that
    gives Sky Muster's 664.9 ms (release 147/24, 5 December 2024,
    <https://www.accc.gov.au/media-release/broadband-performance-of-satellite-services-measured-for-the-first-time>)
    measured **Starlink at 29.8 ms average latency across all hours** and 165.5 Mbps busy-hours
    download. Task-40 writes it as `capability,leo_satellite,latency,29.8` with that URL; the
    assumption sentence quotes it. Which communities have a LEO terminal stays unrecorded
    (OQ10). nbn's own LEO service (Amazon Kuiper, announced for mid-2026 from Tasmania) is a
    report sentence, not a figure: no ACCC measurement of it was found on 2026-09-17.
18. **Licence of the Audit's road-route layers** (the `Main_Audit_Roads` ArcGIS services the
    negatives in Task-39 sample from), beside OQ2 for the non-alignment CSV. Same email as OQ2.
    If refused, the model does not ship and the reliability line rests on the measured
    publisher alone (the Task-39 kill path).
19. **An MBSP-funded base station within 5 km** as a priority component: the MBSP
    all-funded-base-stations zip is CC BY 4.0 (`reports/2026-09-12-arena-failure.md` §4.2) and
    needs no answer; listed here so Task-40 fetches it under `pipeline/fetch/mbsp.py` and
    registers it in provenance. Not a question, a pointer; closed on fetch.

## 10. Deferred decisions (later phases; unanswered on purpose, block nothing today)

D1. **v1.1 — our own coverage model.** Terrain-aware propagation from ACMA site parameters
    (EIRP, azimuth, height, frequency) and open elevation data, added as a *modelled* publisher
    line. Started only after v1 passes its gate. Decide the model and its validation then.
    Since 2026-09-17 the *measured* half of this idea is in v1 (§4.2, fourth batch, Task-39):
    a model trained on the Audit's drive tests, not on propagation. Propagation stays D1.
D2. ~~**v1.1 — "report signal here".**~~ Pulled into v1 on 2026-09-16 as *Report here* (§4.2,
    third batch): no measurement, the person's own word plus the browser's estimate, stored on
    the phone, shared by choice as one text line. Storage is IndexedDB, consent is the tap.
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
| 2026-09-15 | jsQR 1.4.0 carries a wrong alignment table entry for QR version 23 (74 where ISO/IEC 18004 says 78), so it cannot read any version-23 code, which is exactly the size of every transfer frame. Found by the Task-25 worker, re-verified by the main loop over all 40 versions; the one entry is corrected in the vendored copy as a second recorded edit rather than shrinking frames around it | Eko |
| 2026-09-15 | Map points cluster by zoom, the one tactic taken from the AI Challenge app's map (its MapLibre tiles are not, they need the internet): nearby points merge into a bubble with a count and a ring split by telehealth verdict, split apart as the user zooms in, and a tap zooms to the cluster. Computed in the browser from the live zoom; the selected community is never inside a cluster (Task-29) | Tarik |
| 2026-09-15 | Transfer by camera: repair frames only after the first source pass, degree uniform 6..12; the loss bound is 1.75 x K (measured, 50 of 50 seeds at K 224) instead of the planned 1.5 x K, which no measured variant met. At 8 frames a second and K 224 that is about 49 seconds with 10 % of frames missed | Tarik |
| 2026-09-16 | The v2 transfer stalls on a real phone: simulated with the shipped code path at K 233, 50 % loss reaches 129 of 233 blocks by frame 700, 60 % never completes. The uniform 6..12 degree was chosen against 10 % loss only. Robust soliton completes 8 of 8 at 70 % loss in about 2 minutes where uniform completes 3 of 8 in 16. Fix is measured on phones before it is built (Task-31: A, B, C, B+C; decision rule fixed in advance), then built as frame prefix `CZ` (Task-36) | Eko's simulation, Tarik |
| 2026-09-16 | Nearby chat and the Wi-Fi join QR are removed; OQ14 closes as moot. In their place *Report here*, the deferred D2 with no network: the person's own word, the Android browser's estimate, coarse position, on the phone, shared as one 200-byte line by choice. Reason: the product's originality is "what works here, who disagrees, and the community's own evidence", not a room-range chat | Tarik, on Eko's proposal |
| 2026-09-16 | Map and badge glyphs change to one shape in four fill states (`● ◐ ○ ◌`); DESIGN.md's `● ▲ ■ –` are departed from in `design/screens/README.md`. Coverage and region layers off by default; service selector; worst-first list under the map. Heat map rejected: 96 points do not make a surface | Tarik ("üçgen kare falan sevmedim"), Eko |
| 2026-09-16 | Community screen fits one 360 × 780 screen before scrolling: four compact rows, folded sources, two actions (Report here, Share). Task-30's intro line and verdict legend are reversed by this | Tarik |
| 2026-09-16 | A ping from the app is rejected: nothing in the community has an address to ping, the browser cannot send ICMP, and it would break zero runtime requests | Tarik, on Eko's advice |
| 2026-09-16 | Codex quota is exhausted until 2026-09-19; every lane of the third batch is a Claude worker, the main loop (Fable) writes specs and runs the gate | Eko |
| 2026-09-16 (evening) | Tarik: "if the purpose is only an update, why an animated QR at all?" Eko's audit of the chain: the camera could never install the app (the receiver reassembles the frames, so it must already have Crosscheck); the lite copy and `Complete this copy` served a scenario that does not exist; the honest purpose is the **pairing-free, cross-platform data update** (Bluetooth file transfer does not exist on iPhone, AirDrop not on Android, Quick Share not on iPhone; the camera is the one channel a browser has between the two). Task-37: the frames carry the pack only (about 18 KB, K about 25, about 7 s), the lite copy, the constant and the fetch exception are withdrawn, layer rule 7 is whole again. Install stays "open the address once" or a shared file | Tarik, on Eko's proposal ("önerini yap") |
| 2026-09-16 | Round two measured on the S24: the lite copy (K 94) completes in 36 s at 5 fps and 28 s at 3.75 fps, 70 % of read frames decoded; `Open lite copy` runs online and offline. Ship 3.75 fps (Task-36). The Xiaomi Mi 6 (2017) cannot read the frames and is dropped as a reference device: the target is a current phone, and the demo uses the S24 | Tarik ("o kadar eski telefonla yapmayacağız") |
| 2026-09-16 | Transfer sweep round one failed on both phones (best 15 of 233 blocks, A/B/C/B+C, holds 4, 8, 12, laptop sender): the phone decoder is the wall. Round two is one candidate: a *lite* copy (no jsQR, no map layers, about 65 KB gzipped) at 5 frames a second, soliton repair, the v2 reader loop. The lite copy gains `Complete this copy`: on a tap, and only then, it fetches the full page from `APP_URL` and swaps itself through the received-page path — "arrives by light, grows on the first network". Layer rule 7 gets that one exception. B and C are shelved. Share sheet (Quick Share / AirDrop) is the demo's guaranteed offline handoff | Tarik ("evet onaylıyorum"), on Eko's proposal |
| 2026-09-17 | Fourth batch (§4.2). Primary target named: the DCDD analyst, judged by the "analyst's sixty seconds" (§2). Added: the Audit non-alignment tiles as a fifth, *measured* publisher; a map-claim reliability model trained in the pipeline on the Audit with an AUC 0.65 kill criterion; a transparent priority score with weights in a CSV, one intervention and one addressee per community, a sensitivity table, and a fourth tab; one LEO assumption sentence. Cut: changes since the previous snapshot, the mesh text, compare. Kept: the myGov row, the camera transfer (revisited after this batch). Rejected: a restart (13 days, one builder, no report yet) | Tarik ("evet yap, emin ol uygulamanın işlevsel olduğuna"), on Eko's proposal |
| 2026-09-17 | Task-39 fetches the Audit road routes and trains before the OQ18 licence answer, as BushTel was used before OQ1: request on file, Methodology says so; a refusal removes the model from the pack and keeps it in the report | Tarik ("evet, indir ve eğit") |
| 2026-09-17 | Transfer loss budgets become a distribution over 20 fixed seeds (median within the old budgets, worst seed within 2.5 / 3.5 / 4.5 × K, omission within 2.0 × K). Task-38's fifth publisher line pushed K from 24 to 25 and the single-seed check went red; measured, 3 of 20 seeds were already over budget at K 24, so the old check was a seed, not a property | Tarik ("dağılım ölçütü"), on Eko's proposal with the worker's measurement |
| 2026-09-17 (evening) | Task-40 measured: the pack reached 510,477 of 512,000 bytes, K 31, and the 10 % loss median read 1.65 × K against 1.6; the 10 % median budget becomes 1.8 (the one binding row; 50 % and 70 % sit at half their budgets). Two intervention rules added before `monitor`: `verify on the ground` (a drive-test non-alignment within 5 km) and `measure the link here` (a clinic whose telehealth verdict is the unmeasured 4G assumption), because 46 of 96 fell through to `monitor`, Nauiyu at rank 1 among them. The addressee lives once per intervention in a pack header | Tarik (both recommended options), on Eko's proposal with the worker's measurement |
| 2026-09-17 (evening) | Priority weights approved as written in `pipeline/priority_weights.csv` (0.20 / 0.20 / 0.20 / 0.15 / 0.10 / 0.10 / −0.10 / 0 / 0); the report prints the CSV and the sensitivity table beside it | Tarik ("tamam yap") |
| 2026-09-21 | Fifth batch (§4.2): the app opens on a home screen with one sentence, three pack figures and three buttons; service rows read as questions; one summary sentence per community assembled from pack strings; inside words renamed or folded; `Fix first` tab label. No new feature, no new verdict. Goal: the ten-second hand-over test, three of three. The before/after button, service pings, per-service reports and renamed verdict words were considered and dropped | Tarik ("hepsini yapalim"), on Eko's proposal |
| 2026-09-21 (late) | Sixth batch (§4.2): map redesigned on Tarik's free hand. Three lenses (Fix first default, Services, Sources), no clusters (deterministic declutter), region chips that zoom, filters that dim, height capped so the legend shows, a selection card with the summary sentence. Earlier map rules (Task-29 clusters, removing filters) are superseded. The `degraded` summary clause quotes the pack's assumption, not the satellite figure | Tarik ("tamamen özgürsün"), design by Eko |
| 2026-09-22 | Eighth batch (§4.2): compact segmented map lenses, bounded map surface and visible zoom controls; list explains highlight counts while layers remain map-only; Crosscheck gains a small brand mark; Report here toggles and saved/imported reports are grouped and named by origin. Research basis: Apple and Android segmented-control guidance, Mapbox collision/filter patterns and Google map visual hierarchy | Tarik ("Task 54 oluştur, sana güveniyorum"), design by Eko |
| 2026-09-27 | Fix first orders source-based service gaps, evidence checks and monitoring before the existing weighted score; the 96 remain visible in three sections. Automatic source refresh may publish only after a changed official source has been fetched completely and the pipeline and gate pass; a failed or unavailable source leaves the current pack live | Tarik ("tamam yap", "kaynakcalar update aliyorsa duzenli otomatik okey") |
