# Venue Intelligence v2 — integration contract

Research snapshot: **2026-10-22**. Dataset is **NOT an online booking feed**. None of the entries includes operator-confirmed free dates.

## Data consumers

- `data/venues_v2.json`: one JSON object per research lead; primary read-only API seed.
- `data/venues_v2.jsonl`: streaming and agent ingestion format.
- `data/venues_v2.csv`: flat business-intelligence export, not a product table.
- `data/buildings.jsonl`, `spaces.jsonl`, `operators.jsonl`: normalized nodes.
- `data/evidence.jsonl`: provenance per extracted claim. Treat each item as a *statement*, NOT a contract.
- `data/cognee_edges.jsonl`: JSONL graph edges `(from_id, predicate, to_id, source_url)` to ingest into a graph pipeline after validation.
- `data/venue_intelligence_v2.sqlite`: read-only indexed data mart, with JSON payload fields and indexes for graph edges.
- `data/dedupe_review_queue.csv`: possible aliases; nothing silently merged except identical normalized names.
- `data/excluded_catalogue_rows.csv`: directory-only, hypothetical or not-yet-open records that should not appear as venue cards.

## Frontend data contract

`venue_id` remains stable for this export; `legacy_venue_id` preserves backwards join to v1 where present. If a venue changes its public marketing name, use a durable `venue_alias` mapping in production instead of changing ID blindly.

```
GET /api/venue-leads?q=...&type=...&min_classroom=...&after18=yes
GET /api/venue-leads/:venue_id
GET /api/venue-leads/:venue_id/evidence
```

These API endpoints are *proposed*; not implemented by this research deliverable.

Important field distinctions:

- `after18_policy`, `weekend_policy`, `overnight_policy`: `{yes,no,restricted,unknown}`; **policy, never inventory**. Only a listing/official statement, NOT proof that a future date is free.
- `availability_live=false`, `can_advertise_available=false`, `is_currently_bookable=false`: **for all candidates**. No calendar integration exists.
- `capacity_laptops`: explicit people doing laptop work at desks; do not fill it from theatre/seated/standing.
- `capacity_classroom`, `capacity_theatre`, `capacity_boardroom`, `capacity_standing` are NOT interchangeable. `area_sqm` is an area, not capacity.
- `price_gbp_from`, `price_unit`, `price_conditions`: the Enfield £20–31 figures are **normal opening-hours rates**, not confirmed evening pricing. University `from £670` examples have unspecified unit, so the amount is left in evidence notes, not inserted into `price_gbp_from`.
- `room_granularity=legacy_unspecified`: source is about a building/venue, not necessarily a specific bookable room. `listing_granularity=building_or_unspecified` must be excluded from room-level pricing comparisons.
- `source_class=legacy_research`: prior research snapshot had source URLs but no complete retrieval audit.
- `review_status=page_reviewed`: specific official pages reviewed on 2026-10-22; `url_discovered` is NOT the same evidence quality.
- `operator_id=null` is correct when an operator is unknown; a council directory listing does not make the council the operator of a privately owned church, school, etc.
- `research_priority` is a hand-built lead triage heuristic, *not* probability of availability or rental suitability.
- `is_hackathon_confirmed`: should never be used as a commercial availability flag; explicit laptop capacity is exceptionally rare.

### UI approach

Use two separate feeds: **Verified bookable supply** (future first-party agreements with calendar API) vs **Potential venues / leads** (this dataset). Show *Unknown* instead of *No* for missing WiFi, power, access, weekend permission, contact, capacity. Show evidence and date under each field. Never imply current availability from normal public opening hours.

Recommended filters: source reliability, operator, area/postcode, type, evidence status, evening policy, weekend policy, room setup capacity, AV, Wi-Fi, seating/desk format, enquiry link, lead priority. Hide map pins without verified coordinates; do not geocode district-only postcodes to building points.

## Cognee / knowledge graph

The JSONL graph files define a *transport-independent staging format*. Cognee can ingest these nodes/edges via an app-specific adapter or into a separately managed graph database. This export does **not** claim to have performed `cognee.add()` / `cognee.cognify()` calls: no Cognee credentials or backend were available.

Edges:

- `operator_id --OPERATES--> building_id` **only when operator is explicitly recorded**.
- `building_id --HAS_SPACE--> space_id` (for building-wide leads this is a provisional reference, not a proved discrete room).
- `space_id --DESCRIBED_BY--> venue_id`.

Claims are separate objects with provenance and numeric value, including the source URL. A retrieval agent can respond e.g. “I found an advertised Enfield meeting room; £20/hour applies during opening hours; after-hours quote required” with a link to its evidence, rather than hallucinating a booking price.

**Example agent response policy:**

1. Identify `space_id` and its building from nodes.
2. Apply hard filters only for *known* values; for `unknown` ask the operator or mark pending.
3. Retrieve relevant evidence objects for every capacity, price, internet or hire-policy statement.
4. Never say “available Friday 19:00” unless your calendar connector supplies an exact live slot and venue agrees to book it.
5. Suggest enquiries for promising but unverified leads; handle contacts under UK GDPR/PECR.

## Main repository compatibility

As of this research, `aleetreny/spaceXAI` has the `Same Room` app and a `supabase/schema.sql` schema for communities/events. Do not replace these components. Keep venue intelligence under a dedicated `venue-intelligence/` module or an isolated feature branch. The SQL migration in `docs/supabase_venue_intelligence.sql` exclusively creates `vi_*` tables, therefore it does not modify `communities` or `events`.

## Update plan

1. Weekly: revisit permitted first-party URLs with conditional GET, robots.txt, rate limits, caching and host-level throttling. Record retrieval `status`, `date`, `hash`, `licence`, field differences; never overwrite an observation without evidence history.
2. Monthly: municipal directory discovery (borough/source adapters), official venue enrichment, closed/relocated checks.
3. Quarterly: reconcile geographic open data imports after licensing review (GLA 2026 has OS/third-party notices; do **not** silently merge; OSM ODbL must be isolated and attributed).
4. Continuous when integrated: booking calendars and partner webhooks, with separate availability table TTL and transactional verification.

Do not scrape Google Maps to build a persistent competing database. Marketplaces should be approached for a partnership or approved API/data-sharing contract. Follow public source terms and preserve attribution and privacy.

## Known limitations and honest coverage

- No accurate longitude/latitude values in this deliverable; do not draw fictitious map pins.
- Most records have missing Wi-Fi, electrical capacity and true hackathon-with-laptops capacity.
- No paid partner API, no current bookings, no contact outreach, no operator approval.
- Some records are *promising research leads*, not rentals. Audit individual pages before making public commercial claims.
- A global, entirely complete list of venues in Greater London is not realistically possible; source inventories change, many private offices do not advertise hire.

**Calendar limitation:** `weekend_policy=yes` means some weekend hire is advertised; it does not mean both Saturday **and** Sunday all-day, or any particular weekend is free. `after18_policy=yes` may stop at 21:00. A 24-hour or two-day hackathon requires explicit continuous access and power/network confirmation.
