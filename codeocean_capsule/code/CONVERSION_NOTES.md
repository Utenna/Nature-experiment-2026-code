# Conversion notes — private `.Rmd` / `.ipynb` → capsule scripts

What changed when porting the analysis code into this capsule, and what to
verify before uploading. **R was not available in the environment that produced
these ports — smoke-test `02`–`06` once in RStudio.**

## Shared changes (all scripts)

1. **Front-end removed.** Every private `.Rmd` re-derived `df_clean_num`,
   `df_resid`, `df_scores`, `ses_df_model` from `Data/Raw/merged_data0925.xlsx`
   via `bruceR::import` + `missForest`. That whole block is replaced by
   `lib/00_load.R`, which reads the de-identified post-imputation
   `data_analysis.csv` and rebuilds the same objects deterministically
   (residualisation is a plain `lm`; score composition is `rowMeans` + `scale`).
   Verified in Python that `data_analysis.csv` == `df_clean_num` from
   `Data_Forked_Step4.RData` row-for-row.
2. **Paths.** `here::here('Data','Processed', …)`, `data_proc_dir`,
   `out_tables_dir`, `out_fig_dir`, `out_dir`, `out_dir_dag` all now point at
   `RESULTS_DIR` (`/results`). Inputs come from `data_path()` (`/data`).
3. **`load()` / `save()` of `Data_Forked_Step4.RData`** removed — the objects are
   already in scope from `lib/00_load.R`.
4. **Author identity stripped** for double-blind review (the source `.Rmd`
   YAML headers carried an author name and date).
5. **Figure code removed.** `qgraph`, `ggsave`, `pdf()` plotting blocks are not
   ported (not reproduction-critical, and the fragile part on a headless
   runner). All CSV/numeric outputs are kept.
6. **`QUICK` env var** added to gate the heavy resampling (see per-file below).
   Seeds are unchanged from the originals.

## Per file

### `01_balance_test.py`  ← `Code/Python/02_analysis/balance-test-ses.ipynb`
- Reads `data/data_balance.csv` instead of the raw workbook; the SES-derivation
  cells (LivArea/DurRes/CD recodes) are already baked into `data_balance.csv`,
  so they are dropped here.
- `icc_one_way()` copied verbatim (incl. `max(icc, 0)`).
- Added a cell-by-cell comparison against the published Table S12 constants;
  **exits non-zero** on mismatch. Verified locally: all 48 cells reproduce.

### `02_icc_check.R`  ← balance-test ICC, applied to the analysis sample
- New script. One-way ICC(1) with the notebook's exact formula, over
  `Estate_ID`, on the 3,331-row analysis sample. Optional null-model ICC via
  `lme4`/`performance` as an independent cross-check (skipped if not installed).
- Expected vs published S12 (different N + imputation): 7/8 covariates within
  ≤0.001; **Gender 0.112 vs 0.099** — this is the analysis-sample restriction
  `Gender ∈ {1,2}` (restricting the balance file the same way also gives 0.112),
  not an anonymisation artefact. The script encodes this as an explained
  difference, not a failure.
- VERIFY: `lme4` null-model column populates; one-way column equals the Python
  reference in `validation/icc_comparison.csv` to 1e-4.

### `03_reliability_cfa.R`  ← `GRF_project_2026_0413_CronbachMcDonalds.Rmd` (reliability/CFA chunk)
- Logic unchanged: `psych::alpha(check.keys = TRUE)$total$raw_alpha`,
  `psych::omega(nfactors = 1)$omega.tot`, `lavaan::cfa(std.lv = TRUE,
  estimator = "ML")`, `standardizedSolution`.
- VERIFY: fit indices (CFI/TLI/RMSEA/SRMR) match Table S14; α/ω match Table S15;
  standardised loadings match Table S16.

### `04_sem_mediation.R`  ← `GRF_project_2026_0413_SEM-bggm-dag-revised-clean.Rmd` ("Step 5C 中介分析")
- `run_mediation()` model syntax, `set.seed(1234)`, `se = "bootstrap"`,
  `boot.ci.type = "perc"` — all unchanged. Only `bootstrap = N_BOOT`
  (5000 default / 1000 QUICK).
