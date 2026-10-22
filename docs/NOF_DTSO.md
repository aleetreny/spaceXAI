# NOF_DTSO

**Status:** `ready-for-doc`
**Scope:** database matching hackathon communities to London venues with idle out-of-hours capacity
**Vocabulary:** [.claude/skills/doc-vocab] (shared) · [NOF/docs/glossary.md] (project)
**Decisions respected:** ADR 0001 — TLS under Avast interception
**Seams verified by:** `python NOF/verify_db.py`

## Problem Statement

NOF exists to answer one commercial question: **which hackathon community could
use which London venue, at a time that venue is otherwise empty?** Co-working
spaces that close at 18:00 and shut at weekends are idle exactly when
hackathon organisers need space.

Answering it requires two datasets joined on two keys — headcount against
capacity, and event timing against closing time. Four documentation gaps
follow:

1. **The matching logic is invisible in the data.** A list of communities and a
   list of venues do not express the join. Delivered as spreadsheets, the
   relationship between them lives only in whoever built them.

2. **The two join keys are almost entirely unpopulated, and that is easy to
   hide.** Venue capacity is 0 of 11; venue hours 0 of 11; community attendance
   1 of 10. A matching view that treats missing input as "probably fine" would
   return 100 confident pairings from almost no evidence.

3. **One upstream source cannot supply what the model needs, and this is not
   obvious.** Google Business Profile has no capacity field at all — no actor
   setting produces it. Opening hours require a second paid pass, and that pass
   was blocked by Google's consent interstitial. Both facts cost money to
   discover and must not be rediscovered.

4. **A failed scrape still produced usable data, and a naive reading discards
   it.** The consent-blocked run yielded eleven real venue names with
   coordinates before detail extraction failed, plus one junk row that was
   Google's cookie banner captured as a place.

## Solution

A SQLite database, two generator scripts, a seam checker, and this spec,
under [NOF].

- **[NOF/hackathon_db.py]** — builds `hackathon.db`: `communities`, `venues`,
  `observed_events`, `sources`, and the `v_match` view. Exports one Parquet per
  table.
- **[NOF/hackathon_communities.py]** — the community dataset and its `.xlsx` /
  `.csv` form, for reading rather than joining.
- **[NOF/verify_db.py]** — the seams, executable.
- **[NOF/docs/glossary.md]** — field-level vocabulary.

SQLite rather than a spreadsheet because the deliverable *is* a join. A
`.xlsx` can hold both tables but cannot express the relationship, and the
relationship is the product.

## Commercial Model

A community renting a venue through the agent pays **two costs and nothing
else**:

| Cost | Basis |
|---|---|
| **Cleaning** | Restoring the space to its weekday condition |
| **Staff** | Per 50 event members — supervision scaled to headcount |

No rent, no venue hire fee, no hourly rate. This is what makes the match work
on both sides: the venue is not selling time it was otherwise using, so its
marginal cost is cleaning and supervision, and that is exactly what the
community covers. The landlord's alternative is an empty building.

Two consequences for the data model:

1. **`typical_attendance` is a price input, not only a logistics one.**
   Headcount in blocks of 50 determines staff cost. A 300-person event such as
   HackKings is six staff units; a 40-person evening meetup is one. The field
   therefore carries commercial weight and its current coverage — 1 of 10
   communities — is a revenue blocker, not just a data gap.

2. **Venue rows need cost fields.** `cleaning_cost` and `staff_cost_per_50` are
   venue-specific and must be sourced per venue. They follow the same rule as
   every other field: blank until verified, never estimated. A quoted price
   built on an invented cleaning cost is worse than no quote.

## Documentation Requirements

1. **Structure.** Glossary organised by table — the model, community fields,
   venue fields, the matching view, source limits — so a reader looking up one
   column finds it without reading the whole file.
2. **Audience.** Someone operating the match: sourcing venues, approaching
   organisers. Assumed commercially literate; not assumed to know SQL internals
   or Apify.
3. **Tone.** Factual about coverage. Where a field is empty, say how empty and
   why, with the count.
4. **Reference sources.** Every table row carries `source_url` and
   `last_verified`; the glossary names which upstream source can and cannot
   supply each field.
5. **Code examples.** The `v_match` query shown as runnable SQL, since that is
   how the database is meant to be used.
6. **API contracts.** Both join keys documented by name and type on both sides.
   The verdict enumerations listed in full, including the `unknown:` variants.
7. **Decision log.** Record why SQLite over `.xlsx`, why blanks over estimates,
   and why `broker` rows are excluded from matching.
8. **Vocabulary layering.** TLS terms referenced from shared; Apify platform
   terms referenced from [NWS/docs/glossary.md]; only NOF-specific terms
   defined locally.
