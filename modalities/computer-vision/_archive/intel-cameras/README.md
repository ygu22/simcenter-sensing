# Intel cameras (archived)

> **Status:** archived
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

This directory preserves user-authored code from the prior computer-vision
workflow built on **Intel RealSense** cameras. **No active maintenance.** The
current CV platform is ZedBox — see [../../README.md](../../README.md).

## Source

Original working directory: `~/Documents/data_analysis_local/realSense/`

That directory contains ~141 GB of subject data (mp4 videos, landmark CSVs,
PNG frame sequences, `.bag` files) which **deliberately does not live here**.
The data stays in its original location under whatever IRB-appropriate
storage governs that study.

## Contents

| File                        | Purpose                                                   |
|-----------------------------|-----------------------------------------------------------|
| `RS_processing.ipynb`       | MediaPipe pose extraction prototype from a webcam stream. |
| `RS_bag_to_video.ipynb`     | Convert RealSense `.bag` recordings to mp4 + extract pose landmarks per frame. Outputs **stripped** at archival (37 image cells removed). |
| `requirements.txt`          | Python deps (Mediapipe, numpy, opencv-python, ipykernel). |

## What was deliberately not copied

- Any data file (mp4, png, csv, bag) — see [../../data-spec.md](../../data-spec.md)
  and [../../../../docs/data-governance.md](../../../../docs/data-governance.md)
- The `pings/`, `pings2/`, `pings3/`, `pings4/` PNG frame sequences (~36K files each)
- The `bags/` directory of RealSense native recordings
- The `rs_env/`, `rsProcessing/`, `python3.11/` virtualenvs

## Why kept

- Reproducibility for prior collections processed under this stack
- Reference for design decisions inherited by the current ZedBox stack
- Pose-extraction pattern (MediaPipe BlazePose 33-keypoint format) that may
  resurface in the ZedBox pipeline
