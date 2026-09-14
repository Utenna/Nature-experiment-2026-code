#!/usr/bin/env python3
# =============================================================================
# 00_prepare_deidentified_data.py
# -----------------------------------------------------------------------------
# PROVENANCE / REGENERATION ONLY -- NOT part of the Code Ocean "Reproducible Run".
#
# This script documents exactly how the two de-identified data files shipped in
# /data were produced from the restricted source data. It requires files that are
# NOT included in the capsule (and never leave HKU under ethics approval
# EA1910004(A3)):
#
#     <repo>/Data/Raw/merged_data0925.xlsx        (raw questionnaire, 3350 x 329)
#     <repo>/Data/Processed/Data_Forked_Step4.RData (post-imputation modelling data)
#
# Run by the authors from the private analysis repository:
#     python code/00_prepare_deidentified_data.py
#
# Outputs (paths relative to repo root):
#     codeocean_capsule/data/data_balance.csv     3350 rows, pre-imputation SES + group ids
#     codeocean_capsule/data/data_analysis.csv    3331 rows, post-imputation model items + anon estate id
#     codeocean_capsule/data/codebook.csv         one row per variable
#     private/estate_id_map.csv                   Estate_001..224  <-> Chinese estate name   (GITIGNORED)
#     private/district_id_map.csv                 D01..D18         <-> Chinese district name (GITIGNORED)
#
# De-identification rules applied (see capsule README, section "De-identification"):
#   * All direct identifiers removed: ResponseId, address, birthyear, all *_TEXT
#     free-text fields, Others, Height, Weight, name-in-English, numeric estate ID.
#   * All quasi-identifiers not used by any reported analysis removed: area,
#     age_group, occu, mar, unemp, indinco, faminco, livwith*, waist, preg,
#     the 13 ne_* negative-life-event items, the 18 individual diagnosis flags,
#     and all estate-level merged aggregates (X0_*..X800_*, suicide rates,
#     Population, ...).
#   * birthyear -> Age (integer years); Age == 2023 - birthyear exactly.
#   * estate  -> Estate_ID  (Estate_001..Estate_224), assigned by sorting the
#     224 distinct Chinese names by Unicode code point. Deterministic; carries
#     no sample-size ordering.
#   * district -> District_ID (D01..D18), same scheme.
#   * LivArea  = livarea_val / livnum_val  (per-person living area, sq ft),
#     using the R pipeline's ordinal->midpoint maps. Raw livarea / livnum dropped.
#   * DurRes   = duration of residence collapsed to 5 ordinal bands (R case_when).
#   * CD       = 1 if "completely healthy" else 0 (from `disease`).
#   * WINSORIZE (env var, default "0"): if "1", top/bottom-code Age at <=90 and
#     LivArea to [18.75, 375] (0.5th/99th pct). DEFAULT OFF so the capsule
#     reproduces the published Supplementary Table S12 and network inputs to
#     printed precision. Turning it on shifts LivArea mean 97.40 -> 97.22 and
#     ICC 0.198 -> 0.203; documented in the README.
#
# No random component. Fully deterministic.
# =============================================================================
import os
import sys
import hashlib
import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_XLSX = os.environ.get("RAW_XLSX", os.path.join(REPO, "Data", "Raw", "merged_data0925.xlsx"))
STEP4_RDATA = os.environ.get("STEP4_RDATA", os.path.join(REPO, "Data", "Processed", "Data_Forked_Step4.RData"))
OUT_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
OUT_PRIVATE = os.environ.get("OUT_PRIVATE", os.path.join(REPO, "private"))
WINSORIZE = os.environ.get("WINSORIZE", "0") == "1"

# ordinal -> midpoint maps, verbatim from Code/R/02_analysis/GRF_project_2026_0415_bggm.Rmd
LIVNUM_MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7.5}
LIVAREA_MAP = {1: 75, 2: 175, 3: 225, 4: 275, 5: 325, 6: 375, 7: 425, 8: 475,
               9: 575, 10: 675, 11: 775, 12: 825, 13: 875, 14: 975, 15: 1100}
