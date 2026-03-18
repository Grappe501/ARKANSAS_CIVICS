# Phase 07 Implementation Notes

## Goal

Persist the Arkansas civic graph generated in Phase 06 into Supabase PostgreSQL without disrupting the existing filesystem-first architecture.

## Design choice

This implementation keeps the exported JSON graph as the source of truth and treats PostgreSQL as a query and indexing layer.

## Why Arkansas-only

This version intentionally excludes multi-state normalization so the schema can stay simple and fast for your current platform scope. The `jurisdiction` field is still included so future migrations remain possible.

## Install steps

1. Copy this package into your project.
2. Install dependencies if needed:
   - `pip install supabase python-dotenv`
3. Add `.env` values using `config/.env.example`.
4. Run `exports/graph_schema.sql` in the Supabase SQL editor.
5. Build normalized persistence artifacts:
   - `python scripts/build_phase_07_graph_persistence.py`
6. Load to Supabase:
   - `python scripts/load_graph_to_supabase.py`
7. Validate:
   - `python scripts/query_civic_graph.py --limit 10`

## Expected outputs

### Local export outputs

- `exports/graph_persistence/phase_07_nodes.json`
- `exports/graph_persistence/phase_07_edges.json`
- `exports/graph_persistence/phase_07_indexes.json`
- `exports/graph_persistence/phase_07_build_manifest.json`

### Database objects

- `public.civic_nodes`
- `public.civic_edges`
- `public.civic_graph_index`
- `public.civic_relationships_expanded`

## Suggested next phase

Phase 08 should build a civic intelligence query engine that reads from the persisted graph and supports public-facing explainers, dashboards, and actor/policy relationship lookups.
