# Same Room / Night Office — Supabase + Cognee integration

**Stage:** implementation + deterministic dry-run and mocked API tests verified. **NOT LIVE CONNECTED.** Actual Supabase project creation, schema migration, upload, Cognee `add/cognify`, and production search remain blocked until the owner confirms the target organization and privately configures provider credentials. Never treat dry-run/mock results as production connectivity.

## Scope and source

- Dataset imported from PR #4 (`data/london-venue-intelligence-v2-20261022`), 2026-10-22 snapshot.
- Keep existing root `AGENTS.md`, `data.js`, `app.js`, `index.html`, `supabase/schema.sql`, and new teammate `dbs/`/`docs/` files untouched. These are independent assets.
- Database entity counts (asserted before network calls): 23 operators, 337 buildings, 381 venues, 381 spaces, 699 evidence statements, 851 raw edges / **819 unique**; 1,821 ID registry nodes.
- Every complete venue source record preserved in `vi_venues.payload` JSONB. No live availability or verified geocodes.
- Exact FKs: venues → buildings & optional operators; spaces → venue & building; evidence → venue; edges → polymorphic `vi_nodes` registry (both endpoints). Refuse dangling IDs.

## Before provisioning Supabase

1. Ask project owner which **Supabase organization** to use. In the connected account (at initial check), only `aleetreny's Org` (`xrgtbrrmaaiowrfhkqid`) and an existing unrelated `Finanzas` project were visible. **NEVER use Finanzas.** Re-read organizations/projects before creation because state may change.
2. Call Supabase `get_cost` on the chosen organization for a **new project**, quote the actual cost, and get user approval for any nonzero charge. Create exactly `same-room` at $0 if possible; prefer `eu-west-2` only after owner agrees. Stop for payment approval.
3. Inspect the new `same-room` project's public tables and policies *before* migrating. If `communities`/`events` exist, preserve them verbatim. If absent, do not fabricate existing data; their existing `supabase/schema.sql` is separately managed.
4. Apply `supabase_vi_migration.sql` using a privileged migration pathway to **that exact project ref only**. Verify RLS, `GRANT SELECT` for anon/authenticated, and no public INSERT/UPDATE/DELETE on `vi_*` tables; ingestion state is private to service_role.

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

The importer verifies all counts against the *live target* and fails if not exact. It never deletes other rows; because this is a fresh dedicated project, counts should match. An actual report must be produced before claiming load succeeded.

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

### Verification gates before marking connected

1. Create project only after organization and $ cost confirmed.
2. `list_tables`/SQL preflight and post-migration check RLS, privileges, FK constraints.
3. Run importer `--execute` **twice** and verify stable live counts + evidence and `payload` JSONB.
4. Run Cognee document ingestion; verify dataset processing status and a real `/api/v1/search` returning a `venue_id` and evidence identifier. If it doesn't, fix indexing/prompting instead of claiming success.
5. Verify live GET detail and POST graph request through the deployed backend, including an `evidence_id` and original URL; record only **sanitized** example output in PR.
6. Confirm `communities`/`events` unchanged, API RLS denies anon writes (test with disposable dummy ID), and no secrets reach browser/network source control.

## Limitations

Real-time booking availability=none; 0 verified coordinates; only 1 explicit laptop capacity. Some pages are weak research candidates. `unknown` remains `unknown`; prices and reviews are never inferred. Reuse and commercial outreach remain subject to source rights and privacy considerations.
