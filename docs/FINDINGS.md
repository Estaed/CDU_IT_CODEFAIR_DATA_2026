# Findings pack

Generated 2026-09-22 by `pipeline.figures.write_findings_md` from the tables under `data/out/tables/`, `data/out/priority.csv`, `data/out/reliability.csv`, `pipeline/thresholds.csv` and `data/out/PROVENANCE.md`. Every number below is read from those files at write time; re-running the pipeline refreshes them.

## For the report team and their AI assistant

Paste the block below into your assistant, then attach or open the files it names.

> You are helping write the 8-page report, the slide deck and the 10-minute pitch for
> Crosscheck, team DIC005's entry to the CDU IT Code Fair 2026 Data Innovation Challenge
> (theme: Remote Connectivity). Read, in this order, before writing a word:
> 1. `README.md` (the brief, the five tasks, the judging criteria, the judges);
>    `docs/report-requirements.md` (the mandatory report structure and file rules).
> 2. `docs/PRD.md` §1 (purpose), §2 (users; the primary target is the NT Government
>    DCDD analyst, judged by the "analyst's sixty seconds"), §4.2 fourth batch (what was
>    built on 2026-09-17 and why), §7 (ethics, the Discussion section's raw material),
>    §9 (open questions: which licences and figures are still unanswered).
> 3. This file, `docs/FINDINGS.md`: every sentence here names the table that proves it
>    and the number as the pipeline emitted it. Use these sentences; do not invent numbers.
> 4. The tables under `data/out/tables/` (`top10.csv`, `intervention_counts.csv`,
>    `publisher_lines_summary.csv`, `reliability_words.csv`, `reliability_validation.csv`,
>    `priority_sensitivity.csv`, `disagreement_patterns.csv`, `verdict_counts.csv`) and
>    the figures under `data/out/figures/` (six PNG maps and charts, print-ready).
> 5. `data/out/PROVENANCE.md` for every source's URL, date, licence and attribution line
>    (the References section), and `pipeline/thresholds.csv` for every requirement figure.
> 6. `CLAUDE.md`, the Blueprint section, only if you need the architecture in one page.
>
> What the project is, in five sentences. Published coverage sources for 96 remote NT
> communities disagree with each other and none says what a clinic or school can actually
> do with its connection. Crosscheck puts five sources side by side per community (four
> claims and one government drive test), tests the best available path against what
> telehealth, school video, myGov and voice/SMS require, and says where the sources
> disagree. A small model trained on the drive tests rates how reliable each coverage
> claim is. A transparent, weighted score ranks the 96 communities for action, with one
> intervention and one addressee each, and a sensitivity table shows the top of the list
> does not depend on any single weight. It ships as an offline single-file web app, a
> reproducible Python pipeline, this report and a pitch; nothing in the app computes a
> verdict or runs a model.
>
> The priority weights, in plain words: each community gets a score between 0 and 1
> from nine components (population, services present, the telehealth and voice verdicts,
> claim reliability, a drive-test contradiction nearby, an already-funded MBSP base
> station nearby counted against, and two placeholders at weight zero until their data
> licences arrive). Each component is scaled to 0..1 across the 96, multiplied by its
> weight from `pipeline/priority_weights.csv`, and summed. The weights are a choice, not
> a measurement: say so, print the CSV, and cite the sensitivity table, which shows that
> halving or raising any one weight by half keeps at least 6 of the top 10 in place.
>
> Do not claim: that the app measures signal (it does not); that a reliability word is a
> probability (it is a rank; the model is class-balanced on a 2.8 % base rate); that the
> model was validated everywhere (two of five folds held no positives); that a verdict is
> ground truth (95 of 96 rest on one measured satellite latency figure, and a clinic may
> sit on a government link nobody has published). Declare the AI used in building the
> entry (Claude and Codex as coding agents; scikit-learn for the one model) in the
> appendix, as the brief requires. Write in the report's own voice, not the assistant's.

## Methodology

- The map-claim reliability model validates on a five-fold split by ABS SA3 region; the pooled out-of-fold AUC over every claim tested is 0.7915 — evidence: data/out/tables/reliability_validation.csv — value: 0.7915 — run 2026-09-22.
- That pooled AUC rests on 3 of 5 folds: the other 2 folds carried no positive sample, so their AUC is undefined — evidence: data/out/tables/reliability_validation.csv — value: 3 — run 2026-09-22.
- The National Audit records a measured drive-test non-alignment within 5 km for 3 of 96 communities — evidence: data/out/tables/audit_within_5km.csv — value: 3 — run 2026-09-22.

## Findings

- Nauiyu ranks #1 of 96 with a priority score of 0.632 (region Top End, population 411), intervention 'verify on the ground' addressed to DCDD, carrier because Services present and population rank it here; a drive test found no signal inside claimed coverage. Telehealth verdict degraded; map-claim reliability low; publisher agreement 4/5 — evidence: data/out/tables/top10.csv — value: 0.632 — run 2026-09-22.
- 'measure the link here' is the most common intervention, reaching 31 of 96 communities, addressed to DCDD — evidence: data/out/tables/intervention_counts.csv — value: 31 — run 2026-09-22.
- Map-claim reliability words over the 96: high 8, medium 29, low 37, none 22 — evidence: data/out/tables/reliability_words.csv — value: 8 — run 2026-09-22.
- All four longstanding publishers (predicted, listed, licensed, portal) agree covered for 54 communities and agree not covered for 11; 31 communities see disagreement — evidence: data/out/tables/disagreement_patterns.csv — value: 54 — run 2026-09-22.
- No public source records a mobile voice or SMS path in 17 of 96 communities (1,140 people; 8 of them have a health centre). A mobile call needs a path at both ends, so these communities are outside the mobile reach of the other 79 as well as unable to call out; landlines, payphones and satellite phones are not in any source used here. — evidence: data/out/tables/voice_unreachable.csv — value: 17 — run 2026-09-22.
- The measured publisher (National Audit) never records 'covered'; it records a drive-test contradiction for 3 of 96 communities — evidence: data/out/tables/publisher_lines_summary.csv — value: 3 — run 2026-09-22.

## Discussion

- 95 of 96 communities have no NBN path but the satellite residual, so every verdict computed off that path rests on the ACCC-measured Sky Muster latency of 664.9 ms and, where the assumption applies, the sentence quoting the Starlink LEO figure of 29.8 ms from the same ACCC release; only 1 of 96 (fixed line) does not — evidence: pipeline/thresholds.csv — value: 95 — run 2026-09-22.
- A reliability word of 'low' is a rank, not a probability: the model is fit with class_weight=balanced against a pooled base rate of 2.83 %, so 'low' means the claim ranks with the ones the drive test contradicted, not a percent chance of being wrong — evidence: data/out/tables/reliability_validation.csv — value: 0.02832 — run 2026-09-22.
- Only 3 of 96 communities have a drive test within 5 km; every other reliability word is an extrapolation from the nearest audited conditions, not a measurement at the community itself — evidence: data/out/tables/audit_within_5km.csv — value: 3 — run 2026-09-22.
- 2 of the raw sources this pack cites carry an unstated licence with a request on file — evidence: data/out/PROVENANCE.md — value: 2 — run 2026-09-22.
- Communities under 100 people are never shown a raw population figure; the telehealth verdict table suppresses 29 such communities from its population sums — evidence: data/out/tables/verdict_counts.csv — value: 29 — run 2026-09-22.

## Recommendations

- The top 10 priority communities, with their interventions and addressees, are the Recommendations section's evidence base — evidence: data/out/tables/top10.csv — value: 10 — run 2026-09-22.
- The priority ranking is not fragile: the smallest top-10 overlap under any single weight moved to half or one-and-a-half of itself is 6 of 10, on voice_sms_verdict at factor 1.5 — evidence: data/out/tables/priority_sensitivity.csv — value: 6 — run 2026-09-22.
- Eight interventions cover the 96 communities, addressed to DCDD, carriers, nbn or ACMA by pattern — evidence: data/out/tables/intervention_counts.csv — value: 8 — run 2026-09-22.
