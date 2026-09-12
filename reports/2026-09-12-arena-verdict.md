# idea-arena verdict — Data Innovation Challenge 2026

Adjudicated 2026-09-12 by the main loop from four independent research lanes:
`2026-09-12-arena-reconcile.md` (A), `-measured.md` (B), `-failure.md` (C), `-service.md` (D).
Every score below cites the lane note it rests on. The user decides; this recommends.

## Problem, as fixed before research

People in remote NT communities, NTG DCDD, and the carriers do not reliably know how connected
each community is. What exists disagrees (carrier predictions, a 2022 NTG list, ACMA licences,
ADII, anecdote) and none of it shows what fails in a cyclone or the wet season. Investment is
ordered on guesses; a community cannot prove its situation; a provider can say "there is
coverage there".

## Criteria, fixed before research

1. **Datasets** — organiser-listed sources actually joined at community level, licence stated.
2. **Originality** — does published prior art already do this for the NT?
3. **Technical sophistication** — a named method beyond join-and-colour.
4. **Practicality** (tiebreak) — can DCDD act on the output without us; "who does what".
5. **Ethics** — agency vs deficit framing; Indigenous Data Sovereignty handling.
6. **Presentation** — runs live on a judge's phone.
7. **Offline design** — flight mode, phone-to-phone data pack, payload in KB.

Constraints: real data only; NT only; one builder.

## Candidates and their cases (each from its own lane only)

### A — reconcile: per-community agreement count across published coverage sources
- Plumbing confirmed by execution: ACCC 2025 Telstra 4G KML (252 MB) streamed and NT-clipped in
  93.5 s, NT = 6.3 % of vertices; ACMA `spectra_rrl.zip` (64 MB, daily, no key) joined in 11 s
  to isolate **464 NT cellular sites** (Telstra 333 / Optus 162 / TPG 81), 362 within 10 m.
  (A §1.6, §3.5)
- Disagreement is already in the raw data: ACCC says 247 NT Telstra sites, RRL says 333; the
  three NTG lists share no key, 2019 coordinates disagree with 2021/2022 by 6–16 km at Daly
  Waters and Nturiya; Jabiru vanishes after 2021. (A §3.8, §4.3)
- Licences: ACCC CC-BY 2.5; five NTG datasets CC-BY; ACMA custom licence explicitly permits
  derivatives and redistribution of derivatives. BushTel licence TBD. (A §1.2, §3.3, §4.1)
- A stable community key exists: BushTel `Id` + `Sa1Code`; the 2021 NTG sheet is a BushTel
  extract (146/146 name matches). (A §4.4)
- Weak spot the lane itself found: the ACCC guide documents two methodology breaks (Telstra 4G
  2022/23 mislabelled handheld; TPG 3G 2018/19 never re-predicted) and says year-to-year change
  "may not necessarily reflect changes" on the ground. **The 2018→2025 trend half is
  contaminated.** (A §1.9)
- Prior art: the First Nations Connectivity Mapping Tool already overlays ACCC 2024 coverage on
  BushTel communities with 34 sources; ACCC 2025 is a public queryable ArcGIS layer. Nothing
  found computes a per-community agreement count or disagreement flag. (A §5.1–5.6)

### B — measured: measured connectivity vs predicted, per community
- **National Audit of Mobile Coverage non-alignment CSV** (27 May 2026, 1.2 MB): 237 NT ~1 km
  tiles where government drive-testing found no coverage and the carrier map claims coverage
  (Telstra 210 / Optus 25 / TPG 2), 150 with no carrier explanation, concentrated in Roper
  Gulf, Barkly, Victoria Daly, MacDonnell. 10 NT static audit sites, four remote communities.
  (B §3.1.5–3.1.9)
- Ookla open data quantified first-hand via DuckDB over S3: the whole NT has 488 mobile tiles /
  1,380 tests in 2026 Q2; 64.5 % of tiles within 25 km of six towns; **11 of 50 remote
  communities have zero tiles within 5 km over 4.5 years**; remote tiles are routinely one test
  from one device. Licence CC BY-NC-SA 4.0. (B §1.1.3, §1.2)
- OpenCelliD needs a token; the only NT count is a 2020 World Bank raster (1,082 populated km²).
  MLS is dead; beaconDB dumps unavailable. (B §2)
