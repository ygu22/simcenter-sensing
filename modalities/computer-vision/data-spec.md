# CV data spec

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Raw

| File ext              | Source              | Notes |
|-----------------------|---------------------|-------|
| `.svo2`               | ZED SDK recording   | Stereo + depth, H.265-compressed by `multiCameraRecord.py`. Gitignored. One file per camera per session. |
| `fusion_calibration.json` | ZED360 export   | Multi-camera extrinsics. Per-camera-setup, regenerated on any geometric change. **Not subject data** but typically kept with the session for reproducibility. |

## Interim

Not currently a distinct stage — `replay_fusion_enhanced.py` consumes raw SVOs
and emits derived outputs directly.

<!-- TODO(unassigned): If a decoded/per-frame interim becomes useful (e.g., to share frames with another modality's pipeline), define its schema here. -->

## Derived

### `fused_bodies.csv`

Long-form-ish per-detected-body-per-frame. Column groups:

| Column                                       | Type   | Units                | Notes |
|----------------------------------------------|--------|----------------------|-------|
| `timestamp_ns`                               | int    | nanoseconds (SDK clock) | Fused-frame timestamp |
| `person_id`                                  | int    | —                    | Stable across frames (Fusion tracking) |
| `confidence`                                 | float  | 0-100                | SDK body confidence |
| `tracking_state`                             | int    | enum                 | SDK tracking-state enum |
| `k{i}_x`, `k{i}_y`, `k{i}_z`                 | float  | meters (world)       | Keypoint `i`. K=34 or 38 depending on `BODY_FORMAT`. |
| `k{i}_vx`, `k{i}_vy`, `k{i}_vz`              | float  | m/s                  | Finite-difference velocity, median-smoothed over short history. |
| `k{i}_ax`, `k{i}_ay`, `k{i}_az`              | float  | m/s²                 | Currently emitted as zeros — see processing.md TODOs. |
| `head_x`, `head_y`, `head_z`                 | float  | meters (world)       | Head-frame origin, from `compute_head_frame_world()`. |
| `gaze_dx`, `gaze_dy`, `gaze_dz`              | float  | unit vector (world)  | Head-forward direction (heuristic; not eye-tracker gaze). |

Missing-value convention: `NaN` for head/gaze when head-frame computation
fails (see `quality` flag values in `gaze_geometry.py`).

Coordinate system: `RIGHT_HANDED_Z_UP` (set in `init_fusion()`).

### `demo_camN.avi`

Per-camera annotated MJPEG video with local 2D skeleton overlay and (when
projected) red gaze-arrow rays. **Re-identifiable** (contains video of
subjects) — treat as raw-subject-data tier per
[../../docs/data-governance.md](../../docs/data-governance.md).

### `head_crops/`

Heuristic upper-body bounding-box crops resized to 224x224. Same
re-identification status as `demo_camN.avi`.

## Naming

Per [../../docs/identifiers.md](../../docs/identifiers.md):

```
<study>_<subject-or-team>_<session>[_<run>]_cv-<serial-tail>.svo2
```

For derived outputs, drop the per-camera tail since they're fused across cameras:

```
<study>_<subject-or-team>_<session>[_<run>]_cv-bodies.csv
```

<!-- TODO(unassigned): Wire the renaming into shared/identifiers/ helpers when those exist; the recorder currently writes `<serial>.svo2` only. -->
