# ELH natural-experiment — reproduction capsule

De-identified data and code to reproduce the quantitative results of a
natural-experiment study of Hong Kong public-housing residents (Environment →
Lifestyle → Health). Prepared for Nature Cities peer review.

The raw questionnaire (3,350 residents of 224 public housing estates) is
restricted under University of Hong Kong Human Research Ethics Committee
approval **EA1910004(A3)** and cannot be shared. This capsule ships the
**de-identified** data that is sufficient to reproduce every reported statistic.

---

## Layout

```
code/
  run                        entry point (bash); orchestrates all steps
  paths.py / paths.R         /data (read-only in) and /results (out) shims
  00_prepare_deidentified_data.py   PROVENANCE ONLY — how /data was built from
                                    the restricted source; not run by `run`
  01_balance_test.py         covariate balance test  -> Supplementary Table S12
  02_icc_check.R             between-estate ICC on the analysis sample
  03_reliability_cfa.R       Cronbach alpha / McDonald omega + CFA fit
  04_sem_mediation.R         parallel-mediation SEM (lavaan, bootstrap)
  05_bggm_network.R          Bayesian Gaussian Graphical Models (BGGM)
  06_dag.md                  PC-stable DAG (bnlearn) + bootnet stability -- SOURCE ONLY,
                              not executed by `run` (~30 h at published settings; see
                              "Step 06" section below for why and how to run it)
  lib/00_load.R              rebuilds df_clean_num / df_resid / df_scores / …
                             from data_analysis.csv (deterministic; replaces the
                             private pipeline's cleaning + missForest front-end)
data/
  data_balance.csv           3,350 rows — pre-imputation covariates + group ids
  data_analysis.csv          3,331 rows — post-imputation model items + anon ids
  README.md                  data dictionary notes
metadata/metadata.yml
results/                     run outputs land here (incl. results/validation/)
```

## Run

```bash
bash code/run              # published settings for steps 01-05 (~5 h, dominated by 05's
                           #   BGGM 5000-iteration MCMC)
```

`run` executes **steps 01-05 only**, at either setting; it completes inside a
standard Reproducible Run's time limit. Step 06 (DAG + stability) is not run
by this script at any `QUICK` setting — see "Step 06" below.

## What each step reproduces

| Step | Script | Manuscript item | Key outputs in `/results` |
|---|---|---|---|
| 1 | `01_balance_test.py` | Supplementary Table S12 (Kruskal–Wallis + ICC) | `Table_S12_Balance_Test.csv`; `validation/balance_test_comparison.csv` |
| 2 | `02_icc_check.R` | between-estate ICC (Methods / S12) | `Table_ICC_estate_analysis_sample.csv`; `validation/icc_comparison.csv` |
| 3 | `03_reliability_cfa.R` | Tables S14–S16 (CFA fit, α/ω, loadings) | `Table_S15_Reliability.csv`, `Table_S14_CFA_Fit_Indices.csv`, `Table_S16_CFA_Factor_Loadings.csv` |
| 4 | `04_sem_mediation.R` | parallel-mediation SEM (indirect effects, BC/percentile bootstrap CIs) | `Table_Mediation_Results_Final_Beta.csv` |
| 5 | `05_bggm_network.R` | BGGM networks — edges (99% CrI), predictability, bridge EI | `adj_matrix_BGGM_*`, `Table_Edge_CrI_*`, `Table_Predictability_*`, `Table_Bridge_Metrics_*` |
| 6 | `06_dag.md` (**source only, not run by `run`** — see below) | PC-stable DAG + threshold sensitivity + CS-coefficient | `Boot_Object_*.rds`, `Sensitivity_Table_*`, `DAG_Arrows_*`, `Stability_CS_*` |

`results/validation/` holds cell-by-cell comparisons of the reproduced values
against the published numbers. `01`/`02` exit non-zero on any unexplained
mismatch.

## Step 06 (DAG + stability): why it's `.md`, not run by `run`

Step 06 (PC-stable DAG bootstrap + bootnet case-dropping stability, 3 health
domains) is **not** executed by `code/run`. 
At published settings it is ~30 h wall clock for this step alone
(`bnlearn::boot.strength` R=500 × 3 domains + serial `bootnet`
case-dropping, `boots=1000` × 3 domains) — well beyond a single Code Ocean
session. Rather than leave a script in `code/` that a Reproducible Run would try and fail to finish, its source is
kept as **`code/06_dag.md`**.