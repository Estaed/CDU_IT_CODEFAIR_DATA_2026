**CDU IT Code Fair 2026** 

**Data Innovation Challenge**

**Crosscheck**

**A tool to find and fix connectivity gaps in 96 remote NT communities**

**Group: DIC005**

| **Student Name** | **Student ID** |
| --- | :---: |
| Tarik Bulut | S382893 |
| Huu Thanh Le | S378046 |
| Thi Xuan Thanh Tran | S389244 |
| Ngoc Anh Nguyen | S386805 |
CHARLES DARWIN UNIVERSITY

Faculty of SCIENCE and TECHNOLOGY

2026

**Table of Contents**

1.	Summary	2

2.	Introduction	2

3.	Methodology	3

4.	Findings	5

5.	Discussion	8

6.	Recommendations	9

7.	References	11

Appendix	12

# Summary
In Australia's remote Northern Territory, having a mobile signal on a map does not mean you can actually make a call or see a doctor online. Official coverage data comes from five different sources and they often disagree. This makes it very difficult for governments and service providers to know where to spend money and who needs help most urgently.

Crosscheck solves this by pulling all five sources together and checking them against each other for 96 remote NT communities. It then tests whether the available connection in each community is good enough for services people depend on: telehealth video calls, online school lessons, government websites, and basic voice calls.

What we found is serious. Only 1 of 96 communities can reliably run a telehealth video call. In 31 communities, the data sources cannot even agree on whether there is coverage at all. In 17 communities, there is no working voice call or SMS service.

Crosscheck produces a ranked list of all 96 communities, with a specific action and a named agency responsible for each. This gives decision-makers a clear, evidence-based starting point, not a list of problems, but a list of next steps. The app itself works completely offline, so it can be used in the field with no internet connection. 
# Introduction
**The Problem**

Imagine a nurse at a remote health clinic trying to connect a patient with a specialist in Darwin. She opens the telehealth app. The screen freezes. She tries again. It freezes again. The coverage map on the government website shows her community as 'connected' but the connection is too slow for a video call. The patient has to wait another week for the next clinic visit.

This is not a rare case. It is the daily experience across 96 remote communities in the Northern Territory. These communities rely on digital connectivity for healthcare, education, government services, and emergency communication. When connectivity fails, the consequences are real: delayed diagnoses, missed lessons, and people cut off from support during floods or cyclones.

**Why the Data Problem Makes It Worse**

Four different government and industry bodies each publish their own data about mobile coverage across these communities. The problem is that they use different methods, different update schedules, and different definitions of what 'covered' means. As a result, they often disagree, sometimes completely, about whether a community has coverage.

When decision-makers look at this data to decide where to invest, they are working from an incomplete and inconsistent picture. Communities that badly need investment might be overlooked because one source says they are covered. Communities that are well served might be listed as a priority. Nobody is doing this deliberately and the data is simply broken.

A fifth source, the National Audit of Mobile Coverage, is the only one based on actual field measurements, a vehicle driving around and recording signal strength. But it only covers a small number of NT communities.

**What Crosscheck Does**

Crosscheck brings all five sources together for each of the 96 communities and compares them side by side. It then answers a more useful question: not just 'is there coverage?', but 'is this connection actually good enough to run a telehealth call, an online school lesson, or a government website?' It rates how trustworthy each coverage claim is, and ranks all 96 communities so that governments and carriers know exactly where to act first and what to do.

The result is delivered as a simple app that works on a phone without any internet connection so it can be used by field officers in the communities themselves.
# Methodology
This section explains how Crosscheck works. Each step is designed to be transparent and reproducible: every decision is recorded in a configuration file, not hidden inside code.

**Step 1: Bringing Together Five Data Sources**

Crosscheck integrates five sources that each describe connectivity in a different way:

