# Analysis code — *A natural experiment in public housing and resident health*

This repository contains the analysis code for the manuscript submitted to *Nature Cities*
(Paper 1, Environment–Lifestyle–Health framework). It is provided to satisfy the Nature
Portfolio code-availability policy and to allow editors, reviewers, and readers to inspect
and reproduce the analytical pipeline.

- **Corresponding author:** B. Jiang
- **Code author:** X. Liu
- **License:** MIT (see `LICENSE`)

## Scope

This repository contains only the code that produces results reported in the manuscript:
the R scripts for reliability/CFA, SEM mediation, BGGM networks, the DAG and stability
analyses, and the integrated Figure 5 / Figure 6; and the Python notebook for the
covariate-balance test (Kruskal–Wallis and ICC). Purely presentational figure rendering
(e.g. the Figure 7 map) and exploratory analyses that do not appear in the manuscript are
not included.

## What is and is not included

| Included | Not included |
|---|---|
| R analysis scripts (reliability/CFA, SEM mediation, BGGM networks, DAG, Fig 5/6 integration) | Participant-level survey data |
| Python notebook for the covariate-balance test (Kruskal–Wallis, ICC) | Figure 7 map-rendering code; exploratory notebooks not cited in the manuscript |
| Environment record (`SESSION_INFO.md`, `sessionInfo_R.txt`, `installed_packages.csv`, `requirements.txt`) | Intermediate/`Processed` data and rendered `Output/` |

Participant data are not publicly available because consent did not cover open
release. Access requests: see `docs/data-access.md`. All scripts run against files under a
local `Data/` tree with the structure documented in `docs/pipeline.md`; qualified
researchers who obtain the data can reproduce every reported result.

## Repository layout

```
R/                                  R analysis scripts (RMarkdown)
  GRF_project_2026_0413_CronbachMcDonalds.Rmd          reliability + CFA
  GRF_project_2026_0413_SEM-bggm-dag-revised-clean.Rmd data cleaning, missForest, SEM mediation
  GRF_project_2026_0415_bggm.Rmd                       BGGM network estimation, bridge centrality
  GRF_project_2026_0424_DAG.Rmd                        PC-stable DAG, stability analyses
  GRF_project_2026_0415_BGGM_DAG_Integration_Visualization.Rmd  Figure 5 heatmap / Figure 6 alluvial
python/
  balance_test/balance-test-ses.ipynb   covariate-balance test (Kruskal-Wallis, ICC)
docs/
  pipeline.md                       execution order + input/output map
  manuscript-map.md                 script -> figure / table / Reporting Summary crosswalk
  data-access.md                    how to request the participant data
  R-environment.md                  how to restore the R package environment
tools/capture_environment.R         regenerate sessionInfo_R.txt / installed_packages.csv
requirements.txt                    Python dependencies (pin before archiving; see file header)
SESSION_INFO.md                     software versions (R + Python)
sessionInfo_R.txt                   full sessionInfo() from the analysis machine
installed_packages.csv              full R package inventory of the analysis machine
CITATION.cff
```

## Quick start

1. Obtain the data (see `docs/data-access.md`) and place it under `Data/` following
   `docs/pipeline.md`.
2. **R** — R 4.4.x. Install the packages listed in `SESSION_INFO.md` (full machine
   inventory in `installed_packages.csv`, full `sessionInfo()` in `sessionInfo_R.txt`).
   See `docs/R-environment.md`.
3. **Python** (>= 3.10) — `pip install -r requirements.txt` for the covariate-balance
   notebook (needs only pandas, numpy, scipy, openpyxl).
4. Run the scripts in the order given in `docs/pipeline.md`.

## Reproducibility notes

- Random seeds are set inside each bootstrap/MCMC step; re-running reproduces the reported
  point estimates and intervals.
- Package versions used for the submitted analyses are the "versions of record" in
  `SESSION_INFO.md` (lavaan 0.6, BGGM 2.1.1, as stated in the manuscript Methods). The
  committed `sessionInfo_R.txt` is a later snapshot of the same machine; see the note in
  `SESSION_INFO.md`.
- The scripts were reviewed for hardcoded local paths and credentials before release; none
  remain. Python notebook outputs were cleared. Report anything that looks machine-specific
  as an issue.
