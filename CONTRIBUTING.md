# Contributing

Thanks for working on this repo. A few conventions to know before you start.

## Before you push: the PHI/PII checklist

This repository is **public**. Before pushing _any_ change:

- [ ] No subject names, MRNs, emails, or other identifiers anywhere (including code comments, examples, screenshots, logs, commit messages)
- [ ] No raw subject data of any kind (video, physio waveforms, eye-tracking gaze, audio, transcripts)
- [ ] No IRB protocol text or consent forms with institution-specific identifiers
- [ ] No internal hostnames, IP addresses, share paths, or credentials
- [ ] Any sample data is synthetic _or_ fully consented for public release
- [ ] Screenshots are scrubbed of identifying information

If unsure, drop the material in `STAGING/` (gitignored) and ask in PR review.

The PR template includes this checklist; PRs cannot merge until it is completed.

## Section status convention

Each major doc declares its status at the top:

```
> **Status:** stub | drafted | reviewed | complete | archived
> **Owner:** @githubhandle  (or "unassigned")
> **Last reviewed:** YYYY-MM-DD
```

Statuses:

- **not started** — file doesn't exist yet
- **stub** — outline only, headings filled in
- **drafted** — first-pass content, needs review
- **reviewed** — peer-reviewed and accurate as of "Last reviewed" date
- **complete** — stable; only minor updates expected
- **archived** — historical reference; no active maintenance

## TODO markers and issue tracking

Use inline TODO markers paired with a GitHub Issue:

```markdown
<!-- TODO(@username): Document the ZED calibration sequence — see #42 -->
```

When you add a non-trivial TODO, also open an issue using the **Section TODO**
template so it shows up on the project board. Trivial inline TODOs (a single
missing sentence or value) don't need a paired issue.

## Modality scaffolding

To add a new modality or restructure an existing one, copy `modalities/_template/`
and rename. Each modality contains:

- `README.md` — overview, current status, scope, status table for sections
- `hardware.md` — device specs, mounting, cabling, room diagrams
- `pre-session.md` — setup checklist and calibration
- `during-session.md` — run-sheet / SOP for during data collection
- `troubleshooting.md` — known failures and fixes
- `processing.md` — code locations + pipeline documentation
- `data-spec.md` — output schema (what files, what fields)

Subdirectories used as needed:

- `devices/` — one subdir per device when a modality covers multiple
- `_archive/` — historical / superseded material; status: archived

## Code conventions

- **R**: snake_case, document public functions with roxygen, tidyverse style.
- **Python**: PEP 8, type hints encouraged, format with `ruff`/`black`.
- **Examples** must run against synthetic data shipped in `examples/data/` — never against real subject data.

## Issues and PRs

- **Section TODO** template — content gaps and section-fill tasks
- **Bug report** template — reproducible problems with code or instructions
- All PRs must complete the PHI/PII checklist in the PR template
- Reference related issues in PR descriptions
