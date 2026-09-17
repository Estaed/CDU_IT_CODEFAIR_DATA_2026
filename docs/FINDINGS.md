# Findings pack

Generated 2026-09-17 by `pipeline.figures.write_findings_md` from the tables under `data/out/tables/`, `data/out/priority.csv`, `data/out/reliability.csv`, `pipeline/thresholds.csv` and `data/out/PROVENANCE.md`. Every number below is read from those files at write time; re-running the pipeline refreshes them.

## Methodology

- The map-claim reliability model validates on a five-fold split by ABS SA3 region; the pooled out-of-fold AUC over every claim tested is 0.7915 — evidence: data/out/tables/reliability_validation.csv — value: 0.7915 — run 2026-09-17.
- That pooled AUC rests on 3 of 5 folds: the other 2 folds carried no positive sample, so their AUC is undefined — evidence: data/out/tables/reliability_validation.csv — value: 3 — run 2026-09-17.
- The National Audit records a measured drive-test non-alignment within 5 km for 3 of 96 communities — evidence: data/out/tables/audit_within_5km.csv — value: 3 — run 2026-09-17.

## Findings

- Nauiyu ranks #1 of 96 with a priority score of 0.632 (region Top End, population 411), intervention 'verify on the ground' addressed to DCDD, carrier because Services present and population rank it here; a drive test found no signal inside claimed coverage. Telehealth verdict degraded; map-claim reliability low; publisher agreement 4/5 — evidence: data/out/tables/top10.csv — value: 0.632 — run 2026-09-17.
- 'measure the link here' is the most common intervention, reaching 31 of 96 communities, addressed to DCDD — evidence: data/out/tables/intervention_counts.csv — value: 31 — run 2026-09-17.
- Map-claim reliability words over the 96: high 8, medium 29, low 37, none 22 — evidence: data/out/tables/reliability_words.csv — value: 8 — run 2026-09-17.
- All four longstanding publishers (predicted, listed, licensed, portal) agree covered for 54 communities and agree not covered for 11; 31 communities see disagreement — evidence: data/out/tables/disagreement_patterns.csv — value: 54 — run 2026-09-17.
- The measured publisher (National Audit) never records 'covered'; it records a drive-test contradiction for 3 of 96 communities — evidence: data/out/tables/publisher_lines_summary.csv — value: 3 — run 2026-09-17.

## Discussion

- 95 of 96 communities have no NBN path but the satellite residual, so every verdict computed off that path rests on the ACCC-measured Sky Muster latency of 664.9 ms and, where the assumption applies, the sentence quoting the Starlink LEO figure of 29.8 ms from the same ACCC release; only 1 of 96 (fixed line) does not — evidence: pipeline/thresholds.csv — value: 95 — run 2026-09-17.
- A reliability word of 'low' is a rank, not a probability: the model is fit with class_weight=balanced against a pooled base rate of 2.83 %, so 'low' means the claim ranks with the ones the drive test contradicted, not a percent chance of being wrong — evidence: data/out/tables/reliability_validation.csv — value: 0.02832 — run 2026-09-17.
- Only 3 of 96 communities have a drive test within 5 km; every other reliability word is an extrapolation from the nearest audited conditions, not a measurement at the community itself — evidence: data/out/tables/audit_within_5km.csv — value: 3 — run 2026-09-17.
- 2 of the raw sources this pack cites carry an unstated licence with a request on file — evidence: data/out/PROVENANCE.md — value: 2 — run 2026-09-17.
- Communities under 100 people are never shown a raw population figure; the telehealth verdict table suppresses 29 such communities from its population sums — evidence: data/out/tables/verdict_counts.csv — value: 29 — run 2026-09-17.

## Recommendations

- The top 10 priority communities, with their interventions and addressees, are the Recommendations section's evidence base — evidence: data/out/tables/top10.csv — value: 10 — run 2026-09-17.
- The priority ranking is not fragile: the smallest top-10 overlap under any single weight moved to half or one-and-a-half of itself is 6 of 10, on voice_sms_verdict at factor 1.5 — evidence: data/out/tables/priority_sensitivity.csv — value: 6 — run 2026-09-17.
- Eight interventions cover the 96 communities, addressed to DCDD, carriers, nbn or ACMA by pattern — evidence: data/out/tables/intervention_counts.csv — value: 8 — run 2026-09-17.
