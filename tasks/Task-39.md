# Task-39: Map-claim reliability — one model, trained in the pipeline on the Audit, with a kill criterion

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
> ⛔ Before the fetcher runs: OQ18 (licence of the `Main_Audit_Roads` ArcGIS layers) is on the
> same email as OQ2. If the roads cannot be fetched or the answer is a refusal, skip contract
> items 2 to 4, write every `claim_reliability` as `none`, and say so in Status: the kill path
> is a valid completion of this task.

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

Status: TODO
