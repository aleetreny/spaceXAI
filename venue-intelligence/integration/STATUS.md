# Live integration status — 2026-10-22

**Supabase: LIVE LOADED & SQL-VERIFIED. Cognee: NOT YET CONNECTED. Backend/UI: CODE READY, NOT DEPLOYED.**

## Owner-owned target (do not confuse with `Finanzas`)

- Organization: `aleetreny's Org` (`xrgtbrrmaaiowrfhkqid`), selected by owner.
- Existing project: **spaceXAI** (`lrjxjypjccoopejltwyz`), region `eu-west-1`.
- Dashboard: https://supabase.com/dashboard/project/lrjxjypjccoopejltwyz/editor
- No project created/deleted. `Finanzas` was never touched.
- Preflight: 0 tables in `public`; neither `communities` nor `events` existed. Existing Same Room repository app files remain unchanged.
- Migration: `venue_intelligence_v2_initial_rls` applied successfully using the connected Supabase migration tool.

## Confirmed live database counts (queried in actual PostgreSQL)

| Table | Count |
| --- | ---: |
| `public.vi_operators` | 23 |
| `public.vi_buildings` | 337 |
| `public.vi_venues` | 381 |
| `public.vi_spaces` | 381 |
| `public.vi_evidence` | 699 |
| `public.vi_nodes` | 1821 |
| `public.vi_edges` | 819 |
| `public.vi_cognee_sync` | 0 |

- Original graph staging had 851 rows, of which 32 were duplicates; 819 unique relations loaded.
- 381/381 `payload->>'venue_id'` match venue PKs.
- 381/381 `availability_live`, `is_currently_bookable`, `can_advertise_available` remain `false`.
- Orphans (spaces, evidence, graph edge endpoint FKs): **0 / 0 / 0**.
- 8/8 `vi_*` tables have RLS on.
- `anon` and `authenticated`: SELECT only on 7 public research tables; **no INSERT/UPDATE/DELETE privileges**. `vi_cognee_sync` has no public read policy.
- A real `SET LOCAL ROLE anon` SELECT fetched `Ramen Space`.
- The snapshot was imported with idempotent `ON CONFLICT` upserts via the account's authorized Supabase SQL connector, *not* by giving the importer a secret.

## Actual cited database query

```sql
select v.venue_id, v.display_name, v.after18_policy, v.weekend_policy,
       v.capacity_laptops, e.evidence_id, e.field, e.value, e.source_url
from public.vi_venues v
join public.vi_evidence e on e.venue_id = v.venue_id
where v.venue_id = 'v_20788f6d9dad9722'
  and e.field in ('after18_policy','weekend_policy','capacity_laptops')
order by e.field;
```

**Results confirmed in the live database:**

- `v_20788f6d9dad9722` — **Ramen Space**, `after18_policy=yes`, `weekend_policy=yes`, `capacity_laptops=50`.
- `e_f03c44d4651db8e7` — `after18_policy=yes`.
- `e_d65fd73311025030` — `weekend_policy=yes`.
- `e_fa79e1add22bb863` — `capacity_laptops=50`.
- Original evidence URL: https://ramenclub.com/ramen-space/events/

**Caveat:** This proves published venue *policies*, NOT availability for any specific date, nor a booking partnership with Night Office.

## Remaining blockers — explicit

- [ ] Own Cognee instance/API base URL, privately provisioned credentials, and confirmation of token/LLM budget. The teammate's previous ingestion is NOT assumed accessible or complete.
- [ ] Run the existing `cognee_sync.py` only after verifying its API against the actual instance; a dry-run/mock does not prove ingestion. Dataset must be `nightoffice_venue_research_2026_10_22`, separate from community graphs.
- [ ] Verify a real Cognee query returns a grounded `venue_id` and citation that can be joined to `public.vi_evidence`. The 819 explicit edges are **in Supabase**, not claimed to be directly ingested as native Cognee edges.
- [ ] Configure **server-private** environment keys and deploy the `integration/server/server.mjs` backend; existing `/venues/` UI is separate and still not deployed.
- [ ] Confirm production browser request to `/api/venues` and backend `/api/venues/ask`; no request is yet reported as live.
- [ ] Root `communities` and `events` SQL schema remains unapplied because the new project started empty and that is a separate team-managed workflow. Do not claim those tables are present.
- [ ] Agent must ensure no code or credentials from the teammate's local-only worktree were assumed to be in GitHub.

**Do not downgrade this live Supabase success to `pending project creation` in subsequent handoffs, and do not elevate Cognee/backend from pending to connected without evidence.**