- Column `β` renamed to `b` in the CSV header to avoid non-ASCII in output.
- VERIFY: indirect effects and 95% CIs for the four outcomes match the
  manuscript's mediation table.

### `05_bggm_network.R`  ← `GRF_project_2026_0415_bggm.Rmd` ("Step 6 BGGM")
- `run_bggm_full_metrics()` trimmed to the controlled (residualised) model's
  outputs: `BGGM::estimate(iter = ITER_NUM)` → `select(cred = 0.99)` →
  `pcor_adj`, `summary(cred = 0.99)`, `predictability`, `networktools::bridge`.
  All `qgraph` pages dropped.
- `set.seed(42)` unchanged. The .Rmd's raw (unadjusted) `BGGM::estimate` is
  KEPT (result discarded, memory freed with `rm`+`gc`) purely for RNG
  alignment: it runs between `set.seed(42)` and the residualised `estimate`,
  exactly as in the .Rmd, so `fit_ctrl` draws the same MCMC chain as the
  published tables. Dropping it shifted the chain and flipped ~7-11 of the
  weakest edges (|r| ≲ 0.05) in/out of the 99% CrI set vs the published
  negative-partial-correlation table.
- Resume support: a domain whose four `<...>_<domain>.csv` tables already exist
  and are non-empty in `/results` is skipped, so a run killed in the slow
  `predictability` step can just be re-launched. Fresh `/results` = full run.
- New `Table_Bridge_Metrics_<domain>.csv` collects bridge EI/strength + node
  EI/strength (previously only plotted).
- VERIFY: `Post.mean` of predictability + edge CrI match the BGGM supplementary
  tables to ≤ 0.001; edge selection at 99% CrI and bridge-EI ordering match.
  QUICK changes MCMC precision — small numeric drift expected there; use
  default for the record.

### `06_dag.md`  ← `GRF_project_2026_0424_DAG.Rmd` (PHASE 2 + PHASE 3)
(Converted from `06_dag.R` to `.md` 2026-09-11 — `run` does not execute it,
~30 h at published settings; source kept verbatim in the `.md`. See the
capsule README "Step 06" section. Everything below still describes the code.)
- `boot.strength(algorithm = "pc.stable", alpha = 0.01, blacklist = {L,H}→E)`,
  `set.seed(999)`, `R = 500` (100 QUICK). Sensitivity loop over
  thresholds 0.70–0.98; arc CSVs at 0.70/0.75/0.80/0.85/0.90/0.95.
- `DAG_AvgNetwork_0.70_*` written from `as.data.frame(str_fit)` filtered to
  `strength ≥ 0.70 & direction ≥ 0.5` — CHECK this matches how the manuscript
  defines the reported DAG edge set (the `.Rmd` derived edges via
  `averaged.network(threshold = 0.70)$arcs`; both are provided).
- PHASE 3: `bootnet(type = "case", statistics = "bridgeExpectedInfluence")`,
  `set.seed(777)`, `boots = 1000` (200 QUICK). Changed `nCores` from the
  `.Rmd`'s `8` to `1L`: bootnet has no `seed` argument and sets no per-worker
  RNG stream, so `set.seed()` is only honoured when the loop runs serially —
  single-core makes the CS-coefficient bit-identical on any host. (Bridge-EI
  stability saturates the `corStability` grid ceiling `caseMax = 0.75`, so the
  published `CS = 0.75` is seed-robust anyway.) Writes
  `validation/stability_cs_comparison.csv` (reproduced vs published CS = 0.75).
- VERIFY: edge counts per threshold match `Sensitivity_Table_*`; CS-coefficient
  = 0.75 for all three networks (`stability_cs_comparison.csv`).

## If a step fails on Code Ocean

- Missing R package → add to `environment/install.R`.
- Runtime limit → run with `QUICK=1`, and/or request extended limits. (All
  resampling is single-threaded by design; there is no core-count parameter.)
