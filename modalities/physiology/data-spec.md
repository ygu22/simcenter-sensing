# Physio data spec

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Raw (per device)

| Device       | Format           | Fields | Sample rate |
|--------------|------------------|--------|-------------|
| Empatica E4  | Zip of CSVs (BVP, EDA, TEMP, ACC, IBI, HR, tags) | per signal | per signal |
| EmotiBit     | Multiple CSVs by signal | per signal | per signal |
| BioRadio     | EDF / vendor CSV | ECG, respiration channels | per channel |

<!-- TODO(unassigned): Fill exact field names, units, and sample rates per device -->

## Interim

Unified schema across devices, with canonical-clock timestamps:

| Field          | Type   | Units     | Notes |
|----------------|--------|-----------|-------|
| `t_canonical`  | float  | seconds since session start | After sync |
| `device`       | string | —         | `e4` / `emotibit` / `bioradio` |
| `device_tail`  | string | —         | Last 4 of serial |
| `signal`       | string | —         | `bvp` / `eda` / `ecg` / etc. |
| `value`        | float  | per-signal| |

(Long-form preferred for cross-device joins. Wide-form derivable.)

## Derived

<!-- TODO(unassigned): Feature schema — HR (bpm), HRV time-domain (RMSSD, SDNN), HRV freq-domain (LF, HF, LF/HF), EDA tonic/phasic, activity. Window length, overlap, missing-value convention. -->

## Naming

Per [docs/identifiers.md](../../docs/identifiers.md):

```
<study>_<subject-or-team>_<session>[_<run>]_<device-tag>-<serial-tail>.<ext>
```
