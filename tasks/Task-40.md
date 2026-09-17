# Task-40: Priority score, intervention and addressee per community; the LEO sentence; MBSP sites

> **Execution:** agent `claude-worker` (opus) · effort `high`
> *Why:* 2026-09-17. The score is what the report's Recommendations and the app's first tab
> rest on; a weight typed in code instead of the CSV, or a rank that flips on a tie, is the
> kind of defect the pitch cannot survive. Pure functions over dicts, unit-tested with
> hand-built rows. Codex is at 100 % until 2026-09-19.

> **Lane:** OWNS `pipeline/prioritise.py` (new), `pipeline/priority_weights.csv` (new),
> `pipeline/fetch/mbsp.py` (new), `pipeline/sources/mbsp.py` (new; one column), `pipeline/rules.py`
> (the LEO assumption sentence in the satellite-path telehealth reason only),
> `pipeline/thresholds.csv` (one `capability,leo_satellite,latency,29.8` row; OQ17 answered
> 2026-09-17), `pipeline/merge.py` (the MBSP column only), `pipeline/pack.py` (the `priority` list
> and the `priority` pointer per community only), `pipeline/figures.py` (one PNG map by
> priority tier and the two report tables), `pipeline/provenance.py` (append),
> `scripts/run_pipeline.py` (load MBSP; call `prioritise.main` after `reliability.main`),
> `tests/test_prioritise.py` (new), `tests/test_rules.py`, `tests/test_pack.py`,
> `tests/test_figures.py` (append only), `data/out/` (regenerated), this file · MUST NOT TOUCH
> `app/`, `pipeline/reliability.py`, `pipeline/sources/audit.py`, `design/`, `CLAUDE.md` ·
> GATE `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` · DEPENDS ON Task-38, Task-39

## Why

PRD §2 (primary target) and §4.2 fourth batch, third and fourth bullets. The brief's stated
pain is prioritising action and investment; three of the four judges are the people who do
that. Crosscheck today says what is in a community and who disagrees about it, and ranks
nothing. This task turns the table into a ranked, explainable queue: one score from weights
anyone can read, one intervention and one addressee per community, and a sensitivity table
that shows the top of the queue does not depend on a weight nobody can defend.

## Contract

