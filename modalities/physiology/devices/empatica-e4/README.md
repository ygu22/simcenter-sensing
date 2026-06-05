# Empatica E4

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Hardware

- Wrist-worn wearable
- Signals: BVP (PPG-derived), EDA, skin temp, 3-axis accelerometer, IBI, HR
- Sample rates: <!-- TODO(unassigned): fill -->

## Firmware versions tested

<!-- TODO(unassigned): List firmware versions and known compatibility notes -->

## Charging

<!-- TODO(unassigned): Charging time, dock specifics, indicator behavior -->

## Fitting protocol

1. Wipe the wrist with [skin-prep agent].
2. Fasten band [snug but not tight; describe tightness check].
3. Verify EDA signal stabilizes within [X seconds] before starting session.

<!-- TODO(unassigned): Detail the fitting procedure; capture what "good" fitting looks like via the streaming app -->

## Pairing and time sync

<!-- TODO(unassigned): Pairing flow with E4 Manager / E4 streaming server, how clock is set, expected offset/drift -->

## Data offload

- Files produced per session: zip containing per-signal CSVs (`BVP.csv`, `EDA.csv`,
  `TEMP.csv`, `ACC.csv`, `IBI.csv`, `HR.csv`, `tags.csv`)
- Filename conversion to project convention: <!-- TODO -->

## Known issues

<!-- TODO(unassigned): EDA flatlines, band slippage, BVP saturation under bright light, etc. -->
