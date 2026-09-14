# Path shim for the Code Ocean capsule (R side).
#
# Sourced by every analysis script AFTER it has set `CODE_DIR` to the absolute
# path of this capsule's code/ directory (the scripts do this with a small
# file.exists() search, so it works whether you run via `code/run`, `Rscript`,
# or `source()` from the console).
#
# Code Ocean mounts data read-only at /data and expects results in /results.
# Locally you can override with the CO_DATA / CO_RESULTS environment variables;
# otherwise this falls back to the capsule's own data/ and results/ folders.

if (!exists("CODE_DIR")) {
  .p <- Filter(file.exists, c("paths.R", "code/paths.R",
                              "codeocean_capsule/code/paths.R",
                              "../code/paths.R", "/code/paths.R"))
  if (!length(.p)) stop("paths.R: set CODE_DIR, or setwd() into codeocean_capsule/code/")
  CODE_DIR <- normalizePath(dirname(.p[1]))
}
.capsule_root <- normalizePath(file.path(CODE_DIR, ".."), mustWork = FALSE)

DATA_DIR <- Sys.getenv("CO_DATA", unset = NA)
if (is.na(DATA_DIR) || DATA_DIR == "")
  DATA_DIR <- if (dir.exists("/data")) "/data" else file.path(.capsule_root, "data")

RESULTS_DIR <- Sys.getenv("CO_RESULTS", unset = NA)
if (is.na(RESULTS_DIR) || RESULTS_DIR == "")
  RESULTS_DIR <- if (dir.exists("/results")) "/results" else file.path(.capsule_root, "results")

DATA_DIR    <- normalizePath(DATA_DIR,    mustWork = FALSE)
RESULTS_DIR <- normalizePath(RESULTS_DIR, mustWork = FALSE)
dir.create(RESULTS_DIR, showWarnings = FALSE, recursive = TRUE)

data_path    <- function(...) file.path(DATA_DIR, ...)
results_path <- function(...) file.path(RESULTS_DIR, ...)

if (!file.exists(data_path("data_analysis.csv")))
  warning("paths.R: ", data_path("data_analysis.csv"), " not found — check CO_DATA / working dir.")
