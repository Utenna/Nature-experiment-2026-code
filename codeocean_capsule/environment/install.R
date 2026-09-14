# =============================================================================
# R packages for the Code Ocean "Reproducible Run".
# Target: R 4.4.3 (from the analysis machine's sessionInfo_R.txt, in this folder).
#
# Versions below are the ones actually used for the published analysis
# (sessionInfo_R.txt / installed_packages.csv — 567 pkgs — are the authoritative
# record and are shipped alongside this file).
#
# PREFERRED for exact reproduction: replace this with `renv::restore()` against a
# committed renv.lock generated on the analysis machine. Until then this pins the
# analysis-critical packages by version and resolves the rest from a dated
# snapshot (Dockerfile ARG SNAPSHOT_DATE).
# =============================================================================
options(warn = 2)
repos <- getOption("repos")
if (is.null(repos[["CRAN"]]) || repos[["CRAN"]] == "@CRAN@")
  repos["CRAN"] <- "https://packagemanager.posit.co/cran/latest"
options(repos = repos)

install.packages("remotes")

pinned <- c(
  Matrix       = "1.7-2",
  Rcpp         = "1.0.12",
  lavaan       = "0.6-18",   # SEM parallel mediation (ML, bootstrap)
  BGGM         = "2.1.3",    # Bayesian Gaussian Graphical Models + Bayesian R^2
  bnlearn      = "5.0.1",    # PC-stable DAG, boot.strength
  bootnet      = "1.6",      # case-dropping bootstrap, EBICglasso, CS-coefficient
  networktools = "1.5.2",    # bridge Expected Influence
  qgraph       = "1.9.8",
  igraph       = "2.0.3",
  glasso       = "1.11",
  corpcor      = "1.6.10",
  psych        = "2.4.6.26", # Cronbach alpha / McDonald omega + CFA helper
  mgm          = "1.2-14",
  lme4         = "1.1-35.4", # 02_icc_check.R null-model cross-check
  performance  = "0.12.3",
  missForest   = "1.6.1",    # only for 00_prepare regeneration
  dplyr        = "1.1.4",
  tidyr        = "1.3.1",
  tibble       = "3.2.1",
  stringr      = "1.5.1",
  here         = "1.0.1"
)

for (pkg in names(pinned)) {
  if (requireNamespace(pkg, quietly = TRUE) &&
      identical(as.character(utils::packageVersion(pkg)), pinned[[pkg]])) next
  message("install_version: ", pkg, " ", pinned[[pkg]])
  remotes::install_version(pkg, version = pinned[[pkg]], upgrade = "never")
}

invisible(lapply(names(pinned), function(p)
  if (!requireNamespace(p, quietly = TRUE)) stop("missing after install: ", p)))
message("install.R: OK  (R ", getRversion(), ")")
