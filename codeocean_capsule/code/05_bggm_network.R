# =============================================================================
# 05_bggm_network.R  --  Bayesian Gaussian Graphical Models (BGGM)
# -----------------------------------------------------------------------------
# Ported from the "Step 6: BGGM 网络分析" chunk of
# Code/R/02_analysis/GRF_project_2026_0415_bggm.Rmd. Numeric outputs kept;
# qgraph/PDF figure generation removed (not reproduction-critical, and the
# fragile part on a headless runner). Front-end replaced by lib/00_load.R.
#
# For each health domain (Mental / Physical / Social), on the E+L+domain nodes:
#   * set.seed(42), then BGGM::estimate on the RAW network (discarded -- only
#     kept to advance the RNG exactly as the .Rmd did, so the residualised fit
#     lands on the same MCMC chain as the manuscript)
#   * BGGM::estimate on residualised data (df_resid), iter = ITER_NUM
#   * BGGM::select at cred = 0.99  -> signed partial-correlation adjacency
#   * edge 99% credible intervals  (summary)
#   * node predictability (Bayesian R^2)
#   * bridge Expected Influence / Strength (networktools)
#   QUICK=1 -> ITER_NUM = 1000 ; default -> 5000 (published).
#
# COMPUTE NOTE: predictability() is the slow step (order of an hour per domain
# at iter = 5000 on a small runner).
#   * Resume: if a run is killed part-way, just start it again -- a domain whose
#     four output tables are already present and non-empty in /results is
#     skipped. set.seed(42) is re-set per domain, so skipping changes nothing.
#     (Works when /results persists, e.g. an interactive session; a fresh
#     Reproducible Run starts /results empty and recomputes everything.)
#   * PRED_ITER=<n> caps only the predictability iteration count (default =
#     ITER_NUM). PRED_ITER=2500 roughly halves that step's time/memory and keeps
#     Post.mean within ~0.002 of the published table. estimate() always uses the
#     full ITER_NUM.
#
# Outputs (to /results):
#   adj_matrix_BGGM_<domain>_Pearson_Resid.csv
#   Table_Edge_CrI_<domain>.csv
#   Table_Predictability_<domain>.csv
#   Table_Bridge_Metrics_<domain>.csv
# =============================================================================
suppressPackageStartupMessages({
  library(BGGM); library(dplyr); library(networktools)
})

.p <- Filter(file.exists, c("paths.R", "code/paths.R", "codeocean_capsule/code/paths.R",
                            "../code/paths.R", "/code/paths.R"))
if (!length(.p)) stop("Run from the capsule: setwd('.../codeocean_capsule/code') first.")
CODE_DIR <- normalizePath(dirname(.p[1]))
source(file.path(CODE_DIR, "paths.R"))
source(file.path(CODE_DIR, "lib", "00_load.R"))
out_dir <- RESULTS_DIR

ITER_NUM <- if (Sys.getenv("QUICK") == "1") 1000L else 5000L

# predictability() (Bayesian R^2) is the slow step. It post-processes the fit's
# existing posterior draws, so PRED_ITER only trades a little Monte-Carlo
# precision for speed/memory -- default matches ITER_NUM (no change); set e.g.
# PRED_ITER=2500 on a constrained runner (Post.mean stays within ~0.002 of the
# published table). Ignored for estimate(), which must run the full ITER_NUM.
.pred_env  <- suppressWarnings(as.integer(Sys.getenv("PRED_ITER", "")))
PRED_ITER  <- if (is.na(.pred_env) || .pred_env < 1L) ITER_NUM else min(.pred_env, ITER_NUM)

message(sprintf("05_bggm_network.R: iter = %d ; predictability iter = %d %s",
                ITER_NUM, PRED_ITER, if (ITER_NUM < 5000) "(QUICK)" else "(published)"))

e_names <- e_item_names
l_names <- l_item_names
multi_models <- list(
  "Mental_Health"   = mh_item_names,
  "Physical_Health" = ph_item_names,
  "Social_Health"   = sh_item_names
)