- New measurement from a phone: Network Information API absent on iOS, values rounded to
  25 kbps / 25 ms, no cell id or RSRP in any browser; iOS has no signal API even natively.
  (B §4)
- Audit CSV licence unstated; the Audit's per-segment data is viewable, not downloadable.
  (B TBD-4, TBD-5)

### C — failure: network graph, single-point-of-failure under cyclone and power hazards
- Backhaul type per community exists: NTG 2019 XLSX, CC-BY, 64 rows, 45 fibre / 19 microwave,
  last real update 2019-05-16. **No link endpoints, no hop paths, no site IDs.** ACCC site
  files carry no backhaul column. (C §1.1)
- BoM cyclone CSV downloaded: 31,706 rows, 79 columns, 248 disturbances in an NT box, quadrant
  wind radii, current to Cyclone Narelle (March 2026). **BoM returns 403 to automated requests
  and its default terms forbid supplying content to others and scraping**; whether this CSV is
  CC BY is TBD. (C §2.1, §2.3)
- Failure evidence is specific: Cyclone Megan 2024, Telstra confirmed Borroloola and McArthur
  base stations lost power because solar could not recharge batteries; 400 fixed lines down;
  helicopter-only access; BoM flood gauges went dark because of the telecom outage. **Both
  sites are fibre-fed** — the failure was power, not backhaul. (C §3.1)
- NTG's own RTIRC submission: hardening funding "should prioritise areas … based on outage data
  analysis". RTIRC Rec 13: minimum backup power. ACMA remote threshold: 250 services / 3 h,
  natural disasters carved out. (C §3.5, §3.7)
- MNHP has per-site backup hours but only 2 NT Stage-1 sites; STAND 88 NT Sky Muster sites;
  RCP 58 NT records incl. 16 "Fibre Backhaul" completed 2023–2026 (licence TBD); MBSP 49
  unique NT sites, CC BY 4.0. (C §1.3, §1.4, §4.1, §4.2)
- Methods: Oughton et al. 2023 is asset exposure (cells × hazard), not topology; Topology Zoo
  has no Telstra/Optus graph. (C §5)

### D — service: requirement of a needed service vs capability available, per community
- **healthdirect Video Call: 350 kbps up/down and latency ≤ 100 ms. ACCC MBA measured Sky
  Muster at 664.9 ms average latency.** Sky Muster Plus Premium clears every bandwidth
  threshold and misses the telehealth latency threshold by ~6.6×. A bandwidth-only model
  would score these communities as fine. (D §2.1, §2.6, §2.7)
- NBN technology per community: 16 of 18 tested remote communities are SATELLITE; Nhulunbuy
  FTTP, Tennant Creek FTTN. Two routes: the nbn locality API (personal-use terms, not usable
  for republication) or **CC BY 4.0 fixed-line (9.4 MB) and fixed-wireless (361 MB) footprint
  shapefiles**, satellite as the residual. (D §1.3–1.8)
- BushTel per community: coordinates, ABS 2021 SA1 population with code, ~21 typed services
  (health centre, school, store, police, library, council centre, STAND site, public WiFi with
  opening hours), a visiting-services calendar. Licence TBD. (D §3.3)
- Microsoft Teams (Katherine School of the Air) minimum 150/200 kbps, recommended 2.5/4 Mbps
  for meeting video. myGov publishes no requirement. (D §2.4, §2.11)
- ADII 2025 publishes national / state / LGA / remoteness class, dashboards export XLSX;
  whether NT remote LGAs are suppressed is TBD. Mapping the Digital Gap covers five NT
  communities, PDF only, no licence — "ask first". (D §4)
- Prior art: none found joining service requirements to per-community availability. RTIRC
  Rec 6 asks for exactly this kind of tool and it is unimplemented. (D §5.7, §2.10, Other 10)

## Evidence threshold

**C's load-bearing claim has no primary source.** "Which single link, if lost, disconnects how
many people" needs link-level topology; no public dataset carries it (C §1.1.6, Other facts 1:
joining the 2019 file to ACCC sites "is an assumption, not a lookup"). C is therefore **not
scored as a graph model**. It goes into the *needs a spike* box: the claim, why it decides the
candidate, and the cheapest test — one email to the named DCDD custodian
(`officeofdigitalgovernment.DCIS@nt.gov.au`) asking whether a hop/route layer exists. What
*can* be scored from C is the reduced form: an exposure flag per community (backhaul type ×
cyclone tracks within a radius × MNHP/STAND presence), which has real data behind it.

