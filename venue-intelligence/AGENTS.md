# Venue Intelligence data module instructions

- This folder is a **2026-10-22 London venue prospecting snapshot**. It is separate from the existing Same Room app at repository root.
- Do not rewrite `main` app or schemas when adding venue integration. Use docs/TEAM_HANDOFF.md and docs/INTEGRATION.md.
- Treat all records as **research leads** (`lead_status=research_lead`), not bookable inventory. Availability is **never confirmed**.
- Preserve `venue_id`, `building_id`, `space_id`, provenance URLs, evidence caveats and review tier when transforming data.
- Use `data/venues_frontend.json` for cards; `data/venues_v2.json` for full attributes; `data/evidence.jsonl` for citations. Null/unknown must stay unknown.
- Never infer plugged-in laptop capacity from standing/theatre capacity, nor overnight availability from evening/weekend hire.
- Use `docs/supabase_venue_intelligence.sql` in a separate namespaced migration if enabling Supabase; service role server-side only. Treat `data/cognee_documents.jsonl` and `data/cognee_edges.jsonl` as inputs requiring a real integration adapter.
- Rebuild from `cd venue-intelligence && python3 scripts/build_v2.py && python3 scripts/export_frontend.py && python3 scripts/quality_audit.py` and validate with `python3 -m unittest discover -s tests -v`.
- Review third-party licence and terms before adding scraped external databases or exposing commercially in production.