| **Source** | **What It Measures** | **Communities Covered** | **Last Updated** |
| :---: | :---: | :---: | :---: |
| ACC Mobile Infrastructure Report | Predicted signal based on models | 74 of 96 | Nov 2025 |
| NT Government community list | Communities listed as having coverage | 60 of 96 | Jul 2022 |
| ACMA license register | Transmitter towers within 5 km | 78 of 96 | Sep 2026 |
| BushTel community profies | Services described on a public website | 70 of 96 | Sep 2026 |
| National Audit of Mobile Coverage | Actual measurements taken in the field | 3 contradictions | May 2026 |
Each source has its strengths and blind spots. The ACCC maps predict what coverage should exist based on tower locations but predictions are not measurements. The NT Government list has not been updated since 2022. The ACMA register shows where towers are licensed, but a licensed tower is not always switched on. BushTel profiles are written descriptions, not technical data. Only the National Audit is based on someone physically driving through a community and recording the signal but very few NT communities have been audited.

**Step 2: Testing Whether the Connection Is Good Enough**

For each community, Crosscheck checks what type of internet connection is available (most use satellite) and tests it against the actual technical requirements of the services people need:

- Telehealth video call (healthdirect): needs a response time of 100 milliseconds or less. Australia's Sky Muster satellite delivers 664.9 ms, more than six times too slow. This means telehealth video is effectively impossible for satellite communities.

- Online school lesson (Microsoft Teams): Microsoft's official network guide specifies a minimum of 150 kbps upload for 240p video (Microsoft, 2026), with no published latency requirement. Satellite delivers 5,000 kbps upload, well above this minimum, so satellite-served schools are rated 'degraded' rather than 'fails',  reflecting the unverifiable latency dimension rather than a failure.

- Government websites (myGov, Centrelink): Services Australia publishes no numeric bandwidth requirement, so Crosscheck treats these as text-first services that work on any functioning connection, satellite included. Works in all 96 communities.

- Voice calls and SMS: tested against whether any carrier claims to provide signal. 17 communities have no working voice service at all.

These thresholds come from the official technical specifications published by each service provider. They are stored in a configuration file and can be updated if requirements change.

**Step 3: Rating How Trustworthy the Coverage Claims Are**

Because coverage claims from different sources often disagree, Crosscheck trains a simple machine learning model to estimate how reliable each claim is. The model learns from the National Audit field measurements - the only data based on actual physical testing. It looks at factors like how many transmitter towers are within 20 km of a community, and how many sources are claiming coverage.

The model produces a reliability rating for each community: high, medium, low, or none (when no source claims coverage). On a standard accuracy measure (AUC), the model scores 0.79, which is solid for a dataset this small. Importantly, the model is transparent about its limits: only 3 of 96 communities have been physically audited, so all other ratings are estimates, not facts.

**Step 4: Ranking Communities for Action**

Every community receives a priority score between 0 and 1, based on nine factors:

- How many people live there

- Whether there is a health centre, school, or other essential service

- Whether telehealth video works

- Whether voice and SMS work

- How reliable the coverage claims are

- Whether a field measurement has contradicted the coverage claims

- Whether there is already a government-funded mobile tower nearby (counted against the score, since investment is already committed)

The weights for each factor are stored in a plain text file and can be adjusted. A sensitivity check confirms that changing any single weight by 50% in either direction keeps at least 6 of the top 10 communities in place - the ranking is stable, not fragile.

**Step 5: The Offline App**

All the results are packaged into a single app that lives in one HTML file, smaller than 1 MB, the size of a short email attachment. It works in any phone's web browser without needing an internet connection, which is exactly the environment it is designed for.

To share an updated version of the app between two phones without internet, the sending phone displays a series of QR codes on screen. The receiving phone's camera reads them, rebuilding the data in about 20 seconds. No wi-fi, no mobile data, no Bluetooth required.

Community members can also use the app to report what signal they are experiencing right now ('Report here'). Those reports are saved on the device and can be shared by QR code or SMS, making the community an active contributor to the data, not just a subject of it.
# Findings
**Finding 1: One in Three Communities Has Conflicting Coverage Data**

When we compared all four longstanding coverage sources against each other, we found:

- 54 of 96 communities: all four sources agree the community has coverage.

- 11 of 96 communities: all four sources agree there is no coverage path recorded.

- 31 of 96 communities: the sources disagree, at least one says covered, another says not.

The field measurement data (National Audit) confirmed this problem. In 3 of the small number of communities it covers, a carrier predicted there was signal, but when someone actually drove through and tested it, there was none. These 3 communities are flagged as 'verify on the ground' and sit in the top 10 priority list. 

