# Arena lane A — "reconcile": source-agreement counting from published datasets

Research lane A. Mechanism under investigation: for each remote NT community, count how many
independent published sources assert coverage — carrier predicted-coverage polygons (ACCC data
release 2018–2025), NT Government coverage lists (2019/2021/2022), and presence of a licensed
mobile base station within N km (ACMA RRL) — plus the 2018→2025 trend per community.
Lane constraint: already-published official datasets only; no new measurement, no user input.

All findings checked **2026-09-12** unless stated otherwise. Every HTTP probe below was executed,
not inferred; byte sizes and timings are measured values from this machine.

Machine note (2026-09-12): `lxml` 6.1.3, `openpyxl` 3.1.5 and `pypdf` are installed on this
machine's Python 3.13 (`D:\Dev\Python\313`). **`shapely`, `geopandas`, `fiona`, `pyogrio`,
`pandas` and `pyproj` are NOT installed.** Every measurement below was therefore taken with the
standard library plus `lxml`. No packages were installed during this research.

---

## Q1 — ACCC Mobile Infrastructure Report data release: resources, formats, sizes, licence, geometry

**1.1 The CKAN API works; the HTML page was not needed.**
`https://data.gov.au/data/api/3/action/package_show?id=accc-mobile-infrastructure-report-data-release`
returned HTTP 200, 122,865 bytes. No 403, no user-agent spoofing, no mirror required. The
researchdata.edu.au API was probed (`https://researchdata.edu.au/api/v1.0/search`) and returned
HTTP 400 "Class search version v1.0 is not recognised as a valid method" — the mirror's record
exists as an HTML page (`https://researchdata.edu.au/accc-mobile-infrastructure-8211-release/3797170`)
but was not needed. The ACCC's own site returned **HTTP 403 to curl** on a PDF fetch
(`https://www.accc.gov.au/system/files/Regional%20Mobile%20Infrastructure%20Inquiry%20final%20report.pdf`),
confirming accc.gov.au blocks automated fetch; data.gov.au does not.

**1.2 Dataset-level metadata.** Checked 2026-09-12.
- Dataset id `4b472a18-d0fa-409c-994a-ab17162bcb90`, name `accc-mobile-infrastructure-report-data-release`
- Publisher: Australian Competition and Consumer Commission; authors listed as ACCC, Singtel Optus, Telstra, TPG Telecom
- Contact: `datastrategy@accc.gov.au`
- **Licence: Creative Commons Attribution 2.5 Australia** (`license_id: cc-by-2.5`,
  `http://creativecommons.org/licenses/by/2.5/au/`). Note CKAN reports `isopen: false` for this
  dataset despite the CC-BY licence string — a metadata inconsistency, not a stated restriction.
- `metadata_created` 2021-10-26; `metadata_modified` 2026-06-14. Newest **resource** last-modified
  is 2025-11-10 — i.e. the current content is the **2025 release**, covering reporting years 2018–2025.
- **138 resources**: 70 KML, 41 ZIP, 25 CSV, 2 PDF.

**1.3 Format: KML, one file per carrier per technology per coverage-standard per year.**
Not one file per carrier per technology per year — the **coverage standard** is a fourth axis.
Two standards appear in the file names: `Outdoor` and `Ext Ant` (external antenna). ZIP resources
are zipped KML, used inconsistently — the same logical product is a bare `.kml` in one year and a
`.zip` in another (e.g. Optus 3G Outdoor is ZIP for 2018/2019/2021/2023 but KML for 2020/2024/2025).
Any loader must handle both.

Resource families present:
- `Mobile sites - <MNO> - <year>` — 25 CSV
- `Coverage map - <MNO> - <tech> - <Outdoor|Ext Ant> - <year>` — the per-technology maps
- `Coverage maps by frequency band - <MNO> - <year>` — ZIP bundles of per-band maps
- `Coverage map - Optus-TPG MOCN - ...` — new in 2025, the Optus/TPG network-sharing footprint
- 2 PDF: the data interpretation guide v5, and a 2024 Telstra letter to the ACCC on changed 4G
  outdoor coverage methodology

**1.4 File sizes are large and highly variable.** Measured from CKAN `size` fields, 2026-09-12.
Coverage-map resources range from **560,586 bytes** (Coverage map - TPG - 5G - Outdoor - 2021) to
**1,104,167,841 bytes** (Coverage maps by frequency band - Optus - 2022). Representative values:

| Resource | Bytes |
|---|---|
| Coverage map - TPG - 5G - Outdoor - 2021 (smallest) | 560,586 |
| Coverage map - Telstra - 5G - Outdoor - 2020 | 18,812,972 |
| Coverage map - Optus - 3G - Outdoor - 2025 | 20,262,143 |
| Coverage map - Telstra - 4G - Outdoor - 2025 | 252,569,107 |
| Coverage map - Telstra - 4G - Ext Ant - 2025 | 210,887,717 |
| Coverage map - Telstra - 3G - Outdoor - 2024 | 158,746,114 |
| Coverage map - Optus - 5G - Ext Ant - 2025 | 801,656,906 |
| Coverage map - Optus-TPG MOCN - 5G - Ext Ant - 2025 | 706,977,073 |
| Coverage maps by frequency band - Optus - 2022 (largest) | 1,104,167,841 |
| All 25 `Mobile sites` CSVs combined (downloaded) | 11,750,318 |

The full 138-resource dataset is on the order of **20+ GB**. A per-technology subset sufficient for
the mechanism (3 carriers x 3G/4G/5G x Outdoor x 8 years) is still several GB.

**1.5 Geometry is polygon, not raster, and supports point-in-polygon — but resolution differs per carrier.**
Two KMLs were downloaded and inspected directly.

*Small file — `coverage-map-tpg-5g-outdoor-2021.kml`, 560,586 bytes, Content-Type
`application/vnd.google-earth.kml+xml`:*
- 443 `<Placemark>`, 443 `<Polygon>`, **428 `<innerBoundaryIs>`** (interior holes — coverage gaps are
  explicitly modelled), 0 `<MultiGeometry>`, 657 `<coordinates>` blocks, 18,432 total vertices
- Coordinates are **2D lon,lat WGS84** (no altitude component)
- Attributes: a single `<SimpleField name="FID" type="float">` and nothing else. **No signal-strength,
  no dBm, no coverage-class attribute.** The polygon is a binary coverage/no-coverage boundary.
- Schema name is `tpg_5g_2021_cropped`
- Vertex steps cluster on **0.0011° and 0.000901°** (~100 m) with staircase dx/dy alternation —
  i.e. this file is a **vectorised ~100 m raster grid**, not a smooth contour
- bbox lon 115.7086..153.4479, lat −38.1151..−27.0214 — **this file contains no NT geometry at all**
  (NT spans roughly lat −26..−11). TPG had no 5G in the NT in 2021.

*Large file — `coverage-map-telstra-4g-outdoor-2025.kml`, 252,569,107 bytes:*
- Structure differs: no `<Schema>`/`<ExtendedData>` at all, just `<Style>` + `<Polygon>` per Placemark
- Coordinates carry **~12 decimal places** and irregular spacing — a true vector contour, **not**
  the gridded staircase seen in the TPG file. **Geometry generation is not consistent between
  carriers**, so a resolution assumption derived from one file does not transfer to another.
- 15,808 Placemarks, 6,278,543 vertices

Point-in-polygon at a community centroid is therefore well supported by the geometry. What it
returns is a binary "inside the carrier's predicted footprint" — there is no quality gradation in
this dataset.

**1.6 The NT subset can be clipped on this laptop. Measured, not estimated.**
`coverage-map-telstra-4g-outdoor-2025.kml` (252,569,107 bytes) was downloaded in **80.6 s at
3.1 MB/s** and stream-parsed with `lxml.etree.iterparse` (Placemark-scoped, with `el.clear()` and
previous-sibling deletion to bound memory):

