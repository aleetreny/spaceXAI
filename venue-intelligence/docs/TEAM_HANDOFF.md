# HANDOFF — for the SpaceXAI teammate building the venue UI + agent

**Status:** Data-only pull request; deliberately no edits to the existing `app.js`, `data.js`, `index.html`, `README.md`, `AGENTS.md` or `supabase/schema.sql` on `main`. Date of static research snapshot: 2026-10-22.

## 1) What can be used immediately

1. Static front end (no DB required): fetch **`/venue-intelligence/data/venues_frontend.json`** (at the deployed site's correct base path). It's an array of 381 candidate cards. These are research leads, NOT confirmed bookable inventory.
2. Detailed view and filters: load **`data/venues_v2.json`** keyed by `venue_id`, and when citing a field, join **`data/evidence.jsonl`** on `venue_id` and `field`. Types in `docs/types.ts`.
3. Agent: use **`data/cognee_documents.jsonl`** for provenance-aware semantic retrieval; **`data/cognee_edges.jsonl`** plus `buildings.jsonl`, `spaces.jsonl`, `operators.jsonl` for graph adapter. These are staging documents/edges, not a deployed Cognee graph.
4. Database: apply **`docs/supabase_venue_intelligence.sql`** only if you want a real backend. Tables use `vi_*` namespace; the migration does **not** modify the existing communities/events tables. Run privileged server-side ETL for upserts. Never publish service-role secrets in the browser.
5. Reproducibility: run `cd venue-intelligence && python3 scripts/build_v2.py && python3 scripts/export_frontend.py && python3 scripts/quality_audit.py && python3 -m unittest discover -s tests -v`. Build inputs are in `data/` and `legacy_pipeline/` (source reproducibility, not a validated live scraper).

## 2) Proposed loading contract (no implied UI framework)

```js
const response = await fetch('./venue-intelligence/data/venues_frontend.json');
if (!response.ok) throw new Error('Venue research dataset not found');
const venueLeads = await response.json();
const selection = venueLeads.filter(v => v.evening_policy === 'yes' && v.source_quality === 'page_reviewed');
```

For a more detailed card, match `selection[i].id` to `venue_id` in `venues_v2.json`. A row is not a booking slot; `availability` in the card is `not_verified`.

**Important:** if you are building a single-page app with route fallbacks, use its configured PUBLIC BASE URL instead of assuming `/venue-intelligence` resolves at domain root. If using GitHub Pages at `/spaceXAI/`, adjust relative fetch accordingly.

## 3) The frontend MUST NOT pretend verified bookings

- Show 'Potential venue — contact operator' for all seed data.
- `evening_policy` / `after18_policy` means a *published policy*, not a guaranteed evening on the date selected. Weekend 'yes' does NOT mean 48-hour or overnight hire.
- Always show separate laptop/workstation vs classroom/theatre/standing capacities. **Do not** infer laptop positions from theatre seating.
- Missing data are `unknown` / `null`; **do not** render `false`, 0, or a negative red cross for unknown Wi-Fi, availability or accessibility.
- No verified coordinates (`latitude`/`longitude` are null in every record); **do not** generate street-level map markers using only borough or district postcodes. Do not invent prices or user reviews.
- The provenance level matters: `page_reviewed` (79), `previous_research` (279), `url_discovered` (23). Keep evidence drawer and source URLs. Of 381, 47 have some explicit evening/weekend hire policy; 0 have a verified bookable slot.
- Detailed operator contacts are not outreach consent. Take care with terms of reuse and UK GDPR/PECR.

## 4) Minimal data flow

```text
Static JSON/JSONL research leads ──> browser search + filter + evidence drawer
                                  └─> server-side import (optional) ──> Supabase vi_* tables
                                                       ├─> API (anon SELECT only / RLS)
                                                       └─> Cognee: add/cognify (requires credentials) ──> retrieval + cited answers
Future operator onboarding + calendars ──> a DISTINCT booking/availability subsystem
```

No Cognee ingestion, backend deployment or real-time availability API was performed by the data PR; wire them in your own web/backend branch.

## 5) Suggested UI filters and entity hierarchy

- `source_quality=page_reviewed` and `evening_policy=yes` as first exploration filters; allow showing weaker candidates separately.
- Venue category (`type`), postcode and borough (often missing), minimum `laptop_capacity` (rare), `classroom_capacity`, `theatre_capacity`, `standing_capacity`, `wifi`, `av`, `price_from_gbp`, `weekend_policy`, confidence tier, `research_priority` (research heuristic only).
- Building vs room: `building_id` can contain multiple `space_id` rows. Preserve these relationships, and mark unspecified room granularity instead of silently adding 6 pins for 1 venue.
- Show source URL, reviewed status, evidence caveat and snapshot date in detail view.

## 6) SQL, ingestion & graph quality

- The SQL file is a migration, NOT a loader. Implement idempotent upserts in the order `vi_operators` → `vi_buildings` → `vi_venues` → `vi_spaces` → `vi_evidence` → `vi_edges`, after checking FK values and object shapes. In `vi_venues`, preserve the complete payload as JSONB.
- Review and limit anonymous SELECT policy in production if any proprietary outreach notes are added later; RLS on public research only. No browser-side write.
- For Cognee, ingest text documents with clear source citations, then separately map graph edges. `cognee_edges.jsonl` is **not** necessarily Cognee's native wire format; it needs a tested adapter. Agent should answer "unknown / enquiry needed" whenever a claim isn't evidenced.
- Never include secrets in GitHub; use server-only env config.

## 7) Known data gaps / next operational steps

Verify exact street addresses + coordinates, workstation sockets, Internet throughput, after-hours security, food policy, accessibility, insurance terms, individual room prices and calendar availability **with the operator**. The dataset is a prospecting tool until those checks are passed. Investigate licensing before adding London City Hall cultural data, OSM, Google Places or venue marketplace data; none are bulk imported here.

This PR is safe to merge independently. Use the imported files, leave the existing demo unaffected, then implement the UI/agent/Cognee in your own branch.
