# Arena lane D — "service": measuring the gap between what a service needs and what a community can get

Research lane D. Unit of analysis: **a service a person needs**, not a signal.
All checks performed **12 September 2026** unless a different date is stated on the finding.
No verdict, no ranking — findings only.

Conventions used below:
- **Confirmed** = I retrieved the artefact myself (HTTP status, byte size, parsed content recorded).
- **Reported** = a source states it, but I did not retrieve the underlying artefact.
- **TBD — needs validation** = not established; the line says what would settle it.

---

## 1. NBN data: what is public, what the terms are, and whether technology-by-community is obtainable for ~100 NT communities without scraping

### 1.1 The nbn address-lookup API is live, undocumented, and returns technology type — Confirmed
Checked 2026-09-12. Two endpoints on host `places.nbnco.net.au` (a different host from `www.nbnco.com.au`):

- Autocomplete: `https://places.nbnco.net.au/places/v1/autocomplete?query=<text>` → HTTP 200, JSON `suggestions[]` with a Google-Places-style `id` and `formattedAddress`.
- Detail: `https://places.nbnco.net.au/places/v2/details/<id>` → HTTP 200, JSON.

Detail response for `44 Perdjert St, Wadeye NT 0822`:

```json
{"servingArea":{"csaId":null,"techType":"SATELLITE","serviceType":"Satellite","serviceStatus":"available"},
 "addressDetail":{"latitude":-14.23751,"longitude":129.5202507,"reasonCode":"SAT_SA",
                  "serviceType":"Satellite","serviceStatus":"available","techType":"SATELLITE","issuburb":false},
 "addressSplitDetails":{"address1":"44 Perdjert St","locality":"Wadeye","state":"NT","postcode":"0822"}}
```

Fields returned: `techType`, `serviceType`, `serviceStatus`, `reasonCode`, `latitude`, `longitude`, `issuburb`, plus a split address. `v1/details` returns the same plus a `serviceabilityMessage`. Both work with only a `User-Agent` and a `Referer: https://www.nbnco.com.au/` header — no key, no auth, no cookie.

### 1.2 The API answers at **locality level**, not only address level — Confirmed
The autocomplete returns suburb/locality entries (`"Wadeye NT, Australia"`), and the detail call on a locality id returns `"issuburb": true` with a technology type. This is the mechanism that makes ~100 communities cheap: **one autocomplete call + one detail call per community name**, no HTML parsing, no page rendering.

### 1.3 Batch test over 18 NT remote communities — Confirmed
Run 2026-09-12, one autocomplete + one detail per name, 0.4 s between calls, all HTTP 200:

| Community (query) | techType | serviceType | reasonCode |
|---|---|---|---|
| Wadeye NT | SATELLITE | Satellite | SAT_SA |
| Maningrida NT | SATELLITE | Satellite | SAT_SA |
| Galiwinku NT | SATELLITE | Satellite | SAT_SA |
| Yuendumu NT | SATELLITE | Satellite | SAT_SA |
| Papunya NT | SATELLITE | Satellite | SAT_SA |
| Hermannsburg NT | SATELLITE | Satellite | SAT_SA |
| **Nhulunbuy NT** | **FTTP** | Fixed line | FTTP_SA |
| **Tennant Creek NT** | **FTTN** | Fixed line | FTTN_SA |
| Borroloola NT | SATELLITE | Satellite | SAT_SA |
| Ngukurr NT | SATELLITE | Satellite | SAT_SA |
| Yirrkala NT | SATELLITE | Satellite | SAT_SA |
| Lajamanu NT | SATELLITE | Satellite | SAT_SA |
| Ali Curung NT | SATELLITE | Satellite | SAT_SA |
| Gunbalanya NT | SATELLITE | Satellite | SAT_SA |
| Milingimbi NT | SATELLITE | Satellite | SAT_SA |
| Kintore NT | SATELLITE | Satellite | SAT_SA |
| Daly River NT | SATELLITE | Satellite | SAT_SA |
| Elliott NT | SATELLITE | Satellite | SAT_SA |

16 of 18 return `SATELLITE`. Each row also carries a lat/lon.

**Caveat, load-bearing:** a locality-level query returns **one** technology for the whole locality. Where a locality is genuinely mixed (fixed wireless edge, a fixed-line pocket) the single value hides that. Cross-checking against the polygon footprints in 1.5 is the way to detect it. Do not present a locality-level `techType` as a premises-level fact.

### 1.4 Terms of use of the nbn site — Confirmed, and restrictive
`https://www.nbnco.com.au/utility/terms-and-conditions-of-use`, checked 2026-09-12, page states **last updated September 2017**. Relevant clauses (quoted from the page):

- Content may be used "for your own personal purposes" only.
- Users must not "copy, reproduce, republish, frame, post, upload, distribute, transmit, sublicense, delete or modify in any way" site materials without written consent.
- Must not use "any device, software or routine which will or may interfere with the working or functioning of our website".
- Accuracy disclaimer: "we cannot guarantee the accuracy, currency or completeness of the information provided. We accept no responsibility for errors in the content on this website at any time."

`https://www.nbnco.com.au/robots.txt` (HTTP 200, checked 2026-09-12) contains `Disallow: /api/` for `User-Agent: *`. **That robots file governs `www.nbnco.com.au`, not `places.nbnco.net.au`** — `https://places.nbnco.net.au/robots.txt` returns HTTP 404 (no robots file at all).

**Net position:** the API is technically open and unrobots-restricted on its own host, but the site terms are personal-use and forbid republication of content without written consent, and there is no stated open licence. Redistributing a derived per-community technology table sourced from this API is not covered by any licence I could find. TBD — needs validation: whether nbn grants written consent for a student/competition use; an email to nbn's media/data contact would settle it.

### 1.5 Bulk, openly licensed NBN footprint data on data.gov.au — Confirmed, CC BY 4.0
Dataset: **National Broadband Network**, `https://data.gov.au/data/dataset/national-broadband-network`
CKAN API: `https://data.gov.au/data/api/3/action/package_show?id=national-broadband-network` (HTTP 200, 13,632 bytes).

- Publisher: Department of Infrastructure, Transport, Regional Development, Communications, Sport and the Arts; copyright owned by NBN Co.
- Licence: **Creative Commons Attribution 4.0 International** (`cc-by-4.0`).
- Data prepared **as of 26 March 2024**; dataset metadata last modified 2024-10-21.
- Disclaimer in the dataset notes: data provided "as is", no warranty of accuracy/completeness, NBN Co does not independently validate it.

Resources (all verified):

