# Script -> manuscript output crosswalk

| Manuscript element | Script | Method / package |
|---|---|---|
| **Figure 2** (SEM mediation) | `codeocean_capsule/code/04_sem_mediation.R` | `lavaan` parallel mediation, ML, 5000 bootstrap, BC 95% CI |
| **Figure 3** (BGGM networks) | `codeocean_capsule/code/05_bggm_network.R` | `BGGM`, `networktools` (Bridge Expected Influence) |
| **Figure 4** (partially directed acyclic graphs) | `codeocean_capsule/code/06_dag.md` (source only — see file for why it isn't run by `code/run`) | `bnlearn` PC-stable, `boot.strength` R=500 |
| **Figure 5** (direct-pathway heatmap) | presentational visualization of `05_bggm_network.R` x `06_dag.md` outputs; no separate script (see note below) | BGGM x DAG integration |
| **Figure 6** (indirect-pathway alluvial) | presentational visualization of the same outputs; no separate script (see note below) | `ggalluvial` |
| Methods "Missing data" (missForest OOB NRMSE/PFC); imputation-check table | documented in `codeocean_capsule/code/00_prepare_deidentified_data.py` (provenance only); `data_analysis.csv` ships post-imputation | `missForest` ntree=500 |
| Methods "Psychometric evaluation"; reliability / CFA tables | `codeocean_capsule/code/03_reliability_cfa.R` | `psych` alpha/omega, `lavaan::cfa` ML |
| Methods "A natural experiment and data" (Kruskal-Wallis, ICC); balance-test table | `codeocean_capsule/code/01_balance_test.py`, `codeocean_capsule/code/02_icc_check.R` | `scipy.stats.kruskal`; ICC(1) |
| Aggregate SEM results (Results); mediation tables | `codeocean_capsule/code/04_sem_mediation.R` | `lavaan` |
| Item-level partial correlations (Results); association tables | `codeocean_capsule/code/05_bggm_network.R` | `BGGM` posterior mean partial correlations |
| DAG threshold sensitivity | `codeocean_capsule/code/06_dag.md` | `bnlearn` |
| Network stability (CS-coefficient, case-dropping) | `codeocean_capsule/code/06_dag.md` | `bootnet` EBICglasso |

Figures 5 and 6 visualize results already produced by `05_bggm_network.R` and
`06_dag.md` (no separate statistical analysis), so their rendering code is not part of
this repository — same treatment as Figure 7 (public-housing map), a presentational GIS
rendering with no statistical analysis whose sources are attributed in its figure caption.

## Reporting Summary — "Software and code > Data analysis"

Cite from this repo:

- **R** (version in `SESSION_INFO.md`): `lavaan`, `BGGM`, `bnlearn`, `bootnet`,
  `missForest`, `psych`, `networktools`, `qgraph` (versions in `SESSION_INFO.md`;
  versions of record: lavaan 0.6, BGGM 2.1.1).
- **Python** (version in `SESSION_INFO.md`): `pandas`, `numpy`, `scipy` for the
  covariate-balance test.

Point the box at this repository URL and note that full package versions / session
information are in `SESSION_INFO.md`, `sessionInfo_R.txt`, and `installed_packages.csv`
(capsule-specific copies under `codeocean_capsule/environment/`).