DURA_MAP = {
    "1-2 年": 1, "2-3 年": 1, "3-4 年": 1, "4-5 年": 1,
    "5-6年": 2, "6-7年": 2, "7-8年": 2, "8-9年": 2, "9-10年": 2,
    "10-11年": 3, "11-12年": 3, "12-13年": 3, "13-14年": 3, "14-15年": 3,
    "15-16年": 4, "16-17年": 4, "17-18年": 4, "18-19年": 4, "19-20年": 4,
    "超過20年": 5,
}
DISEASE_CH_MAP = {
    "沒有，完全健康": 1,
    "僅患有慢性疾病": 2,
    "僅患有精神疾病": 3,
    "同時患有慢性疾病和精神疾病": 4,
}

# 69 analysis items, order & names from the R imputation block (bggm.Rmd, e_orig_names ...)
E_ORIG = ["e_city", "e_dist", "e_metro", "e_Bus", "e_wlkgrn", "e_wvgrn", "e_wlkblu", "e_wvblu",
          "e_facil", "e_Price", "e_work", "e_eduEL", "e_comCen", "e_medAc", "e_alcig",
          "e_neiAl", "e_neiLow", "e_neiSoci", "e_themCo", "e_clim", "e_poll", "e_lighting",
          "e_privacy", "e_narrow", "e_PA", "e_sleep", "e_heaFood", "e_lifestyle", "e_safe"]
L_ORIG = ["l_palgt", "l_pamed", "l_pahig", "l_lgtdur", "l_meddur", "l_higdur",
          "l_sitdur", "l_leidur", "l_eathealth", "l_eatout", "l_smoking",
          "l_drinking", "l_medictest", "l_adaptCop", "l_med_seek", "l_info_seek"]
M_ORIG = ["m_conc", "m_wea", "m_pos", "m_app", "m_neg", "m_est", "m_res", "m_eat"]
P_ORIG = ["p_energy", "p_pain", "p_medD", "p_genH", "p_sleep", "p_daily", "p_work", "p_mobility"]
S_ORIG = ["SS_1", "SS_2", "SS_3", "SS_4", "SS_5", "SS_6", "SS_7", "SS_8"]
SES_VARS = ["Age", "Gender", "Edu", "Emp", "Imm", "CD", "DurRes", "LivArea"]

E_ITEMS = [f"E{i}" for i in range(1, len(E_ORIG) + 1)]
L_ITEMS = [f"L{i}" for i in range(1, len(L_ORIG) + 1)]
M_ITEMS = [f"M{i}" for i in range(1, len(M_ORIG) + 1)]
P_ITEMS = [f"P{i}" for i in range(1, len(P_ORIG) + 1)]
S_ITEMS = [f"S{i}" for i in range(1, len(S_ORIG) + 1)]
CORE_ITEMS = E_ITEMS + L_ITEMS + M_ITEMS + P_ITEMS + S_ITEMS

