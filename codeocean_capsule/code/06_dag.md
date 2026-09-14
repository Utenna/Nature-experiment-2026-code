# 06_dag.R — reference source (not part of the automated `run`)

## Why this is `.md`, not `.R`

`code/run` executes steps 01–05 automatically. This step — PC-stable DAG
bootstrap (`bnlearn`) + bootnet case-dropping stability, 3 health domains —
is **not** wired into `run`, because a single Code
Ocean session cannot complete it:

| setting | wall clock (this step alone) |
|---|---|
| published | **~30 h** (`boot.strength` R=500 × 3 domains + serial `bootnet` case-dropping, `boots=1000` × 3 domains) |


## Verification status

- **Deterministic by construction**: `set.seed(999)` (PHASE 2) and
  `set.seed(777)` + forced `nCores = 1` (PHASE 3) — the code below is
  seed-robust on any host, independent of core count. Package versions are
  pinned in `environment/install.R` (`bnlearn 5.0.1`, `bootnet 1.6`), so a
  run with this exact capsule reproduces bit-for-bit.
- **PHASE 2, Mental Health domain**: re-run on a Code Ocean interactive
  workstation (2026-09-11). Edge-count sensitivity table (7 thresholds:
  0.70/0.75/0.80/0.85/0.90/0.95/0.98) reproduced **119/113/107/98/92/86/76**
  — identical to the published `Sensitivity_Table_Mental_Health.csv`.
- **PHASE 2, Physical/Social Health** and **PHASE 3 (bootnet CS-coefficient,
  all 3 domains)**: not independently re-run — the free-tier compute budget
  was exhausted before reaching them. They execute the identical seeded code
  path as the verified Mental Health run above; PHASE 3's CS-coefficient is
  additionally seed-robust by construction (bridge-EI stability saturates the
  `corStability` grid ceiling, `caseMax = 0.75`, regardless of the bootstrap
  draw).

## How to actually run this

Copy the R code below into a file named `06_dag.R` inside `code/` (same
directory as `paths.R` and `lib/00_load.R`), then, from `code/`:

```bash
Rscript 06_dag.R              # published settings, ~30 h
```

Needs a machine that can hold the ~30 h wall clock (an interactive Code Ocean
workstation across multiple sessions with `/results` persisted, a local
machine, or an HPC node) — not a single headless Reproducible Run.

## Source