## Rebuttal round (one round; unsourced attacks discarded)

| Attacker → target | Attack | Source | Survives? |
|---|---|---|---|
| B → A | The First Nations tool already overlays ACCC coverage on BushTel; A's overlay is prior art, and ACCC itself says year-to-year change may not be real | A §5.1–5.3, A §1.9 | **Yes.** A's trend half falls; the agreement-count half survives because no source computes it. |
| B → A | Predicted-vs-predicted agreement says nothing about reality; only measurement does, and the Audit found 237 NT tiles claimed-but-absent | B §3.1.6 | **Yes**, partially: A must present agreement as "what the publishers claim", not as truth. |
| A → B | The Audit's NT rows are road tiles, not communities, concentrated in a few LGAs; licence unstated | B §3.1.6, B TBD-4 | **Yes.** B cannot make a per-community claim from the Audit alone. |
| A → B | Ookla remote tiles are single tests from single devices; 11 of 50 communities have nothing | B §1.2.4, §1.2.7 | **Yes.** B's community-level measurement is statistically empty where it matters most. |
| C → A, D | Static status misses that a "covered", fibre-fed Borroloola went dark in Megan; NTG asks for outage-based prioritisation | C §3.1, §3.7 | **Yes.** Any status table needs a fragility column to answer DCDD's stated need. |
| A, D → C | No topology exists; Megan's failure was power at a fibre site, so backhaul type is the wrong failure mode; BoM terms block redistribution | C §1.1.6, §3.1, §2.3 | **Yes.** C's graph is dead on real data; its exposure flag must include power, not just backhaul. |
| D → A, B | Coverage presence ≠ usable service: Sky Muster clears bandwidth and fails latency 6.6×; RTIRC Rec 6 asks for service availability by area | D §2.7, §2.10 | **Yes.** A coverage-only product scores satellite-only communities as fine. |
| A → D | D's requirement side rests on one platform (healthdirect); myGov publishes nothing; nbn API is personal-use; D alone joins none of the mobile sources on the organiser's list | D §2.11, §1.4 | **Yes.** D needs A's mobile inputs and the CC-BY footprints instead of the API. |

## Scores (1–5, note cited)

| Criterion | A reconcile | B measured | C failure (exposure form) | D service |
|---|---|---|---|---|
| Datasets | **5** — NT cov ×5, ACCC, ACMA, ABS via SA1, all licensed bar BushTel (A §1–4) | 3 — Audit licence TBD, Ookla NC-SA, ACCC (B §1, §3) | 3 — NTG 2019 CC-BY, MBSP CC-BY, BoM licence blocked (C §1, §2.3) | 3 — NBN CC-BY, ADII, ABS; no mobile source (D §1, §4) |
| Originality | 2 — overlay is prior art; count is incremental (A §5) | 3 — Audit already does measured-vs-predicted nationally (B §3.1.4) | 4 — no NT resilience analysis found; RTIRC never says SPOF (C §3.7) | **4** — no prior join of requirement to availability (D §5.7) |
| Technical | 3 — spatial joins; RRL EIRP/azimuth weighting available (A Other 5) | 3 — sparse-tile statistics (B §1.2) | 2 — exposure scoring only (C §5.2) | 3 — threshold model with a latency dimension (D §2.7) |
| Practicality | 4 — refreshes DCDD's own stale list with provenance (A §4.1) | 3 — roads, not communities (B §3.1.6) | 3 — vivid, but no lever without topology (C §1.1.6) | **5** — "which communities cannot do telehealth / school"; RTIRC Rec 6 (D §2.10) |
| Ethics | 3 — neutral; deficit risk | 3 — measurement gap is an equity story; crowd data are individuals (B §1.2.4) | 3 | **4** — need-framed; WiFi hours, visiting services humanise (D Other 4–5) |
| Presentation | 4 | 3 | 4 — cyclone story lands | 4 |
| Offline design | **5** — small static table | 4 | 3 — BoM redistribution unresolved (C TBD-4) | **5** — small static table |
| **Total** | **26** | 22 | 22 (spike pending) | **28** |

