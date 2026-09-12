# Arena research — lane C ("failure"): network / single-point-of-failure mechanism

**Scope.** Research only, on the mechanism assigned to this lane: model NT connectivity as a
graph of base stations, backhaul links, communities and hazards, and compute what a single
link or site loss disconnects. No verdict, no ranking, no recommendation.

**All findings checked 2026-09-12** unless stated otherwise. Every figure below was either read
out of a file this lane downloaded, or quoted from a page this lane retrieved. Where a page
could not be retrieved or a number is not published, the finding says **TBD — needs validation**.

**Retrieval note that affects every section.** Several load-bearing sources refuse automated
retrieval. `www.bom.gov.au` returns HTTP 403 with an explicit anti-scraping notice to a default
`curl`/WebFetch request, and returns HTTP 200 to the same request with a browser `User-Agent`.
`securent.nt.gov.au` sits behind a Cloudflare JavaScript interstitial and could not be read at
all. These are recorded as findings, not worked around silently.

---

## 1. Backhaul data

### 1.1 NT Government 2019 dataset — downloaded, parsed, deleted

- **Dataset:** "Remote Communities with Mobile Coverage and Backhaul Transmission 2019"
  <https://data.nt.gov.au/dataset/list-of-remote-communities-with-mobile-coverage>
- **Publisher:** NT Department of Corporate and Digital Development (CKAN org
  `department-of-corporate-and-information-services`, title "Corporate and Digital Development").
- **Licence:** `cc-by` / "Creative Commons Attribution" (CKAN `package_show`).
- **CKAN metadata:** `metadata_created` 2019-05-09, `metadata_modified` 2022-06-29.
  The **XLSX resource itself** has `last_modified` **2019-05-16** — i.e. the 2022 date is a
  metadata edit, not a data refresh.
- **XLSX download URL (HTTP 200, 15,654 bytes, `application/vnd.openxmlformats-...sheet`):**
  `https://data.nt.gov.au/dataset/84fd8432-de2d-407c-977d-3f851adfac75/resource/88a6306f-293e-4048-a5e5-0d6b65e3e589/download/remote-communities-mobile-coverage.xlsx`
- **Data Quality Statement PDF (HTTP 200, 232,628 bytes):**
  `https://data.nt.gov.au/dataset/84fd8432-de2d-407c-977d-3f851adfac75/resource/a1409932-1d8e-44cf-ad5e-13d930f93262/download/data-quality-statement.pdf`

**1.1.1 Structure (read with `openpyxl` 3.1.5).** One sheet, `Sheet1`, range `A1:E66`.
Row 1 is a title banner ("Remote Communities with Mobile Coverage"), row 2 is the header,
rows 3–66 are data: **64 data rows**. Header columns, verbatim, typos included:

| Column | Header as written |
|---|---|
| A | `Remove Community Location` |
| B | `Remote Communinity Latitude` |
| C | `Remote Community Longitude` |
| D | `Remote Community Backhaul transmission` |
| E | `Remote Community Provider` |

**1.1.2 It does name backhaul type per community.** Two values only:

| Backhaul transmission | Rows |
|---|---|
| Optic fibre | 45 |
| Microwave radio | 19 |

There is **no satellite value**, and no per-*site* granularity — the unit of the row is the
community, not the base station.

**1.1.3 Provider / program column** (this is a funding-program label, not a carrier-only field):
Telstra 29, Project 13 13, Telstra/NTG Program 10, Arnhem Fibre Program 8, MBSP 4.

**1.1.4 The 19 microwave-fed communities** (name, lat, lon, provider) — the candidate
single-hop-dependent set: Ampilatwatja, Amoonguna, Arlparra, Atitjere, Bynoe, Galiwinku,
Kintore, Manyallaluk, Milikapiti, Milingimbi, Minjilang, Pirlangimpi, Santa Teresa, Tanami,
Titjikala, Wallace Rockhole, Warruwi, Wurrumiyanga, Yarralin.

**1.1.5 Coordinates.** 63 of 64 rows parse as numeric lat/lon; bounding box lat −25.349 to
−11.151, lon 129.079 to 136.891. The exception is **Weemol**, whose latitude cell is the
*string* `"\xa0-13.644"` (leading non-breaking space) rather than a number. Any loader must
strip `\xa0` or that row drops out.

**1.1.6 What the dataset does not contain.** No link endpoints, no microwave hop paths, no
repeater/relay sites, no fibre route geometry, no capacity, no redundancy flag, no site IDs.
The topology a graph model needs — *which* node each community hangs off — is **not in this
file**. **TBD — needs validation:** whether DCDD holds a route/hop layer internally. What would
settle it: a direct request to the listed custodian contact below, or an NTG spatial-portal
layer naming link endpoints.

**1.1.7 Data Quality Statement (PDF, 2 pages, extracted text).** Self-rated Accuracy 5/5,
Completeness 5/5, Consistency 5/5, **Timeliness 3/5, Integrity 3/5**. Custodian named as
**Barry Garside**, `officeofdigitalgovernment.DCIS@nt.gov.au`, phone 89243840. Disclaimer,
verbatim: *"NT Government gives no guarantee as to the fitness of this data for a particular
purpose … the data is provided 'as is'. The burden for fitness of the data remains completely
with the user."* Note the PDF's own header reveals it was printed from a local file path on
7/1/2019 and the Integrity/Timeliness sections repeat the Completeness bullet text verbatim —
i.e. the statement is partly boilerplate.

The XLSX and PDF were downloaded to `reports/tmp/`, parsed, and the folder deleted, as instructed.

### 1.2 ACCC Mobile Infrastructure Report — data release (does NOT carry backhaul type)

- Dataset: <https://data.gov.au/data/dataset/accc-mobile-infrastructure-report-data-release>
- Licence: **CC BY 2.5 Australia** (`cc-by-2.5`). `metadata_modified` 2026-06-14. 138 resources.
- Latest year present is **2025**; there is no 2026 resource as of today.
- Telstra 2025 sites CSV (HTTP 200, 798,356 bytes):
  `https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/15972aec-64a2-4be8-8e71-eaee74b45824/download/mobile-sites-telstra-2025.csv`
  Optus 2025 (634,567 B) resource id `b8d11f5e-7b74-4280-9cf8-4a32e6a34f18`;
  TPG 2025 (299,718 B) resource id `76b939d6-6974-4564-ae3b-20dc4fcc344e`;
  there is also a new **`Mobile sites - Optus-TPG MOCN - 2025`** (157,495 B, id
  `abca7864-4da1-4df1-9b29-0f4bb882e936`) — a shared-network file, which matters because MOCN
  sites are *correlated failures* across two "different" carriers.

**1.2.1 Columns (Telstra 2025, read directly):** `Year, MNO, RFNSA ID, Latitude, Longitude,`
then one flag column per band (`GSM900, IoT700, LTE700, LTE850, LTE1800, LTE2100, LTE2600,
NR700, NR850, NR2100, NR2600, NR3600, NR26000`), then `Co_funded, Co_contribution_program,
Round`. **There is no backhaul column.** Optus and TPG files have the same shape with a
different band list.

**1.2.2 NT counts** (bounding box lat −26.1…−10.8, lon 128.9…138.1, computed from the files):
Telstra **247**, Optus **130**, TPG **45** — **422 site-rows** in NT in 2025. Note Optus/TPG
MOCN means some of those are the same physical structure; de-duplication by `RFNSA ID` would be
needed.

**1.2.3 Backhaul leaks in indirectly via `Co_contribution_program`.** NT Telstra 2025 has 59
co-funded sites; the program strings include **"REGIONAL CO-INVESTMENT: Small Cell Satellite"
(12)**, "REGIONAL CO-INVESTMENT: EWA - Small Cell Satellite" (6), "NT RSCP - Small Cell
Satellite" (2), "Kakadu Connect - Small Cell Satellite" (2), "RCP - Small Cell Satellite" (1)
— **23 NT sites whose program name asserts satellite backhaul** — plus "RCP - TX Upgrade" (2),
which names a transmission upgrade. NT Optus 2025 co-funding is a single program string,
"Federal Mobile Black Spot Program (MBSP)" (33); NT TPG 2025 has none.

### 1.3 Regional Connectivity Program — has an explicit `Technology_Type` including "Fibre Backhaul"

ArcGIS REST layer, queried directly:
`https://spatial.infrastructure.gov.au/server/rest/services/Regional_Connectivity_Program/MapServer/0/query?where=State='NT'&outFields=*&f=json`

