#!/usr/bin/env python3
"""Snapshot audit; avoid counting missing fields as negatives."""
import json,re
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]/'data'
v=json.loads((P/'venues_v2.json').read_text(encoding='utf-8'))
n=len(v)
full=lambda x: bool(x and re.fullmatch(r'[A-Z]{1,2}\d[A-Z\d]?\s+\d[A-Z]{2}',x,re.I))
field=[('Full postcode',sum(full(x['postcode']) for x in v)),('Any postcode',sum(bool(x['postcode']) for x in v)),('Exact address',sum(bool(x.get('street_address')) for x in v)),('Coordinates',sum(x['latitude'] is not None and x['longitude'] is not None for x in v)),('Laptop work capacity',sum(x['capacity_laptops'] is not None for x in v)),('Classroom capacity',sum(x['capacity_classroom'] is not None for x in v)),('Theatre capacity',sum(x['capacity_theatre'] is not None for x in v)),('Wi-Fi explicitly confirmed',sum(x['wifi_status']=='yes' for x in v)),('After 18:00 policy advertised',sum(x['after18_policy']=='yes' for x in v)),('Weekend policy advertised',sum(x['weekend_policy']=='yes' for x in v)),('Live bookable availability',sum(x['availability_live'] for x in v))]
lines=['# Audited quality — 22 October 2026','','This is a dataset of **research leads**, not a bookable property platform. All commercial listings require operator approval/verification.','',f'Unique research leads: **{n}**. Prior dataset: **295**. Net increase: **{n-295}**.','','| Feature | Present | Coverage |','|---|---:|---:|']
lines += [f'| {name} | {k} | {k/n:.1%} |' for name,k in field]
lines+=['','## Review-level distribution','']
lines += [f'- `{status}`: **{k}** records' for status,k in Counter(x['review_status'] for x in v).most_common()]
lines+=['','## Non-negotiable caveats','',
'- A yes for evening/weekend means **a published hire policy**, not a calendar slot; overnight is unknown almost everywhere.',
'- A theatre seat is not an electrically powered desk for a programmer.',
'- Weak geocoding prevents an accurate pin map. Partial postcode (`W8`, `N1`) is a district, not a precise street address.',
'- Some records refer to a whole building, venue portfolio or future lead. `listing_granularity` prevents treating them as literal rooms.',
'- Normal-hours pricing is never quoted as evening/weekend pricing. Missing values are `null`/`unknown`, not zero/false.',
'- The predecessor 295-row snapshot has source URLs but lacks full independent per-page retrieval logs. Review tier reflects that.',
'- External source licences: do not scrape Google Maps or mirror protected marketplace inventories into a commercial product.',
'','## Practical next fieldwork','',
'- Contact/confirm capacity at laptop desks, power sockets, Wi-Fi speed, event minimum hours, weekend security and price.',
'- Run true postcode/address enrichment using licensed geocoding (or an appropriate open service); verify building-level coordinates.',
'- Add operator contracts and a separate live availability table before advertising bookable inventory.',
'- Implement source-specific schedulers and store raw HTTP hashes and revisions for material field changes.',
]
(Path(__file__).resolve().parents[1]/'docs'/'QUALITY_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Wrote field-by-field quality audit')
