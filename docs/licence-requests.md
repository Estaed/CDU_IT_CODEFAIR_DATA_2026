# Licence requests — drafts for Tarik to send from his CDU address

Drafted 2026-09-12 after the 20-community spike showed which sources ship in the app.
Fill in `[team number]` once registration confirms it. Send all three the same day; log the
send date and any reply under "Status" so the report's References section can cite it.

Sources that need no email: ACCC (CC BY 2.5 AU), ACMA RRL (licence permits derivatives and
their redistribution, attribution "Based on Australian Communications and Media Authority
information"), NT Government coverage lists (CC BY), NBN footprints (CC BY 4.0), ABS (CC BY 4.0).

---

## 1. BushTel — terms of reuse (the one source the app cannot do without)

**To:** Bushtel@nt.gov.au
**Cc:** opendata@nt.gov.au
**Subject:** Reuse of BushTel community profile data in a student competition entry (CDU IT Code Fair 2026)

Dear BushTel team,

I am an IT student at Charles Darwin University and part of Team [team number] in the CDU IT
Code Fair 2026 Data Innovation Challenge (theme: Remote Connectivity), judged on 7 October
2026 with a submission deadline of 30 September 2026.

Our entry is a non-commercial, offline-first web app and an 8-page report that show, for each
of the 96 BushTel "Major" and "Minor" communities, which digital services (telehealth video,
online schooling, government services) the community's connectivity can support, and how the
published coverage sources (ACCC, ACMA, NT Government lists) agree or disagree.

We would like to use the following BushTel profile fields, retrieved from bushtel.nt.gov.au on
12 September 2026:

- community name, aliases, coordinates, community type, NT region, ABS 2021 SA1 population;
- the "Services" list (health centre, school, community store, police station, library,
  council service centre, public WiFi and its hours, STAND site, mobile phone, internet, road
  access and the seasonal-access note).

BushTel publishes a disclaimer but no licence statement, so we are asking:

1. May we redistribute a derived per-community table containing the fields above, with
   attribution to BushTel / Northern Territory Government, inside the app and the report?
2. What attribution wording do you prefer?
3. If the free-text fields (WiFi hours, operator names, road notes) cannot be redistributed,
   may we still publish the presence/absence flags derived from them?

The raw profile JSON will not be redistributed either way. The entry is for assessment and
public presentation at the Code Fair only; there is no commercial use.

Thank you for your time. A reply before 26 September would let us reflect your answer in the
submitted version.

Kind regards,
Tarik [surname]
Team [team number], CDU IT Code Fair 2026 — Data Innovation Challenge
[CDU student email] · [phone, optional]

**Status:** not sent.

---

## 2. DITRDCSA — National Audit of Mobile Coverage, non-alignment CSV

**To:** [contact address on the Audit's data page or the department's data enquiries inbox — verify before sending]
**Subject:** Licence of the National Audit of Mobile Coverage non-alignment data (27 May 2026 release)

Dear Audit team,

I am an IT student at Charles Darwin University, part of Team [team number] in the CDU IT Code
Fair 2026 Data Innovation Challenge (Remote Connectivity), submission due 30 September 2026.

We are building a non-commercial, offline-first app and report that compare published mobile
coverage claims with independent evidence for 96 remote Northern Territory communities. The
Audit's non-alignment dataset (the ~1 km tiles where drive testing found no coverage while a
carrier map claims coverage; CSV release of 27 May 2026) is the only independent measurement of
its kind, and we would like to show, per community, how many non-alignment tiles fall within
5 km.

The CSV carries no licence statement that we could find. Could you confirm:

1. under what licence the non-alignment CSV is published (for example Creative Commons
   Attribution 4.0), and
2. whether a derived count per community, with attribution to the Department and the Audit,
   may be redistributed in a competition entry and its accompanying report?

We will cite the Audit and its methodology in the report's References in any case.

Kind regards,
Tarik [surname]
Team [team number], CDU IT Code Fair 2026 — Data Innovation Challenge
[CDU student email]

**Status:** not sent. Only needed if the Audit tiles are kept as an optional column; the core
table does not depend on it.

---

## 3. Bureau of Meteorology — Southern Hemisphere tropical cyclone track CSV

**To:** webreg@bom.gov.au
**Subject:** Reuse of the tropical cyclone track dataset (IDCKMSTM0S.csv) in a student competition entry

Dear Bureau of Meteorology,

I am an IT student at Charles Darwin University, part of Team [team number] in the CDU IT Code
Fair 2026 Data Innovation Challenge (Remote Connectivity), submission due 30 September 2026.

Our non-commercial entry is a report and an offline-first app about connectivity in remote
Northern Territory communities. We would like to derive, from the Bureau's Southern Hemisphere
tropical cyclone best-track dataset (`http://www.bom.gov.au/clim_data/IDCKMSTM0S.csv`), a
single number per community: how many cyclone tracks passed within 100 km since 1970. Only
that derived count, not the track data itself, would be included in the app and report, with
attribution to the Bureau.

The Bureau's default terms of use restrict supplying content to others, and we could not find
a Creative Commons statement for this file. Could you confirm:

1. whether IDCKMSTM0S.csv is published under Creative Commons Attribution (and which version), and
2. if not, whether the derived per-community count described above may be redistributed in a
   competition entry with attribution?

Kind regards,
Tarik [surname]
Team [team number], CDU IT Code Fair 2026 — Data Innovation Challenge
[CDU student email]

**Status:** not sent. Only needed if the cyclone-exposure flag is kept; the core table does not
depend on it.
