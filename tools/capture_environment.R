# capture_environment.R
# -----------------------------------------------------------------------------
# Run this ONCE, in the ORIGINAL analysis project (Nature-experiment-2026.Rproj),
# from the RStudio Console:
#
#     source("path/to/Nature-experiment-2026-code/tools/capture_environment.R")
#
# It (1) loads the packages the analysis uses, (2) writes full sessionInfo() to
# sessionInfo_R.txt, and (3) prints a compact package-version table to paste into
# SESSION_INFO.md. Optionally also snapshots an renv.lock if renv is set up.
# -----------------------------------------------------------------------------

analysis_pkgs <- c(
  "lavaan", "BGGM", "bnlearn", "bootnet", "missForest", "psych",
  "networktools", "qgraph", "mgm",
  "tidyverse", "here", "openxlsx", "bruceR",
  "ggplot2", "ggalluvial", "ggbump", "ggridges", "corrplot",
  "patchwork", "gridExtra", "scales", "reshape2"
)

loaded <- suppressWarnings(suppressMessages(
  vapply(analysis_pkgs, requireNamespace, logical(1), quietly = TRUE)
))
for (p in names(loaded)[loaded]) suppressPackageStartupMessages(library(p, character.only = TRUE))

if (any(!loaded)) {
  message("Not installed (adjust list or install): ",
          paste(names(loaded)[!loaded], collapse = ", "))
}

# 1. full session info
out_file <- file.path(getwd(), "sessionInfo_R.txt")
writeLines(capture.output(sessionInfo()), out_file)
message("Wrote ", out_file)

# 2. compact table for SESSION_INFO.md
ver <- data.frame(
  package = names(loaded)[loaded],
  version = vapply(names(loaded)[loaded],
                   function(p) as.character(utils::packageVersion(p)),
                   character(1)),
  row.names = NULL
)
cat("\nR:", R.version.string, "\n\n")
print(ver, right = FALSE)

# 3. optional renv snapshot (only if the project already uses renv)
if (requireNamespace("renv", quietly = TRUE) &&
    file.exists(file.path(getwd(), "renv"))) {
  renv::snapshot(prompt = FALSE)
  message("renv.lock updated.")
} else {
  message("renv not initialised here. To create a lockfile: install.packages('renv'); renv::init()")
}
