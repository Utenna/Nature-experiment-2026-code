# validation/

Reference copies of the cell-by-cell comparison CSVs. A live run writes the raw
result tables to `/results/` (and, for the self-checking scripts, comparison CSVs
to `/results/validation/`); the copies committed here are the values obtained
when the capsule was assembled.

## Script self-checks

- `balance_test_comparison.csv` — `01_balance_test.py`: reproduced vs published
  Supplementary Table S12 (48 cells, all match).
- `icc_comparison.csv` — `02_icc_check.R`: between-estate ICC, R one-way vs Python
  one-way vs published S12. `ICC_R_oneway` shows `(pending R run)` until
  `02_icc_check.R` is executed on the target machine.
- `stability_cs_comparison.csv` — `06_dag.md` PHASE 3: bridge-EI case-dropping
  CS-coefficient (per network) vs the published 0.75. `CS_reproduced` shows
  `(pending R run)` until PHASE 3 is executed (its code is no longer run by
  `code/run` at all — see the capsule README "Step 06" section — so this stays
  pending indefinitely unless someone runs `06_dag.md`'s code manually). Soft
  check — prints a NOTE but does not fail the run if a value differs.
  Seed-robust by construction: bridge-EI stability saturates the
  `corStability` grid ceiling (`caseMax = 0.75`), so the reported CS = 0.75
  does not depend on the bootstrap RNG.

## 06 DAG (PHASE 2) — partial reproduction against the published tables

Converted to `code/06_dag.md` 2026-09-11 (source kept verbatim, no longer run
by `code/run` — see the capsule README "Step 06" section). PHASE 2
(`bnlearn::boot.strength`, `pc.stable`, `alpha = 0.01`,
`set.seed(999)`, R = 500) is fully deterministic. It was run on Code Ocean
(interactive workstation, 2026-09-11); the free-tier compute/time budget was
exhausted after the **Mental Health** network, so only that domain's outputs are
archived here:

- `Sensitivity_Table_Mental_Health.csv` — edge count at thresholds
  0.70/0.75/0.80/0.85/0.90/0.95/0.98 = **119 / 113 / 107 / 98 / 92 / 86 / 76**,
  **identical** to `Output/01-Env-health/Figures/Sensitivity_Table_Mental_Health.csv`
  (the capsule script omits only the cosmetic `Description` label column).
- `DAG_Arrows_0.7_Mental_Health.csv` (119 arcs), `DAG_Arrows_0.75_Mental_Health.csv`
  (113 arcs), `DAG_AvgNetwork_0.70_Mental_Health.csv`, `Boot_Object_Mental_Health.rds`
  — arc counts consistent with the sensitivity table.

Physical Health and Social Health PHASE 2, and PHASE 3 stability for all three
networks, were **not** re-run on Code Ocean: at the published settings script 06
alone is ~30 h wall clock, beyond a single Code Ocean session. They use the
identical, seeded code path; with the pinned package versions (`bnlearn 5.0.1`,
`bootnet 1.6`) a `QUICK=0` run — local or on an HPC node — reproduces them
bit-for-bit. The headless capsule run (`code/run`) executes all three domains
and both phases; it defaults to `QUICK=1` (reduced resampling, finishes in
minutes) so a Code Ocean Reproducible Run completes inside the run-time limit.

## 05 BGGM network — comparison against the published tables

`05_bggm_network.R` has no built-in self-check (its outputs are large tables, not
scalar constants). These CSVs were produced post-hoc by
`make_bggm_comparison.py` (repo-side only — it diffs the reproduced tables
against `Output/01-Env-health/Figures/`, which is not part of the capsule).

Reproduced from a full `iter = 5000` run on Code Ocean (interactive workstation),
`PRED_ITER = 2500`, RNG-aligned code, 2026-09-09.

- `Table_Edge_CrI_comparison.csv` — per domain × metric, over all 1378 edges:
  `Post.mean` / `Post.sd` max |Δ| = **0.001** (tol 0.001), credible-interval
  bounds max |Δ| = **0.003** (tol 0.006). All 12 rows `Match = YES`.
- `Table_Predictability_comparison.csv` — per domain × metric, over all 53 nodes:
  Bayesian R² `Post.mean` / `Post.sd` max |Δ| = **0.001**, CrI bounds max |Δ| =
  **0.002**. All 12 rows `Match = YES`. (Held even with `PRED_ITER = 2500`.)
- `adj_matrix_comparison.csv` — signed partial-correlation adjacency after the
  `cred = 0.99` selection. **Agreed-edge weights** reproduce to max |Δ| =
  **0.0002**. Edge *selection* churns 2–4 edges per domain (Mental 4, Physical 2,
  Social 3); `Match = YES` because every agreed edge is bit-faithful and every
  churned edge is sub-threshold noise (see below).
- `adj_matrix_churned_edges.csv` — the 9 individual edges that flip in/out of the
  `cred = 0.99` network. Every one has |partial r| ∈ [0.043, 0.045], i.e. sitting
  exactly on the 99 % credible-interval threshold; 2 of the 9 are cross-community
  (Mental E4–M6, E19–M4). This is the inherent non-determinism of hard-
  thresholding a Bayesian credible interval under finite MCMC — no edge reported
  or discussed in the manuscript is affected, and network structure /
  interpretation is unchanged.

`Table_Bridge_Metrics_<domain>.csv` (in `/results/`, not diffed here) is derived
deterministically from the adjacency matrix, so it inherits the fidelity above;
the only sensitivity is a ≤ 0.045 shift in a node's Bridge-EI if one of the two
cross-community churned edges touches it.
