# =============================================================================
# 03_reliability_cfa.R  --  scale reliability (alpha / omega) + CFA fit
# -----------------------------------------------------------------------------
# Ported from Code/R/02_analysis/GRF_project_2026_0413_CronbachMcDonalds.Rmd
# (the "Reliability and Validity Analysis" chunk). The Rmd's Step 1-5
# cleaning + missForest front-end is replaced by lib/00_load.R, which loads the
# de-identified post-imputation data. Logic below is unchanged.
#
# Outputs (to /results):
#   Table_S15_Reliability.csv        Cronbach alpha & McDonald omega per domain
#   Table_S14_CFA_Fit_Indices.csv    chi-square, df, CFI, TLI, RMSEA, SRMR
#   Table_S16_CFA_Factor_Loadings.csv
#
# Deterministic (ML estimator, no bootstrap).
# =============================================================================
suppressPackageStartupMessages({
  library(psych); library(lavaan); library(dplyr); library(tidyr); library(tibble)
})

.p <- Filter(file.exists, c("paths.R", "code/paths.R", "codeocean_capsule/code/paths.R",
                            "../code/paths.R", "/code/paths.R"))
if (!length(.p)) stop("Run from the capsule: setwd('.../codeocean_capsule/code') first.")
CODE_DIR <- normalizePath(dirname(.p[1]))
source(file.path(CODE_DIR, "paths.R"))
source(file.path(CODE_DIR, "lib", "00_load.R"))
out_tables_dir <- RESULTS_DIR

# psych/lavaan want a plain numeric frame of the 69 items (+ ids dropped)
df_for_psych <- as.data.frame(lapply(df_clean_num[, all_items],
                                     function(x) as.numeric(as.character(x))))

calc_reliability <- function(data, items, domain_name) {
  sub_data <- data[, items]
  alpha_res <- psych::alpha(sub_data, check.keys = TRUE)$total$raw_alpha
  omega_res <- tryCatch(
    suppressWarnings(psych::omega(sub_data, nfactors = 1, plot = FALSE)$omega.tot),
    error = function(e) NA)
  data.frame(Domain = domain_name, Items_Count = length(items),
             Cronbach_Alpha = round(alpha_res, 3), McDonald_Omega = round(omega_res, 3))
}

rel_table <- bind_rows(
  calc_reliability(df_for_psych, e_item_names,  "Environment"),
  calc_reliability(df_for_psych, l_item_names,  "Lifestyle"),
  calc_reliability(df_for_psych, mh_item_names, "Mental_Health"),
  calc_reliability(df_for_psych, ph_item_names, "Physical_Health"),
  calc_reliability(df_for_psych, sh_item_names, "Social_Health")
)
print(rel_table)

cfa_model_syntax <- paste0(
  "Environment =~ ",     paste(e_item_names,  collapse = " + "), "\n",
  "Lifestyle =~ ",       paste(l_item_names,  collapse = " + "), "\n",
  "Mental_Health =~ ",   paste(mh_item_names, collapse = " + "), "\n",
  "Physical_Health =~ ", paste(ph_item_names, collapse = " + "), "\n",
  "Social_Health =~ ",   paste(sh_item_names, collapse = " + ")
)
fit_cfa <- lavaan::cfa(model = cfa_model_syntax, data = df_for_psych,
                       std.lv = TRUE, estimator = "ML")
fm <- fitMeasures(fit_cfa, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))
cfa_summary <- data.frame(
  Metric = c("Chi-Square", "df", "CFI", "TLI", "RMSEA", "SRMR"),
  Value  = c(round(fm["chisq"], 2), fm["df"], round(fm["cfi"], 3),
             round(fm["tli"], 3), round(fm["rmsea"], 3), round(fm["srmr"], 3))
)
print(cfa_summary)

loadings <- standardizedSolution(fit_cfa) %>%
  dplyr::filter(op == "=~") %>%
  dplyr::transmute(Domain = lhs, Item = rhs, Std_Loading = round(est.std, 3),
                   Significance = dplyr::case_when(pvalue < 0.001 ~ "***", pvalue < 0.01 ~ "**",
                                                   pvalue < 0.05 ~ "*", TRUE ~ "ns"))

write.csv(rel_table,   file.path(out_tables_dir, "Table_S15_Reliability.csv"), row.names = FALSE)
write.csv(cfa_summary, file.path(out_tables_dir, "Table_S14_CFA_Fit_Indices.csv"), row.names = FALSE)
write.csv(loadings,    file.path(out_tables_dir, "Table_S16_CFA_Factor_Loadings.csv"), row.names = FALSE)
message("03_reliability_cfa.R: done -> ", out_tables_dir)
