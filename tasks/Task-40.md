# Task-40: Priority score, intervention and addressee per community; the LEO sentence; MBSP sites

**Status: DONE** — verified 2026-09-17 (main loop: gate green, 200 unit + 85 browser, pack 506,343 bytes; mutation: the `verify on the ground` predicate changed to never fire turns `test_each_intervention_reachable` red, restored. Trap recorded: a one-character mutation of the same byte length within the same second left a stale `.pyc`; clear `pipeline/__pycache__` after such a mutation.)

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
   - (added 2026-09-17 evening, Tarik) `audit5 == 1` → `verify on the ground` → `DCDD, carrier`
   - (added 2026-09-17 evening, Tarik) `svc_health_centre == Y and telehealth_video verdict == degraded and best_path != satellite` → `measure the link here` → `DCDD`
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
7. **Pack.** (Encoding amended 2026-09-17 evening for the cap; the Blueprint seam is the
   source of truth.) `pack["priority"]` is the 96 rows in rank order,
   `{id, rank, score, c, i, why}` with the headers `priority_components` and
   `priority_interventions`; each community also carries `priority: {rank, i}` so the
   community screen needs no lookup. `pack_version`
   stays 2 (Task-41 bumps it). The pack cap (512,000 bytes) holds; report the size in Status.
8. **Figures.** `data/out/figures/map_priority.png` (the 96 points by rank tercile, same
   outline and style as the two existing maps), `data/out/tables/priority.csv` (the 96 in
   rank order with the six columns the app shows) and `priority_sensitivity.csv`.

## Tests (`tests/test_prioritise.py`)