- **58 NT point features**, `exceededTransferLimit` not set (complete result).
- Fields: `RCP_Asset_Identifier, Project_Name, Grantee, Project_Description, Technology_Type,
  Status, Completion_Month, Round, State, LGA, Electorate, Remoteness, x, y`.
- **`Technology_Type` (NT):** Fixed Wireless Broadband 18, **Fibre Backhaul 16**,
  Mobile Voice & Data 12, Satellite Broadband 9, Fibre Broadband 3.
- `Status`: Complete 49, In Progress 9. `Round`: R3 30, R1 19, R2 9.
- `Grantee`: Telstra 28, Easyweb Digital 22, NBN Co 6, BizCom NT 1, AARNet 1.
- `Remoteness`: Very Remote 30, Remote 23, Outer Regional 5.
- `Completion_Month` runs from Mar 2023 to Jan 2026, i.e. **this is post-2019 backhaul change**
  the 2019 NT file cannot show. Example rows: "Arnhem Fibre Upgrade Project" (Telstra, Fibre
  Backhaul, Complete, R1, West Arnhem / Unincorporated NT); "Small Cell Tower in Wilora"
  (Telstra, Mobile Voice & Data, Complete, R1, Central Desert).
- **Licence: TBD — needs validation.** A CKAN search for "Regional Connectivity Program" on
  data.gov.au returned no matching package, and `catalogue.data.infrastructure.gov.au`'s CKAN
  `package_search` for the same term returned `count: 0`. The ArcGIS service is open and
  unauthenticated but carries no licence statement this lane could retrieve. What would settle
  it: the service's own `?f=json` `copyrightText`/`licenseInfo` field, or the DITRDCSA
  Communications Programs Mapping Tool item page.

### 1.4 Mobile Black Spot Program — NT site list with coordinates, rounds, and `Base_Station_Type`

- Dataset: <https://data.gov.au/data/dataset/mobile-black-spot-program-mbsp>, licence **CC BY 4.0**,
  `metadata_modified` 2024-08-09.
- Single bulk resource `MBSP - All Funded Base Stations.zip` (HTTP 200, 297,168 bytes):
  `https://data.gov.au/data/dataset/2d988915-1192-4f50-92d5-891efc0ba612/resource/28c8b5c8-9b46-4b61-ad19-84c6dc6483d0/download/mbsp-all-funded-base-stations.zip`
  Contains 8 KML files, one per round (R1, R2, R3, R4, R5, R5A, R6, R7).
- Fields (R1–R5A): `MBSP_ID, Location, Grantee, State, Electorate_2022, Local_Government_Area,
  Base_Station_Type, Remoteness, Site_Status, Completion_Date, MNHP_funded` + coordinates.
  R7 replaces `Base_Station_Type` with `Solution_category, Solution_name, Solution_type`.
- **NT placemark counts:** R1 10, R2 30, R4 24, R5 20, R7 14; R3/R5A/R6 zero. **Total 98.**
- **Data-quality catch:** every NT location appears exactly twice in each file (e.g. "Finke,
  Imanpa, Minjilang, Mt Liebig, Wallace Rockhole" then the same five again), so the placemark
  count is **double** the site count. **49 unique NT sites** across all rounds. Any loader that
  does not de-duplicate will double-count NT MBSP sites.
- `Base_Station_Type` NT: R1 Macro 10; R2 Small cell 24 / Macro 6; R4 Small cell 24; R5 "Small
  Cell" 18 / Macro 2 (note the inconsistent capitalisation between R4 and R5 — `Small cell` vs
  `Small Cell`). R7 `Solution_type`: Microcell 10, Macrocell 4; `Solution_category`: Mobile
  Black Spot 8, **First Nations 6**; `Site_Status` R7 all "In Progress"; R7 NT
  `Solution_name` values: Banka Banka, King Ash Bay, Murray Downs (Imangara), Renner Springs,
  Urapunga, Victoria River Roadhouse, Yilpara (Banyala).
- `MNHP_funded` is present on R1/R2 and links MBSP sites to the hardening program (see §4.1).

### 1.5 NBN

`package_search?q=nbn` on data.gov.au returns `national-broadband-network` (CC BY 4.0,
modified 2024-10-21), `national-broadband-network-connections-by-technology-type` (CC BY 4.0,
2024-08-08), `au-govt-ditrdc-nbn-na` (CC-BY-2.5-AU, 2025-07-31), plus several
service-area-declaration packages (CC BY 3.0 AU). ArcGIS services `NBN_Fixed_Line`,
`NBN_Fixed_Wireless`, `NBN_Coverage_Footprints_2024` also exist at
`https://spatial.infrastructure.gov.au/server/rest/services`.
**TBD — needs validation:** whether any NBN product publishes **Points of Interconnect (POI)
or transit route geometry** for the NT, which is what would let an NBN layer contribute edges
rather than polygons. This lane did not open the NBN resources. What would settle it: reading
the resource list of `national-broadband-network` and checking for a POI/route file.

### 1.6 Telstra regional fibre maps

**TBD — needs validation.** Not retrieved in this lane. Telstra's Arnhem Fibre and NT fibre
routes appear only as *program names* in §1.1 (`Arnhem Fibre Program`, 8 communities) and §1.3
(`Fibre Backhaul`, 16 NT RCP records). No published route geometry was located. What would
settle it: a Telstra InfraCo / Amplitel network map publication, or an RFNSA/ACMA-derived
route inference.

---

## 2. Tropical cyclone data

### 2.1 BoM Southern Hemisphere tropical cyclone database — downloaded and parsed

- URL: `http://www.bom.gov.au/clim_data/IDCKMSTM0S.csv`
- **A default request returns HTTP 403** with body: *"Your access is blocked due to the
  detection of a potential automated access request. The Bureau of Meteorology website does not
  support web scraping: if you are trying to access Bureau data through automated means, you
  should stop."* It also printed the requesting IP and a reference ID.
- The identical request with a browser `User-Agent` returned **HTTP 200, 7,931,754 bytes,
  `text/csv`**. That is a finding about the source's terms, not a recommended method (see §2.3).
- File header lines: `Copyright Commonwealth of Australia 2010 Bureau of Meteorology (ABN 92
  637 533 532)` / `Generated on: 2026-09-12` / copyright-notice link. **The CSV is regenerated
  daily — today's copy is stamped with today's date.**

**2.1.1 Shape.** 31,711 lines; 4 preamble lines; header on line 5; **31,706 data rows**,
**79 columns**, **1,133 unique `DISTURBANCE_ID` values**, `TM` date range **1907 → 2026**.

**2.1.2 Columns** (all 79): `NAME, DISTURBANCE_ID, TM, TYPE, DATA_SRC, SURFACE_CODE, CYC_TYPE,
LAT, LON, POSITION_METHOD, POSITION_UNCERTAINTY, DVORAK_DATA_T_NO, DVORAK_MODEL_T_NO,
DVORAK_PATTERN_T_NO, DVORAK_FINAL_T_NO, DVORAK_CI_NO, CENTRAL_PRES, CENTRAL_PRES_UNCERTAINTY,
CENTRAL_PRES_METHOD, PRES_WIND_RELATION_USED, ENV_PRES, ENV_PRES_UNCERTAINTY,
MN_RADIUS_OUTER_ISOBAR, MN_RAD_OUT_ISOBAR_UNCERTAINTY, MN_RADIUS_GF_WIND, MN_RADIUS_GF_SECNE,
MN_RADIUS_GF_SECSE, MN_RADIUS_GF_SECSW, MN_RADIUS_GF_SECNW, MN_RADIUS_SF_WIND,
MN_RADIUS_SF_SECNE, MN_RADIUS_SF_SECSE, MN_RADIUS_SF_SECSW, MN_RADIUS_SF_SECNW,
MN_RADIUS_HF_WIND, MN_RADIUS_HF_SECNE, MN_RADIUS_HF_SECSE, MN_RADIUS_HF_SECSW,
MN_RADIUS_HF_SECNW, MN_RADIUS_MAX_WIND, MN_RADIUS_MAX_WIND_UNCERTAINTY,
MN_RADIUS_GF_WIND_UNCERTAINTY, MN_RADIUS_SF_WIND_UNCERTAINTY, MN_RADIUS_HF_WIND_UNCERTAINTY,
MN_RADIUS_MAX_WIND_METHOD, MN_RADIUS_GF_WIND_METHOD, MN_RADIUS_SF_WIND_METHOD,
MN_RADIUS_HF_WIND_METHOD, WIND_SPD_PER, MAX_WIND_SPD, MAX_WIND_SPD_UNCERTAINTY,
MAX_WIND_SPD_METHOD, MAX_WIND_GUST_PER, MAX_WIND_GUST, MAX_WIND_GUST_METHOD, MN_EYE_RAD,
MN_EYE_RAD_UNCERTAINTY, MN_EYE_RAD_METHOD, MAX_REP_WIND_SPD, MAX_REP_WIND_DIR,
MAX_REP_WIND_METHOD, MAX_REP_WIND_LON, MAX_REP_WIND_LAT, MAX_REP_WAV_HT, MAX_REP_WAV_METHOD,
MAX_REP_WAV_LON, MAX_REP_WAV_LAT, MAX_REP_SWL_HT, MAX_REP_SWL_DIR, MAX_REP_SWL_PER,
MAX_REP_SWL_METHOD, MAX_REP_SWL_LON, MAX_REP_SWL_LAT, MAX_REP_TIDE_ANOM,
MAX_REP_TIDE_ANOM_UNCERTAINTY, MAX_REP_TIDE_ANOM_METHOD, MAX_REP_TIDE_ANOM_LON,
MAX_REP_TIDE_ANOM_LAT, COMMENT`.

