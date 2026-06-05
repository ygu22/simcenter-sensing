# CV processing

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Pipeline overview

```
raw                       interim                      derived
─────────────             ──────────────               ────────────────────────
<serial>.svo2     →   (decoded via SDK)        →   fused_bodies.csv (3D kinematics)
                       per-camera body tracking      demo_camN.avi (2D overlays)
                       ↓                              head_crops/ (optional)
                       Fusion (multi-cam → world)
```

Body tracking runs once per camera client (publishing locally via shared
memory) and the Stereolabs Fusion module consumes those streams to produce
**fused 3D skeletons in world coordinates**. See:

- Multi-camera body tracking reference: <https://github.com/stereolabs/zed-sdk/blob/master/body%20tracking/multi-camera/python/fused_cameras.py>

## Code

See [code/README.md](code/README.md) for the file inventory. Core entry point:

```bash
conda activate ZED_env
cd modalities/computer-vision/code
# Edit USER CONFIG block at top of replay_fusion_enhanced.py
python replay_fusion_enhanced.py
```

User-config knobs (top of `replay_fusion_enhanced.py`):

- `SVO_FILES` — input SVO paths (one per camera)
- `FUSION_CONF` — path to the `fusion_calibration.json` saved by ZED360
  (see [pre-session.md](pre-session.md))
- `OUT_CSV` — destination for fused 3D bodies + kinematics
- `DEPTH_MODE` — `NEURAL` for accuracy, `PERFORMANCE` for speed
- `BODY_MODEL` — `HUMAN_BODY_FAST` / `MEDIUM` / `ACCURATE`
- `BODY_FORMAT` — `BODY_34` or `BODY_38`
- `WRITE_DEMO_VIDEOS`, `SAVE_HEAD_CROPS`, `RUN_GAZE_MODEL` — optional outputs

## Outputs

See [data-spec.md](data-spec.md).

## Synchronization

The fused 3D output carries SDK timestamps (`fused.timestamp.get_nanoseconds()`)
which are aligned across cameras by Fusion. To align with **other modalities**
(physio, eye-tracking) use the session sync markers per
[../../docs/time-sync.md](../../docs/time-sync.md).

## Open questions / TODOs

<!-- TODO(unassigned): Verify the BODY_34 / BODY_38 keypoint indices used in gaze_geometry.py match the deployed ZED SDK build; comment-pin the SDK version in that file. -->
<!-- TODO(unassigned): Replace the GazeEstimator placeholder with a chosen gaze model (Gaze360 candidate). Document training-domain assumptions and licensing in this file. -->
<!-- TODO(unassigned): Lift USER CONFIG out of replay_fusion_enhanced.py into a YAML/CLI interface so the script doesn't get hand-edited per run. -->
<!-- TODO(unassigned): The acceleration estimate in compute_vel_acc() returns zeros — needs a real second-difference or smoothed estimator using v_hist. -->
