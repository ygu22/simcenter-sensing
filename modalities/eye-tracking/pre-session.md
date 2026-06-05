# Eye-tracking pre-session setup

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## One-time setup

Install **Tobii Pro Eye Tracker Manager** on the host PC. No license required:

- <https://connect.tobii.com/s/g3-downloads?language=en_US>

## Per-session startup sequence

The order below is empirically the most reliable.

1. **Power up the recording unit** — insert battery, connect glasses to the
   recording unit via the HDMI-style cable, then press and hold the power
   button until the unit boots.
2. **Join the unit's Wi-Fi network** _before launching the manager_. The
   networks are labelled `TG03B-XXXXXXXXXX` (where the suffix is the unit
   serial). Default password: `TobiiGlasses` (see warning in
   [hardware.md](hardware.md#default-credentials)).
3. **Launch Tobii Pro Eye Tracker Manager** _after_ the PC has joined the
   unit's Wi-Fi.

### Multi-unit sessions

When running more than one Glasses 3 unit in the same session:

- **Power up units one at a time** so it's unambiguous which `TG03B-XXX...`
  network belongs to which subject.
- **Connect each PC** to its assigned unit's Wi-Fi before launching that PC's
  manager.

## Pre-recording checklist

- [ ] Battery installed and fully charged
- [ ] SD card seated and confirmed (capacity TODO — see [hardware.md](hardware.md))
- [ ] Glasses connected to recording unit via cable
- [ ] PC joined to the correct `TG03B-XXX...` network
- [ ] Tobii Pro Eye Tracker Manager launched and showing live video stream
- [ ] Session ID + subject pseudonym recorded per [docs/identifiers.md](../../docs/identifiers.md)
- [ ] Canonical-clock timestamp captured for cross-modality sync (see [docs/time-sync.md](../../docs/time-sync.md))

## Calibration

<!-- TODO(unassigned): Detail the calibration target, distance, and the manager's calibration sequence. Note acceptable error thresholds before proceeding to record. -->

Calibration is performed once video is streaming reliably and the recording
mode has been selected (see [during-session.md](during-session.md)).
