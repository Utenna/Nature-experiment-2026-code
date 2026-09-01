# Pipeline: execution order and data map

All scripts assume a local `Data/` tree next to the code (paths are resolved with
`here::here()` in R and relative paths in Python). None of this data is distributed with
the code; see `data-access.md`.

```
Data/
  Raw/
    merged_data0925.xlsx            raw survey export (participant level)      [not public]
  Processed/                        written by the cleaning step
Output/
  01-Env-health/
    Figures/                        figure image files
    Tables/                         supplementary table CSV/XLSX
```

## Order of execution

### 1. Covariate balance (Python) — `python/balance_test/balance-test-ses.ipynb`

Reads `Data/Raw/merged_data0925.xlsx`. Recodes the 8 SES covariates to match the main
analysis, then for each covariate computes:

- a **Kruskal–Wallis test** (`scipy.stats.kruskal`) across the 17 housing districts and
  across the 224 estates;
- a one-way **intraclass correlation coefficient** ICC(1) (between-group variance /
  total variance), via a hand-coded function in the notebook.

Output: `Table_S28_Balance_Test.csv` / `.xlsx`.
Manuscript: Methods "A natural experiment and data" (Kruskal–Wallis, ICC 0.03–0.25);
Supplementary balance-test table. (Note: the notebook labels the file `Table_S28`;
confirm the final supplementary number.)

### 2. Data cleaning + imputation + SEM mediation (R) — `R/GRF_project_2026_0413_SEM-bggm-dag-revised-clean.Rmd`

| Step | Detail | Output |
|---|---|---|
| Clean | recode, type-cast, derive analysis variables | `Data/Processed/data_cleaned_step1.csv` |
| Impute | `missForest` (ntree = 500); OOB NRMSE / PFC reported | imputed data frame; `Table_Imputation_Check.csv` |
| Residualise | linear regression of every analysis variable on the 8 SES covariates | `*_Pearson_Resid.csv` used by the network scripts |
| SEM | `lavaan::sem(..., se = "bootstrap", bootstrap = 5000)`; all vars z-standardised; lifestyle = observed composite total | `Table_Mediation_Results_Final_Beta.csv`; Figure 2 |

### 3. BGGM networks (R) — `R/GRF_project_2026_0415_bggm.Rmd`

`BGGM::estimate()` on SES-residualised item data, MCMC; edges retained when the 99%
posterior credible interval excludes zero. Computes Bridge Expected Influence
(`networktools`) and node predictability (Bayesian R2).
Output: partial-correlation matrices `adj_matrix_BGGM_<domain>_Pearson_Resid.csv`;
Figure 3; centrality indices; item-level association tables.

### 4. DAG + stability analyses (R) — `R/GRF_project_2026_0424_DAG.Rmd`

`bnlearn::boot.strength(algorithm = "pc.stable", R = 500)`; edge-inclusion threshold 0.70;
threshold sensitivity 0.70-0.98. Stability via `bootnet` (1000 case-dropping bootstraps,
EBICglasso estimator, `corStability(cor = 0.7)` -> CS-coefficient).
Output: `DAG_Arrows_<thr>_*.csv`; Figure 4; threshold-sensitivity tables.

### 5. Integration figures (R) — `R/GRF_project_2026_0415_BGGM_DAG_Integration_Visualization.Rmd`

Combines BGGM partial correlations with DAG-confirmed directions into the
environment x health heatmap (Figure 5) and the environment-lifestyle-health alluvial
diagram (Figure 6).

### 6. Reliability + CFA (R) — `R/GRF_project_2026_0413_CronbachMcDonalds.Rmd`

`psych::alpha`, `psych::omega` (nfactors = 1); `lavaan::cfa` with ML;
`fitMeasures(fit, c("chisq","df","pvalue","cfi","tli","rmsea","srmr"))`.
Output: `Table_S0A_Reliability.csv`, `Table_S0B_CFA_Fit_Indices.csv`,
`Table_S0C_CFA_Factor_Loadings.csv`. Can be run independently of steps 2-5.
