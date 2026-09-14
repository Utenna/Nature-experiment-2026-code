# =============================================================================
# 04_sem_mediation.R  --  parallel-mediation SEM  (E_Score -> L_Score -> health)
# -----------------------------------------------------------------------------
# Ported from the "Step 5C 中介分析" chunk of
# Code/R/02_analysis/GRF_project_2026_0413_SEM-bggm-dag-revised-clean.Rmd.
# Front-end cleaning/imputation replaced by lib/00_load.R (df_scores is rebuilt
# there, identical to the published Data_Forked_Step4.RData).
#
# lavaan::sem, ML, se = "bootstrap", percentile CIs (boot.ci.type = "perc")
# as in the original. set.seed(1234) before each fit.
#   QUICK=1  ->  1000 bootstrap draws (fast smoke test)
#   default  ->  5000 bootstrap draws (published setting)
#
# Outputs (to /results):
#   Table_S3_Score_Descriptives.csv          z-scored E/L/M/P/S/H residual scores
#   Table_Mediation_Results_Final_Beta.csv   paths a/b/c'/indirect/total/pm  (S4-S7)
#   Table_Mediation_R2.csv                   per-model R^2 (a-path, full outcome, total-effect)
# =============================================================================
suppressPackageStartupMessages({ library(lavaan); library(dplyr) })

.p <- Filter(file.exists, c("paths.R", "code/paths.R", "codeocean_capsule/code/paths.R",
                            "../code/paths.R", "/code/paths.R"))
if (!length(.p)) stop("Run from the capsule: setwd('.../codeocean_capsule/code') first.")
CODE_DIR <- normalizePath(dirname(.p[1]))
source(file.path(CODE_DIR, "paths.R"))
source(file.path(CODE_DIR, "lib", "00_load.R"))
out_tables_dir <- RESULTS_DIR

N_BOOT <- if (Sys.getenv("QUICK") == "1") 1000L else 5000L
message(sprintf("04_sem_mediation.R: bootstrap = %d %s",
                N_BOOT, if (N_BOOT < 5000) "(QUICK)" else "(published)"))

# ---- Table S3: descriptives of the z-scored residual domain scores ----------
score_cols <- c("E_Score", "L_Score", "M_Score", "P_Score", "S_Score", "H_Score_Total")
score_desc <- do.call(rbind, lapply(score_cols, function(k) {
  x <- df_scores[[k]]
  n <- length(x); m <- mean(x); s <- sd(x)
  skew <- mean(((x - m) / s)^3) * n^2 / ((n - 1) * (n - 2))   # psych/e1071 type-2 skew
  data.frame(Index = k, Mean = round(m, 3), SD = round(s, 3),
             Skew = round(skew, 3), Min = round(min(x), 3), Max = round(max(x), 3))
}))
print(score_desc)
write.csv(score_desc, file.path(out_tables_dir, "Table_S3_Score_Descriptives.csv"),
          row.names = FALSE)

run_mediation <- function(data, outcome_var, label) {
  model <- paste0('
    L_Score ~ a * E_Score
    ', outcome_var, ' ~ b * L_Score + c_prime * E_Score
    indirect := a * b
    total    := c_prime + (a * b)
    pm       := indirect / total
  ')
  set.seed(1234)
  fit <- sem(model, data = data, se = "bootstrap", bootstrap = N_BOOT)
  list(fit = fit, label = label, outcome = outcome_var)
}

outcomes <- list(
  "Total_Health"    = "H_Score_Total",
  "Mental_Health"   = "M_Score",
  "Physical_Health" = "P_Score",
  "Social_Health"   = "S_Score"
)

summary_list <- list()
r2_list <- list()
for (name in names(outcomes)) {
  message("   running model: ", name)
  ov  <- outcomes[[name]]
  res <- run_mediation(df_scores, ov, name)

  est <- parameterEstimates(res$fit, standardized = TRUE, boot.ci.type = "perc") %>%
    as.data.frame() %>%
    dplyr::filter(label %in% c("a", "b", "c_prime", "indirect", "total", "pm")) %>%
    dplyr::mutate(
      Path_Label = dplyr::case_when(
        label == "a" ~ "Environment -> Lifestyle",
        label == "b" ~ paste0("Lifestyle -> ", name),
        label == "c_prime" ~ paste0("Environment -> ", name, " (Direct)"),
        label == "indirect" ~ paste0("Env -> Life -> ", name, " (Mediation)"),
        label == "total" ~ paste0("Environment -> ", name, " (Total)"),
        label == "pm" ~ "% Mediation", TRUE ~ NA_character_),
      CI_Str = paste0("[", sprintf("%.3f", ci.lower), ", ", sprintf("%.3f", ci.upper), "]"),
      P_Str  = ifelse(pvalue < 0.001, "<.001", sprintf("%.3f", pvalue))
    ) %>%
    dplyr::select(
      Model = rhs, `Path / Effect` = label, `Path Label` = Path_Label,
      `Standardized Coefficient (b)` = std.all, `Standard Error (SE)` = se,
      `P` = P_Str, `95% CI (Bootstrap)` = CI_Str
    ) %>%
    dplyr::mutate(
      Model = name,
      `Standardized Coefficient (b)` = round(`Standardized Coefficient (b)`, 3),
      `Standard Error (SE)` = round(`Standard Error (SE)`, 3)
    )
  summary_list[[name]] <- est

  # R^2: a-path (L_Score), full outcome model, and total-effect model (outcome ~ E only)
  r2_full <- lavaan::inspect(res$fit, "r2")
  set.seed(1234)
  fit_tot <- sem(paste0(ov, " ~ E_Score"), data = df_scores)
  r2_tot  <- lavaan::inspect(fit_tot, "r2")
  r2_list[[name]] <- data.frame(
    Model = name,
    R2_Lifestyle_a   = round(unname(r2_full["L_Score"]), 3),
    R2_Outcome_full  = round(unname(r2_full[ov]), 3),
    R2_Outcome_total = round(unname(r2_tot[ov]), 3)
  )
}

final_med_tab <- bind_rows(summary_list)
print(final_med_tab)
write.csv(final_med_tab, file.path(out_tables_dir, "Table_Mediation_Results_Final_Beta.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

r2_tab <- bind_rows(r2_list)
print(r2_tab)
write.csv(r2_tab, file.path(out_tables_dir, "Table_Mediation_R2.csv"), row.names = FALSE)
message("04_sem_mediation.R: done -> ", out_tables_dir)