- total placemarks 15,808; total vertices 6,278,543
- **NT-bbox placemarks 1,817 (11.49%); NT-bbox vertices 396,059 (6.31%)**
- **elapsed 93.5 s** for a single full pass on this machine

So the NT is ~6% of the national geometry: a ~250 MB national file yields a ~16 MB NT subset.
Clipping is feasible without geopandas/shapely (neither is installed here — see machine note).

**1.7 Trap — `lxml` fails by default on these files.** The first parse attempt raised:

```
lxml.etree.XMLSyntaxError: xmlSAX2Characters: huge text node, line 32183, column 10023646
```

The largest single `<coordinates>` text node in the Telstra 4G 2025 file is **30,978,161 bytes**
(one ~31 MB polygon ring). libxml2's default 10 MB text-node limit rejects it. `iterparse(...,
huge_tree=True)` parses it. Note also that `etree.iterparse()` **does not accept a `parser=`
keyword** — `huge_tree` must be passed to `iterparse` directly.

**1.8 The server supports HTTP Range requests.** `HEAD` on the Telstra 4G 2025 KML returned
`HTTP/1.1 200`, `Content-Length: 252569107`, `Accept-Ranges: bytes`,
`Last-Modified: Mon, 10 Nov 2025 06:46:08 GMT`, `ETag: "1762757168.716-252569107-3342208892"`.
A ranged request (`-r 0-1200`) returned **HTTP 206** with the requested 1,201 bytes. Partial and
resumable fetches are available.

**1.9 Publisher's own caveats on comparing years — from the data interpretation guide v5**
(`.../download/accc-mobile-infrastructure-report-data-release-data-interpretation-guide-v5.pdf`,
420,379 bytes, 19 pages, downloaded and text-extracted 2026-09-12). These bear directly on the
"2018→2025 trend per community" half of the mechanism. Verbatim:

> "Coverage maps are modelled on predictive coverage and therefore may not reflect the 'on the
> ground' experience for all end users."

> "The parameters that underpin these predictive coverage models differ across the MNOs. These
> parameters can also change across time for a given MNO. These changes could mean that increases
> or decreases in the measurement of coverage from year to year may not necessarily reflect changes
> in the predicted 'on the ground' experience of end users. Instead, the changes may reflect
> differences in parameters that underpin the modelling of the predictive coverage maps or
> variations in the precision/accuracy of the models."

> "Additionally, the introduction of new versions of prediction models/tools and potential
> differences in rounding and aggregation can result in minor variability in coverage predictions
> year to year, even if there are no actual changes in coverage."

Two specific documented discontinuities:

> "As part of its 2024 reporting, Telstra advised the ACCC that its 4G outdoor coverage maps for
> 2022 and 2023 were in fact 'handheld' coverage maps. ... For 2024 data onwards, this issue was
> rectified causing a significant increase in 4G outdoor coverage between 2023 and 2024."

> "TPG's 3G 2018 and 2019 coverage maps are based on higher power thresholds than its 2020 and 2021
> coverage maps due to a bug in its mapping software. Higher power thresholds for mobile sites
> means each site has a wider area of predicted coverage. It is a significant exercise to re-predict
> historical maps. Therefore, 2018 and 2019 coverage maps have not been re-predicted to align with
> the lower power threshold of the 2020 coverage maps onwards."

Also from the guide: the two coverage standards are defined as (1) **Outdoor** — "coverage and
quality of reception a customer can expect when using a device outdoors with typical handheld use,
based on an elevated upright standing, head height position"; (2) **External antenna** — "expected
coverage when a device is augmented using an external antenna or other coverage extension device".
"In general, coverage maps which are based on external antenna coverage predict wider coverage
areas than coverage maps based on outdoor coverage." And: "In providing coverage maps in accordance
with the RKR, the MNOs have interpreted the requirements differently."

**Reference date: "Mobile sites data is at 31 January for each reporting year from 2018 to 2025."**

**1.10 The ACCC has aggregated some maps itself.** From the dataset notes: "the ACCC has aggregated
the frequency band coverage maps submitted by the MNOs to create additional technology level
coverage maps ... (where the technology level maps were not provided by the MNOs)". Some
technology-level maps are therefore ACCC derivations, not carrier submissions; the guide's tables
mark the provenance per file.

---

## Q2 — ACCC "mobile sites" spreadsheets

**2.1 All 25 CSVs downloaded, 11,750,318 bytes total.** URLs follow the pattern
`https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/<res-id>/download/mobile-sites-<mno>-<year>.csv`.

**2.2 Columns.** Confirmed lat/lon per site, carrier, year, and **technology by frequency band**
(not a single "technology" column). Example header, `mobile-sites-telstra-2025.csv`:

```
Year,MNO,RFNSA ID,Latitude,Longitude,GSM900,IoT700,LTE700,LTE850,LTE1800,LTE2100,LTE2600,
NR700,NR850,NR2100,NR2600,NR3600,NR26000,Co_funded,Co_contribution_program,Round
```

Band columns are `Y`/blank flags. Technology is inferred from the prefix: `GSM`=2G,
`UMTS`/`WCDMA`=3G, `LTE`=4G, `NR`=5G, `IoT`/`NBIoT`=NB-IoT.

**2.3 The schema is NOT stable across the 25 files — 20 distinct header signatures.** Band columns
appear and disappear as networks change (Telstra 2025 has no `WCDMA*` columns at all — 3G is gone).
More consequential for joins: **`RFNSA ID` is absent from 7 of the 25 files** — every 2018 and 2019
file for all three carriers, plus Optus 2020. Cross-year site identity for 2018–2019 must fall back
to coordinates.

**2.4 Encoding is not uniform.** 24 of 25 files decode as UTF-8; **1 file fails UTF-8 and requires
cp1252** (`UnicodeDecodeError: 'utf-8' codec can't decode byte 0xa0`). A loader must sniff or fall back.

**2.5 Coordinate precision.** In `mobile-sites-telstra-2025.csv` (11,767 rows), latitude decimal
places are: 5 dp x7,760; 6 dp x2,298; 4 dp x1,342; 3 dp x140; 8 dp x133; 7 dp x64; 2 dp x30.
A 2-decimal-place site is located to ~1 km. **0 rows** across all 25 files had unparseable coordinates.

**2.6 NT site counts, 2018→2025 (the trend, from sites rather than polygons).**
NT selected by bounding box lat −26.1..−10.8, lon 128.9..138.1. Format is `NT / national`:

| MNO | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| Telstra | 160/9,429 | 176/9,972 | 185/10,451 | 195/10,766 | 217/11,002 | 224/11,302 | 234/11,707 | 247/11,767 |
| Optus | 82/7,335 | 90/7,712 | 95/7,980 | 102/8,238 | 108/8,632 | 121/8,821 | 128/9,201 | 130/9,391 |
| TPG | 44/5,422 | 49/5,608 | 52/5,675 | 53/5,892 | 53/5,728 | 53/5,769 | 53/5,712 | 45/5,207 |
| Optus-TPG MOCN | – | – | – | – | – | – | – | 24/2,443 |

NT totals: **286 site-rows in 2018 → 446 in 2025** (including the new MOCN file). TPG's NT count is
flat at 53 for 2021–2024 then drops to 45 in 2025, concurrent with the MOCN file appearing.

**2.7 Co-funding is tracked.** `Co_funded` and `Co_contribution_program` identify publicly subsidised
sites. In Telstra 2025: 1,441 of 11,767 rows are `Co_funded = Y`. Programs named include
`Federal Mobile Black Spot Program (MBSP)` (875), `REGIONAL CO-INVESTMENT: CVMP - Augmentation` (97),
`REGIONAL CO-INVESTMENT: RCP - Greenfield Macro` (51), `REGIONAL CO-INVESTMENT: RCP - Augmentation` (48),
`REGIONAL CO-INVESTMENT: STAND2 - Battery Upgrade` (38), `REGIONAL CO-INVESTMENT: Small Cell Satellite` (30),
`Victoria Mobile Blackspot VMP` (26).

