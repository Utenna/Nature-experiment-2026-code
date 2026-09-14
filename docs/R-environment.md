# Restoring the R + Python environment

The analyses used **R 4.4.x** (the analysis machine ran 4.4.3 on Windows) and
**Python 3.13.2** for the covariate-balance test.

Package versions:

- **Versions of record** (manuscript Methods): lavaan 0.6, BGGM 2.1.1.
- Capsule-pinned R packages (exact versions used for the Code Ocean run):
  `codeocean_capsule/environment/install.R`.
- Capsule Python pin: `codeocean_capsule/environment/requirements.txt`
  (pandas 2.3.1, numpy 2.3.1, scipy 1.16.0).
- Docker image used for the Reproducible Run: `codeocean_capsule/environment/Dockerfile`.
- Full inventory of the analysis machine: `installed_packages.csv` (root) /
  `codeocean_capsule/environment/installed_packages.csv` (capsule copy).
- Full `sessionInfo()` from the analysis machine: `sessionInfo_R.txt` (root) /
  `codeocean_capsule/environment/sessionInfo_R.txt` (capsule copy).
- Headline list with roles: `SESSION_INFO.md`.

No `renv.lock` is provided. `renv::init()` on this project stalls because it tries to
build a project-private library from the full dependency tree of the manuscript `.qmd`
files as well as the analysis scripts; the environment records above serve the same
purpose for reproduction.

## Recommended: capsule install script

```r
source("codeocean_capsule/environment/install.R")
```

This pins the analysis-critical packages at the versions used for the published run
(`lavaan 0.6-18`, `BGGM 2.1.3`, `bnlearn 5.0.1`, `bootnet 1.6`, `networktools 1.5.2`,
`qgraph 1.9.8`, `psych 2.4.6.26`, `mgm 1.2-14`, plus supporting packages) via
`remotes::install_version()`.

## Manual install (broader package list, matches the original analysis machine)

```r
install.packages(c(
  "lavaan", "BGGM", "bnlearn", "bootnet", "missForest", "psych",
  "networktools", "qgraph", "mgm",
  "tidyverse", "here", "openxlsx", "bruceR",
  "ggplot2", "ggalluvial", "ggridges", "corrplot",
  "patchwork", "gridExtra", "scales", "reshape2"
))
```

To match the reported analyses exactly, install the two named packages at their versions
of record:

```r
remotes::install_version("lavaan", version = "0.6")     # or the 0.6.x used; see note below
remotes::install_version("BGGM",   version = "2.1.1")
```

(The manuscript states lavaan "v0.6"; the analysis machine currently has 0.6.18. Use the
0.6.x series.)

## Python

```bash
pip install -r codeocean_capsule/environment/requirements.txt
```

Only pandas, numpy, and scipy are needed to run `01_balance_test.py`. openpyxl / pyreadr /
jupyter are only needed for the provenance-only `00_prepare_deidentified_data.py`.

## Running the scripts

`codeocean_capsule/code/*.R` and `*.py` are plain scripts, not reports — run
`bash codeocean_capsule/code/run` for the whole pipeline, or each script individually in
the order given in `pipeline.md`. They use the `paths.R` / `paths.py` shims to locate
`codeocean_capsule/data/` and write to `codeocean_capsule/results/`; no
`setwd()`/`here::here()` project-root assumption is needed beyond running from
`codeocean_capsule/code/`. Each bootstrap/MCMC block sets its own seed.
