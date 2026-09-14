#!/usr/bin/env python3
# =============================================================================
# 01_balance_test.py  --  SES covariate balance test (reproduces Supplementary Table S12)
# -----------------------------------------------------------------------------
# Port of Code/Python/02_analysis/balance-test-ses.ipynb, reading the
# de-identified /data/data_balance.csv instead of the restricted raw workbook.
#
# For each of the 8 SES covariates:
#   * Kruskal-Wallis H across housing districts (District_ID)
#   * one-way ICC(1) across public housing estates (Estate_ID), hand-coded,
#     identical formula to the notebook's icc_one_way().
#
# Writes:
#   /results/Table_S12_Balance_Test.csv          reproduced table
#   /results/balance_test_district_means.csv     per-district SES means (aux check)
#   /validation/balance_test_comparison.csv      reproduced vs published, cell by cell
#
# Deterministic (no RNG).
# =============================================================================
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import data, results, RESULTS_DIR  # noqa: E402

VALIDATION_DIR = os.path.join(RESULTS_DIR, "validation")
os.makedirs(VALIDATION_DIR, exist_ok=True)

SES_VARS = ["Age", "Gender", "Edu", "Emp", "Imm", "CD", "DurRes", "LivArea"]

# Published Supplementary Table S12 (01-supplementary-ELH.qmd, chunk `table-s12`)
PUBLISHED = {
    "Age":     dict(N=3349, mean=42.67, sd=13.96, KW_H=90.81,  p="< 0.001", ICC=0.102),
    "Gender":  dict(N=3346, mean=1.60,  sd=0.53,  KW_H=192.44, p="< 0.001", ICC=0.099),
    "Edu":     dict(N=3346, mean=2.84,  sd=1.41,  KW_H=91.82,  p="< 0.001", ICC=0.090),
    "Emp":     dict(N=3344, mean=3.15,  sd=1.93,  KW_H=54.09,  p="< 0.001", ICC=0.045),
    "Imm":     dict(N=3322, mean=2.79,  sd=1.20,  KW_H=212.26, p="< 0.001", ICC=0.143),
    "CD":      dict(N=3345, mean=0.82,  sd=0.38,  KW_H=40.33,  p="0.001",   ICC=0.029),
    "DurRes":  dict(N=3349, mean=2.86,  sd=1.55,  KW_H=205.58, p="< 0.001", ICC=0.252),
    "LivArea": dict(N=3339, mean=97.40, sd=62.00, KW_H=115.20, p="< 0.001", ICC=0.198),
}


def icc_one_way(series, groups):
    """One-way ANOVA ICC(1): between-group variance / total variance. Negatives clamped to 0."""
    d = pd.DataFrame({"y": series, "g": groups}).dropna()
    grand = d["y"].mean()
    k = d["g"].nunique()
    n = len(d)
    sizes = d.groupby("g")["y"].count()
    means = d.groupby("g")["y"].mean()
    ss_between = sum(sizes[g] * (means[g] - grand) ** 2 for g in means.index)
    ss_within = sum(((d[d["g"] == g]["y"] - means[g]) ** 2).sum() for g in means.index)
    df_between, df_within = k - 1, n - k
    if df_within == 0 or df_between == 0:
        return np.nan
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    n0 = (n - sum(s ** 2 for s in sizes) / n) / df_between
    return max((ms_between - ms_within) / (ms_between + (n0 - 1) * ms_within), 0.0)


def p_label(p):
    if pd.isna(p):
        return ""
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def main():
    df = pd.read_csv(data("data_balance.csv"))
    print(f"data_balance.csv: {df.shape[0]} rows, "
          f"{df['District_ID'].nunique()} districts, {df['Estate_ID'].nunique()} estates")

    rows = []
    for v in SES_VARS:
        col = df[v].dropna()
        groups = [g[v].dropna().values for _, g in df.groupby("District_ID")
                  if g[v].dropna().shape[0] > 0]
        kw_H, kw_p = stats.kruskal(*groups)
        kw_df = df["District_ID"].nunique() - 1
        icc = icc_one_way(df[v], df["Estate_ID"])
        rows.append({
            "Variable": v,
            "N": int(col.shape[0]),
            "Overall Mean (SD)": f"{col.mean():.2f} ({col.std():.2f})",
            "KW H": round(kw_H, 2),
            "df": int(kw_df),
            "p (district)": p_label(kw_p),
            "ICC (estate)": round(icc, 3),
        })
    tab = pd.DataFrame(rows)
    tab.to_csv(results("Table_S12_Balance_Test.csv"), index=False, encoding="utf-8-sig")
    print("\n" + tab.to_string(index=False))

    df.groupby("District_ID")[SES_VARS].mean().round(2).to_csv(
        results("balance_test_district_means.csv"), encoding="utf-8-sig")

    # ---- cell-by-cell comparison with the published table --------------------
    cmp_rows = []
    max_abs = 0.0
    for _, r in tab.iterrows():
        v = r["Variable"]
        pub = PUBLISHED[v]
        rep_mean, rep_sd = [float(x) for x in
                            r["Overall Mean (SD)"].replace("(", "").replace(")", "").split()]
        checks = [
            ("N", pub["N"], r["N"]),
            ("Mean", pub["mean"], round(rep_mean, 2)),
            ("SD", pub["sd"], round(rep_sd, 2)),
            ("KW H", pub["KW_H"], r["KW H"]),
            ("p (district)", pub["p"], r["p (district)"]),
            ("ICC (estate)", pub["ICC"], r["ICC (estate)"]),
        ]
        for metric, published, reproduced in checks:
            try:
                diff = float(reproduced) - float(published)
            except (TypeError, ValueError):
                diff = np.nan
            match = (str(published).strip() == str(reproduced).strip()) or \
                    (not np.isnan(diff) and abs(diff) < 5e-3)
            if not np.isnan(diff):
                max_abs = max(max_abs, abs(diff))
            cmp_rows.append(dict(Variable=v, Metric=metric, Published=published,
                                 Reproduced=reproduced,
                                 Diff=("" if np.isnan(diff) else round(diff, 4)),
                                 Match=("YES" if match else "NO")))
    cmp = pd.DataFrame(cmp_rows)
    cmp.to_csv(os.path.join(VALIDATION_DIR, "balance_test_comparison.csv"),
               index=False, encoding="utf-8-sig")

    n_bad = (cmp["Match"] == "NO").sum()
    print(f"\n[validation] cells compared: {len(cmp)} | mismatches: {n_bad} | "
          f"max |diff|: {max_abs:.4g}")
    if n_bad:
        print(cmp[cmp["Match"] == "NO"].to_string(index=False))
        print("\n[validation] RESULT: MISMATCH -- see validation/balance_test_comparison.csv")
        sys.exit(1)
    print("[validation] RESULT: all 48 cells reproduce the published Table S12.")


if __name__ == "__main__":
    main()