1. **Weights.** `pipeline/priority_weights.csv`, columns
   `component,weight,source_column,transform,note`. Rows, in this order, weights as the
   starting point Tarik approves in the report (they are the CSV's, never a literal in code):
   `population` (log10 of ABS population, 0.20), `services_present` (count of the ten presence
   flags with `svc_health_centre` counted twice, 0.20), `telehealth_verdict` (fails 1,
   degraded 0.5, nodata 0.25, works 0; 0.20), `voice_sms_verdict` (fails 1, degraded 0.5,
   works 0; 0.15), `claim_reliability` (low 1, medium 0.5, high 0, none 0.25; 0.10),
   `audit_non_alignment_5km` (audit5 == 1; 0.10), `mbsp_funded_5km` (a funded MBSP base
   station within 5 km; **−0.10**, already in someone's pipeline), `cyclone_exposure` (0,
   `note: awaiting OQ3`), `adii_lga` (0, `note: awaiting OQ5`). Each component is normalised to
   0..1 across the 96 before weighting; the transform column names how (`log`, `linear`,
   `map`). The weights sum is not required to be 1; the score is reported as is.
2. **Score and rank.** `prioritise.score(row, weights) -> dict` returns `score`, `components`
   (name, value, weight, contribution) and `rank` is assigned over the 96 by score descending,
   ties broken by telehealth verdict severity, then population descending, then `bushtel_id`
   ascending, so every rank is unique and reproducible. Standard library only, like
   `rules.py`.
3. **Intervention and addressee**, one each, the first matching rule wins, table at the top of
   `prioritise.py` with a comment per row:
   - `svc_health_centre == Y and best_path == satellite` → `low-latency backhaul` → `DCDD, nbn`
   - `voice_sms fails and any_within_5km == 0 and carriers_4g_count == 0` → `mobile site (MBSP nomination)` → `DCDD, carrier`
   - `mobile_says starts accc=0 and rrl5=1` → `verify and publish the licensed site` → `carrier, ACMA`
   - `mobile_says starts accc=1 and ntg2022=0` → `refresh the coverage list` → `DCDD`
   - `backhaul_2019 == microwave or flags contain a cyclone exposure` → `backup power` → `carrier`
   - otherwise → `monitor` → `DCDD`
   `why` is one sentence assembled from the two largest contributions and the rule that fired,
   from pack strings, no new prose per community.
4. **Sensitivity.** For each weight in turn, ×0.5 and ×1.5, recompute ranks, record the size of
   the intersection of the top 10 with the baseline top 10 and Spearman's rho over the 96;
   `data/out/tables/priority_sensitivity.csv`, one row per (component, factor). The report
   prints the smallest top-10 overlap and names the weight.
5. **MBSP.** `pipeline/fetch/mbsp.py` downloads the CC BY 4.0 `MBSP - All Funded Base
   Stations.zip` (`reports/2026-09-12-arena-failure.md` §4.2, 297,168 bytes) to
   `data/raw/mbsp_funded_<date>.zip`; `pipeline/sources/mbsp.py::load` emits `mbsp_within_5km`
   (count) and `mbsp_nearest_km`; registry entry with URL, date, licence, attribution.
6. **LEO sentence.** `rules.telehealth_video` appends to the satellite-path reason's
   `assumption`: `A low-earth-orbit service, where a clinic has installed one, is in no public
   record; the same ACCC report measured Starlink at <figure>.` The figure is read from
   `capability.leo_satellite.latency` in `thresholds.csv`, a row this task adds:
   `capability,leo_satellite,latency,29.8,ms,measured,ACCC Measuring Broadband Australia release 147/24,https://www.accc.gov.au/media-release/broadband-performance-of-satellite-services-measured-for-the-first-time,2026-09-17,Starlink average all hours; same release as the Sky Muster figure (OQ17)`.
   Rendered through `rules.fig` like every figure; never typed into the sentence. No verdict
   changes in this task; the regression test still passes on every column it checks. The
   telehealth verdict's `sources` gain no new entry: the release is already cited for 664.9 ms.
7. **Pack.** `pack["priority"]` is the 96 rows in rank order,
   `{id, rank, score, components, intervention, addressee, why}`; each community also carries
   `priority: {rank, intervention}` so the community screen needs no lookup. `pack_version`
   stays 2 (Task-41 bumps it). The pack cap (512,000 bytes) holds; report the size in Status.
8. **Figures.** `data/out/figures/map_priority.png` (the 96 points by rank tercile, same
   outline and style as the two existing maps), `data/out/tables/priority.csv` (the 96 in
   rank order with the six columns the app shows) and `priority_sensitivity.csv`.

## Tests (`tests/test_prioritise.py`)

`test_weights_come_from_csv` (a copy of the CSV with one weight doubled changes that
component's contribution and nothing else); `test_zero_weight_contributes_zero`;
`test_ranks_unique_and_reproducible` (96 hand-built rows with duplicate scores rank 1..96
twice identically); `test_each_intervention_reachable` (six hand-built rows, one per rule);
`test_sensitivity_one_row_per_weight_and_factor`; `test_stdlib_only` (the layer-rule-9 grep
for `prioritise.py`). `tests/test_rules.py`: the satellite-path telehealth reason carries the
LEO sentence and the verdict word is unchanged. `tests/test_pack.py`: `priority` has 96 rows
in rank order 1..96, every community's `priority.rank` matches, the intervention is one of
the six words.

## Out of the gate

The weights themselves (Tarik reads the CSV and the sensitivity table and decides; the
report prints both); OQ3, OQ5.

## Status

Status: TODO
