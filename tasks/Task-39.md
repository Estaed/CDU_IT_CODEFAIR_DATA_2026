# Task-39: Map-claim reliability — one model, trained in the pipeline on the Audit, with a kill criterion

**Status: DONE** — verified 2026-09-17 (main loop: gate green, 166 unit + 85 browser, pack 476,606 bytes; the model shipped at pooled held-out AUC 0.7915 against the fixed 0.65 floor; mutation: `CUT_LOW` 0.50 → 0.90 turns `test_words_from_cut_points` red, restored; layer-rule-9 grep prints nothing. Deviation 2 accepted as `not-recorded`; deviation 7 decided: the note lives once on the sources entry.)

> **Execution:** agent `claude-worker` (opus) · effort `high`
> *Why:* 2026-09-17. Label construction, a spatial hold-out and a pre-registered kill
> criterion; a leak between train and test would ship a number that is not true, so Opus. The
> decision rule is fixed below and is not the worker's to move. Codex is at 100 % until
> 2026-09-19.

> **Lane:** OWNS `pipeline/reliability.py` (new), `pipeline/fetch/audit_roads.py` (new),
> `pipeline/sources/audit.py` (the `0` value only, contract item 2 of Task-38), `pyproject.toml`
> and `uv.lock` (`uv add scikit-learn`), `pipeline/pack.py` (the `claim_reliability` key per
> community only), `pipeline/provenance.py` (append entries), `scripts/run_pipeline.py` (call
> `reliability.main` after the table is written, before `pack.main`), `tests/test_reliability.py`
> (new), `tests/test_pack.py` (append only), `data/out/` (regenerated), this file · MUST NOT
> TOUCH `app/`, `pipeline/rules.py`, `pipeline/merge.py`, `pipeline/prioritise.py` (Task-40),
> `design/`, `CLAUDE.md` (the version cell in the stack table is the main loop's) · GATE
> `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` · DEPENDS ON Task-38
> Stop marker cleared 2026-09-17 by Tarik ("evet, indir ve eğit"): fetch the roads and train
> before the OQ18 answer, the same policy as BushTel (request on file, the Methodology says so);
> the licence answer decides whether the model ships in the pack, not whether it is built. If
> the roads cannot be fetched, or a refusal arrives, skip contract items 2 to 4, write every
> `claim_reliability` as `none`, and say so in Status: the kill path is a valid completion.

## Why

PRD §4.2 fourth batch, second bullet. Four publishers claim; Task-38 adds where a drive test
disagreed. The question an analyst asks next is "how much should I trust the claim in the
communities nobody drove to?". The Audit gives labelled ground truth on NT roads; the pack
already has, per community, the features that plausibly predict a wrong claim (distance to the
claiming carrier's nearest licensed site, how deep inside the polygon the point sits, how many
sites within 10 and 20 km, how many carriers claim). A small supervised model trained on the
roads and applied at the 96 points gives one word per community, with the two features that
drove it, and the report says what it can and cannot mean. The kill criterion is written
before the first fit.

## Contract

1. **Dependency.** `uv add scikit-learn`; the version is read from `uv.lock` and reported in
   Status. Imported in `pipeline/reliability.py` only (layer rule 9).
2. **Negatives.** `pipeline/fetch/audit_roads.py` queries the `Main_Audit_Roads_DITRDCA_2024`
   MapServer layers (`reports/2026-09-12-arena-measured.md` §3.1.9) for NT geometry and writes
   `data/raw/audit_roads_<date>.geojson`. Verified by the main loop on 2026-09-17: the service
   answers without a token at
   `https://spatial.infrastructure.gov.au/server/rest/services/Main_Audit_Roads_DITRDCA_2024/MapServer`
   (the `/Hosted/` path wants a token), layers `0` Year_1_Roads, `1` Year_2_Roads, `2`
   Year_3_Roads; a `query` with the NT envelope `129,-26,138,-10.9` (`esriGeometryEnvelope`,
   `inSR=4326`, `returnCountOnly=true`) counts 2,518 / 4,191 / 4,191 features (OSM road
   segments, fields `OSM_ID`, `name`, `Major_Urban`); `exceededTransferLimit` is true on a
   full query, so page with `resultOffset` and `resultRecordCount`, and pass
   `returnGeometry=true` and `outSR=4326` explicitly. Union the three years; the sample date
   is the fetch date. Roads in the `Major_Urban = T` set are kept (no community sits in one,
   and the model needs the negatives). `reliability.samples()` places points every 1 km along
   the NT audited roads that lie inside at least one ACCC 2025 4G polygon (the cache the
   pipeline already writes) and labels each point `1` if it lies within a non-alignment tile of
   a carrier that claims it, else `0`. Points within 1 km of another point of the same label
   are thinned to one. Fill `audit5 = "0"` in the audit source for a community that has an
   audited road point within 5 km and no non-alignment tile (Task-38 item 2 defined the value).
3. **Features**, computed by one function over a plain dict so the same code runs on a road
   sample and on a community row: `site_km` (nearest licensed cellular site of the claiming
   carrier, from the RRL sites table `rrl.write_sites` already emits), `depth_km` (distance from
   the point to the claiming polygon's boundary, positive inside), `sites_10km`, `sites_20km`,
   `carriers_claiming`, and `relief_m` only if `data/raw/` holds a coarse DEM when the task
   starts (Geoscience Australia 9-second DEM clipped to the NT; not fetched by this task; a
   missing DEM means the feature is absent and Status says so).
4. **Model and validation.** Logistic regression with standardised features
   (`sklearn.linear_model.LogisticRegression`, `class_weight="balanced"`, `random_state=0`).
   Split **by ABS SA3 region** (`data/raw/abs_sa3_2021_shp.zip`, already in the repo; point in
   polygon), five folds over regions, every sample's region appears in exactly one test fold.
   Report per fold and pooled: AUC, precision and recall at 0.5, the base rate, the sample and
   region counts, in `data/out/tables/reliability_validation.csv`. Coefficients with feature
   names in `data/out/tables/reliability_coefficients.csv`.
5. **Kill criterion, fixed here, 2026-09-17, before any fit:** pooled held-out AUC **≥ 0.65**
   ships the model; below it, every community gets `word: "none"`, `p_wrong: null`,
   `drivers: []`, the validation table is still written, and the pipeline completes. No
   feature or threshold is tuned after seeing the held-out result; the fold assignment is
   seeded and recorded.
6. **Per community.** Fit on all samples once validated; apply at each of the 96 points **per
   claiming carrier** and take the maximum `p_wrong`. Words by fixed cut points: `high`
   reliability when `p_wrong < 0.25`, `medium` in `[0.25, 0.5)`, `low` at `≥ 0.5`; `none` when
   no carrier claims the community (no polygon over the point). `drivers` are the two features
   with the largest absolute standardised contribution for that community. Written to
   `data/out/reliability.csv` (id, name, word, p_wrong, carrier, driver1, driver2) and into the
   pack as `claim_reliability: {word, p_wrong, drivers, src}` with `src` a registry key whose
   entry names the Audit CSV, the roads layer, the model, the fit date and the pooled AUC.
7. **Honesty line**, in the pack entry's `note` and the report: the model is trained on roads
   and applied to community points; a community's word is an extrapolation from the nearest
   audited conditions, not a measurement at the community.

## Tests (`tests/test_reliability.py`)

`test_features_from_hand_built_row` (a row 2 km inside a polygon with one site at 3 km gives
the named values); `test_split_by_region_is_disjoint` (no region on both sides of any fold);
`test_kill_path_completes` (a stub `evaluate` returning AUC 0.5 leaves every word `none`,
`p_wrong` `None`, and still writes the validation table); `test_words_from_cut_points` (0.1,
0.3, 0.7 give `high`, `medium`, `low`; no claim gives `none`); `test_no_sklearn_elsewhere`
(the layer-rule-9 grep). `tests/test_pack.py`: every community carries `claim_reliability`
with a word in the four, `p_wrong` null exactly when the word is `none`, and `src` resolving
in the pack's `sources` table.

## Out of the gate

Whether AUC clears 0.65 (either outcome is a finding the report prints); the DEM (Tarik, if
time allows); OQ2 and OQ18.

## Status

Status: IMPLEMENTED (2026-09-17, claude-worker opus) — awaiting verify-task

**The model shipped.** Pooled held-out AUC **0.7915** against the floor of 0.65, so the kill
path did not run: 74 of the 96 communities carry a word, 22 carry `none` because no carrier
polygon covers them. Gate green, exit 0 (166 unit, 85 browser).

### What landed

- `pyproject.toml` / `uv.lock`: `scikit-learn` resolved to **1.9.1** (with scipy 1.18.1,
  joblib 1.6.0, threadpoolctl 3.7.0, cloudpickle 3.1.2, narwhals 2.26.0). Imported in
  `pipeline/reliability.py` only; layer rule 9 checked by
  `tests/test_reliability.py::test_no_sklearn_elsewhere` and by hand.
- `pipeline/fetch/audit_roads.py` (new): the audited road centrelines, run once by hand to
  `data/raw/audit_roads_2026-09-17.geojson` (2,835,536 bytes, **10,900 segments**, exactly the
  2,518 / 4,191 / 4,191 the contract records per layer — the fetcher asserts that count and
  warns if short). See Deviation 1: the `query` endpoint the contract names returns attributes
  but never geometry, so the geometry comes from `identify`.
- `pipeline/reliability.py` (new): `features` (one pure function over a plain dict, the same
  code on a road sample and on a community row), `road_points`, `Geography` (one spatial index
  for claims, tiles and sites), `thin`, `regions_for`, `fold_of_region`, `samples`, `evaluate`,
  `fit`, `community_rows`, `word_for`, `fill_audit_zero`, the three writers and `main`.
  Distances are metres in EPSG:3577 (Deviation 6).
- `pipeline/sources/audit.py`: `audited_within` only — the ids with an audited road sample
  within `NEAR_M`, which is the `"0"` Task-38 defined and could not write. The module still
  never writes `"0"` itself; `reliability.fill_audit_zero` puts it in the table.
- `pipeline/pack.py`: `claim_reliability` per community — exactly the four seam keys
  `{word, p_wrong, drivers, src}` — plus `reliability_lines`, `pooled_auc`,
  `_no_reliability`, and the `audit5 == "0"` publisher branch (Deviation 2).
- `pipeline/provenance.py`: two entries — `audit_roads_2024` in `SOURCES` (the raw snapshot, so
  PROVENANCE.md records it with its fetch command) and `reliability_model` in `PACK_SOURCES`
  (the pack's `src`, dateless on purpose so the citing line carries the fit date, and
  carrying the honesty `note` whose `{auc}` the pack fills from the validation table).
- `scripts/run_pipeline.py`: `reliability.main()` after the table is written and before
  `pack.main()`. The whole run is **1 m 52 s**, the reliability step **83 s** of it; no new
  cache was needed.
- Tests: `tests/test_reliability.py` (new, 9), `tests/test_pack.py` (+3).

### The numbers

**Sampling.** 32,251 km of audited NT road; 40,895 points at 1 km collapse to **14,304**
distinct locations (the three yearly layers overlap heavily — a road driven twice is published
twice). After labelling, thinning at 1 km within a label and dropping points outside every NT
SA3 polygon: **3,919 samples** (one per point and claiming carrier) over **9 SA3 regions**,
**111 positives, base rate 2.832 %**.

**Validation** (`data/out/tables/reliability_validation.csv`), five folds over regions, seed 0:

| fold | regions | n | pos | AUC | precision@0.5 | recall@0.5 |
|---|---|---|---|---|---|---|
| 1 | Darwin Suburbs; Palmerston | 204 | 0 | — | — | — |
| 2 | East Arnhem; Litchfield | 426 | 4 | 0.9953 | 0.1818 | 1.000 |
| 3 | Alice Springs; Daly - Tiwi - West Arnhem | 2,002 | 38 | 0.8078 | 0.0405 | 0.8158 |
| 4 | Barkly; Katherine | 1,251 | 69 | 0.7150 | 0.1023 | 0.7101 |
| **pooled** | 9 regions, seed 0 | **3,919** | **111** | **0.7915** | **0.0663** | **0.7568** |

Fold 5 (Darwin City, n=36) is omitted from the table above only for width; like fold 1 it holds
no positive, so its AUC is undefined and the cell is blank in the CSV. The NT has just nine SA3
regions and the two urban ones carry no non-alignment. The pooled row — every sample scored by a
model that never saw its region — is what the kill criterion read.

**Coefficients** (standardised, `data/out/tables/reliability_coefficients.csv`):
`sites_20km` **−3.564**, `sites_10km` **−1.531**, `carriers_claiming` **−1.009**, `depth_km`
**−0.430**, `site_km` **+0.407**, intercept −2.713. Every sign is the one a person would
predict: more masts within 20 km, more carriers claiming and deeper inside the polygon all
lower the risk; farther from the claiming carrier's own site raises it.

**Words over the 96:** `high` **8**, `medium` **29**, `low` **37**, `none` **22**.

**The ten highest `p_wrong`** (all Telstra claims, all driven by the same pair):

| id | community | word | p_wrong | carrier | drivers |
|---|---|---|---|---|---|
| 127 | Nturiya | low | 0.7397 | Telstra | sites_20km, carriers_claiming |
| 147 | Arawerr | low | 0.7193 | Telstra | sites_20km, carriers_claiming |
| 65 | Iwupataka | low | 0.7159 | Telstra | sites_20km, carriers_claiming |
| 531 | Milingimbi | low | 0.6494 | Telstra | sites_20km, carriers_claiming |
| 654 | Weemol | low | 0.6437 | Telstra | sites_20km, carriers_claiming |
| 362 | Maningrida | low | 0.6377 | Telstra | sites_20km, carriers_claiming |
| 429 | Warruwi | low | 0.6360 | Telstra | sites_20km, carriers_claiming |
| 549 | Numbulwar | low | 0.6315 | Telstra | sites_20km, carriers_claiming |
| 375 | Minjilang | low | 0.6307 | Telstra | sites_20km, carriers_claiming |
| 587 | Bulman | low | 0.6300 | Telstra | sites_20km, carriers_claiming |

`sites_20km` with `carriers_claiming` drives 69 of the 74 scored communities; `depth_km`
appears in 3 and `sites_10km` in 1. `p_wrong` ranges 0.0045 to 0.7397.

**`audit5 = "0"` written for 37 communities** — an audited road passed within 5 km and carried
no non-alignment. With Task-38's 3 ones, 40 of 96 cells now say something and 56 stay empty.

**Sizes.** `data/out/data_pack.json` 464,416 → **476,606** bytes (limit 512,000; **35,394
left**). `dist/index.html` 911,228 → **923,418** (limit 1,048,576). The pack's +12.2 KB is the
words, probabilities and driver names; the honesty `note` costs 158 bytes once, on the
`sources` entry (Deviation 7). Carrying that note per community instead cost 15,288 bytes
more, measured both ways.

**Tests.** 154 → **166 unit** (+12), **85 browser** unchanged. The transfer budget tests pass at
the larger pack without touching a budget (they became a distribution in Task-38).

### Gate

`PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` → **exit 0**, green on the first run after
the code was complete and again after the Deviation 7 fix loop. Lint `All checks passed!`,
166 unit in 116.2 s, build 923,418 bytes, both size checks ok, 85 browser in 38.8 s.

### Deviations from the Contract

1. **The roads come from `identify`, not `query`** (contract item 2 named the `query` endpoint,
   its paging and its field names). The counts in the contract are right and the fetcher
   reproduces them exactly, but **this service never returns geometry from `query`** — checked
   on 2026-09-17 in every combination (`f=json`, `f=geojson`, `f=pbf`, with and without
   `outSR`, by `objectIds`, with and without `resultOffset`): the response carries no
   `geometryType` and every `geometry` is `null`. `/Hosted/` wants a token and no open
   `FeatureServer` exists. `identify` on the same layers does return the paths, so the fetcher
   walks the NT envelope in 1° tiles, asks all three layers at once, and splits a tile in four
   whenever the answer comes back at the 2,000-record cap (that cap is silent, so an unsplit
   tile would lose roads without saying so). Geometry is generalised to 0.001° (~100 m), well
   inside the 1 km sampling step. The per-layer counts are asserted at the end of the fetch and
   all three matched. Layer 2 also publishes different field names (`osm_id`, `oneway`, no
   `Major_Urban`), which is why an explicit `outFields` list 400s on it.
2. **`pack.publisher_lines` gained the `audit5 == "0"` branch** (outside OWNS, which named the
   `claim_reliability` key only). Without it the 37 communities the contract just gave a `"0"`
   would have kept the line "No audited road within 5 km", which is now false for them. The
   branch keeps `says_covered: "not-recorded"` and says instead "Audited road within 5 km with
   no non-alignment against any carrier's claim; the Audit drove roads, not communities", so
   **no agreement count moves** and the measured line still never says `covered`. Calling it
   `covered` would have been the other reading — the drive test found nothing against the map —
   but that changes `rules.agreement` for 37 communities and contradicts PRD §4.2, which gives
   the audit line two values only. Flagged for verify-task as the one judgement call here.
3. **`tests/test_pack.py::test_measured_publisher_line`, one assertion widened** to accept
   either not-recorded detail. Direct consequence of Deviation 2; nothing weakened.
4. **`tests/test_provenance.py::EXPECTED_IDS`, one line** for `audit_roads_2024`. The set is
   exact, exactly as in Task-38.
5. **No `relief_m`.** `data/raw/` holds no DEM (checked at the start), so the feature is absent,
   as contract item 3 allows. No dead code was left for it; the comment beside `FEATURE_NAMES`
   says what adding it later costs.
6. **Distances in EPSG:3577 (GDA94 Albers), not the MGA zones** `pipeline/sources/audit.py`
   uses. One projection covers the whole NT, which matters when a road sample and its polygon
   straddle 132° E; Task-38 already cross-checked the two against each other and they agreed
   within 10 m. `audit.audited_within` takes the CRS from its caller, so the 5 km radius is
   still measured by the module that owns it.
7. **The `note` lives on the `sources` entry, not on the 96 communities** — raised by this lane,
   **decided by the main loop on 2026-09-17 and applied**. `claim_reliability` now carries
   exactly the four seam keys `{word, p_wrong, drivers, src}`, and the app reads the honesty
   line through `src` like every other citation. The wording lives in the
   `reliability_model` registry entry (`pipeline/provenance.py`), which is where source text
   belongs; only the pooled AUC is a run figure, filled by `pack.citations` from the
   validation table. `tests/test_pack.py` reads the note off the entry and asserts all 96
   lines share one `src`. Worth **15,288 bytes**: the pack is 476,606 with the note said once
   and was 491,894 with it said 96 times.

### Two things the report should not skip

- **`p_wrong` is a class-balanced score, not a calibrated frequency.** The contract fixes
  `class_weight="balanced"` with a 2.83 % base rate, so probabilities are pulled towards the
  middle: precision at 0.5 is **0.066** while recall is **0.757**. Read `low` as "this claim
  ranks with the ones the drive test contradicted", never as "this claim is 63 % likely to be
  wrong". The ranking is what the AUC of 0.79 supports; the level is not.
- **Two of five folds could not produce an AUC** because the NT has nine SA3 regions and the
  urban ones hold no non-alignment. The split is still honest — no region is on both sides —
  but a reader should be told the pooled number rests on three folds.

### One thing for the main loop

Commit `e8f77ca` ("Blueprint replaces Part 2"), made while this lane was running, swept this
lane's in-progress `pipeline/sources/audit.py` change (`audited_within`, +27 lines) into a docs
commit. The content is correct and unchanged; it is simply already committed rather than waiting
in the working tree with the rest of Task-39.
