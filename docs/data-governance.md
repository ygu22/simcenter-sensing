# Data governance principles

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

This document captures _general principles_ for handling unobtrusive
measurement data. Study-specific governance (IRB protocol, consent language,
DUA terms) lives outside this repository.

## Principles

1. **Minimum necessary** — Collect only what the protocol requires; retain only
   as long as the protocol allows.
2. **Separation of identifiers** — Subject IDs used in this repo are study-local
   pseudonyms. The link table to real identifiers never lives in this repo and
   never lives alongside the data.
3. **Default deny on sharing** — Raw multimodal data (video especially) is
   re-identifiable; default to not sharing without explicit IRB cover.
4. **Document chain of custody** — Each session has a run sheet capturing who
   collected what, on which device, with which calibration state.
5. **Differential retention** — Raw video typically has the shortest retention
   horizon; derived features (e.g., pose keypoints, HRV time series) can often
   be retained longer.

## Modality-specific concerns

<!-- TODO(unassigned): Expand per-modality (video re-id risk, ECG identifiability via QT, etc.) — open issue when triaging Phase 1 -->

- **Computer vision** — Highest re-identification risk. Video data is treated as
  the most sensitive class.
- **Physiology** — Some signals (notably ECG) are identifiable; treat as PHI even
  when separated from other identifiers.
- **Eye tracking** — Gaze plus scene video is highly identifying.
- **Communication / audio** — Voice is biometric; transcripts may contain PHI
  spoken aloud.

## What this means for the repo

- No subject data, ever. See [scope.md](scope.md) and the PHI/PII checklist in
  [../CONTRIBUTING.md](../CONTRIBUTING.md).
- Examples use synthetic data only.
- Screenshots and figures must be scrubbed (synthetic subjects, mock IDs).
