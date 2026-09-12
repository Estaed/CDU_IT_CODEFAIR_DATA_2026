# Arena research — lane B ("measured"): measured connectivity vs predicted carrier coverage, NT

**Date of research: 2026-09-12.** All "checked" dates below are 2026-09-12 unless stated.
Scope: Northern Territory. Mechanism researched, not judged — no verdict or ranking appears
in this document, by instruction.

**Method note.** Where a figure is marked *(computed)* it was produced in this session by
querying the live source, not read from a secondary report. The commands are described
inline so they can be re-run. Temporary working files were written under `reports/tmp/`
and deleted afterwards.

**Bounding box used for "NT" throughout:** lon 129–138, lat −26 to −10. This is the NT's
rectangular border approximation; it includes ocean and small slivers of WA/SA/QLD at the
corners, and excludes nothing of the NT mainland. Counts below are therefore slight
over-counts of the true NT, not under-counts.

**Six "main towns" used as the distance reference throughout** (Darwin −12.4634/130.8456,
Palmerston −12.4861/130.9833, Katherine −14.4652/132.2635, Tennant Creek −19.6486/134.1893,
Alice Springs −23.6980/133.8807, Nhulunbuy −12.1806/136.7786).

---

## 1. Ookla Open Data — format, licence, size, and NT sparsity

### 1.1 Format, cadence, access

**1.1.1 Two formats: Shapefile and Apache Parquet, geometry as WKT in EPSG:4326, aggregated
to zoom-16 Web Mercator tiles (~610.8 m × 610.8 m at the equator).** Quadkeys are the tile
identifier and are stable across quarters, which is what makes a time series possible.
Source: <https://github.com/teamookla/ookla-open-data> — checked 2026-09-12.

**1.1.2 Quarterly, from 2019 Q1 to the most recently completed quarter.** As of
2026-09-12 the newest published mobile quarter is **2026 Q2**. *(computed — S3 bucket
listing, see 1.1.4.)*