| Format | Name | Size | URL |
|---|---|---|---|
| ZIP (shapefile) | NBN Fixed Line Footprint | 9,460,437 B — HEAD returned `Content-Length: 9460437`, `Content-Type: application/zip`, `Last-Modified: Mon, 21 Oct 2024 04:17:58 GMT` | `https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc/download/nbn_coverage_fixedline_2024-03-26.zip` |
| ZIP (shapefile) | NBN Fixed Wireless Footprint | 378,833,757 B (~361 MB) | `https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f/download/nbn_coverage_wireless_2024-03-26.zip` |
| WMS | NBN Broadband Service Footprints (March 2024) | n/a | `https://spatial.infrastructure.gov.au/server/services/NBN_Coverage_Footprints_2024/MapServer/WMSServer?request=GetCapabilities&service=WMS` |

**There is no satellite footprint resource in this dataset.** The two polygons published are fixed line and fixed wireless. Sky Muster is the residual: a premises outside both is a satellite premises. That is consistent with the API results in 1.3 (`SAT_SA` = satellite serving area).

### 1.6 The older DITRDCSA dataset — Confirmed, WMS only
**National Broadband Network: Connections by technology type – July 2020**, `https://data.gov.au/data/dataset/national-broadband-network-connections-by-technology-type`. Licence CC BY 4.0, metadata modified 2024-08-08. The CKAN record now lists **one** resource — a WMS service. The per-technology KML/shapefile resources referenced in older search results are no longer enumerated in the package. Superseded by 1.5 for any current work.

### 1.7 Sky Muster coverage footprint — TBD — needs validation
No downloadable Sky Muster footprint polygon was found on data.gov.au or the DITRDCSA catalogue. nbn's public position is that Sky Muster serves the whole country (i.e. the footprint is "everywhere not in the other two footprints"). **What would settle it:** a published Sky Muster beam/spot-beam coverage layer from nbn, or an explicit nbn statement of 100% national coverage with a date. Until then, treat "satellite" as the complement of the fixed-line and fixed-wireless polygons, and say so in the methodology.

### 1.8 Can technology-by-community be obtained for ~100 NT communities without scraping?
**Yes, two independent ways, and they cross-check each other:**
1. **API route** (1.1–1.3): ~200 JSON calls total for 100 communities. No HTML parsing. Licensing is the problem, not the mechanism (1.4).
2. **Open-data route** (1.5): download two CC BY 4.0 shapefiles, point-in-polygon each community centroid, classify as fixed line / fixed wireless / satellite-by-residual. Fully licensed for republication with attribution; the cost is that it is a 26 March 2024 snapshot and it cannot distinguish FTTP from FTTN inside the fixed-line polygon.

Neither is "scraping" in the sense of parsing rendered HTML.

---

## 2. Bandwidth and latency requirements, from official or authoritative sources

### 2.1 Telehealth video — healthdirect Video Call — Confirmed, and this is the one to use
`https://help.vcc.healthdirect.org.au/technical-basics/bandwidthdatausage`, checked 2026-09-12. healthdirect Video Call is the Australian-Government-funded national video consulting platform. Published figures:

| Metric | Value |
|---|---|
| Minimum broadband speed, 2-endpoint call | **350 kbps upstream and downstream** |
| Latency | **"should not be more than 100 milliseconds"** |
| Bandwidth used when available | up to 1 Mbps |
| Data usage, 30-min two-person call | ~158 MB at 350 kbps; ~450 MB at 1 Mbps |
| Group call downstream | **(n − 1) × 350 kbps** (10 participants ≈ 3.1 Mbps) |
| Full HD, two participants | 2.5–3.5 Mbps up and down |
| Full HD, four participants | 7.5 Mbps up and down |

Packet-loss threshold: not published (page mentions packet loss qualitatively). No last-updated date on the page.

**The 100 ms latency line is the sharpest number in this whole lane.** See 2.6: measured Sky Muster latency is ~665 ms.

### 2.2 RACGP — TBD — needs validation
`https://www.racgp.org.au/FSDEDEV/media/documents/Running%20a%20practice/Technology/Video%20consultations/Implementation-guidelines-for-video-consultations-in-general-practice.pdf` returned a 1.1 MB PDF but the fetch tool could not extract readable text from it (binary stream). Other RACGP guides exist:
- `https://www.racgp.org.au/getmedia/764ab82e-7dea-434e-94ca-cab808f7b5eb/Telehealth-video-consultations-guide.pdf.aspx`
- `https://www.racgp.org.au/running-a-practice/technology/clinical-technology/telehealth`

**What would settle it:** download the PDFs and extract text locally (pymupdf works; it parsed other PDFs in this lane fine) and confirm whether RACGP states a numeric kbps/Mbps floor at all. My working expectation is that RACGP gives qualitative guidance and defers to platform specs, which is why 2.1 is the load-bearing source — but that is an expectation, not a finding.

### 2.3 Australian Digital Health Agency — TBD — needs validation
`https://www.digitalhealth.gov.au/healthcare-providers/initiatives-and-programs/telehealth` exists; no numeric bandwidth/latency threshold surfaced in search. An older MBS-online document ("Guidance on Security, Privacy and Technical Specifications for Clinicians", 31/08/2011, `.doc`) is the only ADHA-adjacent technical spec found and is 15 years old. **What would settle it:** fetch and read the ADHA telehealth page and the MBS guidance document in full.

### 2.4 Online learning — Microsoft Teams — Confirmed, and directly relevant to NT distance education
Katherine School of the Air states it "utilises Microsoft Teams as an all in one platform to deliver lessons and course material" (`https://www.ksa.nt.edu.au/`, reported via search 2026-09-12 — **TBD: confirm by fetching the KSA page directly**). Microsoft's published requirements, `https://learn.microsoft.com/en-us/microsoftteams/prepare-network`, page metadata `updated_at: 2026-07-14`, checked 2026-09-12:

| Modality | Minimum (up/down kbps) | Recommended | Best performance |
|---|---|---|---|
| Audio, one-to-one | 10/10 | 58/58 | 76/76 |
| Audio, meetings | 10/10 | 58/58 | 76/76 |
| Video, one-to-one | 150/150 | 1,500/1,500 | 4,000/4,000 |
| **Video, meetings** | **150/200** | **2,500/4,000** | 4,000/4,000 |
| Screen sharing, one-to-one | 200/200 | 1,500/1,500 | 4,000/4,000 |
| **Screen sharing, meetings** | **250/250** | **2,500/2,500** | 4,000/4,000 |

Minimum tier = video up to 240p, screen share 1.875–7.5 fps. Recommended tier = up to 1080p, screen share 7.5–30 fps. Teams events without an eCDN: **~2 Mbps per viewer** (3 Mbps for 1080p). Microsoft's page does **not** publish a numeric RTT/jitter/packet-loss table at this URL; it discusses jitter and packet loss qualitatively. **TBD — needs validation:** Microsoft's separate "Network Planner" / call-quality docs may carry numeric RTT and packet-loss targets; those pages were not fetched.