9. **Negative findings are in scope.** "Capacity is unobtainable from Google
   Maps" and "the scrape cost $0.52 and returned zero venues" are results.
10. **Out-of-scope exclusions.** No outreach material, no pricing model, no
    venue booking workflow.

## Implementation Decisions

**Artifacts.** Three scripts and a database at [NOF] root, documentation in
[NOF/docs]. Scripts sit at the root rather than in `scripts/`, matching [SRP]
and [YFI]; only `docs/` is standardised across the tree.

**Terms defined locally**: idle capacity, out-of-hours window, match,
`org_type` enumeration, `schedule_pattern`, `capacity_total` vs
`capacity_event`, honest verdict, geocode suspect. **Referenced**: TLS
vocabulary from the shared glossary, Apify actor/run/dataset from
[NWS/docs/glossary.md].

**Four choices, each tied to an observed failure:**

| Choice | Prevents |
|---|---|
| Blank rather than estimated values | Fabricated capacity figures becoming the basis of a real approach to a real venue |
| Verdicts return explicit `unknown:` strings | 100 pairs reading as matches when both inputs are NULL |
| `broker` rows excluded from `v_match` | HubbleHQ, an intermediary, being treated as a bookable space |
| `data_confidence` on every row | A single passing mention of an organiser carrying the same weight as a verified one |

**SQLite as the primary artifact, Parquet alongside.** SQLite for the join and
portability; Parquet for columnar reads from pandas without a database
round-trip. The `.xlsx` is retained as a readable export, not the source of
truth.

**The geocode anomaly is recorded in-row, not silently corrected.** HubbleHQ's
coordinates place it in Dumfries & Galloway. The note says so; the value is
unchanged. A silently fixed coordinate would hide that the whole row needs
re-verification.

## Verification / Testing Decisions

**Executable seams** — `python NOF/verify_db.py`:

1. **Schema integrity.** Both join keys present on both tables — without them
   the database cannot do its one job.
2. **Provenance.** Every row in `communities` and `venues` carries a non-empty
   `source_url` and `last_verified`.
3. **Honest verdicts.** `v_match` never returns `fits` or `idle in window` when
   an input is NULL or blank. The load-bearing check: this dataset is almost
   entirely missing, so an optimistic default would make the view actively
   misleading rather than merely incomplete.
4. **Export parity.** SQLite, Parquet and CSV agree on row counts across four
   tables.
5. **Gaps surfaced.** Coverage of the three sparse fields is reported as counts
   on every run, so degradation is visible rather than inferred.
6. **Broker typing.** HubbleHQ is typed `broker` and absent from `v_match`.

**Manual rules** — not automatable:

7. **No estimated values.** A plausible capacity figure is indistinguishable
   from a sourced one once written. Only a reviewer can confirm a number came
   from somewhere.
8. **`data_confidence` honestly assigned.** `low` means one unverified mention.
   No check can tell a generous rating from an accurate one.
9. **Cost awareness before re-scraping.** Apify bills $0.04 per business per
   stage. Re-fetch by run id while developing.

## Out of Scope

- Outreach, pricing, commission model, booking workflow.
- Venue photography, floor plans, amenity data.
- Communities outside London, except global franchises with London reach.
- Fixing the Apify consent-interstitial failure — diagnosed in this session
  (pin `apifyProxyCountry`), not yet implemented or paid for.
- The `.xlsx` as a maintained artifact; it is an export.

## Further Notes

**The database's most useful current output is a list of what it lacks.** All
100 candidate pairs read `unknown` on both axes. Three columns —
`venues.capacity_total`, `venues.weekday_close`/`weekend_open`, and
`communities.typical_attendance` — stand between this structure and a working
match. Naming them precisely is more valuable than a half-populated table that
looks finished.

**The cheapest of the three is community attendance.** Organiser Luma and
Meetup pages publish attendee counts on past events; that is a plain fetch with
no Apify, no cost and no consent wall. Venue capacity and hours are harder and
probably come from a broker.

**A failed run is not necessarily a dataset of zero.** The consent-blocked
scrape returned no venue records, but its *logs* contained eleven venue names
with coordinates, recovered from the blocked URLs. Those seeded the `venues`
table. The same run also deposited Google's cookie banner into the dataset as a
place titled *"Before you continue to Google"* — which is why `verify_db.py`
exists at all.

**Vocabulary note worth acting on.** Apify terms now appear in two projects
([NWS] and NOF). By the scope rule in
[.claude/skills/doc-vocab/README.md], a term used by two or more projects
belongs in the shared glossary. NOF currently references NWS's definitions
instead, which works but inverts the rule — the shared glossary is the correct
home, and moving them is a small pending change.
