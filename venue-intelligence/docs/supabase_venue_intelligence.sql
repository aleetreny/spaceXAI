-- Namespaced venue research schema (independent from Same Room's communities/events).
-- Intended for server-side ETL with service-role credentials only.
-- No anonymous writes. No actual calendar availability is represented.
create table if not exists public.vi_operators (
 operator_id text primary key, name text not null, evidence_url text
);
create table if not exists public.vi_buildings (
 building_id text primary key, name text not null, postcode text,
 borough text, latitude double precision, longitude double precision,
 constraint valid_lat check (latitude is null or latitude between -90 and 90),
 constraint valid_lng check (longitude is null or longitude between -180 and 180)
);
create table if not exists public.vi_venues (
 venue_id text primary key,
 building_id text references public.vi_buildings(building_id),
 operator_id text references public.vi_operators(operator_id),
 display_name text not null,
 venue_type text not null,
 source_url text not null,
 review_status text not null,
 after18_policy text not null default 'unknown',
 weekend_policy text not null default 'unknown',
 overnight_policy text not null default 'unknown',
 capacity_laptops integer,
 capacity_classroom integer,
 capacity_theatre integer,
 capacity_standing integer,
 area_sqm double precision,
 research_priority smallint not null default 0,
 lead_status text not null default 'research_lead',
 payload jsonb not null default '{}'::jsonb,
 updated_at timestamptz not null default now(),
 constraint vi_positive_capacities check (
  (capacity_laptops is null or capacity_laptops>0) and
  (capacity_classroom is null or capacity_classroom>0) and
  (capacity_theatre is null or capacity_theatre>0) and
  (capacity_standing is null or capacity_standing>0)),
 constraint vi_evening_policy check(after18_policy in ('yes','no','restricted','unknown')),
 constraint vi_weekend_policy check(weekend_policy in ('yes','no','restricted','unknown')),
 constraint vi_overnight_policy check(overnight_policy in ('yes','no','restricted','unknown'))
);
create index if not exists vi_venues_priority_idx on public.vi_venues (research_priority desc);
create index if not exists vi_venues_type_idx on public.vi_venues (venue_type);
create index if not exists vi_venues_evening_idx on public.vi_venues (after18_policy, weekend_policy);
create table if not exists public.vi_spaces (
 space_id text primary key,
 building_id text not null references public.vi_buildings(building_id),
 venue_id text not null references public.vi_venues(venue_id),
 name text not null, granularity text not null
);
create table if not exists public.vi_evidence (
 evidence_id text primary key,
 venue_id text not null references public.vi_venues(venue_id),
 field text not null, value jsonb not null,
 source_url text not null, source_class text not null,
 observed_date date, caveat text, evidence_text text
);
create index if not exists vi_evidence_venue_idx on public.vi_evidence(venue_id);
create table if not exists public.vi_edges (
 from_id text not null, predicate text not null, to_id text not null,
 source_url text not null,
 primary key(from_id,predicate,to_id,source_url)
);
create index if not exists vi_edges_from_idx on public.vi_edges(from_id);

-- Supabase policy: public non-sensitive research read only; all writes server-side.
alter table public.vi_operators enable row level security;
alter table public.vi_buildings enable row level security;
alter table public.vi_venues enable row level security;
alter table public.vi_spaces enable row level security;
alter table public.vi_evidence enable row level security;
alter table public.vi_edges enable row level security;
create policy "public read venue research" on public.vi_venues for select to anon using(true);
create policy "public read venue buildings" on public.vi_buildings for select to anon using(true);
create policy "public read venue spaces" on public.vi_spaces for select to anon using(true);
create policy "public read venue evidence" on public.vi_evidence for select to anon using(true);
create policy "public read venue operators" on public.vi_operators for select to anon using(true);
create policy "public read venue graph edges" on public.vi_edges for select to anon using(true);
