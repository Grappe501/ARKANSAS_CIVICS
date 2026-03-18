-- Phase 07 - Civic Graph Persistence Schema
-- Arkansas-only scope

create extension if not exists pgcrypto;

create table if not exists public.civic_nodes (
    id uuid primary key,
    source_key text not null,
    jurisdiction text not null default 'arkansas',
    node_type text not null,
    name text not null,
    county text null,
    district text null,
    chamber text null,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists idx_civic_nodes_unique_source
    on public.civic_nodes (jurisdiction, node_type, source_key);

create index if not exists idx_civic_nodes_type
    on public.civic_nodes (node_type);

create index if not exists idx_civic_nodes_name
    on public.civic_nodes (name);

create index if not exists idx_civic_nodes_county
    on public.civic_nodes (county);

create index if not exists idx_civic_nodes_district
    on public.civic_nodes (district);

create index if not exists idx_civic_nodes_metadata_gin
    on public.civic_nodes using gin (metadata);

create table if not exists public.civic_edges (
    id uuid primary key,
    jurisdiction text not null default 'arkansas',
    source_node_id uuid not null references public.civic_nodes(id) on delete cascade,
    target_node_id uuid not null references public.civic_nodes(id) on delete cascade,
    relationship_type text not null,
    weight double precision not null default 1.0,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists idx_civic_edges_unique_relationship
    on public.civic_edges (source_node_id, target_node_id, relationship_type);

create index if not exists idx_civic_edges_relationship
    on public.civic_edges (relationship_type);

create index if not exists idx_civic_edges_source
    on public.civic_edges (source_node_id);

create index if not exists idx_civic_edges_target
    on public.civic_edges (target_node_id);

create index if not exists idx_civic_edges_metadata_gin
    on public.civic_edges using gin (metadata);

create table if not exists public.civic_graph_index (
    index_key text primary key,
    index_group text not null,
    payload jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_civic_graph_index_group
    on public.civic_graph_index (index_group);

create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

DROP TRIGGER IF EXISTS civic_nodes_set_updated_at ON public.civic_nodes;
create trigger civic_nodes_set_updated_at
before update on public.civic_nodes
for each row execute function public.set_updated_at();

DROP TRIGGER IF EXISTS civic_edges_set_updated_at ON public.civic_edges;
create trigger civic_edges_set_updated_at
before update on public.civic_edges
for each row execute function public.set_updated_at();

DROP TRIGGER IF EXISTS civic_graph_index_set_updated_at ON public.civic_graph_index;
create trigger civic_graph_index_set_updated_at
before update on public.civic_graph_index
for each row execute function public.set_updated_at();

create or replace view public.civic_relationships_expanded as
select
    e.id,
    e.relationship_type,
    e.weight,
    e.jurisdiction,
    s.node_type as source_type,
    s.name as source_name,
    s.county as source_county,
    s.district as source_district,
    t.node_type as target_type,
    t.name as target_name,
    t.county as target_county,
    t.district as target_district,
    e.metadata,
    e.created_at,
    e.updated_at
from public.civic_edges e
join public.civic_nodes s on s.id = e.source_node_id
join public.civic_nodes t on t.id = e.target_node_id;
