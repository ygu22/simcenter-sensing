# Identifier conventions

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

Consistent IDs are the backbone of multimodal data. These conventions apply
across modalities so files produced by different sensors can be joined
unambiguously.

## ID hierarchy

```
Study      →  one funded project / IRB protocol
  Cohort   →  optional grouping (e.g., year, condition)
    Subject (or Team) →  one consented unit
      Session         →  one continuous data-collection event
        Run           →  one segment within a session (optional)
          Device      →  one physical sensor instance
```

## Recommended ID format

| Level    | Format               | Example          | Notes |
|----------|----------------------|------------------|-------|
| Study    | UPPERCASE-SLUG       | `PICU-CAL`       | Stable across years. |
| Cohort   | YYYY or label        | `2026A`          | Optional. |
| Subject  | `S###`               | `S042`           | Study-local pseudonym only. |
| Team     | `T###`               | `T007`           | When the unit is a team. |
| Session  | `YYYYMMDD-HHMM`      | `20260601-0930`  | Local time of session start. |
| Run      | `R##`                | `R02`            | Optional segment within session. |
| Device   | `<modality>-<serial-tail>` | `e4-A8F2` | Last 4 chars of device serial. |

Compose filenames as: `<study>_<subject-or-team>_<session>[_<run>]_<device>.<ext>`.

Example: `PICU-CAL_T007_20260601-0930_R02_e4-A8F2.csv`

## Rules

1. **No real identifiers**, ever — names, MRNs, DOBs, emails.
2. **Pseudonyms are study-local** — `S042` in HERA is not the same person as
   `S042` in PICU-CAL.
3. **Time in filenames is local clock at session start** — _not_ device clock,
   which may drift. See [time-sync.md](time-sync.md).
4. **Device tail keeps device-attribution traceable** without exposing full
   serials in public-facing data.