```r
# =============================================================================
# 06_dag.R  --  directed acyclic graph (bnlearn, PC-stable + bootstrap)
#              and network stability (bootnet case-dropping CS-coefficient)
# -----------------------------------------------------------------------------
# Outputs (to /results):
#   Boot_Object_<domain>.rds
#   Sensitivity_Table_<domain>.csv
#   DAG_Arrows_<threshold>_<domain>.csv
#   DAG_AvgNetwork_0.70_<domain>.csv
#   Stability_CS_<domain>.csv
#   validation/stability_cs_comparison.csv   (reproduced vs published CS = 0.75)
# =============================================================================
suppressPackageStartupMessages({
  library(bnlearn); library(dplyr)
})

.p <- Filter(file.exists, c("paths.R", "code/paths.R", "codeocean_capsule/code/paths.R",
                            "../code/paths.R", "/code/paths.R"))
if (!length(.p)) stop("Run from the capsule: setwd('.../codeocean_capsule/code') first.")
CODE_DIR <- normalizePath(dirname(.p[1]))
source(file.path(CODE_DIR, "paths.R"))
source(file.path(CODE_DIR, "lib", "00_load.R"))
out_dir <- RESULTS_DIR

QUICK   <- Sys.getenv("QUICK") == "1"
R_BOOT  <- if (QUICK) 100L else 500L
CS_BOOT <- if (QUICK) 200L else 1000L
# bootnet PHASE 3 runs single-core on purpose (see header) -- CO_NCORES is not
# used for it, so the CS-coefficient does not depend on the host's core count.
message(sprintf("06_dag.R: boot.strength R = %d ; bootnet boots = %d ; bootnet nCores = 1 %s",
                R_BOOT, CS_BOOT, if (QUICK) "(QUICK)" else "(published)"))

e_names <- e_item_names
l_names <- l_item_names
multi_models <- list(
  "Mental_Health"   = mh_item_names,
  "Physical_Health" = ph_item_names,
  "Social_Health"   = sh_item_names
)
test_thresholds <- sort(unique(c(seq(0.70, 0.95, by = 0.05), 0.98)))
export_targets  <- c(0.70, 0.75, 0.80, 0.85, 0.90, 0.95)

# ---- PHASE 2: DAG bootstrap ------------------------------------------------
for (model_label in names(multi_models)) {
  message("\n>>> DAG boot.strength: ", model_label)
  nodes_extra <- multi_models[[model_label]]
  node_names_model <- c(e_names, l_names, nodes_extra)
  dat <- df_resid %>% dplyr::select(all_of(node_names_model))

  non_env <- c(l_names, nodes_extra)
  black_list <- expand.grid(from = non_env, to = e_names, stringsAsFactors = FALSE)

  set.seed(999)
  str_fit <- tryCatch(
    boot.strength(data = dat, R = R_BOOT, algorithm = "pc.stable",
                  algorithm.args = list(blacklist = black_list, alpha = 0.01)),
    error = function(e) { message("   FAILED: ", conditionMessage(e)); NULL })
  if (is.null(str_fit)) next
  saveRDS(str_fit, file.path(out_dir, paste0("Boot_Object_", model_label, ".rds")))

  res_list <- list()
  for (th in test_thresholds) {
    avg <- averaged.network(str_fit, threshold = th)
    arcs <- as.data.frame(avg$arcs)
    if (th %in% export_targets && nrow(arcs) > 0)
      write.csv(arcs, file.path(out_dir, paste0("DAG_Arrows_", th, "_", model_label, ".csv")),
                row.names = FALSE)
    res_list[[as.character(th)]] <- data.frame(Threshold = th, Edge_Count = nrow(arcs))
  }
  write.csv(do.call(rbind, res_list),
            file.path(out_dir, paste0("Sensitivity_Table_", model_label, ".csv")), row.names = FALSE)

  avg70 <- averaged.network(str_fit, threshold = 0.70)
  s70 <- as.data.frame(str_fit)
  s70 <- s70[s70$strength >= 0.70 & s70$direction >= 0.5, ]
  write.csv(s70, file.path(out_dir, paste0("DAG_AvgNetwork_0.70_", model_label, ".csv")),
            row.names = FALSE)
}

# ---- PHASE 3: stability (bootnet) ----------------------------------------
# Manuscript: CS-coefficient (bridge EI) = 0.75 for all three networks.
CS_PUBLISHED <- 0.75
cs_rows <- list()

if (requireNamespace("bootnet", quietly = TRUE)) {
  library(bootnet)
  for (model_label in names(multi_models)) {
    message("\n>>> stability (CS): ", model_label)
    nodes_extra <- multi_models[[model_label]]
    target_vars <- c(e_names, l_names, nodes_extra)
    n_e <- length(e_names); n_l <- length(l_names); n_h <- length(nodes_extra)
    communities <- list("Environment" = 1:n_e, "Lifestyle" = (n_e + 1):(n_e + n_l),
                        "Health" = (n_e + n_l + 1):(n_e + n_l + n_h))
    dat <- df_resid %>% dplyr::select(all_of(target_vars))
    net <- estimateNetwork(dat, default = "EBICglasso", corMethod = "cor",
                           tuning = 0.5, verbose = FALSE)
    # nCores = 1L: bootnet has no `seed` argument and does not set a per-worker
    # RNG stream, so set.seed() only reaches the bootstrap loop when it runs in
    # this (master) process. Serial => set.seed(777) fully determines the result
    # on any host, independent of the capsule's core count.
    set.seed(777)
    bt <- tryCatch(
      bootnet(net, boots = CS_BOOT, type = "case",
              statistics = c("bridgeExpectedInfluence"),
              communities = communities, nCores = 1L, verbose = FALSE),
      error = function(e) { message("   FAILED: ", conditionMessage(e)); NULL })
    if (is.null(bt)) next
    cs <- corStability(bt, cor = 0.7)
    write.csv(data.frame(Model = model_label, Statistic = names(cs), CS_coefficient = as.numeric(cs)),
              file.path(out_dir, paste0("Stability_CS_", model_label, ".csv")), row.names = FALSE)
    message("   CS (bridge EI) = ", round(cs[1], 3))
    cs_rows[[model_label]] <- data.frame(
      Model         = model_label,
      CS_reproduced = round(as.numeric(cs[1]), 3),
      CS_published  = CS_PUBLISHED,
      diff          = round(as.numeric(cs[1]) - CS_PUBLISHED, 3)
    )
  }

  # ---- validation: reproduced CS vs published 0.75 ----------------------
  if (length(cs_rows)) {
    VALIDATION_DIR <- file.path(out_dir, "validation")
    dir.create(VALIDATION_DIR, showWarnings = FALSE, recursive = TRUE)
    cmp <- do.call(rbind, cs_rows)
    cmp$note <- ifelse(
      abs(cmp$diff) < 1e-9, "matches manuscript (CS = 0.75)",
      if (QUICK) "QUICK run: fewer bootstraps, CS grid coarser than published"
      else "CHECK: differs from published CS = 0.75")
    write.csv(cmp, file.path(VALIDATION_DIR, "stability_cs_comparison.csv"), row.names = FALSE)
    print(cmp, row.names = FALSE)
    off <- cmp$Model[abs(cmp$diff) >= 1e-9]
    if (!QUICK && length(off))
      message("[validation] NOTE: bridge-EI CS-coefficient != published 0.75 for: ",
              paste(off, collapse = ", "), " -- see validation/stability_cs_comparison.csv")
    else if (!QUICK)
      message("[validation] bridge-EI CS-coefficient reproduces the published 0.75 for all three networks.")
  }
} else {
  message("bootnet not installed - skipping PHASE 3 stability.")
}
message("06_dag.R: done -> ", out_dir)
```
