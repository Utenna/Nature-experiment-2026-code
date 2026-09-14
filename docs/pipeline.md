# Pipeline: execution order and data map

All scripts live under `codeocean_capsule/code/` and run against the capsule's own
`codeocean_capsule/data/` (de-identified, git-ignored — see `codeocean_capsule/data/README.md`)
and `codeocean_capsule/results/` (outputs, git-ignored). Paths are resolved by the
`paths.R` / `paths.py` shims (Code Ocean mounts `/data` read-only and `/results` for
output; locally they fall back to the capsule's own `data/` and `results/` folders, or
respect the `CO_DATA` / `CO_RESULTS` environment variables).

```
codeocean_capsule/
  data/
    data_balance.csv       3,350 rows — pre-imputation covariates + group ids   [git-ignored]
    data_analysis.csv      3,331 rows — post-imputation model items + anon ids  [git-ignored]
    codebook.csv                                                               [git-ignored]
  results/                 written by the run; validation/ compares to published numbers
                                                                                [git-ignored]
```

The restricted raw participant data (`merged_data0925.xlsx`) is not part of this
repository; see `data-access.md`. `codeocean_capsule/code/00_prepare_deidentified_data.py`
documents (provenance only, not run by `code/run`) how `data/` was derived from that raw
file.

## Order of execution

Run everything with `bash codeocean_capsule/code/run` (default `QUICK=1`, reduced
resampling, finishes in minutes; `QUICK=0` reproduces published-precision numbers for
steps 01-05, ~5 h, dominated by step 05's BGGM MCMC). Steps below can also be run
individually in this order; step 06 is documentation-only.

### 1. Covariate balance (Python) — `code/01_balance_test.py`

Reads `data/data_balance.csv`. For each of the 8 SES covariates computes:

- a **Kruskal–Wallis test** (`scipy.stats.kruskal`) across the 17 housing districts and
  across the 224 estates;
- a one-way **intraclass correlation coefficient** ICC(1) (between-group variance /
  total variance).

Output: `results/Table_S12_Balance_Test.csv`; compared against published numbers in
`validation/balance_test_comparison.csv`. Manuscript: Methods "A natural experiment and
data" (Kruskal–Wallis, ICC 0.03–0.25); Supplementary Table S12.

### 2. Between-estate ICC (R) — `code/02_icc_check.R`

ICC on the analysis sample (post-imputation). Output:
`results/Table_ICC_estate_analysis_sample.csv`; compared in `validation/icc_comparison.csv`.

### 3. Scale reliability + CFA (R) — `code/03_reliability_cfa.R`

`psych::alpha`, `psych::omega` (nfactors = 1); `lavaan::cfa` with ML;
`fitMeasures(fit, c("chisq","df","pvalue","cfi","tli","rmsea","srmr"))`.
Output: `results/Table_S15_Reliability.csv`, `Table_S14_CFA_Fit_Indices.csv`,
`Table_S16_CFA_Factor_Loadings.csv`. Can be run independently of steps 4-5.

### 4. Parallel-mediation SEM (R) — `code/04_sem_mediation.R`

Uses `lib/00_load.R` to rebuild the analysis frames (SES-residualised items,
z-standardised) from `data_analysis.csv` — deterministic, replacing the original
cleaning + `missForest` imputation front-end (which is documented, not re-run, since
`data_analysis.csv` already ships post-imputation). `lavaan::sem(..., se = "bootstrap",
bootstrap = 5000)`; lifestyle = observed composite total.
Output: `results/Table_Mediation_Results_Final_Beta.csv` -> Figure 2.

### 5. BGGM networks (R) — `code/05_bggm_network.R`

`BGGM::estimate()` on SES-residualised item data, MCMC; edges retained when the 99%
posterior credible interval excludes zero. Computes Bridge Expected Influence
(`networktools`) and node predictability (Bayesian R2).
Output: partial-correlation matrices `adj_matrix_BGGM_<domain>_Pearson_Resid.csv`,
`Table_Edge_CrI_*`, `Table_Predictability_*`, `Table_Bridge_Metrics_*` -> Figure 3;
compared to published numbers in `validation/` (≤0.001).

### 6. PC-stable DAG + stability (R, documentation only) — `code/06_dag.md`

`bnlearn::boot.strength(algorithm = "pc.stable", R = 500)`; edge-inclusion threshold 0.70;
threshold sensitivity 0.70-0.98. Stability via `bootnet` (1000 case-dropping bootstraps,
EBICglasso estimator, `corStability(cor = 0.7)` -> CS-coefficient). At published settings
this is ~30 h wall clock, so it is kept as source (`.md`), not executed by `code/run`; see
that file for how to run it. Output: `DAG_Arrows_<thr>_*.csv`, `Boot_Object_*.rds`,
`Sensitivity_Table_*` -> Figure 4; compared in `validation/` (Mental Health PHASE 2
matches exactly).

Figures 5 and 6 (the environment × health direct-pathway heatmap and the
environment–lifestyle–health indirect-pathway alluvial diagram) are presentational
visualizations of the BGGM partial correlations (step 5) and DAG-confirmed directions
(step 6) above — no separate statistical analysis, so no separate script is included.

Figure 7 (public-housing map) is likewise a presentational GIS rendering with no
statistical analysis; its rendering code is not part of this repository. Data sources for
that map are attributed in the figure caption.
