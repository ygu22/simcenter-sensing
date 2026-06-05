# Physio processing (cross-device)

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Pipeline overview

```
raw (device-native exports)
  → interim (decoded to per-device CSV/parquet with canonical-clock timestamps)
    → derived (cleaned, time-aligned, feature-extracted)
      → reports (QA HTML)
```

## Code locations

- `processing/` (to be populated) — physio-specific cleaning + feature extraction
- `shared/` — time alignment, generic sync helpers (canonical sync code lives here)

<!-- TODO(unassigned): The current canonical sync helpers live in tpd's 1_funcs_generic.R (~/Documents/data_analysis_local/tpd). Decide whether to migrate them in, vendor a copy, or treat tpd as the upstream source. -->

## Feature extraction

[HR / HRV bands, EDA tonic/phasic, accelerometry-derived activity, etc.]

## How to run

<!-- TODO(unassigned): CLI invocation against examples/data once example synthetic data is shipped -->
