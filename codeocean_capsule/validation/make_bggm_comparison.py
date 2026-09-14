#!/usr/bin/env python3
"""Generate the 05 BGGM cell-by-cell comparison CSVs for codeocean_capsule/validation/.
Compares the reproduced tables (currently in validation/) against the published
manuscript tables in Output/01-Env-health/Figures/.
Run from repo root.
"""
import pandas as pd, numpy as np, csv, os

PUB = "Output/01-Env-health/Figures"
NEW = "codeocean_capsule/validation"
OUT = "codeocean_capsule/validation"
domains = ["Mental_Health", "Physical_Health", "Social_Health"]

# tolerances (from codeocean_capsule memory note / manuscript precision)
TOL_POINT = 0.001   # Post.mean, Post.sd  -> reported to 3 dp
TOL_CRI   = 0.006   # credible-interval bounds

def w(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        cw = csv.writer(f)
        cw.writerow(header)
        cw.writerows(rows)
    print("wrote", path, f"({len(rows)} rows)")

# ---------------------------------------------------------------- Edge CrI
rows = []
for d in domains:
    p = pd.read_csv(f"{PUB}/Table_Edge_CrI_{d}.csv").set_index("Relation")
    n = pd.read_csv(f"{NEW}/Table_Edge_CrI_{d}.csv").set_index("Relation")
    common = p.index.intersection(n.index)
    for col, tol in [("Post.mean", TOL_POINT), ("Post.sd", TOL_POINT),
                     ("Cred.lb", TOL_CRI), ("Cred.ub", TOL_CRI)]:
        dd = (n.loc[common, col] - p.loc[common, col]).abs()
        nex = int((dd > tol + 1e-9).sum())
        rows.append([d, col, len(common), f"{dd.max():.4f}", f"{dd.mean():.5f}",
                     tol, nex, "YES" if nex == 0 else "NO"])
w(f"{OUT}/Table_Edge_CrI_comparison.csv",
  ["Domain", "Metric", "N_edges", "MaxAbsDiff", "MeanAbsDiff", "Tolerance", "N_exceed", "Match"],
  rows)

# ---------------------------------------------------------------- Predictability
rows = []
for d in domains:
    p = pd.read_csv(f"{PUB}/Table_Predictability_{d}.csv")
    n = pd.read_csv(f"{NEW}/Table_Predictability_{d}.csv")
    p = p.rename(columns={p.columns[0]: "idx"}).set_index("Node")
    n = n.set_index("Node")
    common = p.index.intersection(n.index)
    for col, tol in [("Post.mean", TOL_POINT), ("Post.sd", TOL_POINT),
                     ("Cred.0.5.", TOL_CRI), ("Cred.99.5.", TOL_CRI)]:
        dd = (n.loc[common, col] - p.loc[common, col]).abs()
        nex = int((dd > tol + 1e-9).sum())
        rows.append([d, col, len(common), f"{dd.max():.4f}", f"{dd.mean():.5f}",
                     tol, nex, "YES" if nex == 0 else "NO"])
w(f"{OUT}/Table_Predictability_comparison.csv",
  ["Domain", "Metric", "N_nodes", "MaxAbsDiff", "MeanAbsDiff", "Tolerance", "N_exceed", "Match"],
  rows)

# ---------------------------------------------------------------- Adjacency / edge selection
summ, churn = [], []
for d in domains:
    p = pd.read_csv(f"{PUB}/adj_matrix_BGGM_{d}_Pearson_Resid.csv", index_col=0)
    n = pd.read_csv(f"{NEW}/adj_matrix_BGGM_{d}_Pearson_Resid.csv", index_col=0)
    p.index = p.index.astype(str); p.columns = p.columns.astype(str)
    n.index = n.index.astype(str); n.columns = n.columns.astype(str)
    nodes = [x for x in p.index if x in n.index and x in p.columns and x in n.columns]
    P = p.loc[nodes, nodes].values.astype(float)
    N = n.loc[nodes, nodes].values.astype(float)
    iu = np.triu_indices(len(nodes), 1)
    Pv, Nv = P[iu], N[iu]
    pe, ne = Pv != 0, Nv != 0
    both = pe & ne
    agreed_maxdiff = np.abs(Nv[both] - Pv[both]).max() if both.any() else 0.0
    ch_mask = pe != ne
    ch_absw = np.concatenate([np.abs(Pv[pe & ~ne]), np.abs(Nv[ne & ~pe])])
    summ.append([d, len(nodes), int(pe.sum()), int(ne.sum()), int(both.sum()),
                 int(ch_mask.sum()),
                 f"{(ch_absw.max() if ch_absw.size else 0):.4f}",
                 f"{agreed_maxdiff:.4f}",
                 # PASS = agreed edge weights bit-faithful AND every churned edge is sub-threshold noise
                 "YES" if (agreed_maxdiff <= 0.001 and (ch_absw.size == 0 or ch_absw.max() < 0.05)) else "NO"])
    for a in range(len(nodes)):
        for b in range(a + 1, len(nodes)):
            pv, nv = P[a, b], N[a, b]
            if (pv != 0) != (nv != 0):
                churn.append([d, f"{nodes[a]}--{nodes[b]}",
                              "published-only" if pv != 0 else "reproduced-only",
                              f"{pv:+.4f}", f"{nv:+.4f}",
                              "yes" if nodes[a][0] != nodes[b][0] else "no"])
w(f"{OUT}/adj_matrix_comparison.csv",
  ["Domain", "N_nodes", "Edges_published", "Edges_reproduced", "Edges_agree",
   "Edges_churned", "Churned_max_abs_weight", "Agreed_edge_max_abs_diff", "Match"],
  summ)
w(f"{OUT}/adj_matrix_churned_edges.csv",
  ["Domain", "Edge", "Present_in", "Pcor_published", "Pcor_reproduced", "Cross_community"],
  churn)
