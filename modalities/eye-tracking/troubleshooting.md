# Eye-tracking troubleshooting

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## "Failed to start live stream" / general manager connection issues

- **Most reliable fix:** quit and restart Tobii Pro Eye Tracker Manager. This
  resolves a large fraction of connection / streaming problems.
- **Prevention:** join the unit's Wi-Fi _before_ launching the manager (see
  [pre-session.md](pre-session.md)).

## PC joined the wrong unit's Wi-Fi

- **Cause:** Multiple `TG03B-XXX...` networks visible; powered up multiple
  units at once.
- **Fix:** Power down all units, then power on one at a time, joining each
  PC to its assigned unit before bringing the next up.

## Recording unit will not power on

- **Cause:** Discharged battery; cable not seated; battery not properly inserted.
- **Fix:** Try a known-charged battery; reseat the HDMI-style cable between
  the glasses and the recording unit; press and **hold** the power button
  until the unit boots.

## Battery dies mid-session

- **Cause:** Battery life shorter than session, or battery wasn't fully charged.
- **Fix:** Swap battery; restart recording. **Record the swap timestamp on
  the canonical clock** in the run sheet — the gap is recoverable only with
  that timestamp.
- **Prevention:** Pre-session battery check; budget a fresh spare per unit.

## SD card not detected / recording fails to save

<!-- TODO(unassigned): Populate as encountered. Candidates: card not seated; card formatted wrong; card full. -->

## Calibration repeatedly fails

<!-- TODO(unassigned): Lighting, glasses fit, subject vision factors. -->
