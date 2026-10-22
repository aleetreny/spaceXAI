# NOF — Project Overview

High-level summary of what this project is for and how it works. For field
definitions see [NOF/docs/glossary.md]; for the full spec and verification
approach see [NOF/docs/NOF_DTSO.md].

---

## The idea

**Rent out space nobody is using.**

London co-working venues close at 18:00 and shut at weekends. The lights go
off, the rent keeps running. Hackathon communities need exactly those hours and
mostly cannot afford commercial event space.

NOF is the agent between them. The arbitrage is on **time**, not property: the
same square metres sold twice, into a window the landlord already writes off.

## What a community pays

Two costs. Nothing else.

| Cost | Basis |
|---|---|
| **Cleaning** | Restoring the space to its weekday condition |
| **Staff** | Per 50 event members — supervision scaled to headcount |

No rent. No venue hire fee. No hourly rate.

This is what makes the deal work on both sides. The venue is not selling time
it was otherwise using, so its marginal cost is cleaning and supervision — and
that is precisely what the community covers. The landlord's alternative is an
empty building earning nothing.

It also means **headcount is a price**, not just a logistics number. A
300-person event is six staff units; a 40-person evening meetup is one.

## How the matching works

Everything reduces to two joins.

```
   COMMUNITY                               VENUE
   ─────────────                           ─────────────
   typical_attendance      ───────────►    capacity_total
   schedule_pattern        ───────────►    weekday_close
   typical_start                           weekend_open
```

A venue qualifies when it is **closed when the community meets** and **big
enough to hold them**. The `v_match` view in `dbs/hackathon.db` evaluates every
community × venue pair and returns two verdicts:

- `capacity_verdict` — `fits` · `too small` · `unknown: …`
- `availability_verdict` — `idle in window` · `occupied` · `unknown: …`

**Design rule: a missing input returns `unknown`, never an optimistic guess.**
A matching engine that assumes the best when it lacks data produces confident
nonsense, and confident nonsense is what gets a real venue approached with a
quote built on an invented number.

## The data

```
dbs/hackathon.db
   communities       who runs hackathons, how often, how many, when
   venues            where they could run, when idle, at what cost
   observed_events   dated events evidencing the schedule patterns
   sources           aggregators and platforms the data came from
   v_match           the join
```

Also exported as Parquet per table, plus `.xlsx` / `.csv` for reading.

Every row carries `source_url`, `last_verified` and `data_confidence`.
Unverified fields are **left blank rather than estimated** — a blank is a
visible gap, an estimate is a liability.

Collection: Apify's Google Maps scraper for venue discovery, web search for
communities. Built by `hackathon_db.py`, checked by `verify_db.py` (six
automated seams).

## Where it stands

| | populated |
|---|---|
| Communities catalogued | **10** |
| Venues identified | **11** (10 co-working + 1 broker) |
| Venue capacity | **0 / 11** |
| Venue hours | **0 / 11** |
| Community attendance | **1 / 10** |
| Match pairs resolved | **0 / 100** |

The structure is right and both join keys are empty. Two reasons, both
documented:

1. **Google Business Profile publishes no venue capacity field.** No scraper
   setting produces it. It has to come from venue websites or a broker.
2. **The hours scrape was blocked** by Google's EU cookie-consent
   interstitial — the proxy exits in FR/IT instead of a country without the
   wall.

The database currently reports, accurately, that it does not know. That is the
correct state, not a failure — but it is the blocker.

## What unblocks it

| Field | Realistic source | Difficulty |
|---|---|---|
| `communities.typical_attendance` | Luma / Meetup past-event pages | **Easy** — plain fetch, no cost, no consent wall |
| `venues.capacity_total` | Venue websites, or a broker such as HubbleHQ | Medium |
| `venues.weekday_close` / `weekend_open` | Venue websites; or fix the proxy country and re-scrape | Medium |
| `venues.cleaning_cost` / `staff_cost_per_50` | Direct conversation with each venue | Hard — commercial, not scrapeable |

Attendance is the cheapest and unlocks the pricing side as well as the
capacity match.

## Related work in this repo

`spaceXAI/` — **Same Room**, the entry for the Grok Bot Community Engineering
London Hackathon (22 Oct 2026, Expedite, Lyric Square). A no-backend app that
pairs two communities *in the room* and publishes a shareable event page.

The two are complementary:

- **Same Room** pairs community × community — the demand side meeting itself.
- **This database** pairs community × venue — the supply side.

One community appears in both datasets: **The Hack Collective**.

Same Room's `AGENTS.md` carries the rule *"Do not invent member quotes,
attendance numbers, or community bios... If a source is missing, say so."* The
database follows the same discipline, which is why its honest answer today is
`unknown` rather than a hundred plausible matches.