### 2.5 NT distance education — partially confirmed
- NT has **3 schools of distance education**: Alice Springs School of the Air, Katherine School of the Air, and the Northern Territory School of Distance Education (`https://nt.gov.au/learning/primary-and-secondary-students/distance-and-online-learning`, reported via search). The NT School of Distance Education appears in the ACARA school location file (see 3.1) at The Gardens NT 0820, lat −12.4396, lon 130.8340.
- **nbn Sky Muster Education Port**: a dedicated modem port for distance-education and home-school students, **50 GB per student** of education data. Reported via search 2026-09-12. **TBD — needs validation:** whether the Education Port still exists after the 1 March 2025 move to uncapped Sky Muster Plus Premium (see 2.7); a current nbn page or RSP page would settle it.
- No NT Department of Education document publishing a minimum bandwidth for its distance-education platform was found. **TBD — needs validation.**

### 2.6 ACCC Measuring Broadband Australia — Confirmed for satellite, the key latency evidence
`https://www.accc.gov.au/media-release/broadband-performance-of-satellite-services-measured-for-the-first-time`, release 147/24, **5 December 2024**, checked 2026-09-12:

| Metric | NBN Sky Muster | Starlink |
|---|---|---|
| Average latency, all hours | **664.9 ms** | 29.8 ms |
| Busy-hour download | 66.1% of maximum plan speed | 165.5 Mbps average |
| Busy-hour upload | 102.6% of plan speed | 27.8 Mbps average |

The media release does not state sample size or packet loss. MBA methodology: data collected by SamKnows; latency defined as the average time to send a packet to the test server and back. MBA also publishes an average web-page load time across eight popular Australian webpages (3.2 s for NBN fixed wireless, all hours and busy hours). Programme and later reports: `https://www.accc.gov.au/by-industry/telecommunications-and-internet/telecommunications-monitoring/measuring-broadband-australia-program/latest-performance-report` and `https://www.accc.gov.au/consumers/telecommunications-and-internet/broadband-performance-data`.

**TBD — needs validation:** whether the ACCC publishes the MBA underlying data as a downloadable file (per-service, per-technology) rather than only PDF reports, and whether any MBA panel devices sit in the NT. MBA volunteers are self-selected and satellite panels are small; NT remote representation is the obvious weak point and should be checked before any per-community claim rests on MBA.

### 2.7 Sky Muster / Sky Muster Plus Premium plan specs — Confirmed
`https://www.nbnco.com.au/learn/network-technology/sky-muster-explained/sky-muster-plus-explained`, checked 2026-09-12:

| Tier | Max wholesale speed | Anticipated typical busy-period download |
|---|---|---|
| Entry | 25/5 Mbps | 21 Mbps |
| Mid | 50/5 Mbps | 38 Mbps |
| High | 100/5 Mbps | 63 Mbps |

All tiers **uncapped data**. The page states satellite users "may also experience latency" without a figure. From **1 March 2025** nbn no longer offers the older capped Sky Muster Plus plans; Sky Muster Plus Premium across three speed tiers replaced them, with installation and equipment at no wholesale cost (reported via search 2026-09-12; nbn media statement `https://www.nbnco.com.au/corporate-information/media-centre/media-statements/nbn-unveils-nbn-sky-muster-plus-premium-offering-even-more-connectivity-options-for-australia` — **TBD: fetch that statement for the exact date and wording**).

**Note the shape of the gap this produces:** on paper a Sky Muster Plus Premium entry tier (21 Mbps typical busy-period download) clears every *bandwidth* threshold in 2.1 and 2.4 comfortably. It fails the *latency* threshold in 2.1 by a factor of about 6.6 (665 ms vs 100 ms). A bandwidth-only model would score these communities as fine.

### 2.8 Universal Service Obligation and Statutory Infrastructure Provider — Confirmed (definitions), reported (figures)
- The **Universal Service Guarantee (USG)** comprises two regimes: the **USO** (voice — Telstra as statutory primary universal provider must supply fixed voice services and payphones on reasonable request) and the **Statutory Infrastructure Provider (SIP) regime** (broadband).
- **SIP obligation: peak download/upload of at least 25/5 Mbps.** Reported via search 2026-09-12 from `https://www.infrastructure.gov.au/media-communications/modernising-universal-telecommunications-services` and ACMA `https://www.acma.gov.au/about-universal-service-obligation`. **TBD — needs validation:** confirm the 25/5 figure and whether it is "peak" or "typical" directly against the Telecommunications Act 1997 Part 19 / the relevant legislative instrument. The legislation is at `https://www.legislation.gov.au/` — a specific instrument URL for the STS standard found was `https://www.legislation.gov.au/F2023L00221`.
- Department consultation "Increasing minimum legislated broadband speeds": `https://www.infrastructure.gov.au/have-your-say/increasing-minimum-legislated-broadband-speeds`. Status and outcome not checked — **TBD**.

### 2.9 Universal Outdoor Mobile Obligation (UOMO) — Confirmed as to scope and timing
- Announced **25 February 2025**. Bill: **Telecommunications Legislation Amendment (Universal Outdoor Mobile Obligation) Bill 2025**, amending the Telecommunications (Consumer Protection and Service Standards) Act 1999.
- **Scope: baseline outdoor mobile SMS and voice only** — not data. Delivered via direct-to-handset LEO satellite; applies to Telstra, Optus and TPG; framed as covering the ~5 million km² of Australia currently without mobile coverage, wherever a handset "can see the sky".
- **Default commencement 1 December 2027**, with power to bring forward or delay.
- Sources: Explanatory Memorandum `https://classic.austlii.edu.au/au/legis/cth/bill_em/tlaomob2025773/memo_0.html`; Parliamentary Library bills digest `https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/bd/bd2526/26bd039`; department page `https://www.infrastructure.gov.au/department/media/news/universal-outdoor-mobile-obligation-improve-outdoor-mobile-obligation-across-australia` (department landing: `https://www.infrastructure.gov.au/have-your-say/consultation-universal-outdoor-mobile-obligation-uomo-draft-legislation`). All reported via search 2026-09-12.
- **TBD — needs validation:** whether the Bill has passed and received assent as at 2026-09-12, and the exact statutory definition of "baseline outdoor mobile coverage". Fetch the AustLII EM and the APH bill homepage directly.

**Relevance to this lane:** UOMO guarantees voice and SMS outdoors. It does not guarantee the bandwidth any service in 2.1 or 2.4 needs. A service-gap model must not treat UOMO as closing a telehealth or online-learning gap.

### 2.10 2024 Regional Telecommunications Review (RTIRC) — Confirmed, full text retrieved
Report: **"Connecting communities, reaching every region"**, provided to the Minister and tabled **13 December 2024**.
- Recommendations PDF (downloaded 2026-09-12, HTTP 200, 1,063,930 B, `application/pdf`): `https://www.rtirc.gov.au/sites/default/files/documents/rtirc-report-2024-recommendations.pdf`
- Full report PDF: `https://www.infrastructure.gov.au/sites/default/files/documents/2024-regional-telecommunications-review.pdf` · DOCX: `.../2024-regional-telecommunications-review.docx`
- Government response: `https://www.infrastructure.gov.au/department/media/publications/australian-government-response-2024-regional-telecommunications-independent-review-committee-report`

