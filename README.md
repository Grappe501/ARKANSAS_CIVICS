# Phase 07 - Civic Graph Persistence Engine

This package adds Supabase/PostgreSQL persistence for the Arkansas Civics civic knowledge graph.

## Purpose

Phase 06 exports civic graph data to JSON/Markdown. Phase 07 ingests that exported graph into PostgreSQL so the platform can support fast, structured civic intelligence queries.

This Phase 07 package is intentionally scoped for **Arkansas-only** deployment.

## What this package adds

- `engine/graph_persistence/` database ingestion engine
- `scripts/build_phase_07_graph_persistence.py` build/export helper
- `scripts/load_graph_to_supabase.py` graph loader
- `scripts/query_civic_graph.py` simple query CLI
- `exports/graph_schema.sql` PostgreSQL schema
- `exports/graph_persistence_manifest.json` phase manifest
- `docs/PHASE_07_IMPLEMENTATION.md` implementation notes
- `config/.env.example` environment template

## Assumptions

- Existing Phase 06 output exists at `exports/graph_expansion/civic_graph_expansion.json`
- Supabase project already exists
- Environment variables will be provided through a local `.env`

## Environment variables

Copy `config/.env.example` into your project root `.env` and fill in values.

Required:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

Optional:

- `SUPABASE_DB_SCHEMA` (defaults to `public`)
- `GRAPH_SOURCE_PATH` (defaults to `exports/graph_expansion/civic_graph_expansion.json`)

## Recommended install order

1. Copy these files into the matching folders in your repository.
2. Create/update your `.env`.
3. Run the schema in Supabase SQL editor using `exports/graph_schema.sql`.
4. Run:
   - `python scripts/build_phase_07_graph_persistence.py`
   - `python scripts/load_graph_to_supabase.py`
5. Test with:
   - `python scripts/query_civic_graph.py --relationship influences --limit 20`

## Notes

- This phase preserves the filesystem-first architecture.
- The filesystem remains the source of truth for generated graph exports.
- PostgreSQL becomes the queryable persistence layer.
# Phase 08 - Civic Query Engine

This layer enables querying the civic graph:

## Features

- Bill influence analysis
- Node relationship traversal
- Influence scoring (v1)

## Run

python scripts/query_influence.py
python scripts/query_connections.py