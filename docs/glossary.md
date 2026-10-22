# NOF Glossary

Vocabulary for NOF — matching hackathon communities to London venues with idle
out-of-hours capacity.

**Shared terms** — TLS interception, combined CA bundle, baselines and
calibration — are defined in [.claude/skills/doc-vocab/glossary.md] and not
repeated here. Apify platform terms (actor, run, dataset, `apify_api_*` token)
are defined in [NWS/docs/glossary.md]; NOF is the second project to use them.

## The model

| Term | Meaning |
|---|---|
| **Idle capacity** | Space a venue is not using. A co-working venue that closes at 18:00 and shuts at weekends has an empty building exactly when hackathon communities need one. NOF exists to find and match those two facts. |
| **Out-of-hours window** | The period a venue is closed but could host — weekday evenings after `weekday_close`, and weekends where `weekend_open` is `closed`. |
| **Match** | A community whose `schedule_pattern` falls inside a venue's out-of-hours window and whose `typical_attendance` fits its `capacity_total`. Expressed as the `v_match` view. |

## Community fields

| Term | Meaning |
|---|---|
| **`community_id`** | Stable slug; the primary key and the join target for any future event table. |
| **`org_type`** | `community` (self-organising, recurring) · `student_society` (university-affiliated) · `franchise` (global brand with local chapters, e.g. Startup Weekend) · `agency` (runs events for clients) · `curator` (aggregates others' events, does not run its own). The distinction matters: curators are a distribution channel, not a venue customer. |
| **`schedule_pattern`** | `evening` · `weekend` · `multi_day` · `mixed`. **Join key** against venue availability. |
| **`typical_attendance`** | Headcount. **Join key** against venue capacity. Populated for 1 of 10 communities. |
| **`cadence`** | How often the organiser runs events — drives how valuable a single relationship is. |
| **`data_confidence`** | `high` · `medium` · `low`. How much of the row is verified rather than inferred from a single mention. |

## Venue fields

| Term | Meaning |
|---|---|
| **`venue_id`** | Stable slug; primary key. |
| **`venue_type`** | `coworking` · `broker` · `university` · `corporate` · `event_space`. Only `coworking` rows enter `v_match`. |
| **`capacity_total`** | Headline capacity. **Not available from Google Maps** — Google Business Profile has no capacity field. Must come from the venue's own site or a broker. Currently 0 of 11 populated. |
| **`capacity_event`** | Capacity in event configuration, usually lower than desk count. |
| **`weekday_close`** / **`weekend_open`** | The availability pair. `weekend_open = 'closed'` is the signal that the whole weekend is idle. Currently 0 of 11 populated. |
| **`broker`** | Intermediary listing the space. [HubbleHQ] is a broker, not a venue — likely the source for the capacity and hours the venue rows lack. |

## The matching view

| Term | Meaning |
|---|---|
| **`v_match`** | SQLite view cross-joining communities against `coworking` venues; 100 candidate pairs at present. |
| **`capacity_verdict`** | `fits` · `too small` · `unknown: venue capacity missing` · `unknown: community size missing`. |
| **`availability_verdict`** | `idle in window` · `occupied` · `unknown: venue hours missing`. |
| **Honest verdict** | The rule that a verdict is never optimistic on absent input. Both verdict columns return an explicit `unknown:` string rather than defaulting to a match. All 100 pairs currently read `unknown` on both axes, which is the correct answer, not a failure. |

## Data sources and their limits

| Term | Meaning |
|---|---|
| **Google Business Profile (GBP)** | What the Apify actor scrapes. Carries `totalScore`, address, coordinates, `openingHours` — but **no capacity**, and no review count despite some examples implying one. |
| **Search mode vs `placeIds` mode** | The actor returns `openingHours: {}` in search mode; hours require a second pass submitting `placeIds`. Two stages, ~$0.08 per venue. |
| **Consent interstitial** | Google's EU cookie wall. RESIDENTIAL proxies exiting in FR/IT receive it instead of the place page, and the actor skips the result. It can also land in the dataset as a fake place titled *"Before you continue to Google"*. The fix is pinning `apifyProxyCountry`. |
| **Geocode suspect** | A coordinate inconsistent with the stated location. HubbleHQ geocodes to 55.13, -3.27 — Dumfries & Galloway, not London — and is flagged rather than silently trusted. |
