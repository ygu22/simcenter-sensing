# Data storage conventions

> **Status:** stub
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

Generic conventions for organizing data outside this repository. Study-specific
paths are intentionally _not_ documented here (public repo).

## Layers

```
raw/        Untouched device exports
interim/    Reformatted / decoded, no scientific decisions yet
derived/    Cleaned, time-aligned, feature-extracted
reports/    Per-session QA reports
```

## Per-session directory layout (recommended)

```
<study>/
  <subject-or-team>/
    <session>/
      raw/
        <modality>/
          <files using the naming convention from identifiers.md>
      interim/
      derived/
      reports/
        sync.html
        qa.html
      run_sheet.md     # The during-session log, see modalities/*/during-session.md
```

## Naming

See [identifiers.md](identifiers.md) for the canonical filename format.

## Retention and backup

These decisions are study-specific (IRB-driven) and intentionally not codified
here. The repo's role is to ensure data _can_ be located and audited; the
actual retention schedule lives in study documentation.

## What goes in this repo vs. on disk

| Lives in repo                          | Lives outside repo                      |
|----------------------------------------|------------------------------------------|
| Code that produces derived/ from raw/  | Anything in raw/, interim/, derived/    |
| Schemas for derived/ outputs           | Reports with subject-identifying content |
| Synthetic example data in `examples/`  | Real subject data of any kind           |
