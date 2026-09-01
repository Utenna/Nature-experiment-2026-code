# Script -> manuscript output crosswalk

| Manuscript element | Script | Method / package |
|---|---|---|
| **Figure 2** (SEM mediation) | `R/GRF_project_2026_0413_SEM-bggm-dag-revised-clean.Rmd` | `lavaan` parallel mediation, ML, 5000 bootstrap, BC 95% CI |
| **Figure 3** (BGGM networks) | `R/GRF_project_2026_0415_bggm.Rmd` | `BGGM`, `networktools` (Bridge Expected Influence) |
| **Figure 4** (partially directed acyclic graphs) | `R/GRF_project_2026_0424_DAG.Rmd` | `bnlearn` PC-stable, `boot.strength` R=500 |
| **Figure 5** (direct-pathway heatmap) | `R/GRF_project_2026_0415_BGGM_DAG_Integration_Visualization.Rmd` | BGGM x DAG integration |
| **Figure 6** (indirect-pathway alluvial) | `R/GRF_project_2026_0415_BGGM_DAG_Integration_Visualization.Rmd` | `ggalluvial` |
| Methods "Missing data" (missForest OOB NRMSE/PFC); imputation-check table | `R/GRF_project_2026_0413_SEM-bggm-dag-revised-clean.Rmd` | `missForest` ntree=500 |
| Methods "Psychometric evaluation"; reliability / CFA tables | `R/GRF_project_2026_0413_CronbachMcDonalds.Rmd` | `psych` alpha/omega, `lavaan::cfa` ML |
| Methods "A natural experiment and data" (Kruskal-Wallis, ICC); balance-test table | `python/balance_test/balance-test-ses.ipynb` | `scipy.stats.kruskal`; hand-coded one-way ICC(1) |
| Aggregate SEM results (Results); mediation tables | `R/GRF_project_2026_0413_SEM-bggm-dag-revised-clean.Rmd` | `lavaan` |
| Item-level partial correlations (Results); association tables | `R/GRF_project_2026_0415_bggm.Rmd` | `BGGM` posterior mean partial correlations |
| DAG threshold sensitivity | `R/GRF_project_2026_0424_DAG.Rmd` | `bnlearn` |
| Network stability (CS-coefficient, case-dropping) | `R/GRF_project_2026_0424_DAG.Rmd` | `bootnet` EBICglasso |

Figure 7 (public-housing map) is a presentational GIS rendering with no statistical
analysis; its rendering code is not part of this repository. Data sources for that map are
attributed in the figure caption.

## Reporting Summary — "Software and code > Data analysis"

Cite from this repo:

- **R** (version in `SESSION_INFO.md`): `lavaan`, `BGGM`, `bnlearn`, `bootnet`,
  `missForest`, `psych`, `networktools`, `qgraph` (versions in `SESSION_INFO.md`;
  versions of record: lavaan 0.6, BGGM 2.1.1).
- **Python** (version in `SESSION_INFO.md`): `pandas`, `numpy`, `scipy` for the
  covariate-balance test.

Point the box at this repository URL and note that full package versions / session
information are in `SESSION_INFO.md`, `sessionInfo_R.txt`, and `installed_packages.csv`.
