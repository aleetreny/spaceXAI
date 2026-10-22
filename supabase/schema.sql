-- Paste into the Supabase SQL editor when a project exists.
-- The demo runs without this. Publish still works as a local page.

create table if not exists communities (
  id text primary key,
  name text not null,
  leads text[] not null,
  focus text not null,
  tags text[] not null default '{}',
  source text not null,
  url text
);

create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  community_a text not null references communities (id),
  community_b text not null references communities (id),
  title text not null,
  reason text not null,
  starts_at text,
  place text,
  member_notes text,
  next_action text not null,
  created_at timestamptz not null default now()
);

alter table communities enable row level security;
alter table events enable row level security;

create policy "public read communities"
  on communities for select
  to anon
  using (true);

create policy "public read events"
  on events for select
  to anon
  using (true);

create policy "anon insert events"
  on events for insert
  to anon
  with check (true);
