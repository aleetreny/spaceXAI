# AGENTS — Live Venue Intelligence Integration (read this first)

This module has **LIVE Supabase data** but **NO verified Cognee production connection**. See `STATUS.md` (the operational source of truth) and `README.md` (runbook).

## Non-negotiable actual target

- **Supabase owner organization:** `aleetreny's Org` (`xrgtbrrmaaiowrfhkqid`)
- **Existing project:** `spaceXAI`, ref `lrjxjypjccoopejltwyz`; **DO NOT create a project named same-room**.
- Never use, modify, pause or delete the `Finanzas` project. Never use a teammate-owned project.
- **The database is populated already. Do NOT reload indiscriminately or apply duplicate schemas on every app start.** First run the counts query below and inspect migration history. Existing `vi_*` schema is applied.
- `main` has team work including `dbs/`, `docs/`, the Same Room app files and its own `supabase/schema.sql`. This PR intentionally does **not** replace them. Root `communities` and `events` tables are **not created in the live project yet**.

## Verified 2026-10-22 live state

23 operators, 337 buildings, 381 venues, 381 spaces, 699 evidences, 1,821 ID registry nodes, 819 unique edges (851 source rows minus 32 exact duplicates). Real SQL query, RLS & privileges, references and JSONB payload validated. All 381 are **research leads**, none live bookable. See `STATUS.md` for the actual example with IDs and source citations.

```sql
select (select count(*) from public.vi_operators) as operators,
       (select count(*) from public.vi_buildings) as buildings,
       (select count(*) from public.vi_venues) as venues,
       (select count(*) from public.vi_spaces) as spaces,
       (select count(*) from public.vi_evidence) as evidence,
       (select count(*) from public.vi_nodes) as nodes,
       (select count(*) from public.vi_edges) as edges;
```

## Agent integration order

1. **Inspect before editing:** read repo root `AGENTS.md`, `venue-intelligence/AGENTS.md`, `integration/STATUS.md`, this file, `integration/README.md`, the existing app/framework and `supabase/schema.sql`. Do not overwrite teammate's work.
2. **Web search/list:** The server already has `GET /api/venues`, `GET /api/venues/:venue_id`, `GET /api/venues/:venue_id/evidence` and separate `/venues/` UI in `integration/server/server.mjs`. Supabase table `public.vi_venues` contains complete `payload` JSONB. Serve public data using a **publishable** key or server-side read-only access; no secret/service key in browser. Deploy and test live HTTP **before** claiming web integration.
3. **Evidence:** Join `public.vi_evidence` on `venue_id`, return real `evidence_id`, `field`, `value`, `source_url` and `caveat`. Missing values are `unknown`/`null`, not `no`. Never infer laptop capacity from theatre capacity, or an available time slot from an advertised evening policy.
4. **Cognee:** `integration/cognee_sync.py` is an adapter needing actual instance URL/keys and budget approval. Use **dataset `nightoffice_venue_research_2026_10_22` only**, no teammate/community dataset reuse. Check API schema/version for `/api/v1/add`, `/api/v1/cognify`, `/api/v1/search`; JSONL edges are staging only. Run one-document smoke test, then ingest/cognify 381 only after account owner approves associated LLM usage. Validate actual cited search. `vi_cognee_sync` is server-private checkpoint and currently empty.
5. **Security:** RLS enabled on all `vi_*`; anon/authenticated only SELECT on 7 public research tables, no read of `vi_cognee_sync`, no public writes. Never expose privileged Supabase/Cognee keys in client bundles, git history, or chat. Use a private secrets manager/environment.
6. **Team coordination:** Keep unrelated app & root migrations unchanged; stage changes on your branch/PR. If code from teammate exists only in their worktree, do not assume it is in this repo.

## Hard safety guardrails

Research leads are **not bookable inventory**. Zero verified dates, zero verified coordinates. No fictional quotes, availability, reviews, prices or geocodes. Preserve full JSONB payload, nulls, source/review tier, stable IDs and original links; public commercial reuse must respect source licence/terms.

**Definition of done:** Live Supabase counts+FK/RLS checks (already DONE); real deployed same-origin API requests (PENDING); Cognee own-instance cognify and a real reference-verified graph query (PENDING). Each must be checked independently.