The `MN_RADIUS_GF/SF/HF_*` columns are gale-force / storm-force / hurricane-force **wind radii
by quadrant** — these are what would let a hazard footprint be built as a swept polygon rather
than a point buffer. They are sparsely populated in older records.

**2.1.3 Selecting NT-relevant cyclones.** There is no state/territory field; selection must be
spatial. Filtering to any track point inside lat −18.0…−9.0, lon 128.0…139.0 gives **248 of 1,133
disturbances**. Most recent 25 by start date (start `TM`, id, name):

| Start | Disturbance ID | Name |
|---|---|---|
| 2026-03-15 | AU202526_34U | Narelle |
| 2026-01-29 | AU202526_21U | Mitchell |
| 2025-12-27 | AU202526_08U | Hayley |
| 2025-12-14 | AU202526_07U | (noname) |
| 2025-11-15 | AU202526_02U | **Fina** |
| 2025-04-16 | AU202425_30U | (noname) |
| 2025-04-09 | AU202425_29U | Errol |
| 2024-03-13 | AU202324_09U | **Megan** |
| 2024-02-14 | AU202324_07U | Lincoln |
| 2024-01-17 | AU202324_05U | Kirrily |
| 2023-04-06 | AU202223_23U | Ilsa |
| 2023-02-22 | AU202223_16U | (noname) |
| 2022-12-21 | AU202223_06U | Ellie |
| 2022-02-24 | AU202122_23U | Anika |
| 2022-01-08 | AU202122_10U | Tiffany |
| 2021-12-23 | AU202122_08U | Seth |
| 2021-01-24 | AU202021_11U | Lucas |
| 2021-01-18 | AU202021_08U | (noname) |
| 2021-01-01 | AU202021_05U | Imogen |
| 2020-02-21 | AU201920_07U | Esther |
| 2020-02-03 | AU201920_05U | Damien |
| 2020-01-05 | AU201920_03U | Claudia |
| 2019-05-09 | AU201819_26U | Ann |
| 2019-05-05 | AU201819_25U | Lili |
| 2019-04-03 | AU201819_21U | Wallace |

Note the box is coarse: it also catches systems (Ilsa, Damien, Seth, Kirrily) whose NT relevance
is marginal, and it does not weight by intensity. A stricter selection would intersect the
gale-force wind radii with a community point rather than the track with a box.

**2.1.4 The four named NT storms this lane was asked about**, computed from the file
(`MAX_WIND_SPD` and `MAX_WIND_GUST` are in knots as stored):

| Storm | Disturbance ID | First → last fix | Fixes | Min central pres (hPa) | Max wind (kn) | Max gust (kn) |
|---|---|---|---|---|---|---|
| Marcus 2018 | AU201718_20U | 2018-03-14 00:00 → 2018-03-25 00:00 | 46 | 905 | 69.5 | 97.7 |
| Trevor 2019 | AU201819_20U | 2019-03-17 00:00 → 2019-03-27 18:00 | 46 | 944 | 51.4 | 72.0 |
| Megan 2024 | AU202324_09U | 2024-03-13 12:00 → 2024-03-21 06:00 | 35 | 950 | 46.3 | 64.3 |
| Fina 2025 | AU202526_02U | 2025-11-15 18:00 → 2025-11-26 06:00 | 60 | 938 | 54.0 | 74.6 |
| Ellie 2022–23 | AU202223_06U | 2022-12-21 06:00 → 2023-01-08 06:00 | 77 | 988 | 20.6 | 28.3 |
| Anika 2022 | AU202122_23U | 2022-02-24 → 2022-03-04 | 34 | 978 | 25.7 | 36.0 |
| Hayley 2025–26 | AU202526_08U | 2025-12-27 → 2026-01-01 | 25 | 953 | 46.3 | 64.3 |
| Mitchell 2026 | AU202526_21U | 2026-01-29 → 2026-02-10 | 53 | 963 | 38.6 | 54.0 |
| Narelle 2026 | AU202526_34U | 2026-03-15 → 2026-03-28 | 58 | 931 | 59.2 | 82.3 |

**There are four NT-box cyclones in the 2025–26 season** (Fina, Hayley, Mitchell, Narelle) plus
an unnamed December 2025 low — i.e. the hazard record is current to this season, not stale.

### 2.2 BoM cyclone history / impact pages

Index: `https://www.bom.gov.au/cyclone/tropical-cyclone-knowledge-centre/history/past-tropical-cyclones/`
(HTTP 200, 165,096 bytes). **Per-storm URLs are case-sensitive** and inconsistently cased:

| Storm | Page | Status | Formal PDF report |
|---|---|---|---|
| Marcus 2018 | `/cyclone/history/marcus.shtml` | 200 | **yes** — `/cyclone/history/pdf/Marcus_Report.pdf` (HTTP 200, `application/pdf`) |
| Trevor 2019 | `/cyclone/history/Trevor.shtml` | 200 | `Trevor_Report.pdf` → **404** |
| Megan 2024 | `/cyclone/history/megan2024.shtml` | 200 | `Megan_Report.pdf` → **404** |
| Fina 2025 | `/cyclone/history/Fina2025.shtml` (also `Fina.shtml`) | 200 | `Fina_Report.pdf` → **404** |

So **only Marcus has a formal BoM post-event report**; Trevor, Megan and Fina have summary
pages only. Verbatim impact text retrieved today:

- **Fina 2025:** *"Severe Tropical Cyclone Fina was a remarkable early season tropical cyclone…
  the most intense tropical cyclone to occur in the Australian region during November and also
  equalled the record for earliest landfall in a season by a cyclone on the Australian mainland."*
  … *"On 22 November, Fina intensified further into a severe (category 3) tropical cyclone as it
  moved to the west southwest through the Van Diemen Gulf over the southern tip of Melville
  Island (of the Tiwi Islands) and to the north of Darwin. **Wurrumiyanga on Bathurst Island
  (Tiwi Islands) was the worst affected community sustaining significant damage.** The greater
  Darwin region missed the very destructive core but still experienced damaging wind gusts
  estimated to 65 kn (120 km/h) that **caused widespread power outages mostly as a result of
  fallen trees**."* Peak intensity 105 kn 10-minute mean (high-end category 4) offshore.
  Wurrumiyanga is one of the 19 **microwave-backhauled** communities in §1.1.4.
- **Megan 2024:** *"Flooding forced the evacuation of many Borroloola residents."* …
  *"Flooding associated with ex-Tropical Cyclone Megan damaged major highways and several
  secondary roads along its path across the Northern Territory during late March."*
- **Trevor 2019:** *"More than 2000 people were evacuated to Darwin and Katherine from
  Alyangula, Borroloola, Numbulwar and Ngukurr in advance of Trevor making landfall…
  Localised flooding cut many roads in these districts, including the Tablelands, Sandover and
  Plenty Highways."*
- **Marcus 2018** (via BoM/secondary summary, `https://www.bom.gov.au/cyclone/history/marcus.shtml`
  and AIDR): strongest to affect Darwin since Tracy 1974; ~430 powerlines downed; ~26,500
  properties without power; 130 km/h gusts in Darwin, a March record 126 km/h at Darwin Airport.

### 2.3 Licence / terms — this is the constraint, not the data

`http://www.bom.gov.au/other/copyright.shtml` (HTTP 200), verbatim:

