# Eye tracking

> **Status:** drafted (setup) / stub (processing)
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Scope

Gaze, fixation, and scene video from wearable **Tobii Pro Glasses 3** worn by
subjects during simulation sessions.

## Current platform

Tobii Pro Glasses 3 — wearable eye tracker with onboard recording unit
(battery + SD card), driven from a host PC via **Tobii Pro Eye Tracker
Manager** (a.k.a. "Glasses 3 manager") over the glasses' built-in Wi-Fi.

## Vendor references

- Tobii Pro Eye Tracker Manager download (no license required):
  <https://connect.tobii.com/s/g3-downloads?language=en_US>

## Section status

| Section          | File                                       | Status      |
|------------------|--------------------------------------------|-------------|
| Hardware         | [hardware.md](hardware.md)                 | drafted     |
| Pre-session      | [pre-session.md](pre-session.md)           | drafted     |
| During-session   | [during-session.md](during-session.md)     | drafted     |
| Troubleshooting  | [troubleshooting.md](troubleshooting.md)   | drafted     |
| Processing       | [processing.md](processing.md)             | stub        |
| Data spec        | [data-spec.md](data-spec.md)               | stub        |

## TODOs for collaborators

- [ ] Document calibration procedure in detail (board / target, acceptable error)
- [ ] Quantify per-hour storage use on the recording unit's SD card
- [ ] Define the Wi-Fi-download vs. SD-pull decision (when to use which)
- [ ] Fill `processing.md` and `data-spec.md` once a processing pipeline is chosen
- [ ] Capture battery-swap mechanics in [hardware.md](hardware.md) (mid-session swap procedure)
