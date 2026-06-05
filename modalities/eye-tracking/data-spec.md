# Eye-tracking data spec

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Raw

Tobii Pro Glasses 3 produces a per-recording bundle. Exact contents depend on
the selected recording mode (_full analyses_ vs _video only_).

<!-- TODO(unassigned): Enumerate exact files produced per recording (scene mp4, audio, gaze JSON/TSV, IMU, events, calibration metadata, project file). Capture from a representative pilot recording. -->

| File / stream         | Format | Notes |
|-----------------------|--------|-------|
| Scene video           | mp4    | **Re-identifiable** (first-person view); treat as PHI. |
| Audio                 | TODO   | Voice is biometric; same treatment as scene video. |
| Gaze data             | TODO   | Per-sample gaze 2D/3D, pupil, validity. |
| IMU                   | TODO   | Useful for head-motion sync markers. |
| Events / metadata     | TODO   | Recording start, calibration result, etc. |

## Interim

<!-- TODO(unassigned): Define after processing pipeline is chosen — see processing.md. -->

## Derived

<!-- TODO(unassigned): Fixations, saccades, gaze-on-object (if scene-aware analysis is done). -->

## Naming

Per [../../docs/identifiers.md](../../docs/identifiers.md):

```
<study>_<subject-or-team>_<session>[_<run>]_et-<unit-tail>.<ext>
```

Use the last 4 of the Tobii unit's serial as `<unit-tail>` to disambiguate
multi-unit sessions.
