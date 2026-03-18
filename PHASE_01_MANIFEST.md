# Phase 01 Manifest — Core Kernel Stabilization

## Objective
Stabilize the kernel so all later phases can rely on:
- canonical config loading
- consistent logging
- explicit engine contracts
- health reporting
- stable export/runtime manifests

## Included in this zip
- new engine support modules for config, logging, contracts, and health
- environment config JSON files
- a hardened `platform_kernel.py`
- a dedicated phase build script
- a direct health-check script
- install documentation

## Not included yet
- authentication
- database connectivity
- production API services
- background queues
- search indexing

## Success signal
When installed correctly, `python scripts/build_phase_01_core_kernel.py` should complete and produce system map artifacts plus a kernel log file.