All 14 recommendations were extracted. The ones that bear on service standards and on this lane's mechanism:

- **Rec 3 — Expedite universal service modernisation.** Merge the USO and SIP regimes into a **unified service obligation**; NBN Co as provider of last resort required to provide **voice-capable broadband services with minimum speeds and standards for all premises**. The modernised USO is to be **technology-neutral** and **flexible, so minimum speeds, quality and other standards are readily adaptable**. Premises without terrestrial mobile coverage to have access to an **affordable secondary redundant broadband service including optional battery backup**. Copper Continuity Obligation to be phased out where proven voice-capable broadband exists. **Note: the Committee recommends minimum speeds exist; it does not name a number.**
- **Rec 5 — Affordability.** Pre-paid low-cost broadband plans in remote First Nations communities, as proposed by the First Nations Digital Inclusion Advisory Group; **unmetered access to critical government websites** for users on limited data plans; ongoing funding for the School Student Broadband Initiative (SSBI).
- **Rec 6 — National telecommunications data platform.** Managed by ACMA or ACCC. For consumers, an interactive tool giving **detailed information on broadband and mobile service availability in their area**. For governments, restricted infrastructure-asset location data. Providers to be **required to supply data to governments in standardised formats to enable comparisons between locations and providers**. MBA to continue beyond its current contract.
- **Rec 2 — Improving the mobile experience:** prioritise capacity/quality/resilience in existing coverage areas over further extending terrestrial coverage; mandate emergency roaming during disasters.
- **Rec 10 — Embedding community Wi-Fi:** continue STAND funding; new community connectivity hubs; **expand mesh Wi-Fi in remote First Nations communities, prioritising communities without mobile coverage**; free public Wi-Fi.
- **Rec 13 — Powering connectivity:** minimum backup power periods for new critical telecommunications infrastructure in regional/remote Australia, mandated by regulation.
- Others: Rec 1 connectivity literacy / Connectivity Champions / First Nations Digital Mentors; Rec 4 consumer protection review; Rec 7 regional connectivity strategy; Rec 8 modernising programs + public project-tracking website; Rec 9 continue the First Nations Digital Inclusion Advisory Group as a standing initiative; Rec 11 transition oversight; Rec 12 expedite planning approvals; Rec 14 permanent Regional Telecommunications Commissioner or Advisory Panel.

### 2.11 Services Australia / myGov bandwidth requirement — TBD — needs validation, and likely does not exist
No published minimum internet speed or latency requirement for myGov or Centrelink online could be found. Pages checked via search 2026-09-12: `https://my.gov.au/en/about/help/mygov-app/help-using-the-mygov-app`, `https://www.servicesaustralia.gov.au/centrelink-online-account`, `https://my.gov.au/en/about/terms`.
**What would settle it:** a Services Australia accessibility/system-requirements page, or an FOI/enquiry response. If nothing exists, the honest modelling move is to derive a myGov requirement from page weight measured directly (fetch the myGov sign-in flow, measure bytes and round-trips) rather than cite a number nobody published.

---

## 3. Service locations in the NT as open data

### 3.1 Schools — ACARA School Location 2025 — Confirmed, downloaded and parsed
- `https://dataandreporting.blob.core.windows.net/anrdataportal/Data-Access-Program/School%20Location%202025.xlsx` — HTTP 200, **2,317,091 B**, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, downloaded 2026-09-12.
- Sheets: `DataDictionary`, `SchoolLocations 2025`. **11,035 school rows nationally; 221 with State = NT.**
- Columns include: Calendar Year, ACARA SML ID, School Name, Suburb, State, Postcode, School Sector, School Type, Special school, Campus Type, **Latitude, Longitude**, ASGS Remoteness Area code and label (e.g. "Outer Regional"), Mesh Block, **SA1, SA2 (code + name), SA3, SA4, LGA (code + name)**, Federal electorate.
- Licence: **"My School terms of use"** — *not* an open CC licence. Listing page: `https://www.acara.edu.au/contact-us/acara-data-access`. **TBD — needs validation:** read the My School terms of use and confirm whether redistribution of a derived table is permitted, and what attribution is required. This matters: a competition submission that republishes derived rows needs to know.
- Companion file, same page and same terms: `School Profile 2025.xlsx` (enrolments, ICSEA, LBOTE, SEA) — useful as a denominator for "students affected".
- The **Australian Schools List** (`https://asl.acara.edu.au/`) links `http://creativecommons.org/licenses/by/4.0` in its footer — so ASL content may be CC BY 4.0 while the Data Access Program files are under My School terms. **TBD — needs validation:** which licence attaches to which artefact.

### 3.2 Schools — NT Department of Education directory — Confirmed, open JSON endpoint
- `https://directory.ntschools.net/api/School/GetAllSchoolsForDirectory` — HTTP 200, 81,935 B, JSON array of **273 NT schools**. Fields: `schoolName`, `schoolType`, `electorate`, `decsRegion`, `isGovernment`, `itSchoolCode`, `isPreSchool`. **No coordinates in this list.**
- Per-school endpoint exists: `/api/School/GetSchool` (address likely present; not exercised).
- Catalogued on the NT open data portal as **School List**, `https://data.nt.gov.au/dataset/school-list`, **licence Creative Commons Attribution**, metadata modified 2021-06-22. The portal's CSV resource points at `https://directory.ntschools.net/#/downloads`.
- Note the count discrepancy: 273 (NT directory, includes preschools) vs 221 (ACARA NT rows). They count different things; reconcile before using either as a denominator.

### 3.3 Health clinics, schools, stores, police, Centrelink-adjacent services — **Bushtel** — Confirmed, and this is the single richest NT source found in this lane
`https://bushtel.nt.gov.au/` is the NT Government's remote community profile portal. It has an **undocumented but open ASP.NET Web API**, discovered from its own JS bundle (`/public/dist/bundle.js?v=2.5.26`). All endpoints below returned HTTP 200 on 2026-09-12 with only a User-Agent and Referer:

| Endpoint | Returns |
|---|---|
| `https://bushtel.nt.gov.au/api/Community/GetCommunities` | JSON array, **797 communities**, `{CommunityId, Name}` |
| `https://bushtel.nt.gov.au/api/Community/ProfileListing` | Communities grouped A–Z with `CommunityTypeName` (Major / Family Outstation / …) |
| `https://bushtel.nt.gov.au/api/Community/CommunityAutocomplete?term=<x>` | Name + alias resolution |
| `https://bushtel.nt.gov.au/api/Community/Suburbs` | Suburb / postcode lookup |
| `https://bushtel.nt.gov.au/api/Community/Boundary?id=<id>` | Boundary layers (Land Councils, LGA, electorate …) with colours and label points |
| **`https://bushtel.nt.gov.au/api/Community/{id}`** | **Full community profile JSON** |
| `https://bushtel.nt.gov.au/api/Community/Report/Profile?ids=<id>&fromPage=PROFILE_PAGE` | The same profile as a PDF |

