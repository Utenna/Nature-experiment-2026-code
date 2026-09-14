# =============================================================================
# lib/00_load.R  --  rebuild the modelling objects from /data/data_analysis.csv
# -----------------------------------------------------------------------------
# In the original private pipeline these objects were produced by
# GRF_project_2026_0415_bggm.Rmd (Step 1 cleaning -> missForest -> Step 4 fork)
# and cached in Data_Forked_Step4.RData. The de-identified data_analysis.csv IS
# the post-imputation df_clean_num (69 items + 8 covariates, complete, 3331 rows),
# so every downstream object is reconstructed here deterministically -- no raw
# data and no imputation step required.
#
# Produces, identical to the published Data_Forked_Step4.RData:
#   df_clean_num  df_raw_bggm  df_resid  df_scores  ses_df_model  continuous_items
# plus:
#   ids (row_id, Estate_ID, District_ID)  estate_group  district_group
#   e_item_names l_item_names mh_item_names ph_item_names sh_item_names  all_items
# =============================================================================
suppressPackageStartupMessages({
  library(dplyr)
})

if (!exists("data_path")) {
  if (!exists("CODE_DIR")) {
    .p <- Filter(file.exists, c("paths.R", "code/paths.R",
                                "codeocean_capsule/code/paths.R",
                                "../code/paths.R", "/code/paths.R"))
    if (!length(.p)) stop("lib/00_load.R: source code/paths.R first (or set CODE_DIR)")
    CODE_DIR <- normalizePath(dirname(.p[1]))
  }
  source(file.path(CODE_DIR, "paths.R"))
}

.f <- data_path("data_analysis.csv")
stopifnot(file.exists(.f))
.raw <- read.csv(.f, check.names = FALSE, stringsAsFactors = FALSE)

e_item_names  <- paste0("E", 1:29)
l_item_names  <- paste0("L", 1:16)
mh_item_names <- paste0("M", 1:8)
ph_item_names <- paste0("P", 1:8)
sh_item_names <- paste0("S", 1:8)
all_items <- c(e_item_names, l_item_names, mh_item_names, ph_item_names, sh_item_names)  # 69
ses_vars  <- c("Age", "Gender", "Edu", "Emp", "Imm", "CD", "DurRes", "LivArea")

stopifnot(all(c("row_id", "Estate_ID", "District_ID", all_items, ses_vars) %in% names(.raw)))
stopifnot(nrow(.raw) == 3331L)

ids            <- .raw[, c("row_id", "Estate_ID", "District_ID")]
estate_group   <- factor(.raw$Estate_ID)
district_group <- factor(.raw$District_ID)

# ---- df_clean_num : 69 items + 8 covariates, numeric, complete ---------------
df_clean_num <- as.data.frame(lapply(.raw[, c(all_items, ses_vars)],
                                     function(x) as.numeric(as.character(x))))
stopifnot(sum(is.na(df_clean_num)) == 0L)

# ---- ses_df_model : covariate types exactly as the R pipeline Step 4 --------
ses_numeric_vars <- c("Age", "Edu", "DurRes", "LivArea")
ses_factor_vars  <- c("Gender", "Emp", "Imm", "CD")
ses_df_model <- df_clean_num %>%
  dplyr::select(all_of(ses_vars)) %>%
  mutate(across(all_of(ses_numeric_vars), ~ as.numeric(as.character(.)))) %>%
  mutate(across(all_of(ses_factor_vars),  ~ as.factor(.)))

# ---- df_raw_bggm : integer items for BGGM type = "ordinal" ------------------
df_raw_bggm <- df_clean_num

# ---- df_resid : each item residualised on the 8 covariates (lm, dummies) ----
df_resid <- df_clean_num
for (item in all_items) {
  tmp <- cbind(Y_Target = df_clean_num[[item]], ses_df_model)
  fit <- lm(Y_Target ~ ., data = tmp, na.action = na.exclude)
  df_resid[[item]] <- residuals(fit)
}

# ---- df_scores : residualised dimension means, z-scored --------------------
.calc_score <- function(data, vars) rowMeans(data[, vars, drop = FALSE], na.rm = TRUE)
df_scores <- df_resid %>%
  mutate(
    E_Score = .calc_score(., e_item_names),
    L_Score = .calc_score(., l_item_names),
    M_Score = .calc_score(., mh_item_names),
    P_Score = .calc_score(., ph_item_names),
    S_Score = .calc_score(., sh_item_names),
    H_Score_Total = rowMeans(cbind(M_Score, P_Score, S_Score), na.rm = TRUE)
  ) %>%
  mutate(across(c(E_Score, L_Score, M_Score, P_Score, S_Score, H_Score_Total),
                ~ as.numeric(scale(.))))

continuous_items <- c()

message(sprintf("lib/00_load.R: %d rows | df_clean_num %d cols | df_scores %d cols | %d estates",
                nrow(df_clean_num), ncol(df_clean_num), ncol(df_scores), nlevels(estate_group)))
