# Eye-tracking during-session SOP

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Start of session

1. Confirm video is streaming live in Tobii Pro Eye Tracker Manager.
2. **Select recording mode** — _full analyses_ or _video only_ — based on the
   protocol's downstream needs. (Video-only is smaller; full analyses includes
   gaze and event data.)
3. **Enter the participant number** using the study pseudonym per
   [docs/identifiers.md](../../docs/identifiers.md). _Never use real names
   or MRNs._
4. **Click Start Recording.**
5. **Perform calibration** — see [pre-session.md](pre-session.md#calibration).
   Repeat until acceptable error is reached.
6. Capture the **opening sync marker** so it's visible in the scene camera
   (visible hand clap or flash; see [docs/time-sync.md](../../docs/time-sync.md)).
7. Note start timestamp on the canonical clock in the run sheet.

## Throughout the session

Monitor:

- **Battery** — swap when low. Mid-session battery swaps stop recording on
  the unit; document any swap timestamp in the run sheet so the gap is
  recoverable downstream.
- **Storage** — usually ample, but verify per the SD card capacity in
  [hardware.md](hardware.md).
- **Wi-Fi link** — manager UI surfaces connection state; brief dropouts are
  common but should self-recover. If they don't, see [troubleshooting.md](troubleshooting.md).

<!-- TODO(unassigned): Document what is monitorable purely from the manager UI vs. what requires looking at the recording unit's own LEDs. -->

## End of session

1. Capture the **closing sync marker**.
2. Click _Stop Recording_ in the manager.
3. Confirm the recording appears in the manager's session list with the
   expected duration.
4. Note end timestamp on the canonical clock in the run sheet.

## Data retrieval

Two options — pick per-session based on file size and bandwidth:

- **SD card pull** — remove the SD card from the recording unit and copy
  files via a card reader on the host PC. Faster for large recordings.
- **Wi-Fi download** — download via Tobii Pro Eye Tracker Manager over the
  unit's Wi-Fi. Slower for large recordings but does not require physical
  access to the SD card.

After retrieval, rename to the canonical filename per
[docs/identifiers.md](../../docs/identifiers.md) and store per
[docs/storage.md](../../docs/storage.md).

<!-- TODO(unassigned): Capture the file types / directory layout that Tobii produces (gaze data, scene video, IMU, audio, project file) — populate data-spec.md. -->