> *"Unless we state otherwise, you can download, copy and use our content for personal use, or
> use within your organisation. **You must not supply it to any other person or use it for any
> commercial purpose.**"*

and

> *"We do not allow you to access and/or use our content in a way that: … **we do not allow you
> to use automated or manual techniques to hack, scrape or otherwise extract material from our
> site.**"*

CC BY 4.0 is offered only *"If the content you're using is subject to this licence"* — i.e. per
page, not by default. **TBD — needs validation:** whether `IDCKMSTM0S.csv` specifically is
released under CC BY. Its own header says only "Copyright Commonwealth of Australia 2010 Bureau
of Meteorology". What would settle it: the tropical cyclone database page's own terms-of-use
statement (`http://www.bom.gov.au/cyclone/tropical-cyclone-knowledge-centre/databases/` —
**returned HTTP 403 to this lane, twice**), or a written answer from BoM's registered-user
service (`webreg@bom.gov.au`, the address the 403 page itself gives).

---

## 3. Evidence that NT telecommunications actually fail, and how

### 3.1 Cyclone Megan / Borroloola, March 2024 — the clearest documented causal chain

The New Daily, "Phone towers down as ex-tropical cyclone heads west", 22 March 2024
<https://www.thenewdaily.com.au/news/weather/2024/03/22/ex-tropical-cyclone-heads-west>
(HTTP 403 to WebFetch; HTTP 200 with browser User-Agent). Verbatim:

> *"Telstra regional general manager Nic Danks on Friday confirmed **two mobile base stations at
> Borroloola and nearby McArthur had lost power**."*
>
> *"**Our equipment in these remote locations are primarily powered by solar panels and the poor
> weather is limiting their ability to recharge the batteries**," he said.*
>
> *"**With roads closed, access to the area is by helicopter only at the moment and they are
> currently in high demand** … The high water levels in the area will also pose challenges for
> our crews to safely land in near proximity to our sites."*
>
> *"He said about **400 fixed line services were also offline at Bing Bong, Mallapunya and
> Borroloola**."*
>
> *"The Bureau of Meteorology believes major flooding had occurred at the McArthur River, but
> said **no recent river level observations were available** as of Friday morning."*

Four distinct mechanisms named in one article: (a) cyclone → cloud → solar recharge fails →
battery depletes → site down; (b) site down → 400 fixed services down; (c) road closure →
helicopter-only access → restoration delayed indefinitely; (d) telecom outage → **BoM flood
gauges stop reporting**, i.e. the hazard-monitoring system depends on the network that the
hazard takes out.

Second, independent source for the same event: ABC News, "Further evacuations out of Borroloola
ahead of major flooding from ex-Tropical Cyclone Megan", 21 March 2024
<https://www.abc.net.au/news/2024-03-21/borroloola-evacuations-flooding-ex-tropical-cyclone-megan/103608350>
(>100 evacuated to Darwin on the Wednesday). Community-side account: SBS NITV, "Borroloola
community suffers after inadequate emergency response to Cyclone Megan"
<https://www.sbs.com.au/nitv/article/borroloola-community-suffer-after-inadequate-emergency-response/g0pbm34f4>,
quoting Senator Malarndirri McCarthy that it was *"not good enough that in times of crises that
we've not been able to have thorough communication and this has caused further anxiety and
stress"*.

Borroloola and McArthur River both appear in the §1.1 NT backhaul file (Borroloola: Optic fibre;
McArthur River: Optic fibre) — so this was a **power** failure at a fibre-fed site, not a
backhaul failure. That distinction matters for any model that treats backhaul type as the only
failure mode.

### 3.2 Cyclone Trevor, March 2019

- BoM history page (§2.2): >2,000 evacuated from **Alyangula, Borroloola, Numbulwar, Ngukurr**.
- Power and Water Corporation, "Crews respond to ex-Tropical Cyclone Trevor"
  <https://www.powerwater.com.au/customers/safety-and-emergencies/updates/news-and-media/news/2019/crews-respond-to-ex-tropical-cyclone-trevor>
  — *"services were restored to Groote Eylandt, Bickerton Island, Ngukurr and Rittarangu"* as of
  late Sunday.
- Australian Disaster Resilience Knowledge Hub event record:
  <https://knowledge.aidr.org.au/resources/2019-cyclone-qld-and-nt-severe-tropical-cyclone-trevor/>
- **TBD — needs validation:** a *telecommunications-specific* statement for Trevor (how many
  base stations, how long). This lane found power-restoration statements but no carrier
  statement. What would settle it: Telstra's 2019 Exchange/media releases for March 2019, or the
  NT Government's post-event report.

### 3.3 Kalkarindji / Daguragu floods, 2023 — the date in the brief is wrong

The evacuation was **early March 2023**, not January 2023.
- NT Police, Fire & Emergency Services, "Emergency Declaration — Evacuation order for Daguragu,
  Kalkarindji, Pigeon Hole and Palumpa", 2023
  <https://pfes.nt.gov.au/newsroom/2023/emergency-declaration-evacuation-order-daguragu-kalkarindji-pigeon-hole-and-palumpa>
- ABC News, 1 March 2023
  <https://www.abc.net.au/news/2023-03-01/nt-kalkaringi-flooding-victoria-daly/102038966> and
  5 March 2023
  <https://www.abc.net.au/news/2023-03-05/nt-flooding-victoria-highway-kununurra-howard-springs-evacuation/102055904>
  — ~700 people relocated by air to Katherine then bus to Darwin; access roads cut; Daguragu
  isolated for two days.
- Victoria Daly Regional Council: <https://www.victoriadaly.nt.gov.au/emergency-declared-in-daguragu-and-kalkrindji/>
- **TBD — needs validation:** telecommunications outage specifics for this event. No source
  located that states whether the Kalkaringi tower stayed up. Kalkaringi is listed as **Optic
  fibre** in §1.1. What would settle it: a Telstra statement from March 2023, or an ACMA
  complaint/outage record for the period.

### 3.4 The nationwide Telstra outage of 8 July 2026 — a documented single point of failure

ABC News, "Telstra outage caused by failure to prioritise well-known network vulnerabilities",
2 September 2026
<https://www.abc.net.au/news/2026-09-02/telstra-outage-review-findings-known-network-issues-not-priority/107106588>

- The 8 July 2026 outage disrupted **~45% of all calls and data sessions** on Telstra's mobile
  network.
- Independent review by **Technology Audit Partners (TAP)**.
- Root cause: a **faulty power supply replacement reset a GPS card date to 2006**; the incident
  began at 2:50am, roughly an hour earlier than Telstra initially disclosed.
- *"The alarms that would usually alert staff to the error were only monitored during business
  hours by a limited number of people."* Two key engineers were on mandatory leave.
- Telstra *"did not treat its timing system as a priority, nor did it treat it as a high risk
  function"*; ABC reports Telstra had been warned for months about positioning-and-timing
  vulnerabilities by federal agencies and academics.
- **ACMA is investigating; fines up to $30 million** are possible. Communications Minister
  Anika Wells called the failures *"preventable"*.
- Live coverage of the event itself: <https://www.abc.net.au/news/2026-07-08/telstra-network-issues-internet-phones-live/106891206>
- **TBD — needs validation:** whether the TAP review report itself is public, and whether it
  breaks impact down by state/remoteness. The ABC article does not mention regional or remote
  impact. What would settle it: the ACMA investigation page, or Telstra's own publication of the
  TAP report.

### 3.5 ACMA outage rules — thresholds, and the natural-disaster carve-out

Primary sources, both retrieved today:

- <https://www.acma.gov.au/articles/2024-11/new-telco-industry-rules-major-outages>
  — `Telecommunications (Customer Communications for Outages) Industry Standard 2024`, made
  under the `Telecommunications (Customer Communications for Outages Industry Standards)
  Direction 2024`, **in effect 31 December 2024**, covering outages affecting **100,000 or more
  services**. Notification soon after the outage, then **at least once every six hours for the
  first 24 hours**. Made in response to the review of the **Optus network outage of 8 November
  2023**.
- <https://www.acma.gov.au/articles/2025-04/stronger-consumer-protections-during-telco-outages>
  — `Telecommunications (Customer Communications for Outages) Industry Standard Variation 2025
  (No.1)`, **commenced 30 June 2025**. Verbatim: *"The new rules announced today now cover
  outages that affect **1,000 or more services in regional Australia (for more than 6 hours)**
  and **250 or more services in remote Australia (for more than 3 hours)**."*
  Also on that page: `Telecommunications (Emergency Call Service) Amendment Determination 2025
  (No. 1)`, **commenced 1 November 2025**, which requires carriers to **"'wilt' a mobile base
  station in the event it loses connectivity to the core network** and the carriage of emergency
  calls is impacted — wilting means to prevent the mobile base station from providing any
  connectivity to mobile phones via that base station, so that emergency calls can be carried on
  another mobile carrier network if available."