run_bggm_metrics <- function(data_raw_full, data_resid_full, node_names, groups_list,
                             model_label, out_dir, n_iter = ITER_NUM, pred_iter = PRED_ITER) {
  stopifnot(all(node_names %in% colnames(data_raw_full)))
  set.seed(42)
  Y_raw_mat   <- as.matrix(data_raw_full[,   node_names]); mode(Y_raw_mat)   <- "numeric"
  Y_resid_mat <- as.matrix(data_resid_full[, node_names]); mode(Y_resid_mat) <- "numeric"

  # RNG alignment: the published .Rmd estimated the RAW (uncontrolled) network
  # here first -- its output only fed a side-by-side figure that this script
  # drops, but the estimate() call advanced the RNG before the residualised fit.
  # Reproduce it (result discarded, memory freed) so fit_ctrl lands on the same
  # MCMC chain as the manuscript's BGGM supplementary tables.
  message("   [", model_label, "] estimate() raw network (RNG alignment, discarded) ...")
  .fit_raw_discard <- BGGM::estimate(Y = Y_raw_mat, iter = n_iter, progress = FALSE)
  rm(.fit_raw_discard); gc(verbose = FALSE)

  message("   [", model_label, "] estimate() residualised network (iter = ", n_iter, ") ...")
  fit_ctrl <- BGGM::estimate(Y = Y_resid_mat, iter = n_iter, progress = FALSE)
  sel_ctrl <- BGGM::select(fit_ctrl, cred = 0.99)

  adj_ctrl <- as.matrix(sel_ctrl$pcor_adj)
  colnames(adj_ctrl) <- rownames(adj_ctrl) <- node_names
  write.csv(adj_ctrl, file.path(out_dir, paste0("adj_matrix_BGGM_", model_label, "_Pearson_Resid.csv")))

  message("   [", model_label, "] summary() ...")
  summary_ctrl <- summary(fit_ctrl, cred = 0.99)
  df_cri <- if (!is.null(summary_ctrl$results)) summary_ctrl$results
            else as.data.frame(unclass(summary_ctrl)[[1]])
  write.csv(df_cri, file.path(out_dir, paste0("Table_Edge_CrI_", model_label, ".csv")), row.names = FALSE)

  message("   [", model_label, "] predictability() (the slow step, iter = ", pred_iter, ") ...")
  pred_res <- tryCatch(BGGM::predictability(fit_ctrl, select = FALSE, iter = pred_iter, progress = FALSE),
                       error = function(e) NULL)
  if (!is.null(pred_res)) {
    pred_sum <- summary(pred_res, cred = 0.99)
    df_pred <- if (!is.null(pred_sum$results)) pred_sum$results
               else as.data.frame(unclass(pred_sum)[[1]])
    write.csv(df_pred, file.path(out_dir, paste0("Table_Predictability_", model_label, ".csv")),
              row.names = FALSE)
  }

  node_count <- length(node_names)
  community_chr <- character(node_count)
  for (g_name in names(groups_list)) {
    gi <- groups_list[[g_name]]; gi <- gi[gi <= node_count]
    if (length(gi) > 0) community_chr[gi] <- g_name
  }
  message("   [", model_label, "] bridge() ...")
  br <- tryCatch(networktools::bridge(adj_ctrl, communities = community_chr,
                                      useCommunities = "all", nodes = node_names),
                 error = function(e) NULL)
  bridge_tab <- data.frame(
    Node = node_names, Community = community_chr,
    Bridge_EI  = if (!is.null(br)) br$`Bridge Expected Influence (1-step)` else NA_real_,
    Bridge_Str = if (!is.null(br)) br$`Bridge Strength` else NA_real_,
    Node_EI  = colSums(adj_ctrl),
    Node_Str = colSums(abs(adj_ctrl))
  )
  write.csv(bridge_tab, file.path(out_dir, paste0("Table_Bridge_Metrics_", model_label, ".csv")),
            row.names = FALSE)
  message("   [", model_label, "] done")
  invisible(adj_ctrl)
}

# The four tables a completed domain writes, in order.
domain_outputs <- function(model_label) file.path(out_dir, c(
  paste0("adj_matrix_BGGM_", model_label, "_Pearson_Resid.csv"),
  paste0("Table_Edge_CrI_",  model_label, ".csv"),
  paste0("Table_Predictability_", model_label, ".csv"),
  paste0("Table_Bridge_Metrics_",  model_label, ".csv")))

for (model_label in names(multi_models)) {
  message("\n>>> BGGM: ", model_label)

  # Resume support: skip a domain whose four tables are all already present and
  # non-empty. A fresh /results skips nothing (normal full run). Because
  # set.seed(42) is re-set per domain, skipping finished domains does not change
  # the result of the ones still to run. Delete a domain's CSVs in /results to
  # force recomputation.
  out_f <- domain_outputs(model_label)
  if (all(file.exists(out_f)) && all(file.size(out_f) > 0)) {
    message("   already complete in ", out_dir, " -- skipping")
    next
  }

  h_nodes <- multi_models[[model_label]]
  current_nodes <- c(e_names, l_names, h_nodes)
  n_e <- length(e_names); n_l <- length(l_names); n_h <- length(h_nodes)
  groups_list <- list("Environment" = 1:n_e, "Lifestyle" = (n_e + 1):(n_e + n_l))
  groups_list[[model_label]] <- (n_e + n_l + 1):(n_e + n_l + n_h)
  tryCatch(
    run_bggm_metrics(df_raw_bggm, df_resid, current_nodes, groups_list,
                     model_label, out_dir, ITER_NUM, PRED_ITER),
    error = function(e) message("   FAILED: ", model_label, " -- ", conditionMessage(e))
  )
  gc(verbose = FALSE)   # release the domain's posterior draws before the next one
}
message("05_bggm_network.R: done -> ", out_dir)
