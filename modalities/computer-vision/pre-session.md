# CV pre-session setup

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Python environment (one-time setup)

The ZedBox uses a conda environment named `ZED_env` containing the ZED SDK
Python bindings (`pyzed`). Follow Stereolabs' guide:

- <https://www.stereolabs.com/docs/development/python/virtual_env>

`code/`-side scripts in this repo (see [code/README.md](code/README.md)) import
`pyzed.sl`, `numpy`, `cv2`. The full dependency list is captured in
`code/requirements.txt` (TODO: extract).

<!-- TODO(unassigned): Produce a `code/environment.yml` so the env is reproducible from a single file. -->

## ZedBox startup checklist

```bash
# 1. Activate the ZED conda environment
conda activate ZED_env

# 2. Change to the ZED tools directory
cd /usr/local/zed/tools

# 3. Verify the cameras are detected
ZED_Explorer
```

`ZED_Explorer` opens a GUI showing connected ZED cameras and their serials.
**Record each camera's full serial in the run sheet** — the recording and
fusion code identifies cameras by serial.

## Per-session checklist

- [ ] ZedBox booted and reachable (or you're working at its console)
- [ ] `conda activate ZED_env` succeeded
- [ ] `ZED_Explorer` shows all expected cameras
- [ ] Disk has capacity for the full session recording (see size estimate below)
- [ ] Lenses clean
- [ ] Room lighting matches documented level (see [hardware.md](hardware.md))
- [ ] **Fusion calibration current** — see ZED360 procedure below
- [ ] ZedBox clock synced against canonical clock — see [../../docs/time-sync.md](../../docs/time-sync.md)
- [ ] Session ID created per [../../docs/identifiers.md](../../docs/identifiers.md)

## ZED360 fusion calibration

Multi-camera body tracking requires extrinsic calibration across cameras.
Use Stereolabs' **ZED360** tool:

1. Position cameras to their final mounted locations (calibration is geometry-
   sensitive — moving a camera after calibrating invalidates it).
2. Launch ZED360 from `/usr/local/zed/tools/`.
3. Walk through the calibration procedure (subject moves through overlapping
   coverage zones until ZED360 reports convergence).
4. **Save the calibration file** — this is the `fusion_calibration.json`
   referenced by `code/replay_fusion_enhanced.py` (`FUSION_CONF` constant).
5. Record the calibration date and the path to the saved JSON in the run sheet.

Recalibrate whenever cameras are moved, bumped, or removed/replaced.

<!-- TODO(unassigned): Document the convergence criteria ZED360 uses, expected calibration duration, and how to verify the calibration sanity-check before a session. -->

## Disk size estimate

<!-- TODO(unassigned): Quantify GB/hour at the chosen resolution + FPS + compression (H.265 in multiCameraRecord.py). Capture from a representative pilot session. -->

## Pre-session test recording

Before the real session, run a brief test capture:

```bash
python code/multiCameraRecord.py
# Ctrl+C after a few seconds; confirm one .svo2 per camera written to ~/zed_rec/
```

Verify the files open in ZED_Explorer or the SDK playback tools before the
subject arrives.