**Finding 2: Telehealth Video Is Effectively Unavailable for 95 of 96 Communities**

| **Service** | **Works reliably** | **Unreliable / slow** | **Fails completely** | **No data available** |
| :---: | :---: | :---: | :---: | :---: |
| Telehealth video call | 1 | 58 | 11 | 26 |
| Online school lesson | 1 | 69 | 0 | 26 |
| Government websites (myGov) | 96 | 0 | 0 | 0 |
| Voice calls and SMS | 74 | 5 | 17 | 0 |
The most important finding is the telehealth result. Almost every remote NT community uses satellite internet. Satellite is fine for browsing websites but it has a built-in delay (latency) that makes video calls stutter and freeze. Healthdirect, Australia's national telehealth service, requires a delay of 100 milliseconds or less. The satellite system used by most remote communities delivers 664.9 milliseconds, more than six times the limit.

The coverage map says these communities are 'connected'. That is technically true. But 'connected' is not the same as 'able to see a doctor online'. Crosscheck shows exactly where that gap is.

Voice calls are a separate and more urgent problem. 17 communities, roughly 525 people, have no working voice or SMS service at all. These communities cannot call an ambulance.

**Finding 3: Coverage Claims Are Often Unreliable**

Our reliability model rated the coverage claims across all 74 communities where at least one source says there is coverage:

- High reliability: 8 communities (about 2,325 people), the claim is probably correct.

- Medium reliability: 29 communities (about 15,598 people), there is meaningful uncertainty.

- Low reliability: 37 communities (about 17,536 people), the claim looks like it was not based on physical measurement.

- No claim: 22 communities (about 1,596 people), no source says there is coverage here.

The pattern behind low-reliability claims is consistent: many sources saying there is coverage, but few actual transmitter towers nearby. This suggests predicted coverage has been over-extended into areas where the signal has never been physically confirmed.

**Finding 4: The Top 10 Communities Most in Need of Action**

| **Rank** | **Community** | **Region** | **Priority Score** | **Recommended Action** | **Who** **Should Act** |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Nauiyu | Top End  | 0.632 | Verify on the ground | DCDD, carrier |
| 2 | Nitjpurru | Big Rivers | 0.608 | Upgrade to low-latency link | DCDD, nbn |
| 3 | Galiwinku | East Arnhem | 0.597 | Add backup power | Carrier |
| 4 | Amanbidji | Big Rivers | 0.596 | Upgrade to low-latency link | DCDD, nbn |
| 5 | Areyonga | Central Australia | 0.586 | Upgrade to low-latency link | DCDD, nbn |
| 6 | Maningrida | Top End | 0.582 | Measure the link here | DCDD |
| 7 | Wurrumiyanga | Top End | 0.568 | Add backup power | Carrier |
| 8 | Milingimbi | East Arnhem | 0.561 | Add backup power | Carrier |
| 9 | Jilkminggan | Big Rivers | 0.553 | Verify on the ground | DCDD, carrier |
| 10 | Numbulwar | Big Rivers | 0.549 | Measure the link here | DCDD |
**Finding 5: Eight Types of Action Cover All 96 Communities**

Crosscheck does not just identify problems. It assigns a specific next step to every community. Across all 96, eight types of action cover the full picture:

| **Recommended Action** | **Communities** | **Health Centres Affected** | **Who Should Act** |
| :---: | :---: | :---: | :---: |
| Measure the link here | 31 | 31 | DCDD |
| Add backup power | 15 | 15 | Carrier |
| Refresh the coverage database | 14 | 8 | DCDD |
| Upgrade to low-latency link | 12 | 12 | DCDD, nbn |
| Monitor and watch | 12 | 1 | DCDD |
| Confirm licensed tower is active | 5 | 0 | Carrier, ACMA |
| Nominate for new mobile tower | 4 | 0 | DCDD, carrier |
| Verify on the ground | 3 | 3 | DCDD, carrier |
The single most common action: 'measure the link here' covers 31 communities, all with a health centre. This action does not require building anything new. It requires someone to go to the community and record what the connection delivers. Until that happens, no well-founded investment decision can be made for these communities.
# Discussion
Data tools that affect communities carry responsibilities. This section addresses the ethical and cultural considerations that shaped how Crosscheck was designed and how it presents information.

