# Shared utilities

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

Cross-modality code used by more than one modality's processing pipeline.

## Planned contents

- `time_sync/` — Sync-marker detection, drift modeling, per-session sync report.
- `identifiers/` — Filename parsing/composing against the
  [identifiers convention](../docs/identifiers.md).
- `qa/` — Generic QA report scaffolding.

## Languages

R and Python both supported. Keep functionally equivalent versions in parallel
subdirectories (`shared/R/...`, `shared/python/...`) when both are needed.

## TODOs for collaborators

<!-- TODO(unassigned): Decide migration vs. vendoring strategy for tpd's `1_funcs_generic.R` sync helpers — see project memory project_tpd_upstream -->

- [ ] Migrate canonical sync helpers from tpd (or treat tpd as upstream)
- [ ] Implement filename parser/composer against identifiers.md
- [ ] Generic QA report template
