# Physio during-session SOP (cross-device)

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Start of session

- [ ] All devices recording, confirmed via per-device status indicator
- [ ] Sync marker captured across all devices (accelerometer-detectable preferred)
- [ ] Run sheet: device assignments, start timestamp on canonical clock

## Monitoring

<!-- TODO(unassigned): What can be monitored remotely (battery, signal quality) vs. requires room access -->

## Mid-session interventions

- Battery / sensor failure: document fully in the run sheet, including any
  reattachment timestamp on canonical clock.
- Re-syncing after reattach: see [docs/time-sync.md](../../docs/time-sync.md).

## End of session

- [ ] Closing sync marker
- [ ] Stop recording on each device
- [ ] Record end timestamp on canonical clock and unfit-time device offsets
- [ ] Initial offload per device protocol
