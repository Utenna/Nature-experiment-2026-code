# Analysis code — *A natural experiment in public housing and resident health*

This repository contains the analysis code for the manuscript submitted to *Nature Cities*
(Paper 1, Environment–Lifestyle–Health framework). It is provided to satisfy the Nature
Portfolio code-availability policy and to allow editors, reviewers, and readers to inspect
and reproduce the analytical pipeline.

- **Corresponding author:** B. Jiang
- **Code author:** X. Liu
- **License:** MIT (see `LICENSE`)

## Scope

This repository is the Code Ocean reproduction capsule (`codeocean_capsule/`): scripts for
the covariate-balance test, between-estate ICC, scale reliability/CFA, parallel-mediation
SEM, Bayesian Gaussian Graphical Models (BGGM), and the PC-stable DAG with bootstrap
stability, run against **de-identified** data shipped in the capsule. Purely presentational
figure rendering (Figures 5-6, which visualize the BGGM/DAG results these scripts already
produce, and the Figure 7 map) and exploratory analyses that do not appear in the
manuscript are not included.

## What is and is not included

| Included | Not included |
|---|---|
| Capsule R/Python scripts (`codeocean_capsule/code/`): balance test, ICC, reliability/CFA, SEM mediation, BGGM networks, PC-stable DAG | Participant-level raw survey data |
| De-identified data sufficient to reproduce every reported statistic (`codeocean_capsule/data/` — **not published to this git repo**, peer-review reproduction only, see below) | Figure 5/6 and Figure 7 presentational rendering code (visualizes the statistics the included scripts produce; no separate analysis); exploratory notebooks not cited in the manuscript |
| Environment record (`codeocean_capsule/environment/`, `SESSION_INFO.md`, `sessionInfo_R.txt`, `installed_packages.csv`, `requirements.txt`) | Intermediate/reproduced `results/` and `validation/` comparison outputs (regenerate by running the capsule) |

Participant data are not publicly available because consent did not cover open
release. Access requests: see `docs/data-access.md`. The capsule ships de-identified data
that reproduces every reported statistic, but that data is restricted to peer-review
reproduction and is **git-ignored** in this repository — see
`codeocean_capsule/data/README.md` and `.gitignore`. Qualified researchers who obtain the
restricted raw data can also reproduce every result from scratch; see
`docs/pipeline.md`.

## Repository layout

```
codeocean_capsule/
  README.md                         capsule overview, layout, run instructions
  UPLOAD_CHECKLIST.md                Code Ocean submission checklist
  code/
    run                              entry point (bash); orchestrates steps 01-05
    paths.py / paths.R               /data (read-only in) and /results (out) shims
    00_prepare_deidentified_data.py  PROVENANCE ONLY — how data/ was built; not run by `run`
    01_balance_test.py               covariate balance test -> Supplementary Table S12
    02_icc_check.R                   between-estate ICC on the analysis sample
    03_reliability_cfa.R             Cronbach alpha / McDonald omega + CFA fit
    04_sem_mediation.R               parallel-mediation SEM (lavaan, bootstrap) -> Figure 2
    05_bggm_network.R                Bayesian Gaussian Graphical Models -> Figure 3
    06_dag.md                        PC-stable DAG + stability -- SOURCE ONLY, not run by `run`
                                      (~30 h at published settings; see the file for why/how)
    lib/00_load.R                    rebuilds analysis frames from data_analysis.csv
  data/                              de-identified data (git-ignored, not in this repo — see below)
  environment/                       Dockerfile, install.R, requirements.txt, sessionInfo_R.txt
  metadata/metadata.yml              Code Ocean capsule metadata
  results/, validation/              run outputs + comparison against published numbers
                                      (git-ignored; regenerate by running the capsule)
docs/
  pipeline.md                        execution order + input/output map
  manuscript-map.md                  script -> figure / table / Reporting Summary crosswalk
  data-access.md                     how to request the restricted raw participant data
  R-environment.md                   how to restore the R + Python package environment
tools/capture_environment.R          regenerate sessionInfo_R.txt / installed_packages.csv
requirements.txt                     legacy root Python pin (see codeocean_capsule/environment/requirements.txt for the capsule's own pin)
SESSION_INFO.md                      software versions (R + Python)
sessionInfo_R.txt                    full sessionInfo() from the analysis machine
installed_packages.csv               full R package inventory of the analysis machine
CITATION.cff
```

## Quick start

1. The capsule ships de-identified data sufficient to reproduce every reported statistic
   (`codeocean_capsule/data/`, git-ignored — restricted to peer-review reproduction, do not
   redistribute; see `codeocean_capsule/data/README.md`). To instead work from the raw
   participant data, request access per `docs/data-access.md` and see `docs/pipeline.md`
   for how `00_prepare_deidentified_data.py` derives the capsule's data.
2. **R** — R 4.4.x. Install the packages listed in `SESSION_INFO.md` (full machine
   inventory in `installed_packages.csv`, full `sessionInfo()` in `sessionInfo_R.txt`; the
   capsule keeps its own copies under `codeocean_capsule/environment/`). See
   `docs/R-environment.md`.
3. **Python** (>= 3.10) — `pip install -r codeocean_capsule/environment/requirements.txt`
   (pandas, numpy, scipy for steps 01; openpyxl/pyreadr/jupyter are only needed for the
   provenance-only `00_prepare_deidentified_data.py`).
4. Run `bash codeocean_capsule/code/run` (steps 01-05; `QUICK=0` for published-precision
   resampling, ~5 h) or the scripts individually in the order given in `docs/pipeline.md`.
   Step 06 (DAG + stability) is documentation-only (`code/06_dag.md`) because published
   settings take ~30 h; see that file for how to run it.

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
- `codeocean_capsule/validation/` holds cell-by-cell comparisons of the capsule's reproduced
  values against the published numbers (steps 01/02 exit non-zero on any unexplained
  mismatch; 05 matches to ≤0.001; 06 Mental Health PHASE 2 matches exactly). These
  comparison files are regenerated by running the capsule and are git-ignored.