`test_weights_come_from_csv` (a copy of the CSV with one weight doubled changes that
component's contribution and nothing else); `test_zero_weight_contributes_zero`;
`test_ranks_unique_and_reproducible` (96 hand-built rows with duplicate scores rank 1..96
twice identically); `test_each_intervention_reachable` (eight hand-built rows, one per rule);
`test_sensitivity_one_row_per_weight_and_factor`; `test_stdlib_only` (the layer-rule-9 grep
for `prioritise.py`). `tests/test_rules.py`: the satellite-path telehealth reason carries the
LEO sentence and the verdict word is unchanged. `tests/test_pack.py`: `priority` has 96 rows
in rank order 1..96, every community's `priority.rank` matches, the intervention is one of
the eight words.

## Out of the gate

The weights themselves (Tarik reads the CSV and the sensitivity table and decides; the
report prints both); OQ3, OQ5.

## Status

Status: IMPLEMENTED (2026-09-17, claude-worker opus) — awaiting verify-task

**Gate green, exit 0** (200 unit, 85 browser), after Tarik's two decisions of 2026-09-17
evening were applied. The figures in "The numbers" and "Gate" below are the **first** run,
before those decisions; **the Amendment section at the end of this Status carries the final
numbers and supersedes them.** The two sections are both kept because the first one is the
evidence the decisions were made on.

### What landed

- `pipeline/fetch/mbsp.py` (new): `download()` / `main()`, streams the CC BY 4.0 bulk zip to
  `data/raw/mbsp_funded_2026-09-17.zip`, skipping a snapshot already on disk. Run once by hand:
  **297,168 bytes**, exactly the size `reports/2026-09-12-arena-failure.md` §1.4 records. The
  only new network touch in the repo; `data/raw/` is already gitignored.
- `pipeline/sources/mbsp.py` (new): `FETCH_COMMAND`, `sites()`, `load()` emitting
  `mbsp_within_5km` (count) and `mbsp_nearest_km`. **The duplication trap is solved exactly**:
  the arena report's "every NT location appears twice" is one `Point` placemark plus its
  coverage `Polygon` twin carrying identical attributes, so reading `Point` placemarks only
  de-duplicates and reproduces the report's **49 unique NT sites** across the eight rounds.
  Sites are kept on an NT-plus-margin bounding box rather than `State == "NT"`, so a funded
  site just over a border still counts (102 sites in the box); the margin also keeps every kept
  site inside MGA zones 52 and 53. Distances are metres in GDA2020 MGA, as
  `pipeline/sources/audit.py` measures them.
- `pipeline/priority_weights.csv` (new): nine rows, the weights of contract item 1 verbatim.
  **The one place a weight lives**;
  `tests/test_prioritise.py::test_every_weight_is_read_from_the_csv` halves each of the nine in
  turn and asserts exactly that contribution halves and no other moves.
- `pipeline/prioritise.py` (new, standard library only): `load_weights`, `raw_components`,
  `normalise`, `score`, `intervention`, `why`, `ranked`, `spearman`, `sensitivity`,
  `reliability_words`, `load_rows`, `write_priority`, `write_sensitivity`, `main`. Ranks on the
  rounded (3 dp) score so two rows printed with the same number are ordered by the stated
  tiebreakers and not by an invisible digit; ties break by telehealth severity, then population
  descending, then `bushtel_id` ascending.
- `pipeline/thresholds.csv`: the one `capability,leo_satellite,latency,29.8` row, exactly as
  contract item 6 gives it.
- `pipeline/rules.py`: `LEO_ASSUMPTION` and `leo_assumption(thresholds)`; **both** satellite
  branches of `telehealth_video` carry the sentence, the figure rendered through `rules.fig`
  and never typed. **No verdict moved** (1/58/11/26 unchanged) and no `sources` entry was
  added — the ACCC release is already cited for the 664.9 ms figure.
- `pipeline/merge.py`: `merge()` takes `mbsp` after `audit`; the frame joins between `audit`
  and `ntg` so its two columns sit after the Audit block. `mobile_says`, `PUBLISHER_KEYS` and
  `mobile_publishers_available` are untouched. Capability table 109 → **111 columns**.
- `pipeline/pack.py`: `priority_components`, `priority_interventions`, `priority_rows`,
  `_short`; the `priority` list and the per-community `priority: {rank, intervention}` pointer.
  `pack_version` stays **2**.
- `pipeline/figures.py`: `load_priority`, `_tercile`, `map_priority`, `write_priority_table`.
- `pipeline/provenance.py`: one registry entry `mbsp_funded`, CC BY 4.0, dated 2024-08-09,
  `pack_source` empty (the pack never cites it per community).
- `scripts/run_pipeline.py`: loads the MBSP frame, passes it to `merge`, calls
  `prioritise.main()` after `reliability.main()` and before `pack.main()`. The whole run stays
  offline.
- Tests: `tests/test_prioritise.py` (new, 14), `tests/test_source_mbsp.py` (new, 5),
  `tests/test_rules.py` (+5, 2 rewritten), `tests/test_pack.py` (+6), `tests/test_figures.py`
  (+4), `tests/test_merge.py` (+1), `tests/test_provenance.py` (1 line).

### The numbers

**Top 10 by rank.**

| # | community | score | intervention | addressee |
|---|---|---|---|---|
| 1 | Nauiyu | 0.632 | monitor | DCDD |
| 2 | Nitjpurru | 0.608 | low-latency backhaul | DCDD, nbn |
| 3 | Galiwinku | 0.597 | backup power | carrier |
| 4 | Amanbidji | 0.596 | low-latency backhaul | DCDD, nbn |
| 5 | Areyonga | 0.586 | low-latency backhaul | DCDD, nbn |
| 6 | Maningrida | 0.582 | monitor | DCDD |
| 7 | Wurrumiyanga | 0.568 | backup power | carrier |
| 8 | Milingimbi | 0.561 | backup power | carrier |
| 9 | Jilkminggan | 0.553 | monitor | DCDD |
| 10 | Numbulwar | 0.549 | monitor | DCDD |

**Interventions over the 96:** `monitor` **46**, `backup power` **15**,
`refresh the coverage list` **14**, `low-latency backhaul` **12**,
`verify and publish the licensed site` **5**, `mobile site (MBSP nomination)` **4**.

**Sensitivity** (18 rows, every weight at ×0.5 and ×1.5). Smallest top-10 overlap **6 of 10**,
on **`voice_sms_verdict` ×1.5**; the same component at ×0.5 gives the smallest Spearman's rho,
**0.967**. Every other perturbation keeps 7 or more of the top 10 and rho at or above 0.975.
**The top of the queue does not rest on a weight nobody can defend**: no single weight, moved
by half, reorders more than four of the top ten, and the ranking as a whole is essentially
unchanged (rho ≥ 0.967 everywhere).

**A zero-weight component (cyclone, ADII) is scored, reported and contributes exactly
nothing.** It appears in `priority_weights.csv` with its `note: awaiting OQ3` /
`awaiting OQ5`, in the pack's `priority_components` header with `weight: 0`, and as a `0` in
every row's `c` array. In `priority_sensitivity.csv` it gets its two rows like any other
component, both reading `top10_overlap 10, spearman_rho 1.0` — moved by half or by half again,
a zero weight moves nothing. Dropping the two components entirely gives the identical ranking
(`test_zero_weight_contributes_zero` asserts it). They are visible and inert, not absent.

**MBSP:** **8 of 96** communities have a funded base station within 5 km — Finke 0.6 km,
Imanpa 0.2, Mount Liebig 1.4, Wallace Rockhole 0.1, Tara 0.2, Minjilang 0.6, Baniyala 0.1,
Rittarangu 0.2. 49 unique NT sites, 102 in the bounding box.

**LEO:** the sentence reaches **69 of 96** communities (58 telehealth `degraded` + 11 `fails`);
the 26 `nodata` and the 1 fixed-line `works` correctly go without it.

**Sizes.** `data/out/data_pack.json` 476,606 → **510,477** bytes (limit 512,000; **1,523
left**). `dist/index.html` 923,418 → **957,289** (limit 1,048,576). The pack's +33.9 KB is
about 24.5 KB of priority and 9.4 KB of the LEO sentence said 69 times.

**Tests.** Unit **166 → 200** (+34). Browser **85 → 85** (84 pass, 1 fail, see Gate).

### Gate

`PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` → **exit 1**.

```
== lint          All checks passed!
== unit tests    200 passed, 85 deselected in 84.88s
== build         ok
== size          dist\index.html: 957,289 bytes (limit 1,048,576) ok
                 data\out\data_pack.json: 510,477 bytes (limit 512,000) ok
== browser       1 failed, 84 passed in 34.28s
                 test_seeded_drop_completes_within_budget[loss10]
                 10 % loss, k 31, 20 seeds: median 1.65 x K, worst 2.48 x K
GATE RED at 'browser smoke' (exit 1)
```

**The one failure, and why this lane did not fix it.** Blueprint fixes the camera transfer's
loss budget at median 1.6 / 2.8 / 4.5 × K and worst-seed 2.5 / 3.5 / 4.5 × K, measured by Tarik
at K 25 on 2026-09-17. This task's contracted content grows the pack 476,606 → 510,477, which
pushes the transfer payload past six more 750-byte block boundaries: **K 25 → 31**. Measured on
the built page, 20 seeds each:

| scenario | budget (median / worst) | observed at K 31 |
|---|---|---|
| 10 % loss | 1.6 / 2.5 | **1.65** / 2.48 |
| 50 % loss | 2.8 / 3.5 | 1.74 / 2.26 |
| 70 % loss | 4.5 / 4.5 | 1.47 / 2.00 |
| sources 0..19 dropped | 2.0 (deterministic) | 1.35 |

Only the 10 % median fails, by 0.05, and its worst seed is inside its own budget by 0.02.
Nothing in the decoder changed; only K did. This is exactly the brittleness Task-38 recorded
and named in advance: *"the budget is a single-seed observation, not a property of the decoder,
and it is brittle in K — which the rest of this batch (Task-39's `claim_reliability`, Task-40's
score) will push further."*

**It is not engineerable away inside this lane's OWNS.** Measured on the real pack:

| pack variant | payload gzip | K |
|---|---|---|
| Task-39 baseline, no LEO, no priority | 19,015 | 26 |
| + LEO sentence only | 19,359 | 26 |
| + priority with `why`, `c` and the pointer all removed | 20,590 | 28 |
| + priority with `why` removed only | 21,686 | 29 |
| **as shipped** | **22,013** | **30** (31 via the browser's `CompressionStream`) |

Stripping the priority list to the bone — which the Contract forbids — still leaves K at 28.
The contracted content costs about four blocks; K must grow.

**Why this lane did not change the number.** The budgets are written in `CLAUDE.md` Blueprint,
which this lane's Lane block lists under MUST NOT TOUCH. Editing
`tests/browser/test_transfer.py` alone would leave the test and Blueprint disagreeing, which is
the invisible deviation Blueprint's own rule forbids. Task-38 changed this same test only after
Tarik amended Blueprint himself in the same session. **This is the same decision, and it is
Tarik's, not this lane's.**

**Recommendation, if it helps the decision.** The 10 % row has been the binding one at both
K 25 and K 31 while 50 % and 70 % sit at roughly half their budgets, which suggests the three
medians were fitted to one measurement rather than to a shape. A budget expressed as a constant
overhead rather than a multiple of K (frames-needed ≤ K + c) would not move every time the pack
grows. Failing that, the smallest honest change is the 10 % median 1.6 → 1.8 at K 31.

### Deviations from the Contract

1. **`addressee` is a pack header, not a field on each of the 96 priority rows** (contract item
   7 and Blueprint's "Priority row" seam both list it per row). The first build came out at
   **512,119 bytes, 119 over the cap**. The addressee is a function of the intervention and of
   nothing else — six pairs repeated 96 times — so it moved into
   `pack["priority_interventions"]: [{word, addressee}]`, 342 bytes instead of 1,818. Nothing is
   lost: the six pairs are still in the pack, and per community in `data/out/priority.csv`. No
   screen prints an addressee beside a community (the Priority tab shows rank, name, glyph,
   intervention; the community screen shows `Priority #n of 96 · <intervention>`), so nothing
   needs it inline. **Blueprint's seam line needs amending to match, which is the main loop's
   call.**
2. **The pack's priority rows carry `c: [contribution, ...]` against a
   `priority_components: [{name, weight}]` header**, not
   `components: [{name, value, weight, contribution}]` as the seam reads. This was the main
   loop's instruction to this lane, for the byte budget; recorded here because it is a seam
   change. `value` is recoverable as `contribution / weight` for every non-zero weight, and is
   exactly 0 for the two zero-weight components.
3. **`tests/test_merge.py` (outside OWNS).** `merge()` gained a positional `mbsp` frame, so the
   two call sites, the `sources` fixture, a `_mbsp_frame` helper and `test_columns` (an exact
   column set) had to change, plus one new join test. The same shape Task-38 used for `audit`.
4. **`tests/test_provenance.py` (outside OWNS, one line).** `EXPECTED_IDS` is an exact set and
   fails `test_sources_shape` without the new `mbsp_funded` id. Added the id only.
5. **`tests/test_source_mbsp.py` is new and the Lane block did not name it.** The
   de-duplication is the one thing that can silently double every MBSP count, and Blueprint's
   verification rule 2 expects a unit test per source module. Five tests, including a
   hand-built KML carrying the `Polygon` twin and a check that the frozen snapshot still yields
   the arena report's 49.
6. **`tests/test_rules.py`: two existing tests rewritten, not appended to.**
   `test_telehealth_fails_has_no_assumption` asserted the opposite of contract item 6 and is now
   `test_telehealth_fails_carries_only_the_leo_assumption`;
   `test_telehealth_degraded_has_assumption_with_telstra` asserted the exact old string. Both
   are inside OWNS. Nothing was weakened — the verdicts and reasons are still asserted exactly.
7. **`data/out/priority.csv` sits at `data/out/`, the two report tables at `data/out/tables/`.**
   Blueprint says `prioritise` "writes data/out/priority.csv and the sensitivity table";
   contract item 8 names `data/out/tables/priority.csv`. Both exist and neither is a copy of the
   other: `data/out/priority.csv` is the machine file the pack reads (score, all nine
   contributions, intervention, addressee, why), and `data/out/tables/priority.csv` is the
   six-column report table item 8 describes. This mirrors `reliability.csv` exactly.
8. **Distances for MBSP are GDA2020 MGA, and sites are filtered by bounding box, not by
   `State`.** The Contract says only "within 5 km". `State == "NT"` would have dropped a funded
   site just across a border from an NT community; the box keeps them and keeps the MGA zones
   valid.

### Two things the report should not skip

- **46 of 96 communities, including the top-ranked one, get `monitor`.** Nauiyu ranks #1 (411
  people, a clinic, all four publishers saying covered, a drive-test non-alignment 4.7 km away)
  and the intervention table has no row that fires for it, so its recommended action is "watch".
  The same is true of **all three communities with a measured drive-test non-alignment within
  5 km** (Nauiyu, Jilkminggan, Barunga) — the publisher line this batch just added is the one
  the six rules cannot act on, because the rules were written before it existed. 35 of the 46
  `monitor` communities have a clinic. The six rules and their order are the Contract's, so
  this lane implemented them as given; a **seventh rule** (`audit5 == "1"` →
  `verify on the ground` → `DCDD, carrier`, placed above `backup power`) is the obvious
  candidate and is exactly the extension the seam describes: "a new intervention is a new rule
  row there and a new chip in the app". Raised, not taken.
- **The score is a ranking, not a measurement.** The weights are Tarik's to set and the
  sensitivity table is there to be read beside them; the report should print both. The score's
  units mean nothing on their own — 0.632 for Nauiyu is only "above 0.608 for Nitjpurru".

### Amendment, 2026-09-17 evening — Tarik's two decisions applied (final numbers)

Tarik decided both open questions and amended Blueprint, `docs/PRD.md` and contract item 3
himself. This lane applied them and nothing else.

**What changed here**

1. `tests/browser/test_transfer.py`: the 10 % loss **median** budget 1.6 → **1.8 × K**, with a
   one-line comment naming the date and K 31. Worst-seed budgets and the 50 / 70 % rows are
   untouched. Observed at K 31: median **1.65**, worst 2.48 — inside both.
2. `pipeline/prioritise.py`: two rules inserted after `backup power` and before `monitor`, in
   this order — `audit5 == "1"` → **`verify on the ground`** → `DCDD, carrier`; and
   `svc_health_centre == "Y"` and telehealth `degraded` and `best_path != "satellite"` →
   **`measure the link here`** → `DCDD`. **Eight** interventions in the table and in the pack's
   `priority_interventions` header, same order as the rules. Their `why` clauses are two new
   `RULE_BECAUSE` strings, authored once like the other six.
3. **The pack went over the cap and the index fallback was applied.** With the two longer words
   spelled out per row the build came to **512,369 bytes, 369 over**. As instructed, the per-row
   `intervention` became **`i`**, an index into `priority_interventions`, and the per-community
   pointer became `priority: {rank, i}`. Nothing else was trimmed. **Final pack 506,343 bytes,
   5,657 under the cap** — the index bought back 6,026 bytes, so the headroom went from 1,523 to
   5,657. *For the seam: a priority row is now `{id, rank, score, c: [...], i, why}` and a
   community's pointer is `{rank, i}`.*
4. Tests: `test_each_intervention_reachable` extended to eight hand-built rows (one per rule,
   each built so no earlier rule fires); the pack test now asserts eight words in the header and
   that every row's `i` indexes it; `test_every_community_carries_its_rank_and_intervention_index`
   checks the pointer. Nothing enumerates the words in a `data/out/tables/priority.csv` consumer
   — `tests/test_figures.py` only asserts the column is non-empty — so no change was needed
   there. Unit tests stay at **200**, browser at **85**.

**Final gate.** `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` → **exit 0**. Last 10 lines:

```
   dist\index.html: 953,155 bytes (limit 1,048,576) ok
   data\out\data_pack.json: 506,343 bytes (limit 512,000) ok

== browser smoke: ...\.venv\Scripts\python.exe -m pytest -m browser
........................................................................ [ 84%]
.............                                                            [100%]
85 passed, 200 deselected in 34.47s

GATE GREEN
GATE EXIT: 0
```

Lint `All checks passed!`; 200 unit passed in 86.8 s; build ok; both size checks ok; 85 browser
passed in 34.5 s.

**Final sizes.** `data/out/data_pack.json` **506,343** bytes (limit 512,000, **5,657 left**).
`dist/index.html` **953,155** (limit 1,048,576).

**Interventions over the 96, all eight reached.**

| intervention | n | addressee |
|---|---|---|
| measure the link here | 31 | DCDD |
| backup power | 15 | carrier |
| refresh the coverage list | 14 | DCDD |
| low-latency backhaul | 12 | DCDD, nbn |
| monitor | 12 | DCDD |
| verify and publish the licensed site | 5 | carrier, ACMA |
| mobile site (MBSP nomination) | 4 | DCDD, carrier |
| verify on the ground | 3 | DCDD, carrier |

**`monitor` fell from 46 to 12, and the top 10 no longer contains it at all.** Every row of the
queue an analyst reads first now names something to do.

**Final top 10** (scores and ranks are unchanged — the interventions do not feed the score):

| # | community | score | intervention | addressee |
|---|---|---|---|---|
| 1 | Nauiyu | 0.632 | verify on the ground | DCDD, carrier |
| 2 | Nitjpurru | 0.608 | low-latency backhaul | DCDD, nbn |
| 3 | Galiwinku | 0.597 | backup power | carrier |
| 4 | Amanbidji | 0.596 | low-latency backhaul | DCDD, nbn |
| 5 | Areyonga | 0.586 | low-latency backhaul | DCDD, nbn |
| 6 | Maningrida | 0.582 | measure the link here | DCDD |
| 7 | Wurrumiyanga | 0.568 | backup power | carrier |
| 8 | Milingimbi | 0.561 | backup power | carrier |
| 9 | Jilkminggan | 0.553 | verify on the ground | DCDD, carrier |
| 10 | Numbulwar | 0.549 | measure the link here | DCDD |

**Sensitivity is unchanged**, because the score did not change: smallest top-10 overlap **6 of
10** on **`voice_sms_verdict` ×1.5**; smallest Spearman's rho **0.967**, `voice_sms_verdict`
×0.5. Every other perturbation keeps ≥ 7 of the top 10 and rho ≥ 0.975. Both zero-weight
components still read `top10_overlap 10, spearman_rho 1.0`.

**Two `why` sentences from the new rules**, assembled from pack strings as before:

- Nauiyu (#1): *Services present and population rank it here; a drive test found no signal
  inside claimed coverage.*
- Maningrida (#6): *Population and services present rank it here; a health centre whose link
  nobody has measured.*

**Line endings.** `git diff --stat` and `git diff --ignore-cr-at-eol --stat` are byte-identical,
so nothing was rewritten to CRLF. Nothing is committed.

The "46 of 96 get `monitor`" finding in the section above is now closed: it was the reason for
decision 2 and the count is 12.