**1.1.3 Licence is CC BY-NC-SA 4.0, not CC BY-NC 4.0.** Two independent sources agree:
the repo README (<https://github.com/teamookla/ookla-open-data>) and the AWS Registry of
Open Data entry (<https://registry.opendata.aws/speedtest-global-performance/>), both
checked 2026-09-12. The registry links
<https://creativecommons.org/licenses/by-nc-sa/4.0/>. The two live obligations are
**NonCommercial** and **ShareAlike** (any adaptation redistributes under the same licence);
attribution wording is suggested in the README and asks for the access date and the time
period analysed.

**1.1.4 S3 access is anonymous, bucket `ookla-open-data`, region `us-west-2`, Requester
Pays = No.** Source: AWS Registry entry, checked 2026-09-12. URL pattern *(computed and
verified live)*:

```
https://ookla-open-data.s3.amazonaws.com/parquet/performance/type={mobile|fixed}/year={YYYY}/quarter={Q}/{YYYY}-{MM}-01_performance_{type}_tiles.parquet
```
where `MM` ∈ {01, 04, 07, 10}. Plain unauthenticated HTTPS GET works; so does
`?list-type=2&prefix=...` for listing.

**1.1.5 File sizes, from live HTTP HEAD / bucket listing** *(computed, 2026-09-12)*:

| File | Bytes | Last-Modified |
|---|---|---|
| mobile 2026 Q2 parquet | 184,560,046 (≈176 MiB) | 2026-08-19 |
| mobile 2026 Q2 shapefile zip | 185,168,307 (≈177 MiB) | 2026-08-19 |
| mobile 2026 Q1 parquet | 175,330,099 (≈167 MiB) | 2026-04-13 |
| mobile 2025 Q4 parquet | 182,319,554 (≈174 MiB) | 2026-01-03 |
| fixed 2025 Q4 parquet | 363,645,901 (≈347 MiB) | 2026-01-03 |

So a *mobile* quarter is ~175–185 MB, not multi-gigabyte. The fixed set is roughly double.

**1.1.6 Schema (mobile 2026 Q2, read live via DuckDB `DESCRIBE`)** *(computed)*:
`quadkey VARCHAR, tile VARCHAR (WKT), tile_x DOUBLE, tile_y DOUBLE, avg_d_kbps BIGINT,
avg_u_kbps BIGINT, avg_lat_ms BIGINT, avg_lat_down_ms DOUBLE, avg_lat_up_ms DOUBLE,
tests BIGINT, devices BIGINT, quarter BIGINT, type VARCHAR, year BIGINT`.
`tile_x`/`tile_y` are the tile centroid in degrees — meaning **a bounding-box filter needs
no geometry parsing at all**, just two numeric predicates.

**1.1.7 The whole file need not be downloaded.** DuckDB `httpfs` reading the S3 URL
directly with a `tile_x`/`tile_y` predicate returned the global row count in 2.7 s and the
full NT extract in ~14 s over a domestic connection *(computed)*. Global mobile rows for
2026 Q2: **3,381,216**. This makes the "it is large" concern largely moot for an NT-scoped
project.

**1.1.8 `tile_x`/`tile_y` are present back to at least 2020 Q2 but NOT in 2019 Q1**
*(computed — a `tile_x` predicate against the 2019 Q1 file raised `Binder Error:
Referenced column "tile_x" not found`).* The README describes them as added in Q3 2023;
in practice earlier files have been backfilled, with 2019 Q1 the exception found. Anything
touching 2019 Q1 must parse the `tile` WKT instead.

**1.1.9 No minimum-test suppression threshold is applied.** *(computed — `min(tests) = 1`
in every region queried, including Sydney.)* The README states only that measurements are
"filtered to results containing GPS-quality location accuracy"; it states no minimum test
or device count for a tile to be published. Confirmed by reading the raw README at
<https://raw.githubusercontent.com/teamookla/ookla-open-data/master/README.md> — checked
2026-09-12. **Consequence: a published tile can rest on a single test from a single
device**, and in remote NT most do (see 1.2.3).

**1.1.10 A 2026 changelog note in the README warns that "supported regions have been
updated. Users may notice that certain geographic areas are no longer available."**
Checked 2026-09-12. Australia is still present (see 1.2.4), so this did not remove
Australia, but it is a live source of discontinuity in any long time series.

### 1.2 NT sparsity — the numbers

**1.2.1 NT-bbox totals, mobile 2026 Q2** *(computed)*: **488 tiles, 1,380 tests, 762
devices** for the entire Territory in a whole quarter. Fixed for the same quarter: 1,318
tiles, 11,470 tests, 4,015 devices.

**1.2.2 Scale comparison, same quarter, same query** *(computed)*:

| Region | Mobile tiles | Mobile tests | max tests in one tile |
|---|---|---|---|
| Sydney bbox (150.5–151.5 E, −34.2 to −33.5) | 5,290 | 33,298 | 562 |
| Australia bbox (112–154 E, −44 to −9) | 43,136 | 179,020 | 1,830 |
| NT bbox | 488 | 1,380 | 105 |

The NT is ~17.5% of Australia's land area and holds **1.13%** of its Ookla mobile tiles.
A single Sydney bounding box has ~11× the NT's tile count.

**1.2.3 Tiles by distance from the six main towns, mobile 2026 Q2** *(computed)*:

| Distance to nearest main town | Tiles | Share | Tests | Devices |
|---|---|---|---|---|
| 0–25 km | 315 | 64.5% | 1,116 | 553 |
| 25–50 km | 19 | 3.9% | 26 | 20 |
| 50–100 km | 41 | 8.4% | 53 | 43 |
| 100–250 km | 91 | 18.6% | 134 | 107 |
| >250 km | 22 | 4.5% | 51 | 39 |
| **Total** | **488** | | **1,380** | **762** |

**Two-thirds of NT tiles, and 81% of NT tests, sit within 25 km of Darwin, Palmerston,
Katherine, Tennant Creek, Alice Springs or Nhulunbuy.** Beyond 50 km there are 154 tiles
carrying 238 tests between them — about 1.5 tests per tile.

**1.2.4 The far tiles are overwhelmingly single-test, single-device** *(computed)*. The 15
most remote NT tiles in 2026 Q2 all have `tests` of 1–5 and `devices` of 1–4. Example rows
(distance km, lat, lon, avg_d_kbps, tests, devices):

```
453  -20.5222  129.9545   16,671   1  1
435  -16.0696  136.3046  100,075   1  1
415  -20.5531  130.3336  375,878   2  1
411  -16.4335  136.1069   11,895   1  1
409  -16.4387  136.0739  180,956   1  1
```

Note the adjacent pair at −16.43/136.10 and −16.44/136.07 (near Borroloola): 11.9 Mbps and
181 Mbps, one test each, ~3.5 km apart. A tile value in remote NT is one person's one test,
carrying that test's full variance.

**1.2.5 NT coverage over time — flat, not growing** *(computed, mobile, one query per
quarter)*:

| Quarter | NT tiles | NT tests | AU tiles | NT % of AU |
|---|---|---|---|---|
| 2019 Q1 | n/a (no `tile_x`) | — | — | — |
| 2020 Q2 | 314 | 1,138 | 53,870 | 0.58% |
| 2021 Q2 | 365 | 1,234 | 54,866 | 0.67% |
| 2022 Q2 | 611 | 2,390 | 53,019 | 1.15% |
| 2023 Q2 | 520 | 1,707 | 48,330 | 1.08% |
| 2024 Q2 | 504 | 1,605 | 48,642 | 1.04% |
| 2025 Q2 | 436 | 1,493 | 42,009 | 1.04% |
| 2025 Q4 | 312 | 936 | 43,523 | 0.72% |
| 2026 Q1 | 327 | 859 | 42,643 | 0.77% |
| 2026 Q2 | 488 | 1,380 | 43,136 | 1.13% |

NT peaked in 2022 Q2 and has not grown since. Australia-wide tile counts have fallen ~20%
since 2020. Quarter-to-quarter NT variation is large (312 → 488 between 2025 Q4 and 2026
Q2) relative to the absolute numbers.

**1.2.6 Pooling 18 quarters (2022 Q1 – 2026 Q2) gives 2,317 distinct NT quadkeys**
from 8,374 tile-quarter rows, 26,558 tests and 15,466 devices in total *(computed)*. That
is the entire measured mobile footprint of the NT in Ookla's open data over four and a half
years.

**1.2.7 Community-level coverage from that 18-quarter pool** *(computed)*. Tested against
a list of 50 NT remote communities (coordinates approximate — see TBD-1):

- **11 of 50 communities have ZERO Ookla mobile tiles within 5 km across all 18 quarters**:
  Amanbidji, Areyonga, Haasts Bluff, Jilkminggan, Minyerri, Nyirripi, Palumpa, Pigeon Hole,
  Robinson River, Utopia, Wutunugurra.
- **39 of 50** have at least one tile within 5 km.
- **13 of 50** have ≥30 tests within 5 km pooled over 4.5 years (i.e. enough for any
  statistical weight at all).
- **18 of 50** have data in ≥8 of the 18 quarters (i.e. a time series is possible).

Selected rows (tiles ≤2 km / tiles ≤5 km / tests ≤5 km / quarters with any data, out of 18):

| Community | ≤2 km | ≤5 km | tests ≤5 km | quarters |
|---|---|---|---|---|
| Wadeye | 7 | 8 | 60 | 10 |
| Maningrida | 7 | 7 | 54 | 12 |
| Galiwinku | 6 | 7 | 80 | 15 |
| Daly River | 5 | 15 | 71 | 12 |
| Ngukurr | 4 | 4 | 70 | 9 |
| Borroloola | 4 | 4 | 36 | 10 |
| Yuendumu | 4 | 4 | 10 | 7 |
| Lajamanu | 3 | 3 | 26 | 8 |
| Barunga | 1 | 1 | 1 | 1 |
| Willowra | 0 | 1 | 1 | 1 |
| Beswick | 0 | 3 | 4 | 3 |
| Areyonga | 0 | 0 | 0 | 0 |
| Utopia | 0 | 0 | 0 | 0 |

**1.2.8 No published report of NT/remote Ookla sparsity was located.** The README carries
no sparsity note (1.1.10 is about region availability, not density). The numbers above are
first-hand from the data rather than cited from a secondary source.

---

## 2. OpenCelliD, Mozilla Location Service, and alternatives

**2.1 OpenCelliD licence is CC BY-SA 4.0.** Sources: OpenCelliD wiki
(<https://wiki.opencellid.org/wiki/Licensing:> returned HTTP 404 on direct fetch on
2026-09-12; the licence statement is reproduced on the Wikipedia article
<https://en.wikipedia.org/wiki/OpenCelliD> and on the downloads page) and the downloads
page <https://www.opencellid.org/downloads.php> — checked 2026-09-12. Attribution
requirement: products or services using derived data must visibly credit "OpenCelliD" with
a link to <https://opencellid.org/>; exceptions are granted by Unwired Labs commercially.
Note **ShareAlike, not NonCommercial** — the opposite trade-off to Ookla.

**2.2 Downloads require an API Access Token.** The downloads page states verbatim: "To see
the download links, please enter your API Access Token." Checked 2026-09-12. An
unauthenticated API call was made in this session and returned
`<rsp stat="fail"><err info="API Key not known: " code="2"/></rsp>` *(computed)* —
confirming no anonymous access path.

**2.3 Country exports are limited to the last 18 months of observations.** Verbatim from
the downloads page: "We limit the data to the last 18 months for several reasons: To avoid
overwhelming our servers and bandwidth limits, To keep file sizes manageable for downloads,
Cell tower configurations change over time, and older data may no longer be accurate."
Checked 2026-09-12. Format is CSV; the schema is on a separate "Database Format
Documentation" page. See TBD-2 for what is unresolved.

**2.4 Australia-wide cell counts, by radio type, from the OpenCelliD public statistics
page** — no token needed *(computed — fetched and parsed
<https://opencellid.org/stats.php>, 2026-09-12)*. Columns confirmed from the table header
as Country / Total Cells / GSM / CDMA / UMTS / LTE / (sixth column, NR):

| Country | Total | GSM | CDMA | UMTS | LTE | NR |
|---|---|---|---|---|---|---|
| Australia | 758,604 | 50,988 | 0 | 296,461 | 404,574 | 6,581 |
| New Zealand | 111,626 | 13,672 | 0 | 63,638 | 34,316 | 0 |
| Canada | 1,064,596 | 145,902 | 8,622 | 439,897 | 469,144 | 1,031 |
| United States | 8,128,968 | 293,821 | 604,579 | 1,642,486 | 5,404,757 | 183,325 |

Australia's UMTS (3G) count of 296,461 is 39% of the national total despite Telstra's and
Optus's 3G shutdowns — the database retains historical records. Only 6,581 NR (5G) cells
are recorded nationally.

**The statistics page does not break Australia down by state or territory**, so this does
not directly answer "how many cells in the NT".

**2.5 An NT cell count was obtained from an independent OpenCelliD derivative: the World
Bank's "Global OpenCellID cell tower map"**, a 1 km global raster of tower counts derived
from an OpenCelliD snapshot dated **2020-07-01**, licensed **CC BY 4.0**, 890.1 MB GeoTIFF,
directly downloadable without registration at
<https://datacatalogfiles.worldbank.org/ddh-published/0038043/1/DR0046250/opencellid_global_1km_int.tif>
(catalogue page <https://datacatalog.worldbank.org/search/dataset/0038043/global-opencellid-cell-tower-map>)
— checked 2026-09-12. Read via a `/vsicurl` windowed read so only the NT rows were
transferred *(computed)*:

| Region | Populated 1 km pixels | Summed cell records |
|---|---|---|
| NT bbox | **1,082** | **3,603** |
| Australia bbox | 90,171 | ≥490,630 (understated — see caveat) |

**Caveat that matters:** the raster dtype is `uint8`, so any 1 km pixel with more than 255
cells is clipped at 255. The NT maximum is 97, so **the NT figures are unclipped and
reliable**; the Australia total is clipped and is a floor, not a count.

**2.6 OpenCelliD NT density by distance from the six main towns** *(computed, same raster)*:

| Distance to nearest main town | Populated 1 km pixels | Share | Cell records |
|---|---|---|---|
| 0–25 km | 659 | 60.9% | 3,063 |
| 25–50 km | 100 | 9.2% | 117 |
| 50–100 km | 83 | 7.7% | 99 |
| 100–250 km | 154 | 14.2% | 197 |
| >250 km | 86 | 7.9% | 127 |

The same shape as Ookla: 60.9% of populated pixels and **85% of the cell records** are
within 25 km of the six towns. Across the whole Territory, 1,082 populated square
kilometres. Snapshot is 2020 and therefore pre-dates the 3G shutdowns and most 5G rollout.

**2.7 Mozilla Location Service was retired in 2024 — confirmed.** MLS ran 2013–2024; in
March 2024 Mozilla announced retirement, with functionality reduced in stages and the
project archived in July 2024. Two contributing reasons are on the record: declining
accuracy with no plan to restart the stumbler programme, and a 2019 patent claim by Skyhook
Holdings whose settlement made further investment difficult. Sources:
<https://en.wikipedia.org/wiki/Mozilla_Location_Service> and
<https://github.com/mozilla/ichnaea/issues/2065> — checked 2026-09-12.

**2.8 beaconDB is the named MLS successor, and its data dumps are NOT yet available.**
Live site statistics on 2026-09-12: 140,632,148 networks, 4,789,437 beacons, **6,799,537
towers**, 217 countries. The site states verbatim: "data dumps currently aren't available
as I'm still working on obfuscating the data to protect the privacy of contributors and AP
owners" — they are intended to be published "under a public domain license" when ready.
*(computed — `https://beacondb.net/dumps/` and `/api/dumps` both returned HTTP 404 on
2026-09-12.)* A geolocate API exists at `https://api.beacondb.net/v1/geolocate` with **no
API key required** (a User-Agent must be set) and uses the same request format as MLS.
Contribution is via NeoStumbler, Tower Collector or Network Survey (all Android; Tower
Collector uploads to beaconDB by default in recent versions). Source:
<https://beacondb.net/> and <https://github.com/beacondb/beacondb> — checked 2026-09-12.
**No per-country or per-region breakdown is published**, so beaconDB's NT density is
unknown (TBD-3).

**2.9 radiocells.org appears defunct.** *(computed)* `https://radiocells.org/` returns
HTTP 200 with a 93-byte empty HTML document
(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>-</title></head><body></body></html>`);
`https://radiocells.org/license` and `/default/download` both return HTTP 404. Checked
2026-09-12.

**2.10 Unwired Labs is the commercial owner of OpenCelliD** and sells geolocation API
access; the OpenCelliD community data is the free tier of that business. OpenCelliD reports
more than 49,000 registered contributors and "more than 1 million new measurements every
day on average". Sources: <https://opencellid.org/about.php>,
<https://en.wikipedia.org/wiki/OpenCelliD> — checked 2026-09-12.

---

## 3. Other measured sources with NT data

### 3.1 The National Audit of Mobile Coverage (Australian Government / Accenture) — the
### single largest measured NT source, and it already performs the measured-vs-predicted comparison

**3.1.1 What it is.** Accenture Australia, engaged by the Department of Infrastructure,
Transport, Regional Development, Communications, Sport and the Arts, delivering the Audit
annually for three years **until 30 June 2027**, under the Better Connectivity Plan for
Regional and Rural Australia. Stated objective, verbatim: "to better identify mobile
coverage black spots across Australia to help target future investment, and to provide an
independent resource that better reflects on the ground experiences of mobile services
provided commercially by Mobile Network Operators (MNOs) Optus, Telstra and TPG."
Source: *National Audit of Mobile Coverage — Audit Methodology Fact Sheet, October 2025*,
<https://www.infrastructure.gov.au/sites/default/files/documents/national-audit-of-mobile-coverage-methodology-fact-sheet-october2025.pdf>
(18 pp., 939,075 bytes, downloaded and text-extracted in this session) — checked
2026-09-12. Second source: programme page
<https://www.infrastructure.gov.au/media-communications-arts/better-connectivity-plan-regional-and-rural-australia/national-audit-mobile-coverage>.

**3.1.2 Three modules.**
- **Module A — Pilot Audit (2024):** ~35,000 km of major roads plus selected static sites.
  Data available now.
- **Module B — Main Audit (from late 2024):** **186,984 km per year for 3 years** of drive
  testing, focused on regional and rural areas, using Accenture vehicles and some Australia
  Post vehicles. Plus **77 fixed static locations** ("Audit Towns"), predominantly Australia
  Post local post offices, with alternatives such as rural fire service buildings where
  there is no post office. **Data is published monthly.**
- **Module C — Crowd-sourced data** collected by an Accenture SDK embedded in consenting
  third-party mobile apps. **Released quarterly.** The programme materials cite roughly
  160,000 active users in Australia at any one time and about 3.5 billion samples annually.

**3.1.3 Hardware and metrics.** Off-the-shelf **Samsung S23+** handsets, one probe per MNO
per vehicle, running **Nemo Handy**; three probes mounted on the vehicle rear window
(Accenture vehicles) or in the passenger footwell / rear cargo compartment (Australia Post
vehicles). Metrics: RSRP (signal strength/coverage), uplink and downlink throughput,
latency, voice quality, SMS success rate, call setup failure, dropped call; derived user-
experience metrics for web browsing, SD and HD video streaming, eGaming, teleconference
voice, teleconference voice+video; and Audit-Towns-only Call Success Rate and Stability
Rate. Coverage is banded as Acceptable / Modest / Limited / No Service. 3G (while
available), 4G and 5G.

**3.1.4 The Audit explicitly compares measured against predicted, and publishes the gap.**
Verbatim from the fact sheet: "The data collected via these 3 methods can be compared to
MNO coverage map data, which is provided via the Australian Competition and Consumer
Commission (ACCC) annually and is published alongside Audit data on the visualisation tool."
Road segments where measured RSRP does not match the MNO coverage map are classified
**"non-aligned"**. Verbatim on why variance arises: physical obstruction and interference;
network development not yet reflected in maps (updated once per year); planned or unplanned
outages; cell saturation; and — listed explicitly — "MNO coverage maps not accurately
predicting real-world mobile coverage."

**3.1.5 The non-alignment data is published as a downloadable CSV.**
<https://www.infrastructure.gov.au/sites/default/files/documents/national_audit_of_mobile_coverage_non-alignment_data_may_2026.csv>
— **1,205,924 bytes, date published 27 May 2026**, downloaded in this session, HTTP 200,
`application/octet-stream`. Linked from
<https://www.infrastructure.gov.au/media-communications/better-connectivity-plan-regional-and-rural-australia/national-audit-mobile-coverage/national-audit-mobile-coverage-mobile-coverage-non-alignments>
— checked 2026-09-12. Columns: `WKT, fid, Tile Id, MNO, State, LGA, Audit Data, MNO
Predicted Coverage, MNO Feedback on non-alignment, Further Details, Year, Day, Month, Batch
Item`. Geometry is a ~0.009° (~1 km) MULTIPOLYGON tile per row. **3,062 data rows** (the
header is repeated as row 1 — a parsing trap).

**3.1.6 NT content of the non-alignment CSV** *(computed)*:

| State | Non-aligned tiles |
|---|---|
| NSW | 933 |
| SA | 633 |
| VIC | 436 |
| WA | 435 |
| TAS | 244 |
| **NT** | **237** |
| QLD | 142 |
| ACT | 2 |

All 237 NT rows have `Audit Data = "No audit roads coverage"` and `MNO Predicted Coverage =
"With MNO claimed coverage"` — i.e. every NT row is a place where the Government's own
drive testing found **no** coverage and the carrier's map claims there **is** coverage.

By carrier: **Telstra 210, Optus 25, TPG 2.**
By MNO response: **"No feedback from MNO" 150, "Coverage not found" 87** — so 63% of NT
non-alignments have no carrier explanation at all.
By LGA: Roper Gulf 76, Barkly 44, Victoria Daly 29, MacDonnell 22, Central Desert 19, West
Arnhem 15, East Arnhem 10, Unincorporated NT 9, Coomalie 7, Katherine 2, Litchfield 1
(plus 3 rows labelled with non-NT LGAs — Ceduna 2, Richmond 1 — which look like data-entry
errors worth flagging).

Batches present across the whole file: `202501-b7, 202505-b1, 202508-b2, 202509-b3,
202510-b4, 202511-b5, 202512-y2b1, 202601-y2b2`. Measurement years: 2024 (616 rows),
2025 (2,302), 2026 (144).

**3.1.7 Non-alignment categories are defined and MNO feedback is solicited.** The published
categories are: Network development/maintenance (planned outage); Network fault (unplanned
outage); **Coverage not found** ("An area where no coverage was found during Audit drive
testing, but the MNO predictive coverage maps show there is coverage. MNOs state that the
signal strength may be marginal or inconsistent due to distance from the nearest mobile
tower (such as at the cell edge) or where there are environmental obstacles."); Pending
Feedback from MNO; No feedback from MNO; Not explained by MNO. Source: non-alignments page
above, checked 2026-09-12.

**3.1.8 The MNO predicted layer comes from the ACCC Infrastructure RKR handheld coverage
datasets, last published 12 November 2025**, reflecting coverage as at 31 January 2025.
(The October 2025 fact sheet still cites the 31 January 2024 publication; the web page is
the newer of the two.) Sources: non-alignments page and fact sheet, checked 2026-09-12.
**MNO coverage maps are updated only once per year** — stated on the non-alignments page.

**3.1.9 The 77 static Audit Towns are queryable via a public ArcGIS REST endpoint, and
there are exactly 10 in the NT** *(computed — queried
`https://spatial.infrastructure.gov.au/server/rest/services/Hosted/Audit_Locations_DITRDCA_2024/FeatureServer/0/query`
anonymously on 2026-09-12)*. Fields: `objectid, location_name, state, latitude, longitude,
stage`. By state: NSW 11, WA 11, QLD 10, VIC 10, SA 10, TAS 10, **NT 10**, ACT 4 (= 76
published; the programme says "up to 77").

NT locations:

| Location | Lat | Lon | Stage |
|---|---|---|---|
| Jabiru | −12.67432 | 132.83829 | Pilot |
| Yulara | −25.23742 | 130.98703 | Pilot |
| Borroloola | −16.06948 | 136.30447 | Pilot |
| Maningrida | −12.05145 | 134.22227 | Main |
| Tennant Creek | −19.65081 | 134.18942 | Main |
| Katherine | −14.46521 | 132.26344 | Main |
| Nhulunbuy | −12.18210 | 136.78256 | Main |
| Nauiyu | −13.75048 | 130.68810 | Main |
| Mataranka | −14.92311 | 133.06679 | Main |
| Yuendumu | −22.25347 | 131.79524 | Main |

Four of these are remote Aboriginal communities (Maningrida, Nauiyu, Yuendumu, Borroloola);
Jabiru and Yulara are Pilot-stage only.

**3.1.10 Other public ArcGIS services under the same portal** *(computed — portal search
`https://spatial.infrastructure.gov.au/portal/sharing/rest/search?q=mobile audit`,
2026-09-12; 9 items)*:
`Main_Audit_Roads_DITRDCA_2024/MapServer` (layers Year_1_Roads, Year_2_Roads,
Year_3_Roads), `Pilot_Audit_Roads_DITRDCA_2024/MapServer`,
`Communications/Mobile_Phone_Coverage/MapServer`,
`Communications/Mobile_Phone_Sites/MapServer`,
`Communications/Mobile_Phone_Coverage_by_provider/MapServer`,
`Communications/Mobile_Phone_Coverage_by_technology/MapServer`. All advertise
`Query,Map,Data` capabilities. **The Audit Roads services carry the planned route
geometry, not the measurement results** — their service descriptions say they are derived
from national/state road datasets for the web map. Copyright text: "Department of
Infrastructure, Transport, Regional Development, Communications, Sport and the Arts ABN:
86 267 354 017".

**3.1.11 The Visualisation Tool is a MapLibre/Nuxt web app at
<https://d1zckiwudrcznp.cloudfront.net/>** (title "National Audit of Mobile Coverage"),
also reachable via the ArcGIS Experience Builder app id
`2c2a2ffb0a9d47e7b0e50590da86ee66`. Non-alignments are a toggleable geospatial layer;
new data is added monthly; historical data is reachable via a date filter. Its underlying
per-segment measurement data endpoint was not identified from the client bundles in this
session (TBD-5).

### 3.2 ACMA — Telecommunications (Mobile Coverage Maps) Industry Standard 2026

**3.2.1 For the first time in Australia, carriers must produce standardised coverage maps.**
Consultation opened 28 Jan 2026, closed 1 Mar 2026; 22 submissions (1 confidential);
outcomes paper published 31 Mar 2026. The standard **commences 1 April** and takes effect
from **30 June 2026**, made under the Telecommunications (Mobile Network Coverage Maps)
Direction 2025. Source:
<https://www.acma.gov.au/consultations/2026-01/proposal-make-mobile-coverage-mapping-standard>
— checked 2026-09-12.

**3.2.2 What it requires.** A consistent set of coverage categories (**good, moderate,
useable, none**) with consumer-facing descriptions; defined signal-strength thresholds for
4G and 5G outdoor handheld coverage based on **RSRP and SSRSRP**, "informed by international
practice and **findings from the National Audit of Mobile Coverage**"; service level
indicators for voice, SMS and data; WCAG 2.2 Level AA accessibility for published maps; and
it "Specify[s] organisations, in addition to emergency service organisations, that can
extract underlying geospatial data used to generate the published maps."

**3.2.3 One published threshold, with a correction on the record.** The minimum 4G/5G
signal-strength threshold for **'Good'** coverage is **−95 dBm**. ACMA published an
erratum on 28 January 2026 stating that Table 1 of Schedule 2 in the draft had shown
−85 dBm in error and that −95 dBm is correct. Same source, checked 2026-09-12. Remaining
thresholds for moderate/useable/none: TBD-6.

### 3.3 ACCC Measuring Broadband Australia — fixed-line only, and now finished

**3.3.1 The MBA programme concluded at the end of June 2026**; the final performance report
(Report 33) was released **17 June 2026**. It was funded to June 2026 in the 2025–26
Federal Budget after a March 2025 announcement. Source:
<https://www.accc.gov.au/by-industry/telecommunications-and-internet/telecommunications-monitoring/measuring-broadband-australia-program>
— checked 2026-09-12.

**3.3.2 MBA measured fixed-line, fixed wireless and satellite — not cellular mobile.**
ACCC framing, quoting Commissioner Anna Brakey: "Australians who live in regional and
remote areas and cannot access a fixed-line network rely on alternatives such as satellite
and fixed wireless services to connect to the internet." Whether MBA whiteboxes were ever
deployed in the NT, and whether raw MBA data is downloadable and under what licence, is
TBD-7.

### 3.4 Opensignal — reports only, no open data

**3.4.1 One NT-specific published statistic was located: Opensignal users in the Northern
Territory "spent more than 5% of the time without any mobile connectivity."** Report:
*"Retention starts with reception: how mobile network experience drives churn in
Australia"*, Opensignal, **28 April 2025**
(<https://insights.opensignal.com/2025/04/28/retention-starts-with-reception-how-mobile-network-experience-drives-churn-in-australia/dt>);
relayed with the same figure by <https://www.reviews.org/au/mobile/opensignal-regional-report-2025/>
— both checked 2026-09-12.

**3.4.2 Opensignal publishes national Australia reports roughly twice a year** — April 2025,
October 2025, **May 2026** are live at `insights.opensignal.com/reports/{YYYY}/{MM}/australia/mobile-network-experience`.
Regional analysis appears inside reports; Opensignal also states that regional Australia
including the NT shows inferior Excellent Consistent Quality and Reliability Experience
scores versus urban areas. **No open/downloadable underlying dataset was found** — the
reports are narrative HTML with charts. Checked 2026-09-12.

### 3.5 nPerf — crowdsourced, commercial licensing only

**3.5.1 nPerf runs a crowdsourced coverage and speed map for Australia** with per-carrier
views (Telstra, Optus, Vodafone) at `https://www.nperf.com/en/map/AU/...`. Data comes from
nPerf app users testing in real field conditions since 2014. For coverage data nPerf retains
only tests with geolocation precision ≤50 m; for download bitrate the threshold is ≤200 m.
Source: <https://www.nperf.com/en/map/AU/-/-/signal> and
<https://simology.io/blog/coverage-map-tools-opensignal-cellmapper-nperf-how-read-them> —
checked 2026-09-12.

**3.5.2 nPerf data in CSV is available only by quote request** — no open licence was found.
Checked 2026-09-12.

### 3.6 RTIRC 2024 — the NT Government's own submission

**3.6.1 The 2024 Regional Telecommunications Review** ("Connecting Communities, Reaching
Every Region") delivered **14 recommendations**; more than 3,900 stakeholders participated
(a fourfold increase on 2021), across 19 face-to-face sessions including in the NT
(Katherine among them). All non-confidential submissions are published. Sources:
<https://www.rtirc.gov.au/news-and-media/2024-regional-telecommunications-review-report-now-available>,
<https://www.rtirc.gov.au/> — checked 2026-09-12.

**3.6.2 The NT Government's submission is published and contains the coverage-area claim
most likely to be quoted in this project.** Verbatim: *"Mobile phone services are estimated
to reach 99% of the Australian population, however by area mobile phone coverage only
covers about 30% of the country. Specifically in the NT, the actual area of coverage is
closer to 5%."* Source: *Regional Telecommunications Review 2024 — NT Government
submission*, p. 9,
<https://www.infrastructure.gov.au/sites/default/files/documents/rtirc-2024-ntg.pdf>
(625,084 bytes, downloaded and text-extracted in this session) — checked 2026-09-12.
**Important provenance caveat:** the "5%" figure's footnote 8 reads "Refer to Figure 1 on
page 6 for mobile coverage map" — i.e. it points to the submission's own figure, **not to
an external published source**. Treat it as an NT Government assertion, not an independently
sourced statistic (TBD-8).

**3.6.3 Other NT Government positions in the same submission, relevant to a measurement
project:**
- On carrier claims: *"The Australian Government's audit into mobile coverage will offer
  independently verified information into the coverage and performance of mobile services
  nationally."* The submission also describes providers selling services to customers
  "outside the company's coverage footprint … often … without customers' full knowledge of
  the contractual obligations, violating consumer protection standards."
- **Recommendation 12:** *"Develop national service delivery standards and reporting of
  major outages, emergency service usage, downtime, signal strength, and speed of services
  in regional and remote areas."*
- **Recommendation 13:** a programme to install funded community Wi-Fi or similar as a
  redundant network in remote communities, prioritising First Nations communities where
  outages affect services.
- The submission cites *Mapping the digital gap: Wadeye, NT community outcomes report 2022*
  (pp. 36–39) as its evidence base on community connectivity.
- On mobile preference: NT Government advocates remote-community services be "wireless,
  pre-paid/pay-per-use, data and voice capable, transportable, affordable, reliable and
  resilient", noting mobile phones are the product of choice and residents largely choose
  pre-paid over post-paid.

---

## 4. Browser capability — what a PWA can and cannot measure

All browser-support figures in this section are *(computed)* from **caniuse-db version
1.0.30001810**, fetched from
`https://cdn.jsdelivr.net/npm/caniuse-db@latest/features-json/{feature}.json` on
2026-09-12. `y` = full support, `n` = none, `a` = partial.

**4.1 Network Information API — no support on iOS Safari, full support on Android Chrome.**

| Browser | Latest version in DB | Support | First full support |
|---|---|---|---|
| iOS Safari | 26.6 | **n** | never |
| Safari (desktop) | TP | **n** | never |
| Chrome for Android | 151 | **y** | 151 |
| Chrome (desktop) | 154 | a | — |
| Firefox for Android | 153 | **n** | never |
| Firefox (desktop) | 157 | **n** | never |
| Samsung Internet | 30 | **y** | 8.2 |
| Android Browser | 151 | **y** | 151 |

Global usage: **49.45% full + 26.99% partial**. Spec status in caniuse: `unoff`
(unofficial). MDN states verbatim: "Limited availability — This feature is not Baseline
because it does not work in some of the most widely-used browsers." Spec lives at WICG, not
W3C: <https://wicg.github.io/netinfo/>. Sources:
<https://developer.mozilla.org/en-US/docs/Web/API/Network_Information_API>,
<https://caniuse.com/netinfo> — checked 2026-09-12.

**4.2 The values the API does expose are deliberately coarsened.** From the spec
(<https://wicg.github.io/netinfo/>, checked 2026-09-12):
- `downlink` is **rounded to the nearest multiple of 25 kbps**, and only updated when the
  new value differs by more than 10%.
- `rtt` is **rounded to the nearest multiple of 25 ms**, same 10% update threshold.
- `effectiveType` is a four-value bucket with these boundaries:

| effectiveType | Minimum RTT (ms) | Maximum downlink (kbps) |
|---|---|---|
| slow-2g | 2000 | 50 |
| 2g | 1400 | 70 |
| 3g | 270 | 700 |
| 4g | 0 | ∞ |

Note `4g` is an open-ended bucket: anything faster than "3g" reports as `4g`, including 5G.
- The spec states explicitly: "The enumeration of available network interfaces and their
  generation and version is not directly exposed to script." **No cell id, no RSRP, no
  carrier, no radio technology.**
- The spec itself concedes the mitigations are modest, noting an attacker can already infer
  similar information from fetch timing.

**4.3 Offline queueing: IndexedDB and Service Workers are universal; Background Sync is
not.** *(computed, same caniuse-db)*

| Feature | iOS Safari 26.6 | Chrome Android 151 | Firefox Android 153 | Samsung 30 | Global `y` |
|---|---|---|---|---|---|
| IndexedDB | **y** (since 10.0) | y | y | y | 96.38% |
| Service Workers | **y** (since 11.3) | y | y | y | 96.07% |
| Background Sync API | **n** (never) | y (since Chrome 49) | n / unknown | y (since 5.0) | 76.73% |
| Web Bluetooth | n | y | n | y | 76.46% |

So: **queueing a measurement offline in IndexedDB and flushing it on next load works on
every target platform including iOS.** *Automatic background* flushing without the user
reopening the app — Background Sync — works on Android Chrome and Samsung Internet and
**does not work on iOS Safari at all**. Periodic Background Sync has no caniuse entry
(feature key `periodic-background-sync` returned HTTP 404), so its support is TBD-9.

**4.4 A lightweight speed test in a PWA is possible without any special API** — it is
ordinary `fetch()` of a known payload against a timed clock, plus `performance.now()`. This
requires no permission and works on every browser above. It measures HTTP throughput to a
chosen endpoint, which is a different quantity from radio signal strength, and its result
depends on the chosen server and route as well as the radio link. No source needed for the
mechanism; the constraint worth recording is that **a PWA speed test cannot attribute a
slow result to the radio link rather than the backhaul, because it cannot see the radio.**

**4.5 What a native Android app can read that a PWA cannot.** From
<https://developer.android.com/reference/android/telephony/TelephonyManager> — checked
2026-09-12:

| Capability | Method | Permissions | API level | Notes |
|---|---|---|---|---|
| All observed cells (serving + neighbours), with identity and signal | `getAllCellInfo()` | `ACCESS_FINE_LOCATION` + `READ_PHONE_STATE` | 17+ | **Deprecated**; **throttled** — repeated calls within a short window return cached results |
| Same, asynchronous | `requestCellInfoUpdate(Executor, Consumer<List<CellInfo>>)` | `ACCESS_FINE_LOCATION` + `READ_PHONE_STATE` | **29+ (Android 10)** | The recommended path on Android 10+ |
| Current signal strength | `getSignalStrength()` | `READ_PHONE_STATE` | 1+ | Returns null without permission / on unsupported devices |
| Event callbacks incl. signal strength and cell location | `registerTelephonyCallback(Executor, TelephonyCallback)` | `READ_PHONE_STATE`; `ACCESS_FINE_LOCATION` for cell-location callbacks | **31+ (Android 12)** | Replaces deprecated `listen()` |

The returned objects are `CellInfoGsm / CellInfoCdma / CellInfoTdscdma / CellInfoLte` (and
`CellInfoNr`), carrying per-cell identity (e.g. cell id, TAC, PCI, EARFCN) and signal
metrics including **RSRP and RSRQ** for LTE. Two structural constraints: `ACCESS_FINE_LOCATION`
is mandatory for any cell-info read (no location permission ⇒ no cell info), and
`getAllCellInfo()` is throttled to limit tracking. Second source on the location-permission
requirement: <https://learn.microsoft.com/en-us/dotnet/api/android.telephony.telephonymanager.allcellinfo>
— checked 2026-09-12.

**4.6 On iOS there is no path at all — not even for a native app.** From Apple Developer
Forums (<https://developer.apple.com/forums/thread/112601>,
<https://developer.apple.com/forums/thread/751785>), checked 2026-09-12: there has never
been a supported API for cellular signal strength on iOS; unsupported private routes are
now blocked by the sandbox; `CoreTelephony` / `CTTelephonyNetworkInfo` is public but exposes
carrier and radio-access-technology only, not signal strength. Apple's undocumented Field
Test Mode shows metrics to the user but is not programmatically accessible. The
`FTMInternal-4` route exists only for private/internal (non-App Store) distribution. This
has held for more than ten years and is described in the forum threads as a deliberate
design choice. **Consequence: the measurement capability gap is Android-vs-iOS, not
PWA-vs-native.** A native iOS app is no better off than an iOS PWA for radio metrics.

---

## 5. Prior art — crowdsourced / measured coverage in Australia and remote Indigenous communities

**5.1 Mapping the Digital Gap (ADM+S / RMIT, funded by Telstra)** — the closest Australian
prior art on remote First Nations connectivity, and **survey-based rather than
technically-measured**. First extensive study of digital inclusion in remote First Nations
communities; part of the Australian Digital Inclusion Index research suite; follows NHMRC
and AIATSIS ethics guidelines with a First Nations Expert Advisory group and **community
co-researchers conducting annual face-to-face surveys**. Phase 1 covered 12 communities
(2022–2024); Phase 2 covers 6 sites (2025–2027). **NT sites: Yuelamu, Tennant Creek,
Wadeye, Gäṉgaṉ homeland, and Utju (Areyonga).** Outputs are community outcomes reports, a
First Nations Data Dashboard, and ADII site scores. Latest: *2025 Outcomes Report*
(DOI 10.60836/1dhh-2e31) from the first phase in 12 communities; *Counting on Connectivity:
Remote and Regional Towns Research 2025 Supplementary Report* released **28 May 2026** with
729 surveys across 10 regional towns; next full report expected **December 2026**. Digital
inclusion scores as low as **39.0** are reported for Gäṉgaṉ and Wadeye. Sources:
<https://mappingthedigitalgap.com/>, <https://www.admscentre.org.au/mapping-the-digital-gap-project-helping-locals-secure-better-digital-services-and-greater-control-over-how-they-connect/>,
<https://digitalinclusionindex.org.au/case-study-mapping-the-digital-gap-digital-inclusion-in-remote-first-nations-communities/>,
<https://apo.org.au/node/334107> — all checked 2026-09-12. No technical measurement
component (speed tests, signal logging) is described in the public methodology, and no
downloadable dataset or data licence was located (TBD-10).

**5.2 Centre for Appropriate Technology Limited (CAT)** — an Aboriginal and Torres Strait
Islander owned not-for-profit, an ACCAN member, has worked with the NT Government and others
to improve mobile connectivity in very remote NT. Source: ACCAN, "Connecting remote
Indigenous communities", <https://accan.org.au/media-centre/hot-issues-blog/1415-connecting-remote-indigenous-communities>
— checked 2026-09-12.

**5.3 The 2016 homelands survey figure that keeps being cited.** A survey of **401
homelands and outstations in the Northern Territory** found only **20% had mobile phone
access**, **37% had internet access**, and of those, **80% had only a single internet access
point**. Relayed via the ACCAN page above — checked 2026-09-12. Primary source and exact
publication not yet traced (TBD-11).

**5.4 ACCAN-commissioned Remote Indigenous Communications Review (2020)** — a review of the
impact of telecommunications infrastructure programs on internet access in Australia's
remote Indigenous communities and outstanding needs, conducted about six months after
COVID-19 arrived in Australia. Source:
<https://www.researchgate.net/publication/345698127_Remote_Indigenous_Communications_Review_Telecommunications_Programs_and_Current_Needs_for_Remote_Indigenous_Communities>
— checked 2026-09-12.

**5.5 CellMapper** — an active crowdsourced cellular tower and coverage mapping service with
Australian carrier coverage, including Optus (MCC 505 MNC 2) and Telstra (MCC 505 MNC 1),
at <https://www.cellmapper.net/map?MCC=505&MNC=1>. Data comes from users running the
CellMapper Android app. *(computed — the map page requires login for most functions and the
interface surfaces an "API Limit Reached" message, indicating a rate-limited API exists.)*
`https://www.cellmapper.net/terms` returned HTTP 404 on 2026-09-12, so **no licence or
redistribution terms could be retrieved** (TBD-12). Treat as closed for bulk use until that
is settled.

**5.6 Carrier-run feedback and coverage tools.** Telstra publishes a predictive coverage map
that also distinguishes indoor vs outdoor coverage and shows planned future coverage
(<https://www.telstra.com.au/coverage-networks/our-coverage>); Optus publishes 4G, 5G,
5G mmWave and NB-IoT coverage including a separate 4G-with-external-antenna layer
(<https://www.optus.com.au/living-network/coverage>). Both checked 2026-09-12. **No
carrier-run tool was found that lets a member of the public submit a measurement and see it
published.** Opensignal's own app-based map at
<https://insights.opensignal.com/coverage-maps/australia/telstra> is the crowdsourced
counterpart, run by a third party rather than the carriers.

**5.7 Stumbler apps that feed open databases, all Android-only.** NeoStumbler (Accrescent,
F-Droid, Google Play, GitHub), Tower Collector (F-Droid, Google Play — uploads to beaconDB
by default in recent versions), Network Survey (F-Droid, Google Play). All three are the
beaconDB-recommended contribution clients. Source: <https://beacondb.net/> — checked
2026-09-12. There is no iOS equivalent, consistent with 4.6.

**5.8 Accenture's crowdsourcing platform is the one crowdsourced source already inside an
Australian government programme** — Module C of the National Audit (see 3.1.2), ~160,000
active Australian users, ~3.5 billion samples annually, released quarterly. It is a
commercial SDK embedded in third-party apps with user consent, not a public contribution
app.

**5.9 No CDU or other Australian university project crowdsourcing NT mobile coverage was
located** in this session. Searches surfaced the ADM+S/RMIT survey work (5.1) and ACCAN
reviews (5.2, 5.4) only. Absence of evidence from ~40 fetches, not evidence of absence
(TBD-13).

---

## Other facts found

**OF-1. NT community Wi-Fi rollout is expanding.** On **12 November 2025** an additional 52
communities were announced for free community Wi-Fi, bringing the total to up to 53
communities announced across WA, SA, TAS, NT and QLD. Source: relayed via
<https://www.infrastructure.gov.au/media-communications/first-nations-digital-inclusion> —
checked 2026-09-12. Exact NT share of those communities: TBD-14.

**OF-2. The ACCC Mobile Infrastructure Report was last published 12 November 2025** and
reflects coverage as at **31 January 2025**. This is the provenance of the "MNO predicted
coverage" layer used in both the National Audit visualisation tool and the non-alignment
comparison. Source: non-alignments page, checked 2026-09-12.

**OF-3. First Nations Digital Inclusion Roadmap 2026 and beyond** is published at
<https://www.digitalinclusion.gov.au/sites/default/files/documents/first-nations-digital-inclusion-roadmap-2026-and-beyond.pdf>
— located 2026-09-12, not read in this session.

**OF-4. First Nations Australians are twice as likely to be digitally excluded**, per the
Australian Digital Inclusion Index. Source:
<https://digitalinclusionindex.org.au/first-nations-australians-twice-as-likely-to-be-digitally-excluded/>
— checked 2026-09-12.

**OF-5. The non-alignment CSV repeats its header row as the first data row.** Row 1 of
`nonalign.csv` is a literal duplicate of the header. Any loader that does not filter it will
carry a junk record. *(computed.)*

**OF-6. Three rows in the NT slice of the non-alignment CSV carry LGA values that are not NT
LGAs** — "Ceduna" (SA) ×2 and "Richmond" ×1 — while `State = NT`. Likely a spatial-join
error in the source. Worth reporting upstream rather than silently dropping. *(computed.)*

**OF-7. Australia-wide Ookla mobile tile counts have declined ~20% since 2020** (53,870 in
2020 Q2 → 43,136 in 2026 Q2) *(computed)*. Whether this is falling Speedtest app usage, the
2026 "supported regions" change, or methodology drift is not established (TBD-15).

**OF-8. Ookla fixed data is ~2.7× denser than mobile in the NT** (1,318 tiles / 11,470 tests
vs 488 / 1,380 for 2026 Q2) *(computed)* — the reverse of what the NT Government submission
describes as remote preference (3.6.3: mobile is the product of choice). Consistent with
fixed tests being run from homes and offices in the towns.

**OF-9. Reading Ookla remotely needs no credentials and no AWS account.** DuckDB with the
`httpfs` extension against the plain HTTPS S3 URL performed predicate pushdown well enough
to extract the NT from a 176 MB global file in ~14 seconds *(computed)*. Tooling used:
Python 3.13.5, duckdb 1.5.5, rasterio 1.5.1, pypdf — all installed in this session; none
were present beforehand.

**OF-10. The National Audit fact sheet is the source of the phrase the NT Government also
uses about carrier maps.** The fact sheet states MNO maps "show outdoor handheld predicted
mobile coverage. There may be some direct measurement by MNOs, but it is largely calculated
through a predictive algorithm. The assumptions and constants used for the predictive
algorithm are determined by each individual MNO." Checked 2026-09-12.

---

## TBD — needs validation

**TBD-1. The 50 NT remote-community coordinates used in §1.2.7 are approximate and were not
taken from a single published gazetteer.** The community-level counts are therefore
directionally reliable but not citable as-is. **What would settle it:** re-run §1.2.7
against an authoritative geometry — the ABS Indigenous Locations (ILOC) boundaries from ASGS
Edition 3, or the NT Government's own remote community locality list — and use polygon
containment rather than a 5 km radius. Both are on the sanctioned dataset list.

**TBD-2. OpenCelliD's NT cell count from the live database is unknown**, as is the Australia
CSV's file size, exact schema and any download rate limit. The only NT number in this report
(§2.5–2.6) comes from a **2020** World Bank derivative, which predates the Telstra and Optus
3G shutdowns and most 5G rollout. **What would settle it:** register a free OpenCelliD
account, obtain an API Access Token, download the Australia (MCC 505) country CSV, and count
rows inside the NT bbox by `radio` type. Note the 18-month observation window (§2.3) means
the result would be "cells seen in the last 18 months", not an all-time count — a different
quantity from the 2020 snapshot and not directly comparable to it.

**TBD-3. beaconDB's NT density is unknown and currently unknowable from public sources** —
no dumps, no per-region statistics. **What would settle it:** wait for the promised
public-domain dumps, or probe the `/v1/geolocate` API with known NT cell identifiers (which
requires already having those identifiers, so it cannot enumerate).

**TBD-4. The licence of the National Audit non-alignment CSV is not stated on its page.**
No Creative Commons or copyright notice appears in the page body *(computed — a regex sweep
of the full fetched HTML for "Creative Commons", "CC BY" and "licence" returned nothing)*.
The ArcGIS services under the same department carry a copyright line naming the department
but no licence. **What would settle it:** the department's site-wide copyright statement
(most Australian Government sites default to CC BY 4.0), or a direct enquiry. **This matters
because the CSV is the most directly on-point dataset found in this entire lane.**

**TBD-5. The per-segment measurement data behind the Audit Visualisation Tool was not
located.** The Nuxt client bundles contain no absolute API base, S3/CloudFront URL, or
`.json`/`.geojson`/`.pbf` asset reference *(computed — grepped all four `_nuxt` bundles,
578 KB largest)*; the only external link found in them was to the non-alignments page. So
the monthly Module B measurements and quarterly Module C crowdsourced data are **viewable**
but there is no confirmed download. **What would settle it:** loading the tool in a browser
with the network panel open and recording the XHR endpoints, or asking the department
whether the underlying data is released.

**TBD-6. Only the 'Good' RSRP threshold (−95 dBm) from the ACMA standard is captured here.**
The thresholds for 'moderate', 'useable' and 'none', and the separate SSRSRP (5G) values,
were not retrieved — the outcomes paper PDF timed out on fetch. **What would settle it:**
download *Outcomes paper: Proposal to make mobile coverage mapping standard* (355 KB) and
*Draft Telecommunications (Mobile Network Coverage Map) Industry Standard 2026* (450 KB)
from the ACMA consultation page, or read the registered instrument on the Federal Register
of Legislation.

**TBD-7. Whether Measuring Broadband Australia ever deployed whiteboxes in the NT, and
whether its raw data is downloadable and under what licence, is unresolved.** The programme
page does not say. **What would settle it:** the appendix tables of Report 33 (June 2026),
which the ACCC publishes alongside the PDF, or the "Broadband performance data" page.

**TBD-8. The NT Government's "coverage is closer to 5% of NT area" figure has no external
source.** Its own footnote points back to a figure inside the same submission (§3.6.2).
**What would settle it:** computing the number directly from the ACCC Mobile Infrastructure
Report coverage polygons against the NT land area — which is a reproducible calculation from
sanctioned datasets — rather than citing the submission.

**TBD-9. Periodic Background Sync support is unknown.** The caniuse feature key
`periodic-background-sync` does not exist (HTTP 404) *(computed)*. **What would settle it:**
the MDN BCD entry for `PeriodicSyncManager`, or the Chrome Platform Status entry.

**TBD-10. Mapping the Digital Gap publishes no downloadable dataset or licence that was
locatable**, and its public methodology does not mention technical measurement. **What would
settle it:** reading the 2025 Outcomes Report methodology appendix (DOI 10.60836/1dhh-2e31)
and checking the First Nations Data Dashboard for an export or API.

**TBD-11. The 2016 "401 NT homelands and outstations" survey primary source was not
traced** — only the ACCAN blog relay. **What would settle it:** identifying the original
survey publication and confirming the 20% / 37% / 80% figures against it. A 2016 figure
should not be used as current in any case.

**TBD-12. CellMapper's terms of use could not be retrieved** (`/terms` → HTTP 404 on
2026-09-12) and its Australian NT density was not measured. **What would settle it:** the
CellMapper wiki at `docs.cellmapper.net`, or the terms link in the site footer once the
correct URL is found. Until then its data should be treated as not licensed for
redistribution.

**TBD-13. No Australian university crowdsourced-coverage project was found, but the search
was not exhaustive.** **What would settle it:** searching CDU's Northern Institute
publications, the ADM+S publication list, and APO (apo.org.au) for NT connectivity
measurement projects specifically.

**TBD-14. How many of the 53 announced community Wi-Fi sites are in the NT is unknown.**
**What would settle it:** the 12 November 2025 announcement's community list on
infrastructure.gov.au.

**TBD-15. The cause of the ~20% national decline in Ookla tile counts since 2020 is not
established** (OF-7). **What would settle it:** the Ookla README changelog history in git,
which records the "supported regions" change, compared against the per-quarter Australian
counts already computed in §1.2.5.

**TBD-16. Ookla's CC BY-NC-SA 4.0 NonCommercial term has not been assessed against this
competition's context.** Recorded as a fact (§1.1.3), not interpreted. **What would settle
it:** a reading of the competition terms on whether entries are commercial, and of the
ShareAlike obligation's reach over a derived visualisation — a licensing question, not a
research one.

---

## Sources

- Ookla Open Data repository — <https://github.com/teamookla/ookla-open-data> (and raw README at <https://raw.githubusercontent.com/teamookla/ookla-open-data/master/README.md>)
- AWS Registry of Open Data — <https://registry.opendata.aws/speedtest-global-performance/>
- Ookla S3 bucket — <https://ookla-open-data.s3.amazonaws.com/>
- OpenCelliD downloads — <https://www.opencellid.org/downloads.php>
- OpenCelliD statistics — <https://opencellid.org/stats.php>
- OpenCelliD about — <https://opencellid.org/about.php>
- OpenCelliD (Wikipedia) — <https://en.wikipedia.org/wiki/OpenCelliD>
- World Bank Global OpenCellID cell tower map — <https://datacatalog.worldbank.org/search/dataset/0038043/global-opencellid-cell-tower-map>
- Mozilla Location Service (Wikipedia) — <https://en.wikipedia.org/wiki/Mozilla_Location_Service>
- Mozilla ichnaea retirement issue — <https://github.com/mozilla/ichnaea/issues/2065>
- beaconDB — <https://beacondb.net/> and <https://github.com/beacondb/beacondb>
- radiocells.org — <https://radiocells.org/>
- National Audit of Mobile Coverage — <https://www.infrastructure.gov.au/media-communications-arts/better-connectivity-plan-regional-and-rural-australia/national-audit-mobile-coverage>
- National Audit methodology fact sheet, October 2025 — <https://www.infrastructure.gov.au/sites/default/files/documents/national-audit-of-mobile-coverage-methodology-fact-sheet-october2025.pdf>
- National Audit non-alignments page — <https://www.infrastructure.gov.au/media-communications/better-connectivity-plan-regional-and-rural-australia/national-audit-mobile-coverage/national-audit-mobile-coverage-mobile-coverage-non-alignments>
- Non-alignment data CSV, May 2026 — <https://www.infrastructure.gov.au/sites/default/files/documents/national_audit_of_mobile_coverage_non-alignment_data_may_2026.csv>
- Audit Locations feature service — <https://spatial.infrastructure.gov.au/server/rest/services/Hosted/Audit_Locations_DITRDCA_2024/FeatureServer>
- Audit visualisation tool — <https://d1zckiwudrcznp.cloudfront.net/>
- ACMA mobile coverage mapping standard consultation — <https://www.acma.gov.au/consultations/2026-01/proposal-make-mobile-coverage-mapping-standard>
- ACCC Measuring Broadband Australia — <https://www.accc.gov.au/by-industry/telecommunications-and-internet/telecommunications-monitoring/measuring-broadband-australia-program>
- Opensignal Australia — <https://insights.opensignal.com/australia> and <https://insights.opensignal.com/2025/04/28/retention-starts-with-reception-how-mobile-network-experience-drives-churn-in-australia/dt>
- nPerf Australia — <https://www.nperf.com/en/map/AU/-/-/signal>
- RTIRC 2024 — <https://www.rtirc.gov.au/>
- NT Government RTIRC 2024 submission — <https://www.infrastructure.gov.au/sites/default/files/documents/rtirc-2024-ntg.pdf>
- MDN Network Information API — <https://developer.mozilla.org/en-US/docs/Web/API/Network_Information_API>
- WICG Network Information API spec — <https://wicg.github.io/netinfo/>
- caniuse — <https://caniuse.com/netinfo>, and caniuse-db 1.0.30001810 via <https://cdn.jsdelivr.net/npm/caniuse-db@latest/>
- Android TelephonyManager — <https://developer.android.com/reference/android/telephony/TelephonyManager>
- Microsoft Learn, TelephonyManager.AllCellInfo — <https://learn.microsoft.com/en-us/dotnet/api/android.telephony.telephonymanager.allcellinfo>
- Apple Developer Forums on iOS signal strength — <https://developer.apple.com/forums/thread/112601> and <https://developer.apple.com/forums/thread/751785>
- Mapping the Digital Gap — <https://mappingthedigitalgap.com/>
- ADM+S Mapping the Digital project — <https://www.admscentre.org.au/mapping-the-digital-project-helping-locals-secure-better-digital-services-and-greater-control-over-how-they-connect/>
- Australian Digital Inclusion Index — <https://digitalinclusionindex.org.au/>
- ACCAN, Connecting remote Indigenous communities — <https://accan.org.au/media-centre/hot-issues-blog/1415-connecting-remote-indigenous-communities>
- CellMapper — <https://www.cellmapper.net/map?MCC=505&MNC=1>
- Telstra coverage — <https://www.telstra.com.au/coverage-networks/our-coverage>
- Optus coverage — <https://www.optus.com.au/living-network/coverage>
