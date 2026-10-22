-- Run on the new same-room project after import.
select 'vi_operators' as name,count(*) as n from public.vi_operators
union all select 'vi_buildings',count(*) from public.vi_buildings
union all select 'vi_venues',count(*) from public.vi_venues
union all select 'vi_spaces',count(*) from public.vi_spaces
union all select 'vi_evidence',count(*) from public.vi_evidence
union all select 'vi_nodes',count(*) from public.vi_nodes
union all select 'vi_edges',count(*) from public.vi_edges;

-- Unbookable by design; must be 0 / 0.
select count(*) filter(where payload->>'availability_live'='true') as asserted_live,
       count(*) filter(where payload->>'is_currently_bookable'='true') as asserted_bookable
from public.vi_venues;

-- Sample grounded query. Not a live availability claim.
select v.venue_id,v.display_name,v.after18_policy,v.capacity_laptops,
       e.evidence_id,e.field,e.source_url,e.caveat
from public.vi_venues v
join public.vi_evidence e on e.venue_id=v.venue_id
where v.venue_id='v_20788f6d9dad9722'
order by e.evidence_id limit 5;

-- Policies and effective grants on the dedicated tables.
select tablename,policyname,cmd,roles from pg_policies
where schemaname='public' and tablename like 'vi_%' order by 1;
select table_name,privilege_type,grantee
from information_schema.role_table_grants
where table_schema='public' and table_name like 'vi_%'
  and grantee in ('anon','authenticated','service_role')
order by table_name,grantee,privilege_type;