- <https://www.acma.gov.au/network-outage-complaints> — verbatim: *"**Where a report relates to
  a network outage caused by a natural disaster, the requirements in the Standard will not
  apply.**"* Also restates the thresholds: major = *"last for longer than 1 hour and affect, or
  are likely to affect, at least 100,000 services, or all services in a State or Territory"*;
  significant local = *"outages in a regional area that are likely to affect at least 1,000
  services for at least 6 hours. In remote areas, they are outages that are likely to affect at
  least 250 services for at least 3 hours."*

Two things follow for a failure model. First, **"250 services / 3 hours in remote Australia" is
a published, citable NT-applicable severity threshold** a model can be calibrated against.
Second, **cyclone- and flood-caused outages are explicitly carved out** of the complaint-handling
standard — the exact events this lane studies are the ones the rules do not reach.

### 3.6 Is any outage dataset public?

**No public outage dataset was located.** Carriers report to ACMA; the reports are not published
as data. A secondary source (Bird & Bird, "Spotlight on Australia's outages and emergency call
services regulation", <https://www.twobirds.com/en/insights/2025/australia/spotlight-on-australia's-outages-and-emergency-call-services-regulation>)
states carriers must give ACMA and DITRDCA a written report **within 45 days** of a major
outage. **TBD — needs validation:** the 45-day figure against the instrument text on the Federal
Register of Legislation, and whether ACMA publishes any aggregate outage statistics. What would
settle it: the registered instrument
`Telecommunications (Customer Communications for Outages) Industry Standard 2024` on
legislation.gov.au, and ACMA's "Action on telco consumer protections" quarterly reports
(e.g. <https://www.acma.gov.au/publications/2025-08/report/action-telco-consumer-protections-april-june-2025>,
not opened by this lane).

Crowd-reported outage trackers exist (`geoblackout.com/au/report/internet/telstra`,
`aussieservicedown.com`) but are third-party, unlicensed for reuse and not a published source —
they would not satisfy a "real data only, traceable to a published source" constraint.

### 3.7 RTIRC 2024 — resilience findings, including the NT Government's own words

`2024 Regional Telecommunications Review: Connecting communities, reaching every region`,
delivered and tabled **13 December 2024**, 154-page PDF (HTTP 200, 12,130,011 bytes),
licence **CC BY 4.0** (stated in the front matter), ISBN 978-1-922879-67-7:
<https://www.infrastructure.gov.au/sites/default/files/documents/2024-regional-telecommunications-review.pdf>
Announcement page: <https://www.rtirc.gov.au/news-and-media/2024-regional-telecommunications-review-report-now-available>
(14 recommendations).

Extracted verbatim:

- **NT Government submission**, quoted in the report: *"Programs such as the **Mobile Network
  Hardening Program (MNHP) have targeted MNOs, enabling them to determine priority areas that
  are not necessarily based on highest needs.** While this funding is appreciated, the Australian
  Government should evaluate whether telecommunications companies could independently fund
  resilience upgrades as part of their regular operations. **Government funding should prioritise
  areas where network hardening is most urgently required (based on outage data analysis)** and
  look for solutions that support resilience across all telecommunications services in a location
  or region."* — i.e. the NT Government has publicly asked for hardening investment to be
  prioritised by analysis rather than by carrier choice.
- **Committee's own position:** *"**Days, rather than hours, of backup capability should be the
  target**, especially as advancements in renewable and battery technologies make this
  increasingly feasible."*
- **Recommendation 13: Powering connectivity** — *"The Committee recommends that regulation be
  introduced to require: • **minimum backup power periods for new critical telecommunications
  infrastructure installations in regional, rural and remote Australia**, with existing assets to
  be captured over time … • energy providers to give **high priority to restorations of power for
  critical telecommunications infrastructure** … • energy providers to prioritise energy
  connections for new telecommunications installations."*
- **Recommendation 6** proposes a **national telecommunications data platform** managed by ACMA
  or ACCC; the surrounding text records submissions asking that *"operators … provide consistent,
  standardised data to the government"*.
- **Recommendation 10** covers community Wi-Fi hubs and continued funding for **STAND** facilities.
- On the scale of the gap: *"**43% of First Nations communities are outside any mobile
  coverage**."*
- On delivery: *"The delivery process is understandably complicated, involving site acquisition
  and access, supply chains, power and backhaul connections, weather contingencies … Other
  obstacles typically include events such as **cyclones or bushfires, wet season conditions
  including flooding**, supply chain delays, workforce shortages…"*
- A comparable-scale precedent the report cites: after **STC Seroja (April 2021)** in WA's Mid
  West, DFES reported 6,000 properties without power and **a loss of 186 mobile base stations**.
- The phrase **"single point of failure" does not appear anywhere in the 154-page report** (zero
  matches). The report frames resilience as backup power and redundancy, not as topology.

---

## 4. Power dependency

### 4.1 Mobile Network Hardening Program — per-site backup hours, downloadable

- Dataset: <https://data.gov.au/data/dataset/mobile-network-hardening-program-mnhp-round-1>
  Licence **Creative Commons Attribution Share Alike 4.0 International**;
  `metadata_created` 2023-10-10, **`metadata_modified` 2026-09-10** (two days before this check).
- Resources: two KMLs, a WMS, a WFS, and a GeoJSON endpoint
  (`https://data.gov.au/geoserver/mobile-network-hardening-program-mnhp-round-1/wfs?request=GetFeature&typeName=ckan_f373655b_e701_43c8_9972_750a3004e66b&outputFormat=json`).
  Stage 1 KML 2,411,655 B (932 placemarks); Stage 2 KML 2,575,861 B (1,000 placemarks).
- Program description, verbatim: MNHP *"assists the mobile network operators … to improve the
  resilience of Australia's regional mobile network telecommunications infrastructure to: prevent
  outages in the event of a Natural Disaster; strengthen the resilience of telecommunications
  facilities to allow them to operate for longer during bushfires and other Natural Disasters;
  and/or enable the rapid restoration of services following an outage."* Round 1 is
  **$23.5 million** across two stages, ~1,000 projects. Stage 1 funds battery backup at **466
  base stations funded under MBSP rounds 1 and 2**, *"to increase backup operation at these base
  stations to **at least 12 hours**"*. Stage 2 funds **530+ resilience upgrades** including
  portable and permanent generators.
- **Stage 1 has a per-site field `Backup Power Capcity after upgrade (Hours)`** (misspelling in
  the source). National distribution: `≥12` 682, `12` 146, `15` 104. **This is the only
  machine-readable per-site backup-duration figure this lane found.**
- **NT content is thin.** Stage 1: **2 NT placemarks**, both Telstra at **Minjilang**
  (−11.1524, 132.5694 and −11.1479, 132.5740), both "Lead-acid Battery Upgrade", both `≥12`
  hours. Stage 2: **12 NT placemarks** — Portable Generator 8, Permanent Generator 4 — at
  Humpty Doo (Optus), Katherine CBD (Optus), Alice Springs (Telstra), Darwin (Telstra),
  Katherine (Telstra), Nhulunbuy (Telstra) and others; Stage 2 carries **no backup-hours field
  at all**.
- Other Stage 2 upgrade types nationally include "Site Hardening", described as *"A range of
  hardening measures targeting sites identified by a **CSIRO bushfire threat analysis**. Specific
  measures at each site are based on the outputs of a detailed site survey tool…"* — a precedent
  for hazard-model-driven site prioritisation, but bushfire, not cyclone.
- Minjilang is also one of the 19 **microwave-backhauled** communities (§1.1.4) and an MBSP
  Round 1 NT site (§1.4) — the three datasets do join on community name.

### 4.2 STAND — 88 NT Sky Muster sites, with names and coordinates

ArcGIS layer, queried directly:
`https://spatial.infrastructure.gov.au/server/rest/services/Strengthening_Telecommunications_Against_Natural_Disasters/MapServer/1/query?where=Jurisdiction='NT'&outFields=*&f=json`

- Layer 1 = "Sky Muster Satellite Deployments"; fields `Site_ID, Jurisdiction, LGA, Site_Name,
  Site_Address, Public_Access` + point geometry.
- **88 NT sites**, complete result (`exceededTransferLimit` unset). `Public_Access`: **Yes 83,
  "No - Emergency Services Only" 5**.
- By LGA: Victoria Daly 14, Roper Gulf 12, East Arnhem 10, West Arnhem 9, West Daly 8,
  Unincorporated NT 7, MacDonnell 7, Tiwi Islands 6, Groote Archipelago 4, Central Desert 3,
  Coomalie 2, Unincorporated 2, Litchfield 1, Barkly 1, Wagait 1.
- Site IDs are `NT001`…; the sites are overwhelmingly **schools** (Adelaide River School,
  Alyangula Area School, Alyarrmandumanja Umbakumba School, Amanbidji School, Angurugu School…).
  This is a satellite-backed fallback layer that is topologically independent of the terrestrial
  backhaul graph.
- Program scale (media release, 2024): STAND has installed NBN Sky Muster connections at
  **1,068 locations Australia-wide**; a further **$14 million** adds community Wi-Fi to 500 more
  sites and extends existing sites four years beyond 2025
  <https://www.infrastructure.gov.au/department/media/news/more-funding-emergency-community-wi-fi-services>.
  Interactive map: <https://experience.arcgis.com/experience/387708c2c6bc44f09cda5167aa1dff68/page/Strengthening-Telecommunications-Against-Natural-Disasters-(STAND)>
- **Licence: TBD — needs validation** (same gap as §1.3 — no licence statement retrieved for the
  ArcGIS service).

### 4.3 Remote community power — Power and Water Corporation / Indigenous Essential Services

`Indigenous Essential Services Annual Report 2024–25`, 84-page PDF, 11,275,341 bytes
(HTTP 403 on a bare request; HTTP 200 with a browser `User-Agent` and a `Referer`):
<https://www.powerwater.com.au/__data/assets/pdf_file/0032/428549/2025-Indigenous-Essential-Services-Annual-Report.pdf>
Prior year: <https://www.powerwater.com.au/__data/assets/pdf_file/0031/376654/PWC_IES-Annual-Report_23-24.pdf>

- Verbatim, twice in the report: IES serves **"72 remote communities and 79 outstations"**.
- Secondary (Power and Water "Remote power sources" page,
  <https://www.powerwater.com.au/about/what-we-do/power-networks-and-supply/remote-power-sources>):
  IES supplies **>100 GWh** to 72 communities and operates **51 diesel-fired power stations,
  ~80 MW installed**. **TBD — needs validation** against the report body; this lane confirmed the
  72/79 figure in the PDF but not the 51/80 MW figures.
- Solar: **NT SETuP** installed 10 MW of solar PV across **25 sites serving 27 communities**
  (ARENA, <https://arena.gov.au/knowledge-bank/nt-setup-a-first-look-at-the-integration-of-pv-and-diesel-power-stations-in-remote-communities/>).
  The 2024–25 report adds the **Wurrumiyanga Solar Infill and Energy Storage Pilot**: 1.1 MW
  solar array, **1.75 MVA / 3 MWh battery storage**, saving 519,000 L of diesel in year one.
- **A reverse dependency, verbatim from the report:** *"The feedback came during a community
  visit due to a **Telstra outage affecting power meters**"* at Maningrida — the electricity
  metering depends on the telecommunications network, not only the other way round.
- **The report publishes no per-community outage counts, no SAIDI/SAIFI, and no restoration
  times.** **TBD — needs validation:** whether AER regulatory reporting for Power and Water's
  distribution network
  (<https://www.aer.gov.au/industry/networks/entities/service-providers/power-and-water-corporation>)
  publishes remote-community reliability metrics. What would settle it: the AER Regulatory
  Information Notice responses or Power and Water's annual regulatory performance report.
- **TBD — needs validation:** a published Telstra or ACMA statement of **typical battery backup
  duration at an un-upgraded remote NT site**. The only hard numbers found are the MNHP
  post-upgrade targets (§4.1: 12 / ≥12 / 15 hours) and the RTIRC committee's aspiration
  ("days, rather than hours"). What would settle it: Telstra's submission to RTIRC 2024, or the
  Telecommunications in New Developments / carrier resilience statements.

---

## 5. Methods: published graph / network-resilience analyses reproducible with NetworkX

### 5.1 Knight et al., "The Internet Topology Zoo" — the data source most directly NetworkX-ready

- Knight, S., Nguyen, H.X., Falkner, N., Bowden, R., Roughan, M. **IEEE Journal on Selected
  Areas in Communications**, Oct 2011, 29(9), 1765–1775. DOI `10.1109/JSAC.2011.111002`.
  Author preprint: <https://roughan.info/papers/jsac_2011b.pdf>
- **Australian** — University of Adelaide, ARC Discovery grants DP110103505 and DP0985063.
- **What data:** >250 real telecommunications networks transcribed from operators' published
  maps into **GraphML and GML**, explicitly *"can be read by NetworkX"*.
- **The canonical host `topology-zoo.org` is down as of 2026-09-12** — both
  `http://www.topology-zoo.org/dataset.html` (connection refused, `ECONNREFUSED 129.127.10.249:443`)
  and `https://topology-zoo.org/files/Aarnet.graphml` (connection timeout).
- **The GitHub long-term data store is live**: <https://github.com/mroughan/InternetTopologyZoo>,
  last pushed **2026-05-24**, ~285 MB, **LICENSE = Creative Commons Attribution 4.0 International**,
  with a `CITATION.cff`. The `graphml/` directory holds **276 files**. `Aarnet.graphml` downloads
  at `https://raw.githubusercontent.com/mroughan/InternetTopologyZoo/master/graphml/Aarnet.graphml`
  (HTTP 200, 11,378 bytes, valid GraphML with `LinkLabel` edge attributes). Australian entries:
  **`Aarnet.graphml` and `Nextgen.graphml`** — no Telstra or Optus topology.
- Relevance to this lane: it is a worked precedent for *transcribing a published operator map
  into a graph*, which is what §1.1's community list would require; it does not supply NT data.
- Practical note: **`networkx` is not installed in the Python 3.13 environment on this machine**
  (`ModuleNotFoundError: No module named 'networkx'`); `openpyxl` 3.1.5 and `pypdf` are.

### 5.2 Oughton et al., "Global Vulnerability Assessment of Mobile Telecommunications
Infrastructure to Climate Hazards using Crowdsourced Open Data"

- Edward J. Oughton, Tom Russell, Jeongjin Oh, Sara Ballan, Jim W. Hall.
  arXiv:2311.04392, submitted **7 November 2023**, v1.  <https://arxiv.org/abs/2311.04392>
- **What data:** **7.6 million 2G/3G/4G/5G cell assets** from open crowdsourced sources,
  intersected with **tropical cyclone** and **coastal flood** hazard layers at stated annual
  exceedance probabilities.
- **Headline results:** at 0.01% annual probability under a high-emissions scenario, **2.26
  million cells affected by tropical cyclones (USD 1.01 bn damage)** and **109.9 thousand cells
  affected by coastal flooding (USD 2.69 bn damage)**.
- This is the closest published method to "cells × cyclone hazard", and it is asset-exposure
  rather than topology — it counts cells in the footprint, it does not compute what a lost link
  disconnects.
- **TBD — needs validation:** whether a code/data repository or a peer-reviewed journal version
  exists. The arXiv abstract page names neither. What would settle it: the paper's own
  data-availability statement (PDF not opened by this lane), or Oughton's GitHub.

### 5.3 Sterbenz et al., "Resilience and survivability in communication networks: Strategies,
principles, and survey of disciplines"

- Sterbenz, J.P.G., Hutchison, D., Çetinkaya, E.K., Jabbar, A., Rohrer, J.P., Schöller, M.,
  Smith, P. **Computer Networks** 54(8), 2010, 1245–1265. DOI `10.1016/j.comnet.2010.03.005`
  <https://dl.acm.org/doi/10.1016/j.comnet.2010.03.005>
- **What it supplies:** the standard vocabulary and the **two-dimensional resilience state
  space** (operational state vs service state) used to *define* a resilience metric, plus the
  D²R²+DR strategy (Defend, Detect, Remediate, Recover, Diagnose, Refine). Not a dataset; the
  citation that lets a metric be named rather than invented.
- It uses no open dataset — it is a framework/survey paper. Any reproduction supplies its own
  topology.

### 5.4 Others located but not verified in depth

- "Critical node identification and resilience analysis against cascading failures", **PLOS ONE**
  (2026), <https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0344005>
- "Resilience evaluation of communication infrastructure networks under multi-scenario disaster
  simulations", **Reliability Engineering & System Safety** (online Feb 2026),
  <https://www.sciencedirect.com/science/article/abs/pii/S0951832026002474> — hurricanes,
  earthquakes, floods; explicitly models physical damage propagating upward into service
  degradation.
- "Critical Nodes Identification in Complex Networks: A Survey", arXiv:2507.06164,
  <https://arxiv.org/pdf/2507.06164>
- **TBD — needs validation** for all three: the datasets used and whether code is released.
  None is Australian.

---

## 6. Wet-season road closures as a proxy hazard

### 6.1 roadreport.nt.gov.au has an undocumented public JSON API — current state only

The site is an Angular single-page app; the API base is `api/{Controller}/` and the controllers
found in the JS bundle (`main.47bd91e6a1a678ce.js`, 1,504,149 bytes) are `Obstruction`,
`Announcement`, `SystemOutageMessage`, with methods `getObstructions() → get("GetAll")`,
`getMajorRoadObstructions() → post("GetAllMajorRoadObstructions")`, and
`downloadReport() → GetObstructionsReportPdf`.

- **`https://roadreport.nt.gov.au/api/Obstruction/GetAll`** returns **HTTP 200,
  `application/json`, 60,328 bytes** with no authentication.
- Envelope: `{$id, response[], success, message}`. **80 records today.**
- Per-record fields: `recordId, obstructionId, status, road, roadName, lane, prpFrom,
  distanceFrom, prpTo, distanceTo, obstructionType, obstructionTypeCode, restrictionType,
  restrictionTypeCode, dateFrom, dateTo, dateActive, dateLastUpdated, startPoint [lat,lon],
  endPoint [lat,lon], comment, locationComment, isDefaultLocationComment, geometry, geometries,
  reversed`.
- **All 80 records have `status: "CURRENT"`** — the endpoint returns the live state, not history.
- `obstructionType` today (**12 September = late dry season**): Roadworks 25, "Maximum Gvm 4.5
  Tonne, Light Vehicles Only" 15, Changing Surface Conditions 15, Road Damage 11, Park Facilities
  Closed 4, **Flooding 3**, Changed Traffic Conditions 2, and six single-record weight/axle
  restriction types.
- `dateFrom` spans 2018-06-20 to 2026-09-11 — i.e. some "current" restrictions are permanent
  standing restrictions, not events.
- Candidate endpoints `api/roads`, `api/RoadReport`, `api/RoadClosures`, `api/incidents`,
  `api/Obstruction` (without `/GetAll`) all return **HTTP 404**.
- **Terms of use: TBD — needs validation.** This endpoint is undocumented, is not listed on
  data.nt.gov.au, and carries no licence. Using it is not obviously sanctioned. What would
  settle it: the Road Report NT terms page, or a data.nt.gov.au listing for road conditions.

### 6.2 Wayback is too sparse to reconstruct a wet-season time series

CDX query
`https://web.archive.org/cdx/search/cdx?url=roadreport.nt.gov.au/api/Obstruction/GetAll&output=json`:

- **19 captures total**, first **2021-09-06**, last **2026-01-06**.
- By year: 2021 × 1, 2022 × 13, 2023 × 3, 2024 × 1, 2026 × 1. **Zero in 2025.**
- **9 distinct months**, of which **7 fall in a wet-season month (Nov–Apr)**: 2022-02, 2022-03,
  2022-11, 2023-03, 2023-11, 2024-01, 2026-01. Several of the 2022 captures are minutes apart
  and byte-identical.
- That is not a time series — it is ~7 wet-season snapshots across five seasons. A daily-closure
  history for the NT **cannot** be reconstructed from Wayback.
- The site as a whole has captures back to **2003-12-25** (`http://www.roadreport.nt.gov.au/`),
  but those are pre-SPA HTML pages with a different structure.

### 6.3 National historical road closure databases

- **National Freight Data Hub**, "Roadworks and Road Closures":
  <https://datahub.freightaustralia.gov.au/explore/interactives/Roadworks%20and%20Road%20Closures>
  — described as sourced daily from *"state and territory governments' open data feeds"*,
  standardised nationally, *"shows where roadworks or road closures are in place, **or have
  occurred in the past**"*. **The page returned HTTP 502 to this lane.**
- **National Road Safety Data Hub**, same product:
  <https://datahub.roadsafety.gov.au/safe-systems/safe-roads/roadworks-and-road-closures>
- **DITRDCSA Data Catalogue**, "Road Report Northern Territory":
  <https://catalogue.data.infrastructure.gov.au/dataset/road-report-northern-territory>
- **TBD — needs validation, and this is the single most consequential gap in section 6:** whether
  the national hub's **historical** roadworks/closures data is downloadable (CSV/API), what its
  temporal coverage for the NT is, and its licence. What would settle it: retrying the Freight
  Data Hub page (it 502'd today, so it may simply have been down), or the DITRDCSA catalogue
  record's resource list.

### 6.4 BoM flood warning history

- Live NT flood warning products exist per catchment (e.g. Daly River
  <http://www.bom.gov.au/nt/warnings/flood/daly-river.shtml>; NT rainfall/river index
  <https://www.bom.gov.au/nt/flood/rain_river.shtml>; NT Government flood monitoring
  <https://nt.gov.au/environment/water/water-in-the-nt/flooding-and-storm-surge/flood-monitoring>).
- **TBD — needs validation:** whether BoM publishes an **archive** of issued flood warnings (as
  opposed to current warnings and raw river-height observations). No archive product was located.
  What would settle it: BoM's Water Data Online / `bom.gov.au/waterdata` service, or the
  registered-user FTP catalogue (`http://www.bom.gov.au/catalogue/anon-ftp.shtml`) —
  note `ftp.bom.gov.au:80` **failed to connect** from this machine today.
- Independent corroboration of the mechanism already exists without the archive: §3.1 records
  BoM itself losing river-level observations during Megan because the telecommunications link
  failed.

---

## Other facts found

1. **The 2019 NT backhaul file and the ACCC 2025 site file cannot be joined on a key.** The NT
   file has no `RFNSA ID`; the ACCC file has no community name. Joining them requires a spatial
   nearest-neighbour match between 64 community points and 422 NT site points, which is an
   assumption, not a lookup.
2. **The ACCC data's reference date is 31 January each year** (per the ACCC's own data-release
   description), so the "2025" file is a 31 January 2025 snapshot — it predates Cyclone Fina
   (November 2025) by nine months.
3. **`Mobile sites - Optus-TPG MOCN - 2025` is new in the 2025 release.** MOCN sharing means a
   single physical failure removes two nominally independent carriers at once — a correlated
   failure that a naive per-carrier model would score as two independent redundant paths.
4. **The ACCC site files carry a `Co_funded` flag and a `Round` field**, so publicly subsidised
   NT sites (59 of 247 Telstra NT sites in 2025) are separable from commercially built ones.
5. **`Mobile_Coverages_and_Sites_ACCC` and `ACCC_Mobile_Sites_and_Coverages` both exist** as
   ArcGIS MapServers at `https://spatial.infrastructure.gov.au/server/rest/services` alongside
   `Communication_Program_Eligibility_Areas`, `Peri_Urban_Mobile_Program_PUMP_Round_1/2`,
   `NBN_Coverage_Footprints_2024` and `Main_Audit_Roads_DITRDCA_2024` (the National Audit of
   Mobile Coverage drive-test road layer). Full service list retrieved today.
6. **`peri-urban-mobile-program-eligible-funding-areas`** (CC BY 4.0) was modified 2026-09-10 —
   the DITRDCSA data.gov.au collection is actively maintained, but PUMP is peri-urban and
   therefore not NT-remote.
7. **The MBSP bulk ZIP ships only KML, not CSV or GeoJSON.** Attributes live in
   `<SimpleData name="...">` elements inside `<ExtendedData>`; the human-readable `<description>`
   CDATA duplicates them as an HTML table. Field names differ between rounds (`Electorate_2022`
   in R1–R5A vs `Electorate` in R6/R7), so a per-round schema map is required.
8. **MBSP NT Round 2, 4 and 5 sites are overwhelmingly tourism/roadhouse locations** — Bark Hut
   Inn, Devils Marbles Hotel, Kings Canyon Resort, Florence Falls, Wangi Falls, Cahills Crossing,
   Mary River Roadhouse, Edith Falls — not remote Aboriginal communities. The community-serving
   NT sites concentrate in Round 1 (Finke, Imanpa, Minjilang, Mt Liebig, Wallace Rockhole) and
   Round 7's six `Solution_category = "First Nations"` sites.
9. **Cyclone Fina's landfall equalled the record for earliest cyclone landfall on the Australian
   mainland** (21 November, tying STC Ines 1973) and was the most intense November cyclone in the
   Australian region on record — i.e. the 2025–26 season falls outside the historical seasonal
   envelope a naive Nov–Apr window assumes.
10. City of Darwin's own Fina page exists
    (<https://www.darwin.nt.gov.au/community/disaster-emergency/cyclones/cyclone-fina-2025>) and
    a secondary source reports ~19,000 properties without power and no fatalities; SecureNT
    published at least **26 numbered updates** for the event
    (`securent.nt.gov.au/respond/november-2025-tropical-cyclone-fina/update-N-tropical-cyclone-fina`).
11. **SecureNT is unreadable by automated retrieval.** Every attempt returned either HTTP 403 or
    a Cloudflare `"Just a moment... Enable JavaScript and cookies to continue"` interstitial.
    The Fina update pages also exist under **three different URL paths** simultaneously
    (`/respond/...`, `/recover-from-an-emergency/ex-tropical-cyclone-fina/...`,
    `/recover-from-an-emergency/active-recoveries-past-events/...`), so any citation must record
    which path resolved.
12. **RMIT published a media comment on 2026-04 headed "Mobile coverage maps fall short for
    regional Australia, expert says"** (<https://www.rmit.edu.au/news/media-releases-and-expert-comments/2026/apr/coverage-maps>) —
    surfaced incidentally while searching for the NT dataset; not opened by this lane.
13. **The 2025 Optus emergency calling outage** has a Wikipedia article
    (<https://en.wikipedia.org/wiki/2025_Optus_emergency_calling_outage>) — a second recent
    national-scale Australian outage event alongside §3.4, not investigated here.
14. **ACMA's `Telecommunications (Emergency Call Service) Amendment Determination 2025 (No. 1)`
    (from 1 Nov 2025) also requires carriers to "prevent the provider's network from impeding
    their customers' emergency calls being carried on another network during an outage"** —
    i.e. cross-carrier emergency-call failover is now a legal obligation, which changes what
    "disconnected" means for a community served by more than one carrier.

---

## TBD — needs validation

Each item states what is unknown and what would settle it.

| # | Unknown | What would settle it |
|---|---|---|
| 1 | Whether DCDD holds link-level backhaul topology (hop endpoints, repeater sites, fibre routes) for the NT. The 2019 file has type-per-community only. | Direct request to the named custodian (`officeofdigitalgovernment.DCIS@nt.gov.au`, Barry Garside, 08 8924 3840); or an NTLIS/NTG spatial layer naming link endpoints. |
| 2 | Whether the 2019 backhaul types are still accurate. RCP Round 1–3 delivered 16 "Fibre Backhaul" NT projects completed Mar 2023 – Jan 2026, after the file was last touched. | Cross-reading RCP `Project_Description` per NT record against the 64 community names; or a refreshed DCDD dataset. |
| 3 | Licence and terms for the ArcGIS layers (RCP, STAND, MNHP WMS, ACCC mobile sites) on `spatial.infrastructure.gov.au`. No licence statement was retrievable; CKAN search returned `count: 0` for RCP on both data.gov.au and the DITRDCSA catalogue. | The MapServer root `?f=json` `copyrightText` / `licenseInfo` fields; or the Communications Programs Mapping Tool item metadata. |
| 4 | Whether `IDCKMSTM0S.csv` specifically is CC BY, and whether bundling it into an offline prototype is permitted given BoM's default "not for supply to any other person, not for commercial purpose" terms and its explicit anti-scraping clause. | The TC knowledge-centre databases page terms (HTTP 403 to this lane, twice); or a written answer from `webreg@bom.gov.au`. |
| 5 | Whether ACMA publishes any outage data or aggregate outage statistics, and whether the "45 days" carrier reporting deadline is correct (currently sourced only to a law-firm commentary). | The registered instrument text on legislation.gov.au; ACMA's quarterly "Action on telco consumer protections" reports. |
| 6 | Telecommunications-specific outage evidence for Cyclone Trevor (2019) and the March 2023 Kalkarindji/Daguragu floods. Power restoration and evacuation are documented; tower status is not. | Telstra Exchange/media releases for March 2019 and March 2023; NT Government post-event reports; or an FOI/direct request. |
| 7 | Whether the Technology Audit Partners review of the 8 July 2026 Telstra outage is public, and whether it breaks impact down by state or remoteness. | The ACMA investigation page; Telstra's own publication of the TAP report. |
| 8 | Typical battery backup duration at an **un-upgraded** remote NT mobile site. Only post-MNHP-upgrade figures (12 / ≥12 / 15 h) and an aspiration ("days, rather than hours") are published. | Telstra's RTIRC 2024 submission; AMTA or carrier resilience statements; ACMA technical reporting. |
| 9 | Per-community electricity reliability for the 72 IES communities (outage counts, durations, restoration times). The IES annual report publishes none. | AER regulatory information notice responses for Power and Water; Power and Water regulatory performance reporting. |
| 10 | Whether the national Freight Data Hub / Road Safety Data Hub historical roadworks-and-closures database is downloadable for the NT, its temporal coverage and its licence. **The page returned HTTP 502 today** — it may simply have been down. | Retry `https://datahub.freightaustralia.gov.au/explore/interactives/Roadworks%20and%20Road%20Closures` and the DITRDCSA catalogue record `road-report-northern-territory`. |
| 11 | Terms of use for the undocumented `roadreport.nt.gov.au/api/Obstruction/GetAll` endpoint. | A Road Report NT terms page; or a data.nt.gov.au listing for NT road conditions. |
| 12 | Whether BoM publishes an archive of **issued flood warnings** (not just current warnings and raw gauge data). `ftp.bom.gov.au:80` failed to connect today. | BoM Water Data Online; the anon-FTP catalogue (`http://www.bom.gov.au/catalogue/anon-ftp.shtml`). |
| 13 | Whether any NBN product publishes NT **Points of Interconnect or transit route geometry** (which is what would turn NBN data into graph edges rather than coverage polygons). | The resource list of `https://data.gov.au/data/dataset/national-broadband-network`. |
| 14 | Any published Telstra regional fibre route map for the NT. | Telstra InfraCo / Amplitel network publications. |
| 15 | Data-availability and code repository for Oughton et al. (arXiv:2311.04392), and whether a peer-reviewed version exists. | The paper PDF's data-availability statement; the authors' GitHub. |
| 16 | Whether Cyclone Fina caused documented NT mobile site outages, how many, and for how long — the single most valuable missing evidence item, because Fina is the most recent and most severe NT event and it struck Wurrumiyanga, a microwave-backhauled community. | SecureNT Fina updates 1–26 (blocked by Cloudflare to automated retrieval — would need manual browser access); Telstra/Optus statements from 22–30 November 2025; ABC NT coverage from that week. |

---

## Retrieval log — what refused, and how

| Source | Result |
|---|---|
| `data.nt.gov.au` (CKAN + XLSX + PDF) | 200, no obstacles |
| `data.gov.au` (CKAN + CSV + ZIP + KML) | 200, no obstacles |
| `spatial.infrastructure.gov.au` ArcGIS REST | 200, no obstacles, full result sets |
| `roadreport.nt.gov.au` API | 200, undocumented |
| `web.archive.org` CDX | 200 (one transient 503, succeeded on retry) |
| `github.com` / `raw.githubusercontent.com` | 200 |
| `www.infrastructure.gov.au` (RTIRC PDF) | 200 |
| `www.acma.gov.au` | 200 with browser User-Agent |
| `www.bom.gov.au` | **403 to default request**, 200 with browser User-Agent |
| `www.powerwater.com.au` (PDF) | **403 to default request**, 200 with User-Agent + Referer |
| `www.thenewdaily.com.au` | **403 to WebFetch**, 200 with browser User-Agent |
| `securent.nt.gov.au` | **403 / Cloudflare JS interstitial — not retrievable** |
| `topology-zoo.org` | **connection refused / timeout — host down** |
| `ftp.bom.gov.au:80` | **connection failed** |
| `datahub.freightaustralia.gov.au` | **502 Bad Gateway** |
| `catalogue.data.infrastructure.gov.au` CKAN API | 200 but `count: 0` for RCP and STAND |