ITEM_LABELS = {
    # Environment (perceived residential environment, higher = more/better of the named attribute)
    "E1": "Proximity to urban centre (perceived)",
    "E2": "Accessibility of district centre",
    "E3": "Proximity to MTR station (perceived)",
    "E4": "Accessibility of bus stops",
    "E5": "Walking accessibility to green space",
    "E6": "Green space visible from home window",
    "E7": "Walking accessibility to blue space",
    "E8": "Blue space visible from home window (passive exposure)",
    "E9": "Density / diversity of daily-life facilities",
    "E10": "Affordability of local prices",
    "E11": "Access to work opportunities nearby",
    "E12": "Access to education facilities (primary+secondary avg.)",
    "E13": "Access to community centre",
    "E14": "Access to medical care",
    "E15": "Low density of alcohol/tobacco retail",
    "E16": "Low neighbourhood social disorder (alcohol-related)",
    "E17": "Low concentrated neighbourhood poverty",
    "E18": "Neighbourhood social interaction",
    "E19": "Thermal comfort of home",
    "E20": "Low climate-hazard exposure/frequency",
    "E21": "Low air/environmental pollution",
    "E22": "Adequate lighting at home",
    "E23": "Adequate privacy at home",
    "E24": "Home not cramped/narrow",
    "E25": "Environment discourages physical inactivity",
    "E26": "Sleep-conducive home environment",
    "E27": "Environment supports healthy eating",
    "E28": "Environment supports a healthy lifestyle overall",
    "E29": "Perceived neighbourhood safety",
    # Lifestyle
    "L1": "Light-intensity physical activity frequency",
    "L2": "Moderate-intensity physical activity frequency",
    "L3": "Vigorous-intensity physical activity frequency",
    "L4": "Light-intensity physical activity duration",
    "L5": "Moderate-intensity physical activity duration",
    "L6": "Vigorous-intensity physical activity duration",
    "L7": "Sitting time (duration)",
    "L8": "Leisure-time physical activity duration",
    "L9": "Healthy eating behaviour",
    "L10": "Frequency of eating out",
    "L11": "Smoking (reverse-coded: higher = less)",
    "L12": "Drinking (reverse-coded: higher = less)",
    "L13": "Regular medical check-ups",
    "L14": "Adaptive coping behaviour count",
    "L15": "Medical help-seeking (any)",
    "L16": "Health-information-seeking count",
    # Mental health
    "M1": "Concentration",
    "M2": "Freedom from weariness/fatigue",
    "M3": "Positive affect",
    "M4": "Appetite (mental-health facet)",
    "M5": "Freedom from negative affect (reverse-coded)",
    "M6": "Self-esteem",
    "M7": "Resilience",
    "M8": "Eating regulation",
    # Physical health
    "P1": "Energy / vitality",
    "P2": "Freedom from pain (reverse-coded)",
    "P3": "Freedom from medication dependence (reverse-coded)",
    "P4": "General health rating",
    "P5": "Sleep quality",
    "P6": "Ability to carry out daily activities",
    "P7": "Ability to work",
    "P8": "Mobility",
    # Social health (social support items 1-8)
    "S1": "Social support item 1", "S2": "Social support item 2",
    "S3": "Social support item 3", "S4": "Social support item 4",
    "S5": "Social support item 5", "S6": "Social support item 6",
    "S7": "Social support item 7", "S8": "Social support item 8",
}
COV_LABELS = {
    "Age": "Age in years (integer)",
    "Gender": "Gender (1 = male, 2 = female; data_balance may also hold other coded/missing values as collected)",
    "Edu": "Highest education attained (ordinal, 1 low - 7 high)",
    "Emp": "Employment status (nominal, 1-7)",
    "Imm": "Immigration / residency status (nominal, 1-6)",
    "CD": "Chronic disease status (1 = completely healthy, 0 = any chronic and/or mental health condition)",
    "DurRes": "Duration of residence (ordinal: 1 = <5y, 2 = 5-10y, 3 = 10-15y, 4 = 15-20y, 5 = >20y)",
    "LivArea": "Per-person living area, square feet (ordinal midpoints, living area / household size)",
}


def safe_map(val, mapping):
    try:
        return mapping[int(float(val))]
    except (ValueError, TypeError, KeyError):
        return np.nan


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_ses_frame(df):
    """Derive the 8 SES covariates exactly as the R pipeline / balance-test notebook do."""
    out = pd.DataFrame(index=df.index)
    out["Age"] = pd.to_numeric(df["age"], errors="coerce")

    livnum_val = df["livnum"].apply(lambda x: safe_map(x, LIVNUM_MAP))
    livarea_val = df["livarea"].apply(lambda x: safe_map(x, LIVAREA_MAP))
    out["LivArea"] = livarea_val / livnum_val

    dur = df["liviDura"].map(DURA_MAP)
    na = dur.isna()
    dur.loc[na] = pd.to_numeric(df.loc[na, "liviDura"], errors="coerce")
    out["DurRes"] = dur

    dn = df["disease"].map(DISEASE_CH_MAP)
    na = dn.isna()
    dn.loc[na] = pd.to_numeric(df["disease"], errors="coerce")[na]
    cd = (dn == 1).astype(float)
    cd[dn.isna()] = np.nan
    out["CD"] = cd

    out["Gender"] = pd.to_numeric(df["gender"], errors="coerce")
    out["Edu"] = pd.to_numeric(df["edu"], errors="coerce")
    out["Emp"] = pd.to_numeric(df["emp"], errors="coerce")
    out["Imm"] = pd.to_numeric(df["imm"], errors="coerce")
    return out[SES_VARS]