`GET /api/Community/426` (Wadeye) returned **225,184 B** of JSON. Structure confirmed:

- Identity: `Id`, `Name`, `DefaultName`, `AliasNames` ("Port Keats"), `Description`, `CommunityTypeName` ("Major").
- **Coordinates**: `Point.Longitude = 129.5205`, `Point.Latitude = -14.2404` (GDA94, from placenames values).
- **Population**: `2259`, `PopulationSource = "Based on ABS 2021 Census SA1"`, with the SA1 code in `PopulationCode`.
- Governance: `ElectorateName`, `WardName`, `LandCouncilName` + permit website, LGA via `Boundaries`.
- **`Capabilities`**: `{FixedPhone: true, Mobile: true, Internet: true, RoadAccess: true}` — four booleans per community, straight from the NT Government.
- **`Services`**: 21 entries for Wadeye, each `{ServiceType, Status (Y/N/U), Comments, VisibleBushtel, SortOrder}`. Observed service types:
  Cross Cultural Awareness Training Providers · Accessible by road · Road Open · Regular transport service · Fuel · Alcohol · Volatile substances · Commercial accommodation · **Community store** · Aerodrome · **Health centre** · Morgue facilities · **Police station** · **School** · **Library** · **Regional council service centre** · Employment services · **Mobile phone** · **STAND Site** · **Internet** · **WiFi**.
  Comments carry the operator and phone number (e.g. Health centre → "Primary Health Care delivered by Top End Health Service (8978 2360)"; School → "Our Lady of the Sacred Heart Thamarrurr Catholic College… Catholic Education Centre"; WiFi → "In the vicinity of the council offices. Mon–Sat 8am–8pm; Sun Off"; STAND Site → "Located at OLSH Thamarrurr Catholic College").
- `Businesses` (17 for Wadeye, with ABN/ORIC, name, email, website, locations), `ArdbServices` (FY 2025/26), `Projects` (137 entries with funder, status, title).
- The PDF form of the same profile (3,673,464 B, 22 pages for Wadeye) carries the disclaimer: "The information contained in this document is for general information purposes only… The Northern Territory of Australia makes no representations and gives no warranties…" and the contact `Bushtel@nt.gov.au`. Footer stamps the print date.

**This is the direct answer to the lane's unit-of-analysis constraint**: Bushtel gives, per community, the presence/absence of the physical service points (clinic, school, store, police, library, council service centre, public WiFi, STAND site) plus coordinates and an ABS-sourced population — the denominator for "how many people are affected".

