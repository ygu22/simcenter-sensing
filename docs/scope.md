# What belongs in this repository — and what doesn't

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

This repo is the operational + analytical layer for unobtrusive measurement at
the simulation center. It is **public** and MIT-licensed.

## In scope

- Hardware setup, mounting, cabling, room layout for each sensor modality
- Pre-session calibration and setup checklists
- During-session SOPs (run sheets)
- Troubleshooting guides (known failures and fixes)
- Data storage conventions (structure, naming, retention — _generic_, not specific)
- Processing code (cleaning, feature extraction, synchrony, QA)
- Cross-modality utilities (time alignment, identifier handling, exporters)
- Worked examples on synthetic data
- Identifier and time-sync conventions

## Out of scope

- Subject data of any kind (raw or derived)
- Institution-specific IRB protocols or consent text
- Internal hostnames, share paths, IP addresses, credentials
- Study-specific configurations or participant rosters
- Analysis code for individual studies (lives in study repos)
- Proprietary vendor firmware/SDKs (link to vendor docs; thin wrappers only)

## Adjacent repos

- Study-specific repos (HERA, PICU_CAL, etc.) — those depend on the methods
  documented here.

## Decision log

- **2026-06-01** — Repo created. Decisions: public from day 1, MIT for everything,
  CV + physiology priority, no formal private-companion repo yet (single
  public repo, generic content only).
