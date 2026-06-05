# CV during-session SOP

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Recording

Recording is driven by `code/multiCameraRecord.py`, which starts one capture
thread per detected ZED camera and writes one `.svo2` per camera (H.265
compression) into `~/zed_rec/`. See also the Stereolabs reference example:

- <https://github.com/stereolabs/zed-sdk/tree/master/recording/recording/multi%20camera/python>

## Start of session

1. Confirm canonical-clock timestamp in the run sheet.
2. Capture the **opening sync marker** so it's visible in every camera's field
   of view (hand clap or flash — see [../../docs/time-sync.md](../../docs/time-sync.md)).
3. Start the recorder:

   ```bash
   conda activate ZED_env
   cd path/to/this/repo/modalities/computer-vision/code
   python multiCameraRecord.py
   ```

4. Confirm in the console that one "recording to ..." line prints per camera.
   If any camera is missing, **stop and resolve** before the subject enters —
   see [troubleshooting.md](troubleshooting.md).
5. Note the file paths (one per camera serial) in the run sheet.

## Monitoring during session

- The recorder runs headless — no GUI; only the console output indicates progress.
- Disk fill: pre-session size estimate (see [pre-session.md](pre-session.md))
  should be well under available space, but spot-check disk usage on a long session.
- Battery / UPS state of the ZedBox if applicable.

<!-- TODO(unassigned): Add a small monitor script that tails disk usage / writes a heartbeat — currently the operator has no in-session signal-quality indicator. -->

## End of session

1. Capture the **closing sync marker**.
2. Stop the recorder with `Ctrl+C`. The script handles SIGINT and writes
   `[serial] stopped` per camera as it closes.
3. Confirm `~/zed_rec/<serial>.svo2` exists for every expected camera; note
   sizes and durations in the run sheet.
4. Rename / move the SVOs to study-canonical paths per
   [../../docs/identifiers.md](../../docs/identifiers.md) and
   [../../docs/storage.md](../../docs/storage.md).
5. Verify each SVO opens in playback before declaring the session captured.

<!-- TODO(unassigned): Codify the rename step into a small helper that applies the canonical filename convention; lives in shared/ when written. -->
