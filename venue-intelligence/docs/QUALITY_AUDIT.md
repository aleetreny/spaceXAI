# Audited quality — 22 October 2026

This is a dataset of **research leads**, not a bookable property platform. All commercial listings require operator approval/verification.

Unique research leads: **381**. Prior dataset: **295**. Net increase: **86**.

| Feature | Present | Coverage |
|---|---:|---:|
| Full postcode | 83 | 21.8% |
| Any postcode | 268 | 70.3% |
| Exact address | 15 | 3.9% |
| Coordinates | 0 | 0.0% |
| Laptop work capacity | 1 | 0.3% |
| Classroom capacity | 4 | 1.0% |
| Theatre capacity | 84 | 22.0% |
| Wi-Fi explicitly confirmed | 33 | 8.7% |
| After 18:00 policy advertised | 44 | 11.5% |
| Weekend policy advertised | 29 | 7.6% |
| Live bookable availability | 0 | 0.0% |

## Review-level distribution

- `previous_research`: **279** records
- `page_reviewed`: **79** records
- `url_discovered`: **23** records

## Non-negotiable caveats

- A yes for evening/weekend means **a published hire policy**, not a calendar slot; overnight is unknown almost everywhere.
- A theatre seat is not an electrically powered desk for a programmer.
- Weak geocoding prevents an accurate pin map. Partial postcode (`W8`, `N1`) is a district, not a precise street address.
- Some records refer to a whole building, venue portfolio or future lead. `listing_granularity` prevents treating them as literal rooms.
- Normal-hours pricing is never quoted as evening/weekend pricing. Missing values are `null`/`unknown`, not zero/false.
- The predecessor 295-row snapshot has source URLs but lacks full independent per-page retrieval logs. Review tier reflects that.
- External source licences: do not scrape Google Maps or mirror protected marketplace inventories into a commercial product.

## Practical next fieldwork

- Contact/confirm capacity at laptop desks, power sockets, Wi-Fi speed, event minimum hours, weekend security and price.
- Run true postcode/address enrichment using licensed geocoding (or an appropriate open service); verify building-level coordinates.
- Add operator contracts and a separate live availability table before advertising bookable inventory.
- Implement source-specific schedulers and store raw HTTP hashes and revisions for material field changes.