**Respecting First Nations Data Rights**

Almost all 96 communities covered by Crosscheck are First Nations communities. Under the CARE Principles for Indigenous data, a framework developed with Indigenous communities, data about First Nations peoples should be governed by those communities, used for their collective benefit, and handled with responsibility and ethics.

In practice, this meant two things for our project. First, BushTel community profile text is used only for structural facts (what services exist, what type of infrastructure is present) and is not reproduced in full until BushTel's licence position has been confirmed, a request is on file. Second, the field measurement data from the National Audit is used only to train the reliability model, not to make definitive statements about any individual community's connectivity. A model rating is an estimate; we make that clear in the app.

**Avoiding the 'Deficit Map' Problem**

A tool that shows remote communities as red dots: 'telehealth fails', 'no voice signal', can unintentionally reinforce a narrative that treats disadvantage as a fixed characteristic of a community, rather than a failure of infrastructure. Communities already carry the burden of poor services; a map that makes them visible only as deficits does not serve them.

Crosscheck tries to shift that framing in two ways. Every community in the ranked list has a named action and a named responsible agency: the problem is presented as something a specific organisation needs to fix, not as something wrong with the community. The 'Report here' feature also lets community members add their own observations to the data. They become contributors, not just subjects.

**What the Reliability Model Can and Cannot Tell Us**

The reliability model estimates how trustworthy a coverage claim is, based on patterns in the data. It does not know whether any specific coverage claim is right or wrong. A 'low reliability' rating means the claim looks similar to others that turned out to be wrong when tested. It is a flag, not a verdict.

The model is also built on a very small number of physical measurements, only 3 of 96 communities have been physically tested within 5 km. All other reliability ratings are extrapolations. We report this limitation in the app next to every rating. The appropriate response to a low-reliability rating is to measure, not to assume the coverage is definitely absent.

**Protecting Community Privacy**

Crosscheck does not collect any personally identifying information. Population figures for communities with fewer than 100 people are not shown in full (affecting 29 communities) to prevent anyone from identifying individuals in very small populations. When community members submit a signal report, their location is rounded to roughly 1 km before it is stored, and the data never leaves the device unless the user deliberately chooses to share it.
# Recommendations
Crosscheck turns five inconsistent datasets into a clear action list. The following recommendations are addressed to the agencies with the authority and resources to act.

**For the NT Government (DCDD)**

- Visit the 3 communities where field measurements contradict carrier predictions (Nauiyu, Jilkminggan, and one other) as the first priority. Someone needs to go and check whether the signal is actually there. This costs travel time, not capital expenditure.

- Commission link speed and quality measurements at the 31 communities assigned 'measure the link here'. All of them have health centres. A government cannot make a well-founded infrastructure investment without knowing what the connection actually delivers.

- Use Crosscheck's ranked community list as the evidence base for the next round of Mobile Black Spot Programme (MBSP) nominations. Three communities in the top 10 (Nitjpurru, Amanbidji, Areyonga) have health centres on satellite links where upgrading to a low-latency connection would directly enable telehealth video.

- Update the NT Government community coverage list. It has not changed since July 2022 and now disagrees with other sources for 14 communities.

**For Mobile Carriers (Telstra, Optus, TPG)**

- Three communities in the top 8: Galiwinku, Wurrumiyanga, and Milingimbi, already have microwave backhaul connections that are fast enough for telehealth. The issue is that the towers go down during cyclones when backup power runs out. Carriers should prioritise backup generator capacity at the relay sites serving these communities before cyclone season.

- Confirm and publish whether the licensed transmitter towers near 5 communities are actually active. The licence register shows the towers should exist; carrier confirmation would remove a significant source of uncertainty.

**For** **nbn**

- The 12 communities assigned 'upgrade to low-latency link' all have health centres currently on satellite internet. Sky Muster satellite delivers 664.9 ms delay, far too slow for telehealth. Low Earth Orbit satellite (such as Starlink, which delivers a measured 29.8 ms delay) or the Sky Muster Plus prioritised tier would restore telehealth viability for these communities. Crosscheck provides the specific community list and the evidence to support a funding submission.