---

## Q3 — ACMA Register of Radiocommunications Licences

**3.1 The daily bulk extract is live and needs no key.** The URL in older documentation
(`https://www.acma.gov.au/sites/default/files/2021-02/spectra_rrl.zip`) returns **HTTP 404**. The
working URL is `https://web.acma.gov.au/rrl/spectra_rrl.zip`, which **301-redirects to
`https://cdn.acma.gov.au/rrl/spectra_rrl.zip`**.

- **Size: 67,363,855 bytes (64 MB) zipped**, `Last-Modified: Sat, 12 Sep 2026 00:35:18 GMT` —
  i.e. rebuilt the morning it was checked. Confirmed daily.
- Downloaded in **24.9 s**. No authentication, no key, no registration.
- Landing page: `https://www.acma.gov.au/radiocomms-licence-data`

**3.2 Contents: 31 entries, ~600 MB uncompressed.** Largest members:

| Member | Uncompressed bytes |
|---|---|
| `device_details.csv` | 384,975,073 |
| `applic_text_block.csv` | 175,604,022 |
| `licence.csv` | 20,698,724 |
| `site.csv` | 13,605,006 |
| `antenna_pattern.csv` | 2,308,512 |
| `client.csv` | 1,689,063 |
| `auth_spectrum_area.csv` | 1,595,236 |
| `antenna.csv` | 621,348 |

Plus lookup tables (`licence_service.csv`, `licence_subservice.csv`, `class_of_station.csv`,
`industry_cat.csv`, `nature_of_service.csv`, `licence_status.csv`, …), `LICENCE.PDF`/`LICENCE.TXT`,
`README.TXT`, and a `DOC/` directory containing `RRLDataDownloads_ERD.jpg`,
`Summary_of_Spectra_RRL_Format.xlsx` and `cr_tables_oracle.sql`.

Row counts: `site.csv` 129,558; `licence.csv` 164,243; `client.csv` 14,324.

**3.3 Licence terms are NOT open — this is the one non-CC dataset in the mechanism.**
From `LICENCE.TXT` inside the zip, verbatim:

> "Intellectual Property in the Register is retained by the ACMA."
> "All rights in the Register are reserved, and you may not make copies of the Register or any part
> of the Register, except as expressly provided in this Licence."
> "Subject to these Terms and Conditions, the ACMA grants you a non-transferable, non-exclusive
> Licence to use, reproduce and adapt the Register, including the right to incorporate the Register
> in an electronic information retrieval system or in any other software product, to merge the
> Register with other material ... to develop derivative material based on the Register, and to
> distribute any derivatives developed by you to third parties."

So derivative works and redistribution of derivatives **are** permitted. Two restrictions are
explicit: client/personal information may be used only "for the purposes of management of the
radiofrequency spectrum in accordance with the Radiocommunications Act 1992", and not for
unsolicited commercial electronic messages (Spam Act 2003) or unsolicited telemarketing.
`README.TXT` requires reading LICENCE.TXT/PDF before use. The same terms are restated on
`https://www.acma.gov.au/radiocomms-licence-data` under "Terms and conditions".

**3.4 The API needs authentication; the bulk download does not.** Per
`https://www.acma.gov.au/radiocomms-licence-data`, the API is documented at
`http://backend.acma.gov.au/prtl/webapi/rrl/swagger/RRL-v1/swagger.json` and requires generating
system credentials — access is gated behind **Digital ID authentication**. For a lane restricted to
published datasets with no credentials, the daily zip is the access path.

**3.5 Yes — carrier base stations can be isolated, with coordinates. Executed end to end.**
The join path is `client.csv` → `licence.csv` → `device_details.csv` → `site.csv`:

- `client.csv` has `CLIENT_NO, LICENCEE, TRADING_NAME, ACN, ABN, ...` — name matching on LICENCEE
  found **34 client records** for the carrier groups, including `TELSTRA LIMITED` (9 records),
  `Optus Mobile Pty Limited` (8), `Vodafone Australia Pty Limited` (3), `Optus Networks Pty Limited`,
  `Telstra 3G Spectrum Holdings Pty Ltd`, `Vodafone Hutchison Australia Pty Limited`,
  `TPG INTERNET PTY LTD`, and **`MOBILE JV PTY LIMITED`** (the Telstra/TPG regional sharing JV).
  Non-mobile affiliates that must be excluded by name also appear: `TELSTRA PAY TV PTY LTD`,
  `TELSTRA BROADCAST SERVICES PTY LIMITED`, `OPTUS VISION MEDIA PTY LIMITED`,
  `OPTUS SATELLITE NETWORK PTY LIMITED`, `TPG TV PTY LTD`. Note also false positives from personal
  names (`Rj & Dc Hutchison`, `Jason Hutchison`).
- `licence.csv` has `LICENCE_NO, CLIENT_NO, SV_ID, SS_ID, LICENCE_TYPE_NAME, LICENCE_CATEGORY_NAME,
  DATE_ISSUED, DATE_OF_EFFECT, DATE_OF_EXPIRY, STATUS, STATUS_TEXT, ...` — **16,557 active carrier
  licences**. Breakdown by type: Telstra Fixed 7,736; Optus Fixed 6,489; Telstra Land Mobile 936;
  TPG/Vodafone Fixed 670; Telstra PTS 258; **Telstra Spectrum 25, Optus Spectrum 23,
  TPG/Vodafone Spectrum 13, Mobile JV Spectrum 4**.
- `device_details.csv` (54 columns) has `LICENCE_NO, FREQUENCY, BANDWIDTH, EMISSION, DEVICE_TYPE
  (T/R), TRANSMITTER_POWER, SITE_ID, ANTENNA_ID, AZIMUTH, HEIGHT, TILT, EIRP, ...`
- `site.csv` has `SITE_ID, LATITUDE, LONGITUDE, NAME, STATE, LICENSING_AREA_ID, POSTCODE,
  SITE_PRECISION, ELEVATION, HCIS_L2` — **`STATE` gives a direct NT filter: 3,776 NT sites** of
  129,558 nationally.

**Critical nuance: cellular base stations sit under `Spectrum` licences, not `Land Mobile`.**
`licence_service.csv` maps `SV_ID 85 = Spectrum`, `10 = PTS`, `110 = PTS 900 MHz`, `3 = Land Mobile`.
The subservice table contains no "cellular"/"mobile phone" entry — `Land Mobile System > 30MHz` is
private radio, not carrier cellular. Filtering on `LICENCE_TYPE_NAME = 'Land Mobile'` would return
the **wrong** sites. Measured licence types behind the NT cellular-band transmitters: Telstra
Spectrum 2,814 device rows; TPG/Vodafone Spectrum 1,631; Optus Spectrum 1,477; Telstra PTS 195;
Optus PTS 104; Telstra Fixed 19.

**Frequency banding is required to separate base stations from microwave backhaul**, because the
carriers' `Fixed` licences dominate by count and are point-to-point links. Filtering
`DEVICE_TYPE = 'T'` and frequency into cellular bands (700/850/900/1800/2100/2300/2600/3500/26000 MHz)
gives, for the NT:

| Carrier | 700 | 850 | 900 | 1800 | 2100 | 2300 | 2600 | 3500 | 26000 | ANY band |
|---|---|---|---|---|---|---|---|---|---|---|
| Telstra | 296 | 208 | 0 | 101 | 137 | 1 | 139 | 11 | 0 | **333** |
| Optus | 130 | 0 | 125 | 80 | 83 | 0 | 88 | 5 | 9 | **162** |
| TPG/Vodafone | 55 | 55 | 0 | 54 | 53 | 0 | 0 | 0 | 0 | **81** |

