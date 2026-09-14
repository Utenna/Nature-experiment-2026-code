# Code Ocean upload — checklist

This folder (`codeocean_capsule/`) is the thing to upload. It is **not** tracked
by this repo; move or copy it into the code repo / upload it as-is.

## Status of each piece

| piece | state |
|---|---|
| `data/data_balance.csv`, `data_analysis.csv`, `codebook.csv` | ✅ generated + verified (de-identified; no names, no CJK, no free text) |
| `code/00_prepare_deidentified_data.py` | ✅ provenance script; ran clean; **not** part of `run` |
| `code/01_balance_test.py` | ✅ runs; reproduces all 48 cells of Supplementary Table S12 |
| `code/02_icc_check.R` … `05_bggm_network.R`, `lib/00_load.R` | ✅ 01/02/03/05 run clean on Code Ocean (2026-09) — see validation/ |
| `code/06_dag.md` | ⚠️ SOURCE ONLY, converted from `.R` 2026-09-11 — `run` does not execute it (~30 h at published settings, exceeds a single CO session). Mental Health PHASE 2 independently verified; see README "Step 06" section |
| `environment/` (Dockerfile, requirements.txt, install.R) | ⚠️ drafted; pins `pandas/numpy/scipy` + `BGGM 2.1.1` + `lavaan 0.6-19`; rest via dated PPM snapshot |
| `private/estate_id_map.csv`, `district_id_map.csv` | ✅ written to repo-root `private/`, git-ignored — **never upload** |

## Before uploading

1. **Smoke-test R locally.** In RStudio, `setwd()` to `codeocean_capsule/code/`
   (running from the repo root also works — the scripts find their own folder):
   ```r
   setwd("path/to/codeocean_capsule/code")
   source("02_icc_check.R")          # fast; fills validation/icc_comparison.csv
   source("03_reliability_cfa.R")    # ~1 min
   Sys.setenv(QUICK = "1")
   source("04_sem_mediation.R"); source("05_bggm_network.R")
   ```
   06_dag.md's R code (copy the fenced block out to a `.R` file first — `run`
   never sources it) needs its own multi-hour/multi-session pass, not a quick
   local smoke test; see the README "Step 06" section.
   Outputs go to `codeocean_capsule/results/` (override with `CO_RESULTS`).
   Fix any package / API snags, then re-run `04–05` without `QUICK` for the
   record. Confirm outputs match the manuscript tables; note any gap.

2. **Lock the R environment (recommended).** In the private analysis project:
   `renv::init(bare = TRUE)` → install the packages from `install.R` →
   `renv::snapshot()`. Drop the resulting `renv.lock` into `environment/` and
   switch the Dockerfile to `renv::restore()` (commented stanza already there).

3. **Fill `metadata/metadata.yml`** TODOs — keep authors redacted until
   acceptance; set license.

4. **Re-scan for identifiers** (from repo root):
   ```bash
   grep -rnE 'R_[A-Za-z0-9]{15,17}|[一-龥]|Data/Raw|<your name>' codeocean_capsule/data codeocean_capsule/code
   ```
   Expect only: the raw filename in `00_prepare_*.py` comments (provenance).

5. **Compute strategy (D7) — SETTLED:** the full run is ~35 h wall clock
   (01–04 < 10 min, 05 ~5 h, 06 ~30 h), which exceeds a single Code Ocean
   session (10 h quota) and most verification wall clocks. `code/run` therefore
   **defaults to `QUICK=1`**: a reduced-resampling pass that runs the whole
   pipeline (01–06, all 3 domains, both phases) in minutes and lets a headless
   Reproducible Run complete. `QUICK=0` = published settings, to be run locally /
   on HPC. Full-precision comparison vs. the manuscript is archived in
   `validation/` (05 to ≤0.001; 06 Mental-Health PHASE 2 identical). When
   contacting Code Ocean support, ask them to confirm this arrangement is
   acceptable for verification rather than only asking for more compute hours.

## Upload

1. Code Ocean → **New Capsule → Copy from local** (not "Import from Git").
   Upload the contents of `code/` into the capsule's `code/`.
2. **Add Data Asset:** upload `data/` (the 3 CSVs + `README.md`); attach it so it
   mounts at `/data`.
3. **Environment:** either upload `environment/Dockerfile` (+ `renv.lock` if made)
   or recreate the lists in the CO environment editor.
4. Set run parameter `QUICK` (default `0`; `1` for the fast path). No core-count
   parameter is needed — every resampling step is single-threaded and seeded,
   so results do not depend on the capsule's core count.
5. **Reproducible Run.** Check `/results` + `/results/validation`. `01` and `02`
   fail the run on an unexplained mismatch; `06` writes
   `stability_cs_comparison.csv` (reproduced CS vs the published 0.75) as a
   soft check.
6. Keep the capsule **private**; generate the anonymous reviewer link through the
   Nature Cities / Springer Nature submission system. Publish (mint DOI) only at
   acceptance, then de-redact `metadata.yml` and `CONVERSION_NOTES.md`.

## Regenerating the data (authors only)

```bash
python codeocean_capsule/code/00_prepare_deidentified_data.py
# needs Data/Raw/merged_data0925.xlsx + Data/Processed/Data_Forked_Step4.RData
# WINSORIZE=1 to also top/bottom-code Age & LivArea (off by default; see README)
```
