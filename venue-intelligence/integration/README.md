# Same Room / Night Office — Supabase + Cognee integration

**Operational stage:** Supabase is **LIVE, LOADED, RLS-SECURED AND SQL-VERIFIED** in the owner's existing `spaceXAI` project. Cognee indexing and HTTP backend deployment are **NOT** yet verified. For current authoritative counts and example SQL, read [`STATUS.md`](STATUS.md); for agent instructions, read [`AGENTS.md`](AGENTS.md).

## Scope and source

- Dataset imported from PR #4 (`data/london-venue-intelligence-v2-20261022`), 2026-10-22 snapshot.
- Keep existing root `AGENTS.md`, `data.js`, `app.js`, `index.html`, `supabase/schema.sql`, and new teammate `dbs/`/`docs/` files untouched. These are independent assets.
- Database entity counts (asserted before network calls): 23 operators, 337 buildings, 381 venues, 381 spaces, 699 evidence statements, 851 raw edges / **819 unique**; 1,821 ID registry nodes.
- Every complete venue source record preserved in `vi_venues.payload` JSONB. No live availability or verified geocodes.
- Exact FKs: venues → buildings & optional operators; spaces → venue & building; evidence → venue; edges → polymorphic `vi_nodes` registry (both endpoints). Refuse dangling IDs.

## Existing Supabase project — already provisioned and populated

**Do not create `same-room` or use `Finanzas`:** The owner explicitly selected the existing **spaceXAI** project in `aleetreny's Org`. Project ref: `lrjxjypjccoopejltwyz`; region: `eu-west-1`.

- Dashboard: https://supabase.com/dashboard/project/lrjxjypjccoopejltwyz/editor
- Preflight public-table count: 0; no `communities`/`events` existed. These root app tables have not been migrated here.
- Applied namespaced migration: `venue_intelligence_v2_initial_rls` from `supabase_vi_migration.sql`. **Do not reapply on every app start.**
- Live count: operators 23, buildings 337, venues 381, spaces 381, evidence 699, nodes 1821, unique edges 819. All 381 have full JSONB payload and no live booking flags. Orphan FK checks 0.
- RLS: eight tables protected. Seven public research tables grant `anon`/`authenticated` SELECT only, no writes; `vi_cognee_sync` not public.
- Verified read as `anon`; verified Ramen Space `venue_id` and evidence IDs/URLs (see `STATUS.md`).
- Imported once using authorized Supabase SQL connector with upserts, **not by exchanging a service-role key**. External `supabase_import.py --execute` is a reproducible option for future server-only refreshes, *not* a prerequisite to this live snapshot. No agent should require owner to paste secrets in chat.

## Data import (server / trusted shell only)

No Python third-party packages required. Python ≥3.10; Node ≥20.

```bash
cd venue-intelligence/integration
python3 supabase_import.py --dry-run
python3 cognee_sync.py --dry-run
python3 -m unittest discover -s tests -v
node --test tests/api.test.mjs
```

The following values belong in **private deployment secrets or a private terminal environment** (never commit `.env`, never paste tokens in chat):

```text
SUPABASE_PROJECT_REF=<new same-room project ref>
SUPABASE_URL=https://<new same-room project ref>.supabase.co
SUPABASE_SECRET_KEY=<private sb_secret_... OR legacy service_role JWT; server ONLY>
SUPABASE_PUBLISHABLE_KEY=<safe sb_publishable_... for read-only API>
COGNEE_URL=https://<YOUR Cognee API base URL>
COGNEE_API_KEY=<private key from YOUR Cognee instance>
COGNEE_AUTH_MODE=api_key    # or bearer for authenticated self-hosted Cognee
VENUE_PORT=4343
```

**Private credential handoff:** use the trusted environment's secrets manager / agent secret input. If using Supabase MCP through ChatGPT, the user chooses the organization and explicitly authorizes project creation. This chat does not expose or copy any secret keys.

When the project schema is verified and private import credentials are present:

```bash
python3 supabase_import.py --execute --report import_report.json
# Rerun identical command: 100% idempotent on primary/edge compound keys.
```

**Order is fixed:** `vi_operators` → `vi_buildings` → `vi_venues` → `vi_spaces` → `vi_evidence` → `vi_nodes` (FK registry) → `vi_edges`. The first five match business requirements; the extra node registry enables real foreign keys for edge endpoints. Use `--report` for the counts; never commit a real `.env`.

Production expected counts:

| table | rows |
| --- | ---: |
| `vi_operators` | 23 |
| `vi_buildings` | 337 |
| `vi_venues` | 381 |
| `vi_spaces` | 381 |
| `vi_evidence` | 699 |
| `vi_nodes` | 1,821 |
| `vi_edges` | 819 |

The importer verifies all counts against the *live target* and fails if not exact. It never deletes other rows; this owner-owned project already has the exact expected counts. They were verified directly in the live database via the authorized SQL connector (see STATUS.md).

## Cognee ingestion — own separate dataset

- Uses **REST** `POST /api/v1/add` with multipart `data` + `datasetName`, `POST /api/v1/cognify` with `datasets: [name]`, `POST /api/v1/search` with `search_type: 'CHUNKS'` and scoped `datasets`. These forms were verified against published Cognee REST reference and current `cognee/cli/api_client.py`.
- Dataset is `nightoffice_venue_research_2026_10_22`, distinct from any teammate/community dataset.
- Each document embeds `venue_id`, `building_id`, `space_id`, optional `operator_id`, `evidence_id`, exact source URLs, values, caveats and *unknown* distinctions. `cognee_edges.jsonl` is staging-only: **not sent to a Cognee graph endpoint**. Cognee derives any semantic graph from the text; explicit edges stay in Supabase.
- `vi_cognee_sync` is private server-only state keyed by SHA256, so reruns skip unchanged documents. Changed documents are rejected until a versioned reindex plan is chosen (avoids silently retaining conflicting old chunks).

```bash
python3 cognee_sync.py --execute --limit 1          # optional smoke ingestion first
python3 cognee_sync.py --execute --cognify         # complete dataset + process graph
```

**Do not run these commands against your teammate's Cognee instance.** The user has not granted access; no previous ingestion is assumed complete. Cognee graph processing may use billable LLM tokens: confirm quotas/usage limits with the account owner before running the full 381-document pipeline.

## Local same-origin platform API + separate UI

```bash
node integration/server/server.mjs
# http://127.0.0.1:4343/venues/
```

When working from the repository root, use `node venue-intelligence/integration/server/server.mjs`. The backend supplies public read-only research via Supabase using a publishable/anon key; **privileged tokens are only in the offline importer**, never in browser JS or this server. Cognee requests are server-side, and `/api/venues/ask` is rate-limited to 10 per hour per IP as a basic abuse guard (add managed perimeter limits in production).

Implemented endpoints:

```text
GET /api/venues?q=Ramen&after18=yes&weekend=yes
GET /api/venues/v_20788f6d9dad9722
GET /api/venues/v_20788f6d9dad9722/evidence
POST /api/venues/ask {"question":"Which spaces allow programming after 18:00?"}
```

The graph query endpoint only returns matches if Cognee retrieved actual IDs that also exist in Supabase. Evidence is re-read from Supabase, including `evidence_id` and source URLs. **No unverified LLM-generated conclusion** is returned. A no-results response means insufficient evidence, not a negative fact. Root `Same Room` UI is intentionally unchanged; `/venues/` is an independent venue research interface ready for your teammate to link or incorporate.

### Example grounded *local dataset* query (not a live run)

`venue_id=v_20788f6d9dad9722`: Ramen Space. An evening hire policy is described on its official site (generally weekdays 18:00–21:30, weekends 08:00–20:00); a venue-specific evidence entry is `e_fee8f5654104909f` (`research_lead_mentioned`), with URL `https://ramenclub.com/ramen-space/events/`. This particular evidence field attests listing discovery, *not* a date-specific slot: the separate venue text describes hours and must be confirmed with the operator. Laptop-work capacity is explicitly 50; theatre capacity 70 is a separate measure.

### Verification gates — current status

1. [x] Owner's existing `spaceXAI` project selected; no new project created or destroyed.
2. [x] Live `vi_*` migration applied; 8 tables have RLS and grants/foreign keys verified.
3. [x] Full static dataset loaded using upserts and SQL counts cross-checked against source, `payload` and FK audits passed. The standalone credentialed importer is not required to redo this now.
4. [ ] Own Cognee instance, private credentials and budget; real `add`/`cognify` plus cited `search` check — **NOT YET DONE**.
5. [ ] Configure publishable Supabase key in backend's private environment and deploy standalone venue API/UI; do real GET evidence and POST Cognee request via backend.
6. [x] Existing team root app files and other products untouched. `communities` and `events` were absent on creation and remain a separate team step.

## Limitations

Real-time booking availability=none; 0 verified coordinates; only 1 explicit laptop capacity. Some pages are weak research candidates. `unknown` remains `unknown`; prices and reviews are never inferred. Reuse and commercial outreach remain subject to source rights and privacy considerations.