Whose idea each was is not a tiebreaker and was not consulted. For the record: A was the
candidate the team walked in with.

## Verdict: a combination, D as spine, A as component

D wins on the criteria and on the tiebreak, but every surviving attack on D is answered by A,
and every surviving attack on A is answered by D. The combination satisfies the three
conditions:

1. **Each half carried its own evidence.** D: healthdirect thresholds, ACCC satellite latency,
   CC-BY NBN footprints, BushTel services. A: ACCC KML clip, ACMA RRL join, NTG lists, BushTel
   key — all executed, not inferred.
2. **One mechanism, one failure mode.** A per-community table: *services people need there*
   (from BushTel: clinic, school, store, council, STAND, WiFi) × *what each service requires*
   (sourced thresholds) × *what the community can get* (fixed: NBN technology by footprint;
   mobile: how many published sources agree it is covered). The product is the gap per
   service per community, and a fragility flag. The one failure mode: **the requirement
   thresholds are thin** — if only healthdirect and Teams can be sourced, the model rests on
   two numbers.
3. **What changed in each half.** D drops the nbn API (personal-use terms) for the CC-BY
   footprints and takes its mobile capability from A instead of having none. A drops the
   2018→2025 trend (contaminated by ACCC's documented breaks) and becomes an input column —
   "N of 4 publishers say covered" — rather than the product.

**What the app shows per community:** the services that exist there; for each, whether the
community's connectivity meets it (green / amber / red with the number that fails, e.g.
"telehealth video: latency 665 ms vs 100 ms required"); how many sources agree on mobile
coverage; a fragility flag; population affected. NT map coloured by the count of failing
services. Recommendations addressed to DCDD, carriers, and the community.

**Optional flags, gated on licence TBDs, not in the core:** the Audit non-alignment tiles
within 5 km of a community (B, if the CSV licence is open); cyclone exposure from BoM (C, if
the CSV is CC BY or a derived count is permissible).

The combination itself was never researched or attacked. Its kill criterion is fresh, below.

## Kill criteria

| Candidate | Wrong choice if… | Cheapest way to find out |
|---|---|---|
| A | The agreement count is uniform — publishers agree almost everywhere, so there is nothing to show | Point-in-polygon the 96 BushTel Major/Minor communities against ACCC 2025 + NTG 2022 + RRL-within-40-km. If < 10 % disagree, A is empty. Half a day. |
| B | The Audit CSV cannot be redistributed, or its 237 NT tiles fall > 5 km from every community | One email to DITRDCSA; one spatial join. |
| C | No hop/route topology exists anywhere; the graph cannot be built from real data | One email to the 2019 dataset custodian. If no within a week, C stays exposure-only. |
| D | No sourced requirement exists beyond healthdirect and Teams | Read the RACGP PDF and the Teams network-planner page; check the NT Education distance-learning pages. One day. |
| **Combination** | The capability table shows no variation across the 96 communities (all satellite, all "covered", all fail the same service), so the map is one colour; or DCDD judges treat service delivery as outside a connectivity brief | Build the table for 20 communities as a spike before the PRD locks screens. One day. The second half is a question for the pitch, not for us. |

## TBD — carried into the PRD as open questions, not facts

1. BushTel terms of reuse (all four lanes hit this). Email `Bushtel@nt.gov.au`; DCDD may be
   custodian.
2. National Audit non-alignment CSV licence (B TBD-4).
3. BoM cyclone CSV: CC BY or not; whether a derived per-community count may ship offline
   (C TBD-4).
4. ACARA School Location licence vs the NT School List (CC-BY) (D T15).
5. Whether NT remote LGAs are suppressed in ADII 2025 (D T12).
6. ACMA 2026 Standard thresholds verbatim, and whether standardised four-category maps are
   downloadable as a fifth source (A TBD-1, TBD-2).
7. Ookla CC BY-NC-SA: acceptable for a non-commercial competition entry, ShareAlike reach
   over a derived visualisation (B TBD-16).
8. Requirement thresholds beyond healthdirect and Teams (D T3–T5, T7–T8).
9. ACCC vs ACMA NT site-count reconciliation method (A TBD-12).

## Next step

If the combination is chosen: `create-prd` describes the per-community service-gap table as
the thing being built, with A's agreement count as one input column, and every item above as
an open question. Then the 20-community spike before screens are locked.
