# Night Office — London Venue Intelligence v2

**Snapshot 2026-10-22.** A candidate-lead universe for London hackathon venues, not a booking marketplace feed and not licensed marketplace listing content.

This independent data package was prepared to avoid conflicts with the current `aleetreny/spaceXAI` repository, whose `main` branch currently contains a separate Same Room hackathon demo.

## What is inside

- `data/venues_v2.json`: complete validated-shape staging seed for website / agent.
- `data/venues_v2.csv`: spreadsheet-friendly wide table.
- `data/venues_v2.jsonl`: NDJSON ingestion stream.
- `data/venue_intelligence_v2.sqlite`: local query database.
- `data/buildings.jsonl`, `spaces.jsonl`, `operators.jsonl`: candidate node catalogs.
- `data/evidence.jsonl`: claim-level provenance.
- `data/cognee_documents.jsonl`: cited text documents for a Cognee ingestion adapter.
- `data/cognee_edges.jsonl`: normalized edge staging file for a graph adapter.
- `data/researched_candidates.tsv`: manually curated and sourced second-pass additions.
- `data/targeted_enrichment.tsv`: additional source-backed fields for 15 highest-signal rooms.
- `data/legacy_venues_v1.csv`: untouched first-pass input; reproducible merge.
- `data/stats_v2.json`: actual dataset and data-quality totals.
- `docs/INTEGRATION.md`: complete implementation contract, filters, licenses and caveats.
- `docs/types.ts`: frontend TypeScript contract.
- `docs/supabase_venue_intelligence.sql`: independent migration for named `vi_*` tables, **not applied** to a database.
- `tests/test_data.py`: invariants; `python -m unittest discover -s tests -v`.
- `legacy_pipeline/`: initial V1 connector prototypes; external scraping untested, included for reference only.

## Generate outputs reproducibly (no Internet required)

```bash
python3 scripts/build_v2.py
python3 -m unittest discover -s tests -v
```

`build_v2.py` is standard-library Python; it does not scrape or modify any website and does not require API secrets. Results are deterministic given the included seed files.

For high-level counts open `data/stats_v2.json`. The source file names and URLs are provided by each record. **Only exact venue pages actually reviewed are tagged `page_reviewed`.** Records from the prior research without an independent retrieval audit remain `previous_research` even if they look plausible. Most data points remain unknown. Do not represent leads as live bookable supply.

## Deployment recommendation

Your colleague can load the static JSON in a browser or ingest JSONL/CSV into his own database, and use the typed contract. For best integrity, build source-specific ETL that upserts `vi_venues`, `vi_buildings`, `vi_spaces`, `vi_operators`, and `vi_evidence` with service role, then indexes `vi_edges` for Cognee/graph retrieval. Avoid client-side writes. Prove capacity and policy with cited evidence; build an independent availability calendar connector when you actually have partner agreements.

**Potential data licensing:** governmental cultural infrastructure 2026 carries Ordnance Survey / third-party notices and was not bulk imported; Google Maps and venue marketplaces were deliberately not scraped; OSM is not included here. Terms must be reviewed before commercial reuse of new bulk external sources.

## Convenient implementation extras

- `data/venues_frontend.json`: preselected public card fields; all cards visibly labelled as *potential venue*, with no bookable availability claims.
- `data/first_party_time_window_shortlist.csv`: highest-signal leads with **page-reviewed** published hire policies (not live bookings).
- `docs/QUALITY_AUDIT.md`: actual coverage and weaknesses.
- `scripts/export_frontend.py`, `scripts/quality_audit.py`: regenerate these derived outputs.

Regenerate those two exports after running `scripts/build_v2.py`:

```bash
python3 scripts/export_frontend.py
python3 scripts/quality_audit.py
```