**TBD — needs validation, and it is important:** Bushtel publishes **no licence statement** that I could find, only a disclaimer. It is not listed as a dataset on `data.nt.gov.au`. **What would settle it:** email `Bushtel@nt.gov.au` (or ask the DCDD judges' department, which is plausibly the custodian) for terms of reuse. Do not assume CC BY because other NT portal datasets are CC BY.

### 3.4 NT Remote Areas Mobile Coverage — Confirmed, downloaded and parsed (cross-reference for the "what can they get" side)
- Dataset: `https://data.nt.gov.au/dataset/mobile-phone-coverage-in-remote-areas-of-the-nt` — **Mobile Phone Coverage in Remote Areas of the NT 2022**, licence **Creative Commons Attribution**, metadata modified **2022-07-04**.
- File: `https://data.nt.gov.au/dataset/f39b9805-e333-4ce3-abae-d3a7e56284fa/resource/65a7e5d8-ac73-44e8-b87c-d691653d86b3/download/mobile-coverage-all-sites.xlsx` — HTTP 200, **24,602 B**, XLSX, downloaded 2026-09-12.
- Sheet `Communities with Mobile`, **188 data rows**. Columns: SITE NAME, SITE TYPE, POPULATION, MACRO CELL, SMALL CELL, PROXIMITY TO CELL, PROVIDER, **LATITUDE, LONGITUDE**.
- Site types: 148 COMMUNITY, 17 HIGHWAY, 15 TOURISM, 8 VILLAGE. Providers: 134 TELSTRA, 40 OPTUS/TELSTRA, 14 OPTUS.
- The sheet's own explanation note states macro cell ≈ up to 40 km, small cell ≈ up to 5 km, and — verbatim — **"Coverage varies according to local conditions especially topography and vegetation and this list is a GUIDE only."** Cities and towns (Darwin, Palmerston, Tennant Creek, Katherine, Alice Springs, Nhulunbuy, Jabiru) are excluded from the dataset.
- Two companion NT datasets exist with the same CC BY licence: `remote-communities-with-mobile-coverage` (3G/4G, 2021), `list-of-remote-communities-with-mobile-coverage` (Mobile Coverage and Backhaul Transmission, 2019), `remote-sites-with-mobile-phone-small-cell-coverage`, and `centre-for-appropriate-technology-mobile-phone-hotspots`.
- **This is a list of communities that HAVE coverage.** It is not a list of communities. The complement — communities absent from this file — is only derivable against a full community register such as Bushtel's 797 (3.3). That join is the mechanism by which "no coverage" becomes a positive finding rather than an absence of data.

### 3.5 Aboriginal community controlled health services — AMSANT — partially reported
AMSANT is the peak body for Aboriginal community controlled health services in the NT, with **26 member services** in urban, regional and remote locations, and publishes a map of member-service primary locations. `https://amsant.org.au/community-controlled-health-in-the-northern-territory/`. AMSANT's own note is that each dot is a head office or main clinic while operational reach extends much further. **TBD — needs validation:** whether member locations are downloadable with coordinates and under what licence; AMSANT would need to be asked. Bushtel's `Health centre` service field (3.3) is the machine-readable substitute that exists today.

### 3.6 Services Australia agents / access points / remote servicing — TBD — needs validation
- Programme pages confirmed to exist: `https://www.servicesaustralia.gov.au/agents-and-access-points`, `https://www.servicesaustralia.gov.au/agents-and-access-points-where-to-find-us?context=22636`, mobile service centres `https://www.servicesaustralia.gov.au/when-and-where-to-find-mobile-service-centres?context=22651`, and the **National Agent and Access Point (NAAP) program** via NIAA `https://www.niaa.gov.au/our-work/closing-gap/national-agent-and-access-point-naap-program-services-australia`.
- What an agent/access point provides is directly relevant: "self-service equipment including phones, **free Wi-Fi** and internet enabled self-service terminals with a scanning capability".
- The locator is `https://findus.servicesaustralia.gov.au/` — an ASP locator, not an open dataset. No open-data release of agent/access-point locations was found on data.gov.au (the only matching CKAN hit was `services-australia-service-delivery-quarterly-operational-data`, which is operational statistics, not locations, CC BY 2.5 AU).
- **What would settle it:** query `findus.servicesaustralia.gov.au` for NT and see whether it returns structured results; or find the NAAP host list published by NIAA. Until then, treat Centrelink access-point locations as **not available as open data**.

### 3.7 Banks and Australia Post — TBD — needs validation
No open dataset of Australia Post outlet or bank branch locations was found on data.gov.au (search returned no relevant hits). Australia Post publishes an outlet locator on its own site; APRA publishes an **Authorised Deposit-taking Institutions Points of Presence** statistical publication which historically included branch counts by SA2/postcode. Neither was fetched. **What would settle it:** check `https://www.apra.gov.au/` for the current Points of Presence release and its licence, and check whether Australia Post has a locator API. Bushtel's `Community store` and `Regional council service centre` fields (3.3) cover the physical-access-point question for many communities in the meantime.

---

## 4. ADII 2025 and the First Nations component

### 4.1 ADII 2025 geography — Confirmed
Report: **"Measuring Australia's Digital Divide: Australian Digital Inclusion Index 2025"**, PDF downloaded 2026-09-12, HTTP 200, **4,946,520 B**, 27 pages: `https://digitalinclusionindex.org.au/wp-content/uploads/2025/10/ADII-Report-2025_V6-Remediated.pdf` (also at APO `https://apo.org.au/node/332322`).

- Published geographies in the report text: **national, state/territory, and Local Government Area (LGA)**, plus the **five ASGS remoteness classes** (Major cities, Inner regional, Outer regional, Remote, Very remote). The report explicitly discusses "the LGA results".
- **No SA4 or Statistical Area language appears in the report text** (zero hits for "SA4", "Statistical Area").
- Dashboards: national/total `https://dashboard.digitalinclusionindex.org.au/Total.aspx`; First Nations `https://dashboard.digitalinclusionindex.org.au/FirstNations/Home/`. Both pages contain an export panel offering **XLSX and PDF** export via `Export.aspx` ("Please select the data format you would like to export", "Exporting to Excel will allow you to create your own chart"). So **the dashboard data is downloadable as XLSX**, per selected view.
- Note: `https://digitalinclusionindex.org.au/interactive-data-dashboards/` currently returns **HTTP 404** (checked 2026-09-12) even though it is linked from the ADM+S site; the two dashboard URLs above work.

### 4.2 ADII 2025 NT figures — Confirmed (quoted from the report)
- Sample: **3,065 respondents** to the Australian Internet Usage Survey, plus **807 First Nations respondents in remote and very remote communities through the Mapping the Digital Gap project** and **1,998 First Nations respondents across urban, regional and some remote areas through the Measuring Digital Inclusion for First Nations Australians project**.
- Overall Index scores by jurisdiction: NSW 74.0, Vic 74.1, WA 73.9 above national average; Qld 72.9, **NT 72.5**, SA 71.3 below; Tasmania lowest at 69.4.
- "The Northern Territory continues to face significant Access challenges."
- "Across all jurisdictions, inner-metropolitan areas score highly, while **remote and very remote Local Government Areas (LGAs) record the lowest scores**." Outliers noted: resource/mining centres score relatively higher despite remoteness.
- "**Access declines with remoteness. Very remote areas record Access scores of 19.4 points below the national average**, with remote First Nations communities facing even greater barriers to Access."
- National-level indicators: 9.7% rely only on a mobile connection; 11.5% have no fixed connection at home; 30.4% of mobile users use pre-paid.
- Telstra's stated commitment (in the report foreword): digital inclusion support for 1 million people by FY30, "with at least 200,000 in the Northern Territory, South Australia or Tasmania".

### 4.3 Are NT remote LGAs present or suppressed? — TBD — needs validation
The 2025 report contains **zero occurrences of "suppress" and zero of "sample size"** in its body text, and it reports LGA results in aggregate narrative form rather than as a published table. Whether individual NT remote LGAs (West Daly, East Arnhem, Central Desert, Barkly, MacDonnell, Roper Gulf, Victoria Daly, Tiwi Islands, West Arnhem) each carry a published score, or are collapsed/withheld for small sample, could **not** be established from the report.

**What would settle it:** drive the `Total.aspx` dashboard's geography selector to NT → LGA and export the XLSX, then check which LGAs return a value and which return blank/suppressed. The export panel exists (4.1); the selector options are loaded by AJAX and were not enumerated in this lane. Also relevant: `https://digitalinclusionindex.org.au/how-we-collect-the-data/` and `https://digitalinclusionindex.org.au/national-data-collection/` were not fetched.

### 4.4 Mapping the Digital Gap — Confirmed as to scope, reports and NT communities
- Project: partnership between the **ARC Centre of Excellence for Automated Decision-Making and Society (ADM+S, RMIT)** and funding partner **Telstra**, part of the Australian Digital Inclusion Index research suite. Landing page `https://www.admscentre.org.au/mapping-the-digital-gap/`.
- **Phase one 2022–2024: 10–12 remote and very remote First Nations communities**, three annual research visits each, with local First Nations partner organisations and community co-researchers. **Phase two from 2025: 8 new communities.**
- Latest national release: **2025 Outcomes Report, 3 December 2025** — `https://apo.org.au/node/333014`; RMIT repository record `https://research-repository.rmit.edu.au/articles/report/Mapping_the_digital_gap_2025_outcomes_report/31290223` with a direct PDF at `https://research-repository.rmit.edu.au/articles/report/Mapping_the_digital_gap_2025_outcomes_report/31290223/1/files/61945360.pdf`. Prior: 2024 Outcomes `https://apo.org.au/node/329174`; 2023 Outcomes `https://apo.org.au/node/324397`. Background paper (objectives, context, methods): `https://research-repository.rmit.edu.au/articles/report/Mapping_the_digital_gap_-_background_paper_project_objectives_context_and_methods/31350880`.
- **Watch the domain.** The project site is `https://mappingthedigitalgap.com` (HTTP 200, WordPress/Automattic). `https://mappingthedigitalgap.com.au` also returns HTTP 200 but served a **parked "This domain may be for sale" page** when fetched on 2026-09-12, even though ADM+S links to the `.com.au` form. Cite the `.com` form.
- Publications index: `https://mappingthedigitalgap.com/about/publications/`.

**NT community reports confirmed on that index (all via APO, which is a stable repository):**

| Community | Reports found |
|---|---|
| **Galiwin'ku, NT** | 2026 `https://apo.org.au/node/333650` (6 Mar 2026) · 2023 `https://apo.org.au/node/327013` · 2022 `https://apo.org.au/node/321218` |
| **Gäṉgaṉ, NT** | 2026 `https://apo.org.au/node/334107` (21 Apr 2026) · 2023 `https://apo.org.au/node/327085` · 2022 `https://apo.org.au/node/321338` |
| **Yuelamu, NT** | 2024 `https://apo.org.au/node/331536` (28 Jul 2025) · 2023 `https://apo.org.au/node/326602` · 2022 `https://apo.org.au/node/321027` |
| **Wadeye, NT** | 2023 `https://apo.org.au/node/327673` · 2022 `https://apo.org.au/node/323181` |
| **Tennant Creek, NT** | 2023 `https://apo.org.au/node/328210` · 2022 `https://apo.org.au/node/320686` |

Five NT communities in phase one. Note Wadeye and Galiwin'ku both appear here **and** in the Bushtel register (3.3) and the nbn batch test (1.3) — those three sources can be joined on the same community.

### 4.5 Mapping the Digital Gap variables and data availability — TBD — needs validation
- Variables measured: the three ADII dimensions **Access, Affordability, Digital Ability**, plus **media and information services / service delivery** as a fourth strand in the outcomes reports.
- **The community reports appear to be PDFs only.** The publications index shows no data files, no CSV, no repository dataset. No licence statement and no data-sovereignty statement was found on the publications page or the ADM+S project page, despite the project's stated Indigenous leadership and community co-researcher model.
- **What would settle it:** (a) check the RMIT research repository record for a dataset (not report) deposit and its licence; (b) read the 2025 Outcomes Report's methods section for a data-access/data-sovereignty statement; (c) ask ADM+S directly. **Given Indigenous Data Sovereignty obligations, the absence of an explicit reuse licence should be read as "ask first", not as "public domain".** That is a finding worth carrying into the ethics section regardless of which mechanism wins.

### 4.6 First Nations connectivity headline figure — reported, primary source not retrieved
"**About 43% of the 1,545 First Nations communities and homelands across Australia have no mobile service** — including some with only a shared public phone or no telecommunications access." Attributed to the Mapping the Digital Gap 2023 Outcomes Report via RMIT's release `https://www.rmit.edu.au/news/all-news/2023/sep/mapping-digital-gap` and EurekAlert `https://www.eurekalert.org/news-releases/1002863`. Related published figures: 45.9% of remote First Nations research participants are highly digitally excluded vs 9.4% of the Australian population; 53.3% sacrifice paying for food/essentials to stay connected vs 19.1% for non-First Nations people.
The **interactive First Nations connectivity map** was developed as an outcome of the First Nations Digital Inclusion Advisory Group's advocacy — this is the organisers' sanctioned "First Nations Connectivity Mapping Tool". Advisory Group initial report: `https://www.digitalinclusion.gov.au/sites/default/files/documents/first-nations-digital-inclusion-advisory-group-initial-report.pdf`; roadmap discussion paper `https://www.infrastructure.gov.au/sites/default/files/documents/roadmap-discussion-paper.pdf`.
**TBD — needs validation:** the 43% / 1,545 figures against the 2023 Outcomes Report itself, and whether the mapping tool exposes downloadable data (that tool sits in another lane's scope; flagged here only because the NT subset of those 1,545 is the natural denominator for a service-gap model).

---

## 5. Prior art: service-reachability / "digital service desert" analyses for remote Australia

### 5.1 Mapping the Digital Gap — the closest prior art, and it is survey-based not model-based
See 4.4–4.6. What it measures: lived digital inclusion (Access / Affordability / Digital Ability) via in-community surveys with local co-researchers, per community, repeated annually. What it does **not** do: compute a per-service requirement-versus-availability gap. **Reusability:** the reports are readable and citable; the microdata is not published (4.5). Reusable as **ground truth to validate against**, not as an input layer.

### 5.2 Ngaanyatjarra Lands Telecommunications Project — Confirmed as prior art, WA not NT
Featherstone et al. — a documented case of a region with "one of the poorest levels of telecommunications service in Australia" leading to a fibre network across six desert communities plus satellite for the outer communities. `https://www.nnigovernance.arizona.edu/ngaanyatjarra-lands-telecommunications-project-quest-broadband-western-desert`. Method is case-study/action-research, not a reusable dataset.

### 5.3 Rennie et al., "At home on the outstation: Barriers to home Internet in remote Indigenous communities" — Confirmed as existing
*Telecommunications Policy*, `https://www.sciencedirect.com/science/article/abs/pii/S0308596112001309`. Examines cultural factors in uptake and use and how they should inform telecommunications policy. Paywalled abstract; not retrieved in full. **Relevance to this lane:** it is the standing counter-argument to any availability-only model — availability is not uptake, and a gap model that ignores affordability and household context will overstate what infrastructure alone fixes.

### 5.4 Infrastructure Australia — reported
- **2019 Australian Infrastructure Audit**: found that in regional centres and rural and remote areas, telecommunications infrastructure "often delivers costly services that provide poor connectivity, low speeds and data allowances, and poor reliability".
- **2021 Australian Infrastructure Plan**: telecommunications/digital infrastructure identified as critical to the regionalisation agenda.
- Infrastructure Priority List items: `https://www.infrastructureaustralia.gov.au/ipl/regional-telecommunications-transmission-capacity` and `https://www.infrastructureaustralia.gov.au/evaluations/western-australia-regional-digital-enhancement`.
- **TBD — needs validation:** whether the Audit or IPL publishes any underlying spatial data. My expectation is no — these are narrative documents with appendices — but I did not fetch them.

### 5.5 Productivity Commission — reported, and thin for this purpose
PC work on the data and digital dividend and on digital transformation discusses the digital divide at a national/economic level; nothing found that measures per-community service reachability. **TBD — needs validation:** the PC's "Australia's Data and Digital Dividend" interim/final reports, not fetched.

### 5.6 Optimizing Digital Solutions to Improve Access to Comprehensive Primary Health Care Services in Remote Indigenous Communities — Confirmed as existing
Protocol for a participatory action research project, PMC `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12489406/`. Open access. Not retrieved in full. This is the closest thing found to a **health-service-reachability** framing in remote Indigenous Australia. **TBD — needs validation:** read it; a protocol paper may name the outcome measures a judge from a health-adjacent department would recognise.

### 5.7 What was NOT found
No published analysis was found that does what this lane's mechanism describes: **per-community, per-service, requirement-versus-available-capability gaps for remote Australia.** The components all exist separately — service requirements (§2), technology availability (§1), service point locations (§3), lived inclusion (§4) — but I found no prior work that joins them. This is stated as a search result, not as a claim that none exists; absence of evidence after ~40 checks is weak evidence of absence.

---

## Other facts found

1. **`places.nbnco.net.au` returns coordinates for every lookup.** A community name goes in, a lat/lon comes out alongside the technology type. That means the API doubles as a geocoder for community names, independent of Bushtel's coordinates — two independent coordinate sources for the same community, which is exactly what a cross-check needs. Wadeye: nbn returns −14.2416, 129.5208 (locality) and −14.2375, 129.5203 (a street address); Bushtel returns −14.2404, 129.5205. All three agree to ~400 m.
2. **Bushtel's `Capabilities` block is an NT Government assertion of Internet/Mobile/FixedPhone presence per community**, separate from the 2022 mobile coverage spreadsheet and separate from carrier maps. That makes it a third independent source on the same question for 797 communities — directly useful to the brief's "sources disagree" framing.
3. **The NT mobile coverage spreadsheet is a list of the covered, not a census of communities.** 188 sites, of which 148 are communities, against Bushtel's 797 communities. The arithmetic of that difference is itself a finding, though the two registers use different inclusion rules (Bushtel counts family outstations) and must be reconciled before any percentage is quoted.
4. **Bushtel records STAND sites and public WiFi per community, with opening hours.** Wadeye's WiFi is "In the vicinity of the council offices. Mon–Sat 8am–8pm; Sun Off". A service-reachability model that treats connectivity as a 24/7 property of a place will be wrong for any community where the only access is a council-office hotspot that closes on Sunday.
5. **Bushtel carries a live visiting-services calendar.** The Wadeye profile printed 12 Sep 2026 lists Hearing Australia, Renal, Physicians, Physiotherapy, Paediatrics, Podiatry, Exercise physiology, Endocrinology and Hearing Services Audiology visits scheduled between 14 Sep and 13 Oct 2026, plus DriveSafe NT, Bush Court and a departmental visit. Telehealth demand is not hypothetical in these communities; it is what happens between visits.
6. **Bushtel population figures are ABS 2021 Census SA1-based and the SA1 code is in the payload** (`PopulationCode`), which gives a ready join to ABS TableBuilder without re-deriving the geography.
7. **ACARA's file carries SA1/SA2/SA3/SA4/LGA codes and an ASGS remoteness class per school.** Anything that needs a school-level geography join already has it; no spatial join required.
8. **The ADII dashboards export to XLSX** via `Export.aspx`, which is a cleaner path to ADII numbers than transcribing the PDF.
9. **`data.nt.gov.au` runs a standard CKAN API** (`/api/3/action/package_search`, `package_show`) and returns licence and modification dates. Every NT dataset inspected in this lane is **Creative Commons Attribution**. The connectivity-relevant ones are all stale: 2019, 2021, 2022 — none updated since 2022-07-04.
10. **RTIRC Rec 6 is, in substance, a request for the artefact this competition is asking teams to build**: a consumer-facing interactive tool showing detailed broadband and mobile service availability by area, with providers required to supply standardised data. Worth knowing that the recommendation exists and is unimplemented; judges from DCDD will know it.
11. **The ACCC's satellite measurement is only ~21 months old** (Dec 2024) and was the first time Sky Muster was measured in MBA at all. Before that release there was no independent measured latency figure for the technology most remote NT communities depend on.
12. **Sky Muster Plus Premium's uncapped data from 1 March 2025 removes the data-allowance dimension** that dominated earlier analyses of remote connectivity. Any study or dataset older than March 2025 that frames the remote broadband problem as "running out of data" is describing a product that no longer exists. Latency and busy-period contention are what remain.

---

## TBD — needs validation

Consolidated, each with what would settle it.

| # | Open question | What would settle it |
|---|---|---|
| T1 | Whether the nbn address/locality API may be used and its outputs republished for a public competition entry | Written consent from nbn, or an nbn open-data statement. The site ToU (Sept 2017) says personal purposes only. |
| T2 | Whether a Sky Muster coverage footprint is published anywhere as a spatial layer | An nbn or DITRDCSA spatial release, or an explicit nbn statement of 100% national coverage with a date |
| T3 | Whether RACGP publishes a numeric bandwidth/latency floor for video consultations | Download the two RACGP PDFs and extract text locally |
| T4 | Whether the Australian Digital Health Agency publishes any current numeric telehealth network spec | Fetch the ADHA telehealth page and the 2011 MBS technical guidance doc in full |
| T5 | Whether Services Australia/myGov publishes any minimum connection requirement | A Services Australia system-requirements page, or measure the myGov sign-in flow's bytes and round-trips directly |
| T6 | Whether the nbn Sky Muster Education Port (50 GB/student) survived the March 2025 move to uncapped plans | A current nbn or RSP page |
| T7 | Whether NT Department of Education publishes a minimum bandwidth for distance-education delivery, and confirmation that KSA uses Microsoft Teams | Fetch `https://www.ksa.nt.edu.au/` and the NT distance-learning pages directly |
| T8 | Whether Microsoft publishes numeric RTT/jitter/packet-loss targets for Teams | Fetch the Teams Network Planner and call-quality documentation pages |
| T9 | Whether ACCC publishes MBA underlying data as a file, and whether any MBA panel devices are in the NT | The MBA latest-performance-report page and its data annexes |
| T10 | The exact statutory SIP speed standard (25/5 peak?) and its instrument | Read Telecommunications Act 1997 Part 19 / the SIP instrument on legislation.gov.au |
| T11 | Whether the UOMO Bill has passed and received assent as at 2026-09-12, and the statutory definition of "baseline outdoor mobile coverage" | Fetch the APH bill homepage and the AustLII Explanatory Memorandum |
| T12 | Whether individual NT remote LGAs carry published ADII 2025 scores or are suppressed for small sample | Drive the `Total.aspx` dashboard geography selector to NT → LGA and export the XLSX |
| T13 | Whether Mapping the Digital Gap community-level data (not reports) is obtainable, and under what licence / data-sovereignty terms | RMIT research repository dataset records; the 2025 Outcomes Report methods section; ask ADM+S |
| T14 | Bushtel's terms of reuse — there is a disclaimer but no licence | Email `Bushtel@nt.gov.au`; Bushtel is an NT Government product and DCDD may be the custodian |
| T15 | Whether the ACARA "My School terms of use" permit republication of a derived table | Read the My School terms of use; also resolve whether ASL (CC BY 4.0 in footer) and the Data Access Program files carry different licences |
| T16 | Whether Services Australia agent / access point locations are obtainable as structured data for the NT | Query `findus.servicesaustralia.gov.au` for NT; check NIAA's NAAP program pages for a host list |
| T17 | Whether AMSANT member service locations are downloadable with coordinates and under what licence | Ask AMSANT |
| T18 | Whether APRA Points of Presence and/or an Australia Post locator give NT outlet locations as data | Check `https://www.apra.gov.au/` for the current Points of Presence release; check Australia Post for a locator API |
| T19 | Verification of the "43% of 1,545 First Nations communities have no mobile service" figure against its primary report | Read the Mapping the Digital Gap 2023 Outcomes Report (`https://apo.org.au/node/324397`) |
| T20 | Whether Infrastructure Australia or the Productivity Commission published any reusable spatial data alongside their narrative reports | Fetch the 2019 Audit / 2021 Plan and the PC data-and-digital-dividend reports |
| T21 | Reconciliation of NT school counts: 273 (NT directory, includes preschools) vs 221 (ACARA NT rows) | Compare the two lists on name/suburb |
| T22 | Reconciliation of community registers: Bushtel 797 vs NT mobile coverage 188 sites (148 communities) — different inclusion rules | Compare inclusion criteria before quoting any "X% of communities" figure |
| T23 | Whether locality-level `techType` from the nbn API ever disagrees with the CC BY footprint polygons for the same community | Point-in-polygon the community centroids against the two 2024 shapefiles and diff against the API results |
