# Licence requests — drafts for Tarik to send from his CDU address

Drafted 2026-09-12 after the 20-community spike showed which sources ship in the app;
shortened the same day. Team number DIC005.
Send all three the same day; log the send date and any reply under "Status" so the report's
References section can cite it.

**House style for these drafts: the ask comes first, the context after.** A government inbox
triages on the first two lines, and a request that opens with three paragraphs about a student
project gets read as an introduction rather than as a question needing an answer. Numbered
questions so the reply can answer them in order. Do not re-inflate these.

Sources that need no email: ACCC (CC BY 2.5 AU), ACMA RRL (licence permits derivatives and
their redistribution, attribution "Based on Australian Communications and Media Authority
information"), NT Government coverage lists (CC BY), NBN footprints (CC BY 4.0), ABS (CC BY 4.0).

---

## 1. BushTel — terms of reuse (the one source the app cannot do without)

**To:** Bushtel@nt.gov.au
**Cc:** opendata@nt.gov.au
**Subject:** Permission to reuse BushTel community data in a student competition entry

Dear BushTel team,

May we republish a derived per-community table built from BushTel profiles, with attribution,
in a non-commercial student competition entry? BushTel carries a disclaimer but no licence
statement, so we are asking rather than assuming.

1. May we redistribute the derived table described below, attributed to BushTel / Northern
   Territory Government?
2. What attribution wording do you prefer?
3. If the free-text fields cannot be redistributed, may we still publish presence or absence
   flags derived from them?

The fields, retrieved from bushtel.nt.gov.au on 12 September 2026 for the 96 Major and Minor
communities: name, aliases, coordinates, community type, NT region, ABS 2021 SA1 population,
and the Services list (health centre, school, store, police station, library, council service
centre, public WiFi and its hours, STAND site, mobile phone, internet, road access and the
seasonal-access note). The raw profile JSON will not be redistributed either way.

We are Team DIC005 in the CDU IT Code Fair 2026 Data Innovation Challenge: an offline web app
and a report showing which digital services each community's connectivity can support, and
where published coverage sources disagree. Non-commercial, for assessment and public
presentation on 7 October 2026.

A reply before 26 September would let us reflect your answer in the submitted version.

Kind regards,
Tarik Bulut
Team DIC005, CDU IT Code Fair 2026 — Data Innovation Challenge
tarik.bulut@cdu.edu.au

**Status:** not sent.

---

## 2. DITRDCSA — National Audit of Mobile Coverage, non-alignment CSV

**To:** [contact address on the Audit's data page or the department's data enquiries inbox — verify before sending]
**Subject:** Licence of the National Audit of Mobile Coverage non-alignment data

Dear Audit team,

Two questions about the non-alignment dataset (the CSV release of 27 May 2026). We could find
no licence statement on the file or its page.

1. Under what licence is the non-alignment CSV published?
2. May a derived count per community, attributed to the Department and the Audit, be
   redistributed in a non-commercial student competition entry and its report?

We are Team DIC005 in the CDU IT Code Fair 2026 Data Innovation Challenge, comparing published
mobile coverage claims with independent evidence for 96 remote Northern Territory communities.
The Audit is the only drive-tested evidence of its kind; we would show, per community, how many
non-alignment tiles fall within 5 km. The Audit and its methodology are cited in our References
either way.

A reply before 26 September would let us include the column. Without one we will leave it out.

Kind regards,
Tarik Bulut
Team DIC005, CDU IT Code Fair 2026 — Data Innovation Challenge
tarik.bulut@cdu.edu.au

**Status:** not sent. Only needed if the Audit tiles are kept as an optional column; the core
table does not depend on it.

**Follow-up, drafted 2026-09-17 (PRD OQ18; send as a reply on the same thread).** Since
2026-09-17 the tiles are the fifth publisher line and the training labels of the reliability
model (Task-38, Task-39), so the answer now decides a feature, not a column.

> One further question, if we may. To tell "no signal was found here" apart from "no road was
> audited here", we would sample the audited road routes published in the
> `Main_Audit_Roads_DITRDCA_2024` map service on spatial.infrastructure.gov.au.
>
> 3. May the road-route geometry be used for that purpose and a derived per-community
>    flag redistributed, attributed to the Department and the Audit, on the same terms as
>    question 2?
>
> We would not redistribute the route geometry itself.

---

## 3. Bureau of Meteorology — Southern Hemisphere tropical cyclone track CSV

**To:** webreg@bom.gov.au
**Subject:** Licence of the tropical cyclone best-track dataset (IDCKMSTM0S.csv)

Dear Bureau of Meteorology,

Two questions about `http://www.bom.gov.au/clim_data/IDCKMSTM0S.csv`. Your default terms of use
restrict supplying content to others, and we could not find a Creative Commons statement for
this file.

1. Is IDCKMSTM0S.csv published under Creative Commons Attribution, and if so which version?
2. If not, may we redistribute one derived number per community, attributed to the Bureau: how
   many cyclone tracks passed within 100 km since 1970?

Only that count would appear in our output, never the track data itself. We are Team DIC005 in
the CDU IT Code Fair 2026 Data Innovation Challenge, a non-commercial student entry: a report
and an offline app about connectivity in remote Northern Territory communities, submitted
30 September 2026.

A reply before 26 September would let us keep the figure. Without one we will drop it.

Kind regards,
Tarik Bulut
Team DIC005, CDU IT Code Fair 2026 — Data Innovation Challenge
tarik.bulut@cdu.edu.au

**Status:** not sent. Only needed if the cyclone-exposure flag is kept; the core table does not
depend on it.

## Status

| # | Source | Sent | Reply |
|---|---|---|---|
| 1 | BushTel (NTG) | 2026-09-12 | awaited |
| 2 | DITRDCSA National Audit non-alignment CSV | 2026-09-12 | awaited |
| 3 | Bureau of Meteorology cyclone track CSV | 2026-09-12 | awaited |

All three sent by Tarik from his CDU address on 2026-09-12. Reply dates go in the last column
as they arrive; the report's References section cites this table. PRD open question 2 drops the
non-alignment column if #2 is unanswered by 2026-09-26.
