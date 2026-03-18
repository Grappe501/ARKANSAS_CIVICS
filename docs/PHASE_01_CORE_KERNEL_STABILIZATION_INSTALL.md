# Phase 01 — Core Kernel Stabilization

This phase adds environment-aware kernel configuration, central logging, health checks, and stronger export/runtime manifests.

## New files
- `engine/kernel_config.py`
- `engine/kernel_logger.py`
- `engine/kernel_contracts.py`
- `engine/kernel_health.py`
- `scripts/build_phase_01_core_kernel.py`
- `scripts/kernel_health_check.py`
- `config/kernel.defaults.json`
- `config/kernel.local.json`
- `config/kernel.production.json`

## Full replacements
- `engine/platform_kernel.py`
- `scripts/build_all.py`

## Placement
Copy each file into the matching path inside your repo.

## Run order
1. `python scripts/build_phase_01_core_kernel.py`
2. `python scripts/kernel_health_check.py`
3. Optional full-platform check: `python scripts/build_all.py`

## New outputs
- `exports/system_map/platform_kernel_snapshot.json`
- `exports/system_map/kernel_runtime_manifest.json`
- `exports/system_map/kernel_health_report.json`
- `logs/platform_kernel.log`

## Environment override examples
PowerShell:
```powershell
$env:ARK_CIVICS_ENV="local"
$env:ARK_CIVICS_LOG_LEVEL="INFO"
python scripts/build_phase_01_core_kernel.py
```

## Purpose
This phase is about hardening the kernel before auth, database, and multi-user scale. It keeps filesystem-first development intact while making later phases cleaner.
