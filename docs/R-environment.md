# Restoring the R environment

The analyses used **R 4.4.x** (the analysis machine ran 4.4.3 on Windows).

Package versions:

- **Versions of record** (manuscript Methods): lavaan 0.6, BGGM 2.1.1.
- Full inventory of the analysis machine: `../installed_packages.csv`.
- Full `sessionInfo()` from the analysis machine: `../sessionInfo_R.txt`.
- Headline list with roles: `../SESSION_INFO.md`.

No `renv.lock` is provided. `renv::init()` on this project stalls because it tries to
build a project-private library from the full dependency tree of the manuscript `.qmd`
files as well as the analysis scripts; the environment records above serve the same
purpose for reproduction.

## Manual install

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

## Running the scripts

The `.Rmd` files are analysis scripts, not reports. Run them in RStudio with the working
directory at the project root (they use `here::here()`), or `rmarkdown::render()` each in
the order given in `pipeline.md`. Each bootstrap/MCMC block sets its own seed.
