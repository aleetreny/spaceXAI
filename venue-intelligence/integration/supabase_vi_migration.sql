-- Dedicated append-only namespaced venue research, separate from communities/events.
-- Apply to a NEW chosen same-room Supabase project AFTER inspecting existing tables.
-- Idempotent under repeated application; does not alter existing app tables.
create table if not exists public.vi_operators (
 operator_id text primary key, name text not null, evidence_url text
);
create table if not exists public.vi_buildings (
 building_id text primary key, name text not null, postcode text, borough text,
 latitude double precision, longitude double precision,
 constraint vi_building_lat check(latitude is null or latitude between -90 and 90),
 constraint vi_building_lng check(longitude is null or longitude between -180 and 180)
);
create table if not exists public.vi_venues (
 venue_id text primary key,
 building_id text not null references public.vi_buildings(building_id),
 operator_id text references public.vi_operators(operator_id),
 display_name text not null, venue_type text not null, source_url text not null,
 review_status text not null, after18_policy text not null default 'unknown',
 weekend_policy text not null default 'unknown', overnight_policy text not null default 'unknown',
 capacity_laptops integer, capacity_classroom integer, capacity_theatre integer,
 capacity_standing integer, area_sqm double precision,
 research_priority smallint not null default 0,
 lead_status text not null default 'research_lead',
 payload jsonb not null default '{}'::jsonb,
 updated_at timestamptz not null default now(),
 constraint vi_capacity_positive check (
  (capacity_laptops is null or capacity_laptops > 0) and
  (capacity_classroom is null or capacity_classroom > 0) and
  (capacity_theatre is null or capacity_theatre > 0) and
  (capacity_standing is null or capacity_standing > 0)),
 constraint vi_after18_value check(after18_policy in ('yes','no','restricted','unknown')),
 constraint vi_weekend_value check(weekend_policy in ('yes','no','restricted','unknown')),
 constraint vi_overnight_value check(overnight_policy in ('yes','no','restricted','unknown')),
 constraint vi_lead_status check(lead_status='research_lead'),
 constraint vi_no_live_booking check(
   (payload->>'availability_live')::boolean is false and
   (payload->>'is_currently_bookable')::boolean is false and
   (payload->>'can_advertise_available')::boolean is false)
);
create index if not exists vi_venues_priority_idx on public.vi_venues(research_priority desc);
create index if not exists vi_venues_type_idx on public.vi_venues(venue_type);
create index if not exists vi_venues_windows_idx on public.vi_venues(after18_policy, weekend_policy);
create index if not exists vi_venues_building_idx on public.vi_venues(building_id);
create table if not exists public.vi_spaces (
 space_id text primary key,
 building_id text not null references public.vi_buildings(building_id),
 venue_id text not null references public.vi_venues(venue_id),
 name text not null, granularity text not null
);
create table if not exists public.vi_evidence (
 evidence_id text primary key, venue_id text not null references public.vi_venues(venue_id),
 field text not null, value jsonb not null, source_url text not null,
 source_class text not null, observed_date date, caveat text, evidence_text text
);
create index if not exists vi_evidence_by_venue on public.vi_evidence(venue_id);
-- Unified graph node IDs permit FK checks across heterogeneous entity tables.
create table if not exists public.vi_nodes (
 node_id text primary key, node_type text not null
 check (node_type in ('operator','building','venue','space','evidence'))
);
create table if not exists public.vi_edges (
 from_id text not null references public.vi_nodes(node_id),
 predicate text not null check(predicate in ('OPERATES','HAS_SPACE','DESCRIBED_BY')),
 to_id text not null references public.vi_nodes(node_id),
 source_url text not null,
 primary key(from_id,predicate,to_id,source_url)
);
create index if not exists vi_edges_by_to on public.vi_edges(to_id);
-- Internal ingestion tracking. Never publicly readable.
create table if not exists public.vi_cognee_sync (
 venue_id text primary key references public.vi_venues(venue_id),
 dataset_name text not null, document_sha256 text not null,
 indexed_at timestamptz not null default now()
);
-- RLS all new tables, including metadata and ingestion state.
alter table public.vi_operators enable row level security;
alter table public.vi_buildings enable row level security;
alter table public.vi_venues enable row level security;
alter table public.vi_spaces enable row level security;
alter table public.vi_evidence enable row level security;
alter table public.vi_nodes enable row level security;
alter table public.vi_edges enable row level security;
alter table public.vi_cognee_sync enable row level security;
-- Opt in to narrow read-only permissions. No anon/authenticated writes.
revoke all on public.vi_operators, public.vi_buildings, public.vi_venues,
 public.vi_spaces, public.vi_evidence, public.vi_nodes, public.vi_edges,
 public.vi_cognee_sync from anon, authenticated;
grant select on public.vi_operators, public.vi_buildings, public.vi_venues,
 public.vi_spaces, public.vi_evidence, public.vi_nodes, public.vi_edges to anon, authenticated;
grant select, insert, update, delete on public.vi_operators, public.vi_buildings, public.vi_venues,
 public.vi_spaces, public.vi_evidence, public.vi_nodes, public.vi_edges, public.vi_cognee_sync to service_role;
-- Strictly idempotent policy creation.
do $$
declare t text;
begin
 foreach t in array array['vi_operators','vi_buildings','vi_venues','vi_spaces','vi_evidence','vi_nodes','vi_edges'] loop
  if not exists(select 1 from pg_policies where schemaname='public' and tablename=t and policyname='vi_public_research_read') then
   execute format('create policy vi_public_research_read on public.%I for select to anon, authenticated using (true)',t);
  end if;
 end loop;
end $$;
