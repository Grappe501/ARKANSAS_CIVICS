# Phase 03 — Progress Registry and Civic Credentials

This phase adds the first long-term learner advancement layer for the Arkansas Civics platform.

## New files

- `engine/progress_registry.py`
- `engine/certification_rules.py`
- `engine/civic_credential_engine.py`
- `scripts/build_phase_03_progress_credentials.py`
- `config/certification_tiers.json`

## What this phase introduces

- learner progress profiles
- course completion rollups
- civic action logs
- badge and certification rule evaluation
- leadership tier progression
- exportable credential records

## Install steps

1. Copy the `engine` files into your project `engine/` directory.
2. Copy the build script into `scripts/`.
3. Copy `certification_tiers.json` into `config/`.
4. Run:

```powershell
python scripts/build_phase_03_progress_credentials.py
```

## Expected outputs

- `exports/progress_registry/progress_registry_index.json`
- `exports/progress_registry/progress_registry_report.md`
- `exports/credentials/credential_index.json`
- `exports/credentials/credential_report.md`

## Notes

- This phase remains filesystem-first.
- It is designed to be lifted into the future database layer without rewriting the business logic.
- It gives you the beginnings of statewide credentialing, advancement, and civic workforce pathways.
