#!/usr/bin/env python3
"""Read-only public lead cards for collaborator's viewer, no booking assertions."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'data'
r=json.loads((P/'venues_v2.json').read_text(encoding='utf-8'))
public=[]
for v in r:
    public.append({
      'id':v['venue_id'],'name':v['display_name'],'type':v['venue_type'],
      'postcode':v['postcode'],'borough':v['borough'],'address':v.get('street_address'),
      'building_id':v['building_id'],'space_id':v['space_id'],
      'room_granularity':v['listing_granularity'],
      'evening_policy':v['after18_policy'],'weekend_policy':v['weekend_policy'],
      'laptop_capacity':v['capacity_laptops'],'classroom_capacity':v['capacity_classroom'],
      'theatre_capacity':v['capacity_theatre'],'standing_capacity':v['capacity_standing'],
      'wifi':v['wifi_status'],'av':v['av_status'],
      'price_from_gbp':v['price_gbp_from'],'price_unit':v['price_unit'],
      'price_conditions':v.get('price_conditions'),
      'research_priority':v['research_priority'],'source_url':v['source_url'],
      'source_quality':v['review_status'],'availability':'not_verified',
      'label':'Potential venue — enquire; no live availability',
    })
(P/'venues_frontend.json').write_text(json.dumps(public,indent=2,ensure_ascii=False),encoding='utf-8')
print('Exported',len(public),'public lead cards')
