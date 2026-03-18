# Phase 06 — Civic Knowledge Graph Expansion

This phase expands the Arkansas Civics platform into an influence-aware civic graph system.

## New files

- `engine/civic_knowledge_graph_expansion_engine.py`
- `engine/graph_expanders/legislator_graph_expander.py`
- `engine/graph_expanders/committee_power_expander.py`
- `engine/graph_expanders/donor_influence_expander.py`
- `engine/graph_expanders/policy_impact_expander.py`
- `scripts/build_phase_06_graph_expansion.py`
- `config/graph_expansion_sources.json`

## What this phase introduces

- legislator influence graph expansion
- committee power mapping
- donor-to-recipient relationship mapping
- policy-to-community impact mapping
- graph-ready node/edge exports

## Install steps

1. Copy the engine files into your project `engine/` directory.
2. Copy the graph expander files into `engine/graph_expanders/`.
3. Copy the build script into `scripts/`.
4. Copy the config file into `config/`.
5. Run:

```powershell
python scripts/build_phase_06_graph_expansion.py
```

## Expected outputs

- `exports/graph_expansion/civic_graph_expansion.json`
- `exports/graph_expansion/civic_graph_expansion.md`
- `exports/graph_expansion/civic_graph_manifest.json`

## Suggested source folders

Create these if they do not already exist:

- `data/civic_sources/legislators/`
- `data/civic_sources/committees/`
- `data/civic_sources/donors/`
- `data/civic_sources/policy_impacts/`

## Notes

- This phase remains filesystem-first.
- It is designed to flow naturally into the future persistent graph/database layer.
- It supports explainers, influence mapping, public education tools, and pathway recommendations.
