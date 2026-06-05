# STAGING (private workspace)

This directory exists locally as a place to drop fragmented source material
(notes from Joplin, code from prior repos, screenshots-to-redact) before
sorting it into the public structure.

**Everything in here is gitignored** except this README. See `.gitignore`:

```
STAGING/*
!STAGING/README.md
```

## How to use

1. Dump material in subdirs by modality: `STAGING/cv/`, `STAGING/physio/`, etc.
2. Triage during a working session — decide what belongs public, what needs
   redaction, what's discardable.
3. Move public-ready material into the matching `modalities/*/` location and
   delete from STAGING when done.

## What does **not** go here

- Any data file containing subject identifiers — those don't belong on a public
  repo's filesystem at all, even gitignored. Keep those in your secure storage
  per [docs/storage.md](../docs/storage.md).
- Long-term reference material. STAGING is transient.
