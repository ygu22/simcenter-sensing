# Time synchronization across modalities

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

Multimodal analysis lives or dies on accurate time alignment. This document
covers the conventions and procedures for keeping clocks aligned across
sensors, and the file-level metadata required to verify alignment after the
fact.

## Clock sources at a glance

| Device family   | Clock source             | Typical drift / offset | Sync strategy |
|-----------------|--------------------------|-------------------------|---------------|
| ZedBox          | TBD                      | TBD                     | TBD           |
| Empatica E4     | Device RTC, set at pair  | ~seconds per hour       | Set RTC against NTP host immediately before session |
| EmotiBit        | TBD                      | TBD                     | TBD           |
| BioRadio        | TBD                      | TBD                     | TBD           |
| Tobii           | TBD                      | TBD                     | TBD           |

<!-- TODO(unassigned): Fill the table above with measured drift/offset values per device — open issue per device -->

## Required pre-session sync steps

1. **Pick one canonical clock** for the session — typically a laptop running NTP.
2. **Set every device's RTC** against the canonical clock immediately before fitting.
3. **Record the offset** (canonical − device) at fit time _and_ at unfit time so
   linear drift can be modeled.
4. **Capture a sync marker** in every modality at session start and session end
   (see below).

## Sync markers

A sync marker is a deliberate, visible/audible/measurable event that can be
detected in every modality:

- Hand clap or wrist tap visible on camera and detectable in accelerometer
- Bright flash + audible tone for camera + audio + (if available) ambient sensor

Record the canonical-clock timestamp of each marker in the session run sheet.

## Verification after the fact

`shared/time_sync/` contains (or will contain) utilities to:

- Detect sync markers automatically in each modality
- Compute residual offset and linear drift
- Emit a per-session sync report

<!-- TODO(unassigned): Migrate canonical sync helpers from tpd's 1_funcs_generic.R; see project memory project_tpd_upstream -->