# References
ACCC (2025). Mobile Infrastructure Report 2025 - outdoor coverage maps. Australian Competition and Consumer Commission. [https://www.accc.gov.au/consumers/phone-internet-and-tv-at-home/mobile-coverage-maps](https://www.accc.gov.au/consumers/phone-internet-and-tv-at-home/mobile-coverage-maps) 

ACMA (2026). Register of Radiocommunications Licences. Australian Communications and Media Authority. [https://www.acma.gov.au/register-radiocommunications-licences](https://www.acma.gov.au/register-radiocommunications-licences) 

ABS (2021). Australian Statistical Geography Standard (ASGS) Edition 3. Australian Bureau of Statistics. CC BY 4.0. [https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3) 

BushTel (2026). Community profiles - Major and Minor remote communities. [https://bushtel.nt.gov.au/](https://bushtel.nt.gov.au/)  

Department of Infrastructure, Transport, Regional Development, Communications and the Arts (2026). National Audit of Mobile Coverage - non-alignment tile dataset. CC BY 4.0. [https://www.infrastructure.gov.au/media-communications-arts/internet/mobile-coverage-programme/national-audit-mobile-coverage](https://www.infrastructure.gov.au/media-communications-arts/internet/mobile-coverage-programme/national-audit-mobile-coverage) 

healthdirect Australia (2024). Video Call technical requirements. [https://about.healthdirect.gov.au/video-call-technical-requirements](https://about.healthdirect.gov.au/video-call-technical-requirements) 

Microsoft. (n.d.). *Prepare your organization's network for Teams - Microsoft Teams*. Microsoft Learn. Retrieved September 24, 2026, from [https://learn.microsoft.com/en-us/microsoftteams/prepare-network](https://learn.microsoft.com/en-us/microsoftteams/prepare-network)

NT Government (2022). Mobile Phone Coverage in Remote Areas of the NT. Department of Corporate and Digital Development. [https://dcdd.nt.gov.au/](https://dcdd.nt.gov.au/) 

Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830.

Carroll, S. R., Herczog, E., Hudson, M., Russell, K., & Stall, S. (2021). Operationalizing the CARE and FAIR Principles for Indigenous data futures. Scientific Data, 8, 108. [https://doi.org/10.1038/s41597-021-00892-0](https://doi.org/10.1038/s41597-021-00892-0) 

[https://learn.microsoft.com/en-us/microsoftteams/prepare-network](https://learn.microsoft.com/en-us/microsoftteams/prepare-network)

# Appendix
**AI Usage Declaration**

Claude (Anthropic) and Codex were used as coding assistant during development of the data pipeline and the interactive offline application. The scikit-learn library (Pedregosa et al., 2011) was used to implement the map-claim reliability model described in Methodology Step 3. All coverage verdicts and priority scores reported here are computed by a deterministic, rule-based pipeline; no AI model computes a verdict at runtime inside the shipped application. AI assistance was not used to generate or alter any of the underlying data, measurements, or figures presented in this report.

**Source Code**

The full Python source code (data pipeline, verdict rules, reliability model, priority scoring, and the offline application) and the reproduction README are included in the submitted zip file, and are also available at [https://github.com/Estaed/CDU_IT_CODEFAIR_DATA_2026](https://github.com/Estaed/CDU_IT_CODEFAIR_DATA_2026)  

**Dataset Links**

Every dataset used (ACCC Mobile Infrastructure Report, NT Government coverage list, ACMA Register of Radiocommunications Licences, BushTel community profiles, National Audit of Mobile Coverage, and ABS ASGS boundaries) is listed with its full URL and licence in the References section above.

**Group contributions**

| **Member** | **Main** **Role** |
| :---: | :---: |
| Tarik Bulut | Data pipeline, app development, technical architecture |
| Huu Thanh Le | Priority scoring, action framework, data analysis |
| Thi Xuan Thanh Tran | Report, slides, pitch, documentation lead |
| Ngoc Anh Nguyen | Ethics & community considerations, future work |