**Union: 464 distinct NT cellular-band transmit sites.** Without the band filter (any cellular or
backhaul frequency) the union is 751 NT sites — Telstra 615, Optus 171, TPG/Vodafone 82.

**3.6 Coordinate quality is published per site.** Of the 464 NT cellular sites: **362 "Within 10
metres", 40 "Within 100 metres", 62 "Unknown"**. Sample records:
`Optus GSM Tower Lot 550 Stuart Highway HOWARD SPRINGS (−12.529121, 131.048046)`;
`Telstra Repeater Site 18km NW of Mount Bundey MARRAKIA RIDGE (−12.759251, 131.467456)`;
`Telstra Site via Kaczinsky Rd WARUMUNGU (−19.63414, 134.223606)`.

**3.7 Performance is not a constraint.** The full join — streaming the 385 MB `device_details.csv`
from inside the zip without extracting it, plus all lookups — ran in **11.0 s** on this machine
using only the standard library (`zipfile` + `csv` + `io.TextIOWrapper`).

**3.8 A cross-source count disagreement is already visible.** For Telstra in the NT, the ACCC 2025
sites CSV gives **247** sites (NT bbox) while the ACMA RRL gives **333** NT cellular transmit sites
on the day checked. The two are not measuring the same object — ACCC counts RFNSA-identified sites
at 31 January 2025, RRL counts distinct `SITE_ID` records live at 2026-09-12, and a single physical
facility may carry more than one RRL `SITE_ID`. The gap is a finding, not a reconciliation yet.

---

## Q4 — NT Government open data (data.nt.gov.au)

**4.1 The CKAN API works; no blocking.**
`https://data.nt.gov.au/api/3/action/package_search?q=mobile+coverage&rows=30` returned HTTP 200,
**5 datasets**. All five carry **Creative Commons Attribution (`cc-by`, `isopen: true`)**.
All are **XLSX only — no CSV, no geospatial format**. Three have a separate Data Quality Statement PDF.

| Dataset | CKAN name | Resource | Bytes | metadata_modified |
|---|---|---|---|---|
| Remote Communities with Mobile Coverage and Backhaul Transmission 2019 | `list-of-remote-communities-with-mobile-coverage` | `remote-communities-mobile-coverage.xlsx` | 15,654 | 2022-06-29 |
| Remote Communities with 3G/4G Mobile Coverage 2021 | `remote-communities-with-mobile-coverage` | `communities-with-mobile-coverage.xlsx` | 53,787 | 2022-06-29 |
| Mobile Phone Coverage in Remote Areas of the NT 2022 | `mobile-phone-coverage-in-remote-areas-of-the-nt` | `mobile-coverage-all-sites.xlsx` | 24,602 | 2022-07-04 |
| Remote Sites with Mobile Phone Small Cell Coverage | `remote-sites-with-mobile-phone-small-cell-coverage` | `remote-small-cell-coverage-nt.xlsx` | 13,631 | 2021-06-22 |
| Centre for Appropriate Technology Mobile Phone Hotspots | `centre-for-appropriate-technology-mobile-phone-hotspots` | `opendataportal_cfat_final-july-2022.xlsx` | 12,963 | 2022-07-06 |

Owner org for the first four: "Corporate and Digital Development" (`department-of-corporate-and-information-services`).
**The most recent metadata change across all five is 2022-07-06** — confirming the brief's premise
that the NT list has not been updated since 2022.

**4.2 Columns and row counts. All five downloaded and opened.**

*2019 (`nt2019.xlsx`, Sheet1, A1:E66):* title row, then header at row 2 —
`Remove Community Location` [sic], `Remote Communinity Latitude` [sic], `Remote Community Longitude`,
`Remote Community Backhaul transmission`, `Remote Community Provider`. **64 data rows.**
Backhaul values: `Optic fibre` 45, `Microwave radio` 19. Provider values: `Telstra` 29,
`Project 13` 13, `Telstra/NTG Program` 10, `Arnhem Fibre Program` 8, `MBSP` 4 — note this column
mixes **carriers and funding programs**, so it is not a clean carrier field. Two header typos.
**This is the only one of the three with backhaul information.**

*2021 (`nt2021.xlsx`) — two sheets:*
- `Communities with Mobile` (A1:D73): `COMMUNITY_NAME, COMMUNITY_TYPE, LONGITUDE, LATITUDE`. **72 rows.**
- `Communities` (A1:F783): `COMMUNITY_NAME, COMMUNITY_TYPE, LONGITUDE, LATITUDE, MOBILE_PHONE,
  MOBILE_PHONE_COMMENTS`. **782 rows** — this is the full NT community gazetteer and supplies the
  denominator. `MOBILE_PHONE` values: **`Not recorded` 698, `Y` 67, `N` 17.** Only 84 of 782
  communities have any recorded determination.

*2022 (`nt2022.xlsx`, `Communities with Mobile`, A1:I193):* rows 1–4 are an explanation block;
**header is on row 5**: `SITE NAME, SITE TYPE, POPULATION, MACRO CELL, SMALL CELL,
PROXIMITY TO CELL, PROVIDER, LATITUDE, LONGITUDE`. **188 data rows.** Richest of the three.
- Coverage-type distribution: `PROXIMITY TO CELL` only 96; `MACRO CELL` only 56; `SMALL CELL` only 29;
  `MACRO+SMALL` 5; `SMALL+PROXIMITY` 1; `MACRO+PROXIMITY` 1
- `PROVIDER`: `TELSTRA` 134, `OPTUS/TELSTRA` 40, `OPTUS` 14. **TPG/Vodafone never appears.**
- `SITE TYPE`: `COMMUNITY` 148, `HIGHWAY` 17, `TOURISM` 15, `VILLAGE` 8
- Carries **POPULATION** per site

The embedded explanation, verbatim:

> "EXPLANATION - This list provides details of mobile phone coverage outside the main centres in the
> NT. It includes the type of site covered - Aboriginal community, remote villages (usually on a
> major highway), tourism and highway (usually roadhouse) locations. It provides type of coverage -
> macro cell (up to 40 km coverage), small cell (up to 5 km coverage) or a smaller community close
> enough to a macro cell installation to receive coverage. Some communities receive coverage from
> more than one service provider. NOTE: Coverage varies according to local conditions especially
> topography and vegetation and this list is a GUIDE only."

**This gives published radii — macro 40 km, small cell 5 km** — i.e. the NT Government's own stated
value for the "within N km" parameter in the mechanism. Note "PROXIMITY TO CELL" is applied to 98 of
188 rows: for more than half the list, the NT Government's coverage claim is itself a distance
inference, not an observation.