def maybe_winsorize(frame):
    if not WINSORIZE:
        return frame
    f = frame.copy()
    f["Age"] = f["Age"].clip(upper=90)
    f["LivArea"] = f["LivArea"].clip(lower=18.75, upper=375.0)
    return f


def main():
    for p in (RAW_XLSX, STEP4_RDATA):
        if not os.path.exists(p):
            sys.exit(f"ERROR: required input not found: {p}\n"
                     "This script is provenance-only and needs the restricted source data.")
    os.makedirs(OUT_DATA, exist_ok=True)
    os.makedirs(OUT_PRIVATE, exist_ok=True)

    print(f"raw   : {RAW_XLSX}\n        sha256 {sha256(RAW_XLSX)}")
    print(f"step4 : {STEP4_RDATA}\n        sha256 {sha256(STEP4_RDATA)}")
    print(f"WINSORIZE = {WINSORIZE}")

    raw = pd.read_excel(RAW_XLSX)
    assert raw.shape[0] == 3350, raw.shape

    # ---- anonymisation maps -------------------------------------------------
    estates = sorted(raw["estate"].dropna().unique().tolist())
    districts = sorted(raw["district"].dropna().unique().tolist())
    estate_map = {name: f"Estate_{i:03d}" for i, name in enumerate(estates, 1)}
    district_map = {name: f"D{i:02d}" for i, name in enumerate(districts, 1)}
    assert len(estate_map) == 224, len(estate_map)

    est_counts = raw["estate"].value_counts()
    pd.DataFrame({
        "Estate_ID": [estate_map[n] for n in estates],
        "estate_cn": estates,
        "n_respondents_raw": [int(est_counts.get(n, 0)) for n in estates],
    }).to_csv(os.path.join(OUT_PRIVATE, "estate_id_map.csv"), index=False, encoding="utf-8-sig")

    dist_counts = raw["district"].value_counts()
    pd.DataFrame({
        "District_ID": [district_map[n] for n in districts],
        "district_cn": districts,
        "n_respondents_raw": [int(dist_counts.get(n, 0)) for n in districts],
    }).to_csv(os.path.join(OUT_PRIVATE, "district_id_map.csv"), index=False, encoding="utf-8-sig")
    print(f"wrote private maps -> {OUT_PRIVATE}  (NEVER commit / upload these)")

    raw_estate_id = raw["estate"].map(estate_map)
    raw_district_id = raw["district"].map(district_map)

    # ---- data_balance.csv : all 3350 rows, pre-imputation ------------------
    ses_all = maybe_winsorize(build_ses_frame(raw))
    bal = pd.concat([
        pd.Series(np.arange(len(raw)), name="row_id"),
        raw_estate_id.rename("Estate_ID").reset_index(drop=True),
        raw_district_id.rename("District_ID").reset_index(drop=True),
        ses_all.reset_index(drop=True),
    ], axis=1)
    bal.to_csv(os.path.join(OUT_DATA, "data_balance.csv"), index=False, encoding="utf-8")
    print(f"data_balance.csv   {bal.shape}  (Estate_ID {bal.Estate_ID.nunique()}, "
          f"District_ID {bal.District_ID.nunique()})")

    # ---- data_analysis.csv : 3331 rows, post-imputation model data ---------
    import pyreadr
    r = pyreadr.read_r(STEP4_RDATA)
    clean = r["df_clean_num"].reset_index(drop=True)
    assert list(clean.columns) == CORE_ITEMS + SES_VARS, "df_clean_num column mismatch"
    assert clean.isna().sum().sum() == 0, "df_clean_num has NaN"

    g = pd.to_numeric(raw["gender"], errors="coerce")
    keep = g.isin([1, 2]).values
    raw_f = raw[keep].reset_index(drop=False).rename(columns={"index": "row_id"})
    assert len(raw_f) == len(clean) == 3331, (len(raw_f), len(clean))

    # position alignment assertions (raw filtered row i  <->  df_clean_num row i)
    age_raw = pd.to_numeric(raw_f["age"], errors="coerce")
    m = age_raw.notna()
    assert np.array_equal(age_raw[m].values, clean.loc[m.values, "Age"].values), "Age misaligned"
    gen_raw = pd.to_numeric(raw_f["gender"], errors="coerce")
    assert np.array_equal(gen_raw.values, clean["Gender"].values), "Gender misaligned"
    la_raw = (raw_f["livarea"].apply(lambda x: safe_map(x, LIVAREA_MAP))
              / raw_f["livnum"].apply(lambda x: safe_map(x, LIVNUM_MAP)))
    m = la_raw.notna()
    assert np.allclose(la_raw[m].values, clean.loc[m.values, "LivArea"].values), "LivArea misaligned"
    print("row-position alignment raw(gender-filtered) <-> df_clean_num: OK (3331/3331)")

    ana = clean.copy()
    if WINSORIZE:
        ana["Age"] = ana["Age"].clip(upper=90)
        ana["LivArea"] = ana["LivArea"].clip(lower=18.75, upper=375.0)
    ana.insert(0, "District_ID", raw_f["district"].map(district_map).values)
    ana.insert(0, "Estate_ID", raw_f["estate"].map(estate_map).values)
    ana.insert(0, "row_id", raw_f["row_id"].values)  # index into data_balance.row_id
    ana.to_csv(os.path.join(OUT_DATA, "data_analysis.csv"), index=False, encoding="utf-8")
    print(f"data_analysis.csv  {ana.shape}  (Estate_ID {ana.Estate_ID.nunique()}/224)")

    # ---- codebook.csv -----------------------------------------------------
    rows = []
    rows.append(dict(file="both", variable="row_id", label="Opaque respondent row index (aligns the two files)",
                     type="integer", values_or_range="0-3349", dimension="id", processed="Y: replaces ResponseId"))
    rows.append(dict(file="both", variable="Estate_ID", label="Anonymised public housing estate",
                     type="categorical", values_or_range="Estate_001-Estate_224", dimension="id",
                     processed="Y: replaces estate name / English name / numeric ID; mapping held privately"))
    rows.append(dict(file="both", variable="District_ID", label="Anonymised housing district",
                     type="categorical", values_or_range="D01-D18", dimension="id",
                     processed="Y: replaces district name"))
    grp = {"E": "environment", "L": "lifestyle", "M": "mental_health", "P": "physical_health", "S": "social_health"}
    for it in CORE_ITEMS:
        rows.append(dict(file="data_analysis", variable=it, label=ITEM_LABELS[it],
                         type="numeric (Likert)",
                         values_or_range="original item Likert scale; see Supplementary questionnaire table for wording/anchors",
                         dimension=grp[it[0]],
                         processed=("Y: missing values imputed (missForest, set.seed(123), ntree=500). "
                                    "Item scores are pre-residualisation; lib/00_load.R residualises on the "
                                    "8 covariates to reproduce df_resid / df_scores.")))
    for c in SES_VARS:
        win = ""
        if WINSORIZE and c == "Age":
            win = "; top-coded at 90"
        if WINSORIZE and c == "LivArea":
            win = "; winsorised to [18.75, 375]"
        rng = COV_LABELS[c].split("(", 1)[-1].rstrip(")") if "(" in COV_LABELS[c] else ""
        rows.append(dict(file="data_balance + data_analysis", variable=c, label=COV_LABELS[c],
                         type="numeric", values_or_range=rng, dimension="covariate",
                         processed=("Y: derived per R pipeline" + win
                                    + ". data_balance = pre-imputation (may be blank); "
                                      "data_analysis = post-imputation (complete).")))
    pd.DataFrame(rows, columns=["file", "variable", "label", "type", "values_or_range",
                                "dimension", "processed"]).to_csv(
        os.path.join(OUT_DATA, "codebook.csv"), index=False, encoding="utf-8-sig")
    print(f"codebook.csv       {len(rows)} variables")
    print("\nDONE.")


if __name__ == "__main__":
    main()
