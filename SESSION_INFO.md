# Computational environment

This records the software used for the analyses in the manuscript. It also feeds the
Nature Reporting Summary "Software and code > Data analysis" box.

## Versions of record (as reported in the manuscript Methods)

These are the versions under which the reported estimates were produced:

| Component | Version | Used for |
|---|---|---|
| R | 4.4.x | all analyses except covariate balance |
| lavaan | 0.6 | CFA + SEM parallel mediation (ML, 5000 bootstrap, bias-corrected 95% CI) |
| BGGM | 2.1.1 | Bayesian Gaussian Graphical Models + Bayesian R2 node predictability |
| Python | 3.x | covariate-balance test (Kruskal-Wallis, ICC) |

## Full environment snapshot

Files committed alongside this document:

- `sessionInfo_R.txt` — output of `sessionInfo()` on the analysis machine (R 4.4.3, Windows).
- `installed_packages.csv` — every R package installed on that machine, with versions.

The capsule (`codeocean_capsule/environment/`) keeps its own copies of both, plus a
version-pinned `install.R` and a Python `requirements.txt` — those are what the Code
Ocean Reproducible Run actually installs from; see `docs/R-environment.md`.

Note: this snapshot was taken after submission. Some packages had been updated on the
machine in the interim (e.g. `sessionInfo_R.txt` shows lavaan 0.6.18 and BGGM 2.1.3),
whereas the analyses reported in the manuscript were run under the "versions of record"
above (lavaan 0.6, BGGM 2.1.1). Package version drift of this size does not affect the
reported results; re-running under either version reproduces the point estimates and
intervals.

## R packages (from the analysis machine)

```
R version 4.4.3 (2025-02-28 ucrt) — Windows

lavaan        0.6.18    # CFA + SEM parallel mediation      (manuscript: 0.6)
BGGM          2.1.3     # Bayesian Gaussian Graphical Models (manuscript: 2.1.1)
bnlearn       5.0.1     # PC-stable DAG via boot.strength (500 resamples)
bootnet       1.6       # network accuracy / case-dropping bootstrap / EBICglasso / CS-coefficient
missForest    1.6.1     # random-forest missing-data imputation (ntree = 500)
psych         2.4.6.26  # Cronbach alpha, McDonald omega, descriptive statistics
networktools  1.5.2     # Bridge Expected Influence centrality
qgraph        1.9.8     # network visualisation
mgm           1.2.14    # loaded in the network scripts
tidyverse     2.0.0     # data management (dplyr, tidyr, stringr, ...)
here          1.0.1
openxlsx      4.2.7.1
bruceR        2024.6    # data import helper
ggplot2       4.0.2
ggalluvial    0.12.6    # indirect-pathway alluvial diagram (Fig 6)
ggridges      0.5.6
corrplot      0.94
patchwork     1.3.0
gridExtra     2.3
scales        1.4.0
reshape2      1.4.4
```

(ggbump is not installed on this machine and is not required to reproduce the reported
results; remove it from any dependency list.)

## Python packages

Only the covariate-balance script (`codeocean_capsule/code/01_balance_test.py`) is in
this repository; it imports `pandas`, `numpy`, `scipy` and reads `data/data_balance.csv`.
The one-way ICC(1) is a hand-coded function in the script (no extra package).
`codeocean_capsule/code/00_prepare_deidentified_data.py` (provenance only, not run by
`code/run`) additionally uses `openpyxl`/`pyreadr` to read the original `.xlsx`/`.RData`.

Captured from the analysis kernel (`import x; x.__version__`):

```
Python 3.13.2

pandas      2.3.1
numpy       2.3.1
scipy       1.16.0     # scipy.stats.kruskal
openpyxl    3.1.5      # read_excel backend
et_xmlfile  2.0.0      # openpyxl dependency
```

The manuscript does not state Python package versions; the above is a snapshot of the
current analysis environment and reproduces the reported covariate-balance statistics.