*Bonus datasets (not in the brief's three):*
- `ntsmallcell.xlsx` (Sheet1, A1:D26): `Location of Small Cell, Small Cell Latitude,
  Small Cell Longitude, Small Cell Provider` — **24 rows** with coordinates and provider.
- `ntcfat.xlsx` (Sheet1, A1:O55): `LOCATION, LOCATION TYPE, LATITUDE, LONGITUDE` (+ 11 empty
  columns) — **54 rows**, Centre for Appropriate Technology mobile phone hotspots.

**4.3 No shared community identifier. Name is the only join key — but coordinates reveal lineage.**
None of the three files carries an ID column. Normalising names (uppercase, strip non-alphanumerics):

| Pair | Common names | Identical coordinates | >2 km apart |
|---|---|---|---|
| 2021 vs 2022 | 68 | **68 (all)** | 0 |
| 2019 vs 2022 | 56 | **2** | 2 |
| 2019 vs 2021 | 54 | **0** | 2 |

**2021 and 2022 share the same coordinate source exactly** (e.g. Adelaide River is
`−13.2378, 131.104729999999` in both, to 12 decimal places). **2019 is an independent coordinate
set rounded to 3 dp** (Adelaide River `−13.238, 131.106`) and agrees with neither. Two communities
disagree by more than 2 km between 2019 and the later files: **DALY WATERS** (2019
`−16.307, 133.386` vs `−16.25333, 133.36932`, ~6 km) and **NTURIYA** (2019 `−22.132, 133.418` vs
`−22.12379, 133.26529`, ~16 km).

Membership churn between lists:
- 2019 has 64 rows, 8 of which are absent from 2022: `ALYANGULA, BARKLY HOMESTEAD, BYNOE,
  DALY RIVER, JABIRU, KALKARINGI, MCARTHUR RIVER, TANAMI`
- 2021 has 72 rows, 4 absent from 2022: `ACACIA LARRAKIA, FINKE, JABIRU, OLD MISSION`
- **120 of the 188 names in 2022 are not in the 2021 with-mobile list** — the 2022 list is a large
  expansion in scope (tourism/highway sites), not just an update
- **JABIRU is in both 2019 and 2021 but in neither's successor** — a disappearance worth flagging

160 of the 188 names in the 2022 list are present in the 782-row 2021 gazetteer. The 28 that are not
are almost all roadhouses/tourism sites: `AILERON STATION, AURORA KAKADU, BARROW CREEK, COOINDA
LODGE, CURTAIN SPRINGS ROADHOUSE, DEVILS MARBLES HOTEL, DUNMARRA ROADHOUSE, ERLDUNDA, FLORENCE
FALLS, GEMTREE PARK, GLEN HELEN HOMESTEAD, KINGS CANYON RESORT, KINGS CREEK STATION, MARY RIVER
ROADHOUSE, MOUNT BUNDEY, MOUNT EBENEZER, ORMISTON RANGER STATION, RENNER SPRINGS ROADHOUSE, ROSS
RIVER RESORT, STUARTS WELL ROADHOUSE, THREE WAYS ROADHOUSE, TILMOUTH WELL ROADHOUSE, TIPPERARY
STATION, TOP SPRINGS ROADHOUSE, VICTORIA RIVER ROADHOUSE`, …

**4.4 A stable NT community identifier does exist — in BushTel, not in the spreadsheets.**
`https://bushtel.nt.gov.au/api/community/{id}` is a **public, unauthenticated JSON API** (ASP.NET
Web API) returning a **66-field** record per community. It was discovered by probing the `/api/`
route and confirmed against the app bundle (`https://bushtel.nt.gov.au/public/dist/bundle.js?v=2.5.26`).
BushTel is operated by the NT Department of the Chief Minister and Cabinet.

Fields relevant to the mechanism: `Id` (numeric, stable), `Name`, `DefaultName`, `AliasNames`
(array — e.g. Adelaide Bore has `["Woola","Woolla"]`), `CommunityTypeName`, `Point`
(`{Longitude, Latitude}`), `Population` + `PopulationSource` + `PopulationDescription`,
**`Sa1Code`** (ABS SA1 — e.g. `7105410`), `ElectorateName`, `LandCouncilName`, `NTRegionName`,
`Boundaries` (array of boundary ids), `Services` (array of `{ServiceType, Status, Comments}`),
`LastUpdated` (per-section timestamps).

**ID 1 is `ADELAIDE BORE` — exactly the first row of the 782-row 2021 `Communities` sheet.**
A sample of IDs 1–200 returned 146 live records, and **146 of 146 matched the 2021 gazetteer by
normalised name**. The 2021 spreadsheet is therefore a BushTel extract with the identifier stripped;
re-attaching `Id` by name is possible and gives the three NT lists a common key, plus alias names to
resolve spelling variants and an ABS SA1 code to bridge to ABS TableBuilder.

**4.5 Negative result — BushTel's `Capabilities.Mobile` is NOT a coverage indicator.** The record
contains `Capabilities: {FixedPhone, Mobile, Internet, RoadAccess}`, which looks like a live
per-community mobile flag. It is not. Across the 146 sampled communities **`Capabilities.Mobile` was
`true` for all 146**, including all **7** that the 2021 NT list marks `MOBILE_PHONE = 'N'`
(`AREYONGA, HAASTS BLUFF, LARAMBA, NYIRRIPI, WILLOWRA, WILORA, YUELAMU`) and all 120 marked
`Not recorded`. It is a UI feature flag for which profile tabs to render. Recorded here so a later
session does not mistake it for a fourth coverage source.

The `Services` array is real per-community status data but covers roads, alcohol restrictions,
homelands service providers, funded dwellings and power programs — **no mobile/telecommunications
service type appeared** in the record inspected. `LastUpdated.Profile` for ID 1 was
`06/08/2025, 02:14:29 PM`.

---

## Q5 — Prior art

**5.1 Yes — the First Nations Connectivity Mapping Tool already overlays carrier coverage on
communities.** The ArcGIS portal item API 403s
(`https://spatial.infrastructure.gov.au/portal/sharing/rest/content/items/cebfe7afe0894bd9bda06edbd65b9d17?f=json`
→ `{"error":{"code":403,...}}`), but the **portal search and the ArcGIS Server REST directory are both
fully public and unauthenticated**:
- `https://spatial.infrastructure.gov.au/portal/sharing/rest/search?q=First Nations&f=json` → 19 items
- `https://spatial.infrastructure.gov.au/server/rest/services?f=json` → ArcGIS **11.5**, folders
  `BBRF, Communications, DataHub, FirstNationsDataTool, Hosted, iPAMS-DB, KeyFreightRoutes,
  NLTN_KFR_2026, Utilities`

The item id in the brief is the **webappviewer** app. The current tool is an Experience Builder app:
`First Nations Connectivity Mapping Tool`, item `81c5ae65fbf74ce3a89cf25b1f323d50`,
`https://spatial.infrastructure.gov.au/portal/apps/experiencebuilder/experience/?id=81c5ae65fbf74ce3a89cf25b1f323d50`.
Its web map is `First Nations Connectivity Map`, item `6cef1c9f63674348817e3f57e88ed9bc` (public).

**5.2 Layers in the web map** (read from
`https://spatial.infrastructure.gov.au/portal/sharing/rest/content/items/6cef1c9f63674348817e3f57e88ed9bc/data?f=json`):
- State Borders (ABS) 2021
- **National Native Title Tribunal** group — 11 live layers (RATSIB areas, s31 agreements, future act
  applications/objections/notices, register of claims, ILUAs, determination applications, outcomes,
  determinations, RNTBCs) served from `services2.arcgis.com`
- **ABS Indigenous Boundary Data** — Indigenous Regions (IREG), Indigenous Areas (IARE),
  **Indigenous Locations (ILOC)**, live from `geo.abs.gov.au`
- **ABS Boundary Data** — Remoteness Areas, Local Government Areas
- **Mobile Coverage Data → "Mobile Sites and Coverages (ACCC), 2024"** — 37 sublayers, pointing at
  `https://spatial.infrastructure.gov.au/server/rest/services/ACCC_Mobile_Sites_and_Coverages/MapServer`
- **NBN Coverage Data → NBN Coverage Footprints (NBN Co) 2024**
- **Media Coverage Data** — TV Signal Strength (ACMA) 2017, Predicted FM Radio Signal Coverage (ACMA)
  2020, Indigenous Broadcasting and Media Program Data (NIAA) 2023
- **WiFi and Telecommunication Data** — Community Payphones (NIAA) 2023, Wi-Fi Hubs, Wi-Fi Telephones,
  Communities in Isolation Wi-Fi Program (NBN Co) 2025

**5.3 The full source list is published.** "First Nations Connectivity Mapping Tool: Data Dictionary
(DITRDCSA) 2025", item `e5f932b32bb2488f8fa0e49c2833ed02`, downloaded from
`https://spatial.infrastructure.gov.au/portal/sharing/rest/content/items/e5f932b32bb2488f8fa0e49c2833ed02/data`
(237,923 bytes, 5 pages, dated **September 2025**, marked OFFICIAL). It enumerates **34+ sources**,
including — directly relevant to Q4 — **"2. BushTel Community Profile (date extracted 30 August 2024)
is sourced from Department of the Chief Minister and Cabinet"**, plus AGIL (2019) Outstations and
Homelands from Services Australia, ABS UCL points, MBSP/MNHP/PUMP funded base stations, RICT activity
(NIAA 2024), Communities in Isolation Wi-Fi (NBN Co 2025), and **"24. ACCC Mobile Sites and Coverages
(2024) ... sourced from Australian Competition & Consumer Commission"**.
A companion "How to use the First Nations Connectivity Mapping Tool Guide (DITRDCSA) 2025" exists as
item `0aa000dadca848a38b917e1ddd5434c1`.

So the tool already joins BushTel NT communities to ACCC carrier coverage in one map.

**5.4 The ACCC coverage is exposed as a queryable REST service, and point-in-polygon works.**
`https://spatial.infrastructure.gov.au/server/rest/services/Mobile_Coverages_and_Sites_ACCC/MapServer`
— `copyrightText: "ACCC - Mobile Infrastructure Report 2025"`, `capabilities: Map,Query,Data`,
`maxRecordCount: 2000`. **This is the 2025 vintage**, one year newer than the 2024 service the
First Nations web map points at. Layers are organised per carrier per technology per coverage
standard, including 3G, and the MOCN footprint:
`60 Mobile Sites - as published by ACCC`; `1–5` site layers (all networks, Optus, Telstra, TPG,
TPG-on-Optus); `6–11` all-networks coverage (5G/4G/Total x Outdoor/Ext Ant); `12–17` Optus + `50, 51`
Optus 3G; `18–22` Telstra; `23–28` TPG; `29–34` TPG-on-Optus MOCN.

A live point-in-polygon test at **Ali Curung (134.40694, −21.00333)** via
`/MapServer/{layer}/query?geometry=...&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects`:

| Layer | Result |
|---|---|
| 8 — Total Outdoor, all networks | **1 feature** (OBJECTID 5541, FID_GRID_Web 25801) |
| 20 — Telstra Total Outdoor | **1 feature** (OBJECTID 5433, FID_GRID_Web 25801) |
| 14 — Optus Total Outdoor | **0 features** |
| 25 — TPG Total Outdoor | **0 features** |

This **agrees with the NT 2022 list**, which records Ali Curung as `MACRO CELL`, `PROVIDER = TELSTRA`.
One cross-source agreement, confirmed by execution.

Returned attributes are only `OBJECTID, FID_GRID_Web, Shape_Length, Shape_Area` — the field name
`FID_GRID_Web` and the returned `Shape_Area` of 0.0255 deg² indicate the served geometry is chunked
into grid tiles rather than dissolved. No signal-strength attribute here either.

**5.5 A second national service carries the same data with an explicit caveat.**
`https://spatial.infrastructure.gov.au/server/rest/services/Communications/Mobile_Phone_Coverage/MapServer`
— one layer, `ALL_Network_Operators_ALL_Mobile_Coverage_2022_Web`, `copyrightText` ACCC. Its own
service description states verbatim:

> "Coverage maps are modelled on predictive coverage and therefore may not reflect the 'on the
> ground' experience for all end users. There are several factors that can impact mobile coverage
> including buildings, foliage/trees, bad weather, hills or mountains, the number of nearby people
> using the same mobile site and hardware compatibility."

**5.6 Other published reconciled or measured views.**
- **National Audit of Mobile Coverage** (DITRDCSA),
  `https://www.infrastructure.gov.au/media-communications-arts/better-connectivity-plan-regional-and-rural-australia/national-audit-mobile-coverage`
  — commenced May 2024 with a pilot (3 roads and 3 locations per state/territory), then drive testing
  ~180,000 km of regional and rural roads annually for 3 years, complemented by crowd-sourced data
  collected by Accenture (~160,000 active Australian users, ~3.5 billion samples annually). This is a
  government programme that measures rather than models. **Whether its NT results are published as a
  downloadable dataset: TBD** (see TBD section).
- **Academic**: "Mobile Coverage Analysis using Crowdsourced Data", Timothy Wong et al.,
  `https://arxiv.org/pdf/2510.13459` — framework for coverage and weak-spot analysis from crowdsourced
  QoE data at cell then site level. Not NT-specific and not a reconciliation of published sources.
- Commercial aggregators exist (`https://www.mobilecoverage.com.au/`,
  `https://www.mobilecoverageaustralia.com/nt/`) but are carrier-map republishers, not reconciliations.
- No published source-agreement/disagreement count per community — for the NT or nationally — was
  found in this lane's searching. The First Nations tool overlays the layers for visual inspection;
  nothing found computes a per-community count across sources or a disagreement flag.

---

## Q6 — Known critiques of predicted coverage maps in Australia

**6.1 ACMA made a binding standard — this is the largest recent change and it postdates most commentary.**
`https://www.acma.gov.au/articles/2026-03/new-rules-mobile-phone-coverage-maps`, dated
**31 March 2026**, media release **MR 10/2026**. Instrument: **Telecommunications (Mobile Network
Coverage Maps) Industry Standard 2026**. Carriers must, **by 30 June 2026**, publish maps of 4G and
5G coverage in one of four categories — **good, moderate, basic, or no coverage**. Verbatim:

> "Mobile providers make available network coverage maps, but they are measured and presented
> differently. We know that consumers are frustrated that, as a result, they can't make any
> meaningful comparison between them." — ACMA Chair Nerida O'Loughlin

> "These new rules will ensure every carrier is giving the public a like-for-like comparison of
> service coverage in any location across Australia." — Nerida O'Loughlin

> "The maps will be based on predictive modelling and provide consumers with plain English
> descriptions of what good, moderate and basic mobile coverage mean."

> "In areas shown as having 'no coverage', the ACMA acknowledges that people in some locations may
> still be able to make calls and send SMS, but overall service is expected to be very limited,
> inconsistent or non-existent."

> "Over time, the ACMA will look at whether the maps can be enhanced with alternative sources of data
> such as infield measurement and crowd-sourced information on coverage."

Maps must be reviewed/updated **at least every three months**. Optus, Telstra and TPG must also supply
maps to their MVNO partners. Breaches may attract enforceable undertakings, remedial directions and
financial penalties. The ACMA acted on a direction from the Minister for Communications "to ensure
coverage maps accurately reflect reasonable service levels".

Supporting documents: consultation paper and draft standard (Jan 2026)
`https://www.acma.gov.au/sites/default/files/2026-01/Draft%20Telco%20(Mobile%20Networks%20Coverage%20Maps)%20Industry%20Standard%202026.pdf`;
outcomes paper (Mar 2026)
`https://www.acma.gov.au/sites/default/files/2026-03/outcomes_paper_-_proposal_to_make_mobile_coverage_mapping_standard.pdf`;
landing page `https://www.acma.gov.au/mobile-network-coverage-maps-standard`.

Reported thresholds (4G RSRP / 5G SS-RSRP): good ≥ −95 dBm; moderate −105 to −95 dBm; useable/basic
−115 to −105 dBm; no coverage < −115 dBm. **Sourced from search-result summaries of the standard, not
read verbatim from the instrument — see TBD.**

**6.2 ACCC, 1 July 2026 — welcomed the standard and warned on claims.**
`https://www.accc.gov.au/media-release/accc-welcomes-new-mobile-coverage-map-standard-and-warns-on-misleading-coverage-claims`
(accc.gov.au 403s to curl; retrieved via WebFetch). ACCC Deputy Chair **Catriona Lowe**, verbatim:

> "We remain concerned about ongoing coverage issues, and we continue to receive a significant number
> of complaints from consumers, including about patchy service and the accuracy of coverage maps."

> "This new Standard is an important step because it will provide consumers with coverage maps showing
> varying levels of coverage quality in different areas."

> "While the new Standard does not expressly cover geographical coverage claims, the ACCC expects
> mobile providers to align these claims with the mobile coverage maps published under the Standard."

> "We will continue to consider providers' claims about coverage and will take enforcement action
> where appropriate."

**6.3 ACCC Regional Mobile Infrastructure Inquiry, final report July 2023.**
`https://www.accc.gov.au/system/files/Regional%20Mobile%20Infrastructure%20Inquiry%20final%20report.pdf`
(403 to curl; PDF text extraction via WebFetch also failed — the binary was returned unparsed). From
the ACCC's own summary pages and search-result extracts: the report records consistent concerns about
patchy coverage and difficulty interpreting and comparing coverage maps; notes that MNOs use predicted
coverage as the basis for their maps with differing input assumptions and metrics which can change
over time, making coverage change hard to assess; and that many regional consumers find it difficult
to check what coverage is available. **Verbatim quotes with page numbers: TBD** (see TBD section).
Related: `https://www.accc.gov.au/media-release/mobile-tower-access-may-be-limiting-regional-mobile-coverage-expansion`.

**6.4 ACCC data interpretation guide v5 — the publisher's own caveat.** Already quoted at 1.9. This is
the strongest primary-source critique because it is the ACCC describing the limits of the exact
dataset the mechanism consumes: predicted coverage "may not reflect the 'on the ground' experience";
parameters "differ across the MNOs" and "change across time"; year-to-year changes "may not
necessarily reflect changes in the predicted 'on the ground' experience"; and documented
methodology breaks in Telstra 4G 2022/2023 and TPG 3G 2018/2019.

**6.5 RTIRC 2024.** Report "Connecting communities, reaching every region"; the recommendations
document was downloaded directly
(`https://www.rtirc.gov.au/sites/default/files/documents/rtirc-report-2024-recommendations.pdf`,
1,063,930 bytes, 4 pages) and its full text searched. **14 recommendations. The word "coverage map"
does not appear in the recommendations document.** Recommendation 2, "Improving the mobile
experience", addresses "diminishing mobile experience in existing regional, rural and remote coverage
areas" and advises government to "prioritise funding to improve existing terrestrial mobile network
capacity, service quality, and resilience, rather than further extending terrestrial coverage".
Recommendation 9 supports continuing the First Nations Digital Inclusion Advisory Group;
recommendation 10 covers community Wi-Fi, noting "communities without mobile coverage should be
prioritised". Coverage-map criticism appears in **submissions** to the review rather than in the
recommendations. **Whether the main RTIRC report body (as distinct from the recommendations extract)
contains a coverage-map finding: TBD.**

**6.6 ABC News, 24 July 2026 — the standard did not close the gap.**
`https://www.abc.net.au/news/2026-07-24/new-mobile-coverage-maps-still-not-accurate-claim-customers/106944100`,
published 24 July 2026 (updated 5:12pm) — i.e. **three weeks after the standard's 30 June 2026
compliance date**. Verbatim:

> "We purchased, we moved in, and discovered we have absolutely no coverage, none." — Helen Wood,
> Bairnsdale VIC (whose street the new standardised maps predict as good 4G and moderate-to-good 5G NSA)

> "I feel like we've all been had." — Helen Wood

> "We continue to hear from consumers who are given incorrect advice about coverage that doesn't
> reflect the service they receive." — Cynthia Gebert, Telecommunications Industry Ombudsman

> "Accurate coverage information and clear advice about what people can realistically expect is
> crucial for consumers to make informed decisions about the service they choose." — Cynthia Gebert

> "It's a freezing cold night and you want to talk to your son or daughter or the grandkids, and
> you've got to sit outside or miss out." — Greg Hinten, Lake Macquarie NSW

> "What we would really like to see is not the carriers releasing a map, but having a national
> map..." — Kristy Sparrow, co-founder, Better Internet for Rural, Regional and Remote Australia (BIRRR)

**6.7 ACCAN.** Reported finding that **30% of Australians surveyed did not receive the coverage they
expected from their telco**, with ACCAN hearing from regional, rural and remote customers that
experienced coverage does not match what was advertised. **This figure was obtained from search-result
summaries, not from an ACCAN publication read directly — the primary ACCAN report, its title and date
are TBD.** Also reported: coverage maps have functioned "more as marketing tools than a source of
meaningful consumer information", with coverage definitions set by telcos themselves and limited
transparency, and the ACCC noting they are "largely based on predictions, and not auditable" —
**second-hand paraphrase, primary source TBD.**

---

## Other facts found

1. **The ACCC dataset now includes an Optus-TPG MOCN network-sharing footprint (2025 only)** —
   `Mobile sites - Optus-TPG MOCN - 2025` (157,495 bytes) plus four coverage maps (4G Outdoor/Ext Ant
   as ZIP, 5G Outdoor/Ext Ant as KML at 592 MB and 707 MB). 24 of its 2,443 sites fall in the NT bbox.
   A naive per-carrier count in 2025 will double-count these unless MOCN is handled explicitly.
2. **TPG's ACCC maps understate its usable footprint by design.** Guide footnote: "TPG's coverage maps
   do not include coverage it could access via its roaming agreement with Optus."
3. **Telstra 3G maps stop at 2024; Telstra 4G/5G continue to 2025.** Optus 3G runs to 2025. Any
   per-year technology matrix will be ragged, and 3G shutdown is a confound in any 2018→2025 trend.
4. **TPG 5G first appears in 2021 at 560 KB nationally** (443 polygons) and contained **no NT geometry
   at all** that year — a genuine zero, not missing data.
5. `site.csv` in the RRL includes an `ELEVATION` column and an `HCIS_L2` code alongside
   `SITE_PRECISION`; `device_details.csv` includes `AZIMUTH`, `HEIGHT`, `TILT`, `EIRP` and
   `TRANSMITTER_POWER` per device — enough to distinguish a sector antenna from an omni repeater,
   and to weight a "within N km" test by radiated power rather than treating all sites equally.
6. **`MOBILE JV PTY LIMITED` holds 4 active Spectrum licences** in the RRL — the Telstra/TPG regional
   network-sharing JV appears as a distinct licensee and will be missed by a Telstra/Optus/TPG-only
   name filter.
7. The RRL `client.csv` name-matching produced false positives from personal names
   (`Rj & Dc Hutchison`, `Jason Hutchison`) and from non-mobile carrier affiliates
   (`TELSTRA PAY TV`, `OPTUS VISION MEDIA`, `TPG TV`, `OPTUS SATELLITE NETWORK`,
   `TELSTRA BROADCAST SERVICES`). An exclusion list is required, not just an inclusion list.
8. **data.nt.gov.au publishes two further mobile datasets not named in the brief** — the 24-row small
   cell site list with coordinates and provider, and the 54-row CfAT hotspot list. Both CC-BY.
9. The NT 2019 file has two header typos (`Remove Community Location`, `Remote Communinity Latitude`)
   and its `Provider` column mixes carriers with funding programs (`Project 13`, `MBSP`,
   `Arnhem Fibre Program`, `Telstra/NTG Program`).
10. `https://data.gov.au/data/dataset/communications-sites-acma` ("Communications Sites (ACMA)",
    modified 2025-06-25) sounds like an ACMA site layer but its two resources are a **Tasmanian
    LISTmap viewer link** and a link to `web.acma.gov.au/pls/radcom/`. Licence `notspecified`.
    Not a usable national extract.
11. The ArcGIS portal hosts `Regional Connectivity Program (RCP) Funded Sites`
    (item `ae9b8d0978b04e84a6774a7772da612b`) and services for `Mobile_Black_Spot_Program_Funded_Base_Stations`,
    `Mobile_Network_Hardening_Program`, `Peri_Urban_Mobile_Program`,
    `Strengthening_Telecommunications_Against_Natural_Disasters`, `NBN_Coverage_Footprints_2024`,
    `NBN_Fixed_Line`, `NBN_Fixed_Wireless`, and `Communication_Program_Eligibility_Areas` — all public,
    all queryable via the same REST pattern.
12. The RRL zip ships `DOC/Summary_of_Spectra_RRL_Format.xlsx`, `DOC/RRLDataDownloads_ERD.jpg` (entity
    relationship diagram) and `DOC/cr_tables_oracle.sql` — the schema is documented in-band.
13. ACCC dataset notes record a revision event: on 8 September 2022 "the following mobile sites
    spreadsheets were subject to a very small number of revisions: Telstra 2020, Telstra 2021, Optus
    2020 and Optus 2021", and "All coverage map file names have been amended to indicate their
    standard of coverage". Resource names still carry `v2` suffixes for those four files.
14. **`isopen: false` on the ACCC dataset** despite `license_id: cc-by-2.5` — a CKAN metadata
    inconsistency worth not over-reading in either direction.

---

## TBD — needs validation

1. **TBD — the exact signal-strength thresholds and minimum mapping resolution in the
   Telecommunications (Mobile Network Coverage Maps) Industry Standard 2026.** The good/moderate/basic
   thresholds at 6.1 (−95 / −105 / −115 dBm RSRP) and the existence of a "minimum mapping resolution"
   parameter come from search-result summaries, not from the instrument. *Settled by:* reading the
   registered instrument on the Federal Register of Legislation, or the draft at
   `https://www.acma.gov.au/sites/default/files/2026-01/Draft%20Telco%20(Mobile%20Networks%20Coverage%20Maps)%20Industry%20Standard%202026.pdf`
   and the outcomes paper, and quoting the schedule directly.
2. **TBD — whether the new Standard's maps are published as downloadable data or only as web viewers.**
   If carriers publish standardised four-category coverage under the Standard, that is a fifth source
   per community with a quality gradation the ACCC dataset lacks. Nothing in this lane's searching
   established a machine-readable release. *Settled by:* checking Telstra/Optus/TPG coverage-map pages
   for a data download or tile/REST endpoint, and checking whether ACMA publishes a consolidated layer.
3. **TBD — verbatim quotes with page numbers from the ACCC Regional Mobile Infrastructure Inquiry final
   report (July 2023).** accc.gov.au returns HTTP 403 to curl and the PDF returned via WebFetch could
   not be text-extracted. *Settled by:* fetching the PDF through a browser session or a mirror and
   extracting text locally.
4. **TBD — whether the main body of the 2024 RTIRC report contains a coverage-map finding.** Only the
   4-page recommendations extract was retrieved and searched; "coverage map" does not appear in it.
   *Settled by:* downloading the full report from `https://www.rtirc.gov.au/` and searching it.
5. **TBD — the ACCAN "30% did not receive the coverage they expected" figure.** Title, date, sample
   size and methodology of the underlying ACCAN research are unverified; the figure reached this report
   through a search-result summary only. *Settled by:* locating the ACCAN publication on accan.org.au
   and citing it directly. Same for the "not auditable" characterisation at 6.7.
6. **TBD — whether the National Audit of Mobile Coverage publishes NT results as a downloadable
   dataset, and under what licence.** This is the only Australian programme found that measures rather
   than models coverage, so its data status is material to what "independent published source" can
   mean here. *Settled by:* checking the audit page and data.gov.au for a published resource.
7. **TBD — the total number of distinct BushTel community IDs and whether the API permits bulk
   retrieval.** IDs 1–200 yielded 146 live records; 1,100/1,200/1,500/2,000 returned nothing, so the
   range appears to end somewhere between 1,000 and 1,100. The bulk endpoint referenced in the app
   bundle (`/api/Community/Report/Profile?ids=`) returned HTTP 404 for both `ids=1,2,3` and a 1,200-id
   list — wrong method, casing or parameter format. *Settled by:* enumerating ids 1..1200 individually
   (~1,200 requests), or inspecting the bundle's call site for the correct verb and payload.
8. **TBD — BushTel's terms of use and whether its API is intended for programmatic reuse.** No licence
   statement was located for the API. The five data.nt.gov.au spreadsheets are explicitly CC-BY;
   BushTel is a separate NT Government web service and its terms were not established. *Settled by:*
   reading the BushTel site's terms/copyright page, or asking NT DCMC.
9. **TBD — whether any `Services` entry in BushTel covers mobile or telecommunications.** Only one
   community record (ID 1, a family outstation with 7 services) was inspected in full. A larger
   community may carry a telecommunications service type. *Settled by:* inspecting `Services` across a
   sample of `Major`/`Minor` community records.
10. **TBD — the true geometric resolution of each carrier's ACCC coverage KML.** Measured for two files:
    TPG 5G 2021 is a ~100 m vectorised grid; Telstra 4G 2025 is an irregular high-precision contour.
    The other carriers/years/standards were not measured and **should not be assumed to match either**.
    *Settled by:* sampling vertex spacing per carrier per year on the NT subset after clipping.
11. **TBD — whether the ACCC coverage maps can be attributed to individual sites.** The polygons carry
    only `FID`; nothing links a polygon to the `RFNSA ID` of the site that generates it. Whether
    coverage at a community can be traced to a specific base station is therefore unresolved from this
    dataset alone. *Settled by:* checking whether the per-frequency-band ZIP bundles carry richer
    attributes than the aggregated technology-level maps.
12. **TBD — ACCC vs ACMA NT site-count reconciliation.** ACCC 2025 gives 247 NT Telstra sites; ACMA RRL
    gives 333 NT Telstra cellular transmit sites on 2026-09-12. The causes (different reference dates,
    multiple RRL `SITE_ID`s per physical facility, different definitions of "site") are hypothesised,
    not verified. *Settled by:* matching RRL sites to ACCC sites by coordinate proximity and inspecting
    the unmatched residue.
13. **TBD — whether `Ext Ant` or `Outdoor` is the right standard for a community-level claim**, and
    whether every carrier/year pair even has both. The inventory shows many gaps (e.g. Telstra 5G has
    Outdoor only, never Ext Ant; Optus 4G 2021 is a combined "Outdoor & Ext Ant" file). A trend across
    2018–2025 cannot hold the standard constant for all carriers. *Settled by:* building the full
    carrier x technology x standard x year availability matrix from the guide's tables.
14. **TBD — NT bounding box vs true NT boundary.** All NT counts above use the bbox
    lat −26.1..−10.8, lon 128.9..138.1, which includes small areas of WA, SA and QLD near the corners.
    *Settled by:* clipping to the ABS NT state polygon (available live at
    `https://geo.abs.gov.au/arcgis/rest/services/ASGS2021/...`) and re-counting.
15. **TBD — the licence status of the First Nations Connectivity Mapping Tool's ArcGIS services for
    reuse.** The portal item API 403s, so per-item `licenseInfo` could not be read; the data dictionary
    marks the document OFFICIAL and names CC-BY-4.0 only for the ABS and NNTT layers. *Settled by:*
    reading the tool's disclaimer page (pages 4–5 of the data dictionary) in full and the service-level
    `copyrightText` for each layer used.

---

## Artefacts

All files downloaded during this research were written to `reports/tmp/` and **deleted on completion**,
as instructed. Nothing from this lane remains on disk except this report. Every URL cited above was
resolved on 2026-09-12; sizes and timings are measured values from this machine on that date.
