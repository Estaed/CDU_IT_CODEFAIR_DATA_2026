# What we are building — plain-English explainer for the team

Data Innovation Challenge 2026, theme Remote Connectivity. Written 2026-09-12 after the
idea-arena decision (`reports/2026-09-12-arena-verdict.md`). Numbers marked * were verified
against the source on 2026-09-12; "say" marks illustrative values that the first data run
will replace.

## The one-sentence version

Coverage maps ask "is there signal here?". We ask "can the clinic here actually run a
telehealth call with that signal?" — for 96 remote NT communities, every number sourced,
in an app that works on a phone in flight mode.

## The problem in one paragraph

Nobody knows, community by community, what the connectivity in a remote NT community
actually lets people do. The carriers publish predicted coverage maps. The NT Government's
community coverage list was last updated in 2022*. The NBN satellite service is fast enough
on paper but has 665 ms latency*. These sources disagree with each other, and none of them
say whether a nurse can see a patient over video. So investment gets ordered on guesses,
and a community cannot prove its own situation.

## A scenario: Wadeye

Wadeye is about 250 km south-west of Darwin, population 2,259*. The NT Government's
BushTel profile lists a health centre*, a school*, a store*, a police station*, a council
office* and public WiFi next to the council office, open Monday to Saturday 8am to 8pm*.
Specialist teams (renal, paediatrics, physiotherapy) visit on a calendar*; between visits,
patients are meant to be followed up by telehealth.

Today: the carrier map says Wadeye has mobile coverage. The clinic's internet is NBN
satellite* at 21 to 63 Mbps*, which looks fine. But healthdirect Video Call, the national
telehealth platform, requires latency of 100 ms or less*, and satellite delivers 665 ms*.
The nurse's experience is "we have internet but the call freezes". No map shows that.

Our pipeline builds one row for Wadeye:

| Column | Value | Source |
|---|---|---|
| Services present | clinic, school, store, WiFi (with hours) | BushTel |
| Fixed connection | SATELLITE | NBN footprint files (CC-BY) |
| Mobile: how many publishers say "covered" | say 3 of 4 | ACCC carrier maps, NT Government list, ACMA licence register |
| Measured use | 60 speed tests in 4.5 years* | Ookla open data |
| Fragility | coastal, cyclone exposure | BoM tracks, backhaul type |

And the app shows, per service:

- Telehealth video: **red**. "Latency 665 ms, requires 100 ms. Cause: satellite."
- School lessons (Teams): **amber**. "Bandwidth fine, latency degrades quality."
- myGov, banking: **green**.
- Voice and SMS: **green**, Telstra.
- Tap any row: which source says so, and when it was published.

## What the NT Government analyst sees

A map of 96 communities coloured by how many services fail. Filters:

- "Has a clinic and is satellite-only": say 60 communities where telehealth cannot work
  whatever the coverage map says.
- "Carrier says covered, NT Government list says not": say 12 communities to verify on the
  ground.
- "Gets satellite SMS in 2027 but telehealth still fails": the gap the new Universal
  Outdoor Mobile Obligation will not close.

That is where the report's Recommendations come from: "prioritise low-latency backhaul for
these 60 clinics; verify these 12 disagreements; community mesh and zero-rated government
services for these communities."

## What the judges see on Challenge Day

They scan a QR code, switch their phone to flight mode, open Wadeye, see the red row, tap
the reason. They share the data pack to a colleague's phone by QR; it opens with no
network. Three of the four judges work for the NT department that would act on this.

## What this is not

- Not a messaging app and not a new network. The phone-to-phone idea survives as a
  recommendation ("community mesh"), not as the prototype.
- Not synthetic data. Every number traces to a published dataset; where a licence is
  unclear we ask first (BushTel, the national coverage audit, BoM).
- Not a national tool. NT only, 96 communities, unless NT is finished early.

## Who does what

- Tarik: data pipeline, the scoring table, the offline app, README, report-ready figures.
- Emma, Thanh, Will: the 8-page report, the 10-minute slide deck, the pitch. The Findings
  section is built from the tables and charts the pipeline emits.
- Deadline 30 September 2026 (zip by email). Challenge Day 7 October 2026.
