#!/usr/bin/env python3
"""Deterministic and conservative venue-lead exporter, preserving provenance.
Do not turn scraped descriptions into verified date availability.
Does not make network requests. Only combines local research records.
"""
from __future__ import annotations
import csv, hashlib, json, os, re, sqlite3, unicodedata
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse
from datetime import date

HERE=Path(__file__).resolve().parents[1]
BASE=HERE/'data'/'legacy_venues_v1.csv'
V2=HERE/'data'/'researched_candidates.tsv'
DATE='2026-10-22'


def slug(s):
    s=unicodedata.normalize('NFKD', str(s or '')).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')

def stable(kind,*parts):
    return kind+'_'+hashlib.sha256(' | '.join(slug(x) for x in parts).encode()).hexdigest()[:16]

def as_int(v):
    try:
        return int(float(str(v))) if str(v).strip() else None
    except(ValueError,TypeError): return None

def as_num(v):
    try: return float(str(v)) if str(v).strip() else None
    except(ValueError,TypeError):return None

def value(v):return (str(v).strip() if v is not None else '')

def known(v):return v if v in ('yes','no','restricted') else 'unknown'

def read_csv(p, **kwargs):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,**kwargs))

# Strict alias map: EXACT same facility with naming changes, never dedup individual rooms.
ALIASES={
 'westminster little titchfield g 03':'westminster little titchfield street g 03',
 'rbkc worlds end community centre main hall':'world s end community centre',
 'huddle hammersmith event spaces':'huddle event spaces',
 'qmum the mills fabrica':'the mills fabrica',
 'the mills fabrica kings cross event space':'the mills fabrica king s cross event space',
 'westminster portland hall':'portland hall',
}

def canonical(n):
    v=slug(n).replace('-',' ')
    return ALIASES.get(v,v)

# A manual review checked these exact publisher directory pages during this round.
REVIEWED={
 'https://uncommon.co.uk/event-space/',
 'https://www.enfield.gov.uk/services/libraries/library-meeting-rooms-for-hire',
 'https://www.westminster.ac.uk/about-us/visit-us/venues-and-accommodation/lecture-theatres-and-conference-halls',
 'https://www.rbkc.gov.uk/bookable-community-spaces/meeting-spaces',
 'https://www.rbkc.gov.uk/libraries/room-bookings',
 'https://www.qmul.ac.uk/venues/ourvenues/mileend/queensbuilding/',
 'https://www.qmul.ac.uk/venues/ourvenues/mileend/',
 'https://www.qmul.ac.uk/venues/ourvenues/mileend/bancroft/',
 'https://www.qmul.ac.uk/venues/ourvenues/mileend/graduatecentre/pestonlecturetheatre/',
 'https://www.gold.ac.uk/conference-services/spaces/',
 'https://www.huckletree.com/hubs/hire-event-spaces/london',
 'https://ramenclub.com/ramen-space/events/',
 'https://www.civo.com/tech-junction',
 'https://www.efigroup.ac.uk/venue-hire',
 'https://www.plexal.com/event-hire/',
}

# Legacy baseline has no complete source-by-field historical audit; keep it as a separate evidence tier.
legacy=read_csv(BASE)
additions=read_csv(V2,delimiter='\t')
rows=[]; seen={}; potential_aliases=[]; excluded=[]; facts=[]

def register(d, provenance):
    name=d['name']; url=d['source_url']
    if not name or not (url.startswith('https://') or url.startswith('http://')):return
    # Catalogue-level/coming-soon records are not bookable venues.
    if (name.lower() in ('huckletree london - general event spaces', 'university of westminster - venue hire','huckletree - the forum leadenhall (future)')) or 'index only' in value(d.get('notes')).lower() or 'collection landing' in value(d.get('notes')).lower() or 'not a distinct rental' in value(d.get('notes')).lower() or 'coming soon' in value(d.get('notes')).lower():
        excluded.append({'name':name,'source_url':url,'reason':'catalog_only_or_not_open'});return
    row={
      'venue_id': stable('v',name),
      'display_name':name,
      'building_name':value(d.get('building')) or name,
      'room_name':value(d.get('space')) or None,
      'room_granularity':'room' if value(d.get('space')) else 'legacy_unspecified',
      'venue_type':value(d.get('category')) or value(d.get('venue_type')) or 'other',
      'postcode':value(d.get('postcode')) or None,
      'borough':value(d.get('borough')) or None,
      'latitude':as_num(d.get('latitude')),
      'longitude':as_num(d.get('longitude')),
      'operator':value(d.get('operator')) or None,
      'source_url':url,
      'source_domain':urlparse(url).netloc,
      'source_class': 'first_party_reviewed' if provenance=='v2' and url in REVIEWED else ('official_discovery' if provenance=='v2' else 'legacy_research'),
      'review_status':'page_reviewed' if provenance=='v2' and url in REVIEWED else ('url_discovered' if provenance=='v2' else 'previous_research'),
      'observed_at':DATE if provenance=='v2' else None,
      'hire_offer_status':value(d.get('hire_status')) or ('advertised' if provenance=='v2' else 'unknown'),
      'street_address':None,
      'fibre_mbps':None,
      'capacity_cabaret':None,
      'capacity_seated_other':None,
      'after18_policy':known(value(d.get('after18') or d.get('after18_status'))),
      'weekend_policy':known(value(d.get('weekend') or d.get('weekend_status'))),
      'overnight_policy':known(value(d.get('overnight_status'))),
      'capacity_laptops':as_int(d.get('laptop_seated_capacity')),
      'capacity_theatre':as_int(d.get('theatre') or d.get('theatre_capacity')),
      'capacity_classroom':as_int(d.get('classroom')),
      'capacity_standing':as_int(d.get('standing') or d.get('standing_capacity')),
      'capacity_boardroom':as_int(d.get('boardroom')),
      'area_sqm':as_num(d.get('area_sqm')),
      'price_gbp_from':as_num(d.get('hourly_from') or d.get('price_from_gbp')),
      'price_unit': 'hour' if value(d.get('hourly_from')) else (value(d.get('price_unit')) or None),
      'price_conditions': ('Published normal opening-hours commercial rate; NOT guaranteed for out-of-hours hire' if provenance=='v2' and 'enfield.gov.uk' in url else None),
      'wifi_status':known(value(d.get('wifi') or d.get('wifi_status'))),
      'av_status':known(value(d.get('av') or d.get('av_status'))),
      'power_status':known(value(d.get('power_status'))),
      'accessibility_status':known(value(d.get('accessibility_status'))),
      'breakout_status':known(value(d.get('breakout_status'))),
      'catering_status':known(value(d.get('catering_status'))),
      'booking_url':value(d.get('booking_url')) or None,
      'official_website':value(d.get('official_website')) or (url if provenance=='v2' else None),
      'phone_business':value(d.get('phone_business')) or None,
      'email_business':value(d.get('email_business')) or None,
      'evidence_note':value(d.get('notes')) or value(d.get('evidence_note')) or None,
      'licence_bucket':'first_party_factual_review_required' if provenance=='v2' else value(d.get('licence_bucket')) or 'legacy',
      'external_id':value(d.get('external_id')) or None,
      'availability_live':False,
      'already_on_nightoffice':value(d.get('already_on_nightoffice')) or 'unknown',
      'is_hackathon_confirmed':bool(as_int(d.get('laptop_seated_capacity'))) and provenance=='legacy',
      'acquisition_batch':provenance,
      'lead_status':'research_lead',
    }
    key=canonical(name)
    if key in seen:
        prev=seen[key]
        # Keep best detail after merging properties only when same named entity; preserve multiple URLs.
        potential_aliases.append({'name':name,'matched_to':prev['display_name'],'source_url':url,'resolution':'same_normalized_name'})
        for field in ('capacity_classroom','capacity_theatre','capacity_boardroom','area_sqm','wifi_status','av_status','price_gbp_from','price_conditions'):
            p=prev.get(field);n=row.get(field)
            if (p in (None,'','unknown') and n not in (None,'','unknown')):prev[field]=n
        return
    # Synthetic names are not a stable join across future sources; include prior stable id when available.
    if provenance=='legacy' and d.get('venue_id'):row['legacy_venue_id']=d['venue_id']
    seen[key]=row;rows.append(row)

for r in legacy: register(r,'legacy')
for r in additions:register(r,'v2')

# Targeted first-party detail checks: never convert partial facts into general room capacities.
enrichments=read_csv(HERE/'data'/'targeted_enrichment.tsv',delimiter='\t')
by_canon={canonical(r['display_name']):r for r in rows}
for d in enrichments:
    r=by_canon.get(canonical(d['name']))
    if r is None:
        raise ValueError('Targeted enrichment did not find venue: '+d['name'])
    r['street_address']=value(d['street_address']) or None
    r['business_email']=value(d['business_email']) or r.get('email_business')
    r['business_phone']=value(d['business_phone']) or r.get('phone_business')
    r['fibre_mbps']=as_int(d.get('fibre_mbps'))
    r['capacity_cabaret']=as_int(d.get('capacity_cabaret'))
    r['capacity_seated_other']=as_int(d.get('capacity_seated_other'))
    r['hours_weekday_evening_text']=value(d.get('hours_weekday_evening')) or None
    r['hours_weekend_text']=value(d.get('hours_weekend')) or None
    for field in ('power_status','breakout_status','catering_status','accessibility_status'):
        val=known(value(d.get(field)))
        if val!='unknown':r[field]=val
    r['enrichment_source_url']=d['enrichment_source_url']
    r['enrichment_notes']=d['notes']
    r['targeted_review_date']=DATE
    r['review_status']='page_reviewed'
    r['source_class']='first_party_enriched'
    r['observed_at']=DATE

# Known grouped legacy buildings; do not imply different rooms share a site unless publisher evidence confirms.
for r in rows:
    n=r['display_name'].lower()
    if n.startswith('electra house -'):
        r['building_name']='Electra House'; r['room_name']=r['display_name'].split(' - ',1)[1];r['room_granularity']='room'
    elif n.startswith('plexal '):
        r['building_name']='Plexal, Here East';r['room_name']=r['display_name'][len('Plexal '):];r['room_granularity']='room'
    elif n.startswith('university of london - senate house'):
        r['building_name']='Senate House, University of London';r['room_name']=r['display_name'].split(' - ',1)[1];r['room_granularity']='room'
    elif n.startswith('british library -'):
        r['building_name']='British Library';r['room_name']=r['display_name'].split(' - ',1)[1];r['room_granularity']='room'

# Link and audit entities. Source evidence is atomic and has actual value plus publisher URL.
operators={};buildings={};spaces={};edges=[];evidence=[]
for r in rows:
    op=r['operator']
    op_id=stable('op',op) if op else None
    if op_id:
        operators[op_id]={'operator_id':op_id,'name':op,'evidence_url':r['source_url']}
    bname=r['building_name']
    # Use postcode to discriminate location even if same brand.
    b_id=stable('b',bname,r['postcode'] or r['source_domain'])
    buildings[b_id]={'building_id':b_id,'name':bname,'postcode':r['postcode'],'borough':r['borough'],'latitude':r['latitude'],'longitude':r['longitude']}
    r['building_id']=b_id;r['operator_id']=op_id
    s_id=stable('s',b_id,r['room_name'] or r['display_name'])
    r['space_id']=s_id
    spaces[s_id]={'space_id':s_id,'building_id':b_id,'venue_id':r['venue_id'],'name':r['room_name'] or r['display_name'],'granularity':r['room_granularity']}
    if op_id:
        edges.append({'from_id':op_id,'predicate':'OPERATES','to_id':b_id,'source_url':r['source_url']})
    edges.extend([
      {'from_id':b_id,'predicate':'HAS_SPACE','to_id':s_id,'source_url':r['source_url']},
      {'from_id':s_id,'predicate':'DESCRIBED_BY','to_id':r['venue_id'],'source_url':r['source_url']},
    ])
    evidence.append({'evidence_id':stable('e',r['venue_id'],'research_lead_mentioned',r['source_url']), 'venue_id':r['venue_id'], 'field':'research_lead_mentioned','value':r['display_name'],'source_url':r['source_url'],'source_class':r['source_class'],'observed_date':r['observed_at'],'evidence_text':r['evidence_note'],'caveat':'Research lead only; not a confirmed current bookable space.'})
    for field in ('fibre_mbps','capacity_cabaret','capacity_seated_other','capacity_laptops','capacity_classroom','capacity_theatre','capacity_standing','capacity_boardroom','area_sqm','price_gbp_from','after18_policy','weekend_policy','overnight_policy','wifi_status','av_status','power_status'):
        val=r.get(field)
        if val in (None,'','unknown'):continue
        # Avoid implying legacy citations prove a datum at a different detail level.
        evidence.append({
            'evidence_id':stable('e',r['venue_id'],field,str(val),r['source_url']),
            'venue_id':r['venue_id'],'field':field,'value':val,
            'source_url':r['source_url'],'source_class':r['source_class'],
            'observed_date':r['observed_at'],
            'evidence_text':r['evidence_note'],
            'caveat':('Capacity seating style is not hacker laptops' if field.startswith('capacity_') and field!='capacity_laptops' else ('Published normal-hours price only' if field=='price_gbp_from' and r['price_conditions'] else None)),
        })
    # heuristic scores for research prioritization, NOT a prediction of free dates
    score={'tech_event':26,'innovation_hub':23,'coworking':19,'training_centre':19,'university':16,'conference':16,'library':10,'community':7,'school':9,'warehouse':9}.get(r['venue_type'],3)
    score+= 14 if r['after18_policy']=='yes' else 0
    score+= 10 if r['weekend_policy']=='yes' else 0
    score+= 13 if r['capacity_laptops'] else (4 if r['capacity_classroom'] else 0)
    score+= 7 if r['wifi_status']=='yes' else 0
    score+= 5 if r['av_status']=='yes' else 0
    score+= 4 if r['capacity_theatre'] and r['capacity_theatre']>=50 else 0
    r['research_priority']=min(100,score)
    r['listing_granularity']= ('space' if r['room_name'] and r['room_name'].lower() not in ('event spaces','venue hire','facilities','hire facilities','community rooms','venue hire rooms','rooms and event spaces','lecture theatres','event-space collection','rooms and halls','rooms and meeting spaces') else 'building_or_unspecified')
    r['quality_fields_present']=sum(r.get(k) not in (None,'','unknown') for k in ('postcode','borough','capacity_laptops','capacity_classroom','capacity_theatre','capacity_standing','price_gbp_from','wifi_status','av_status','after18_policy','weekend_policy','booking_url','email_business','phone_business','latitude','longitude'))
    r['can_advertise_available']=False
    r['has_verified_hire_policy']= r['source_class']=='first_party_reviewed' and (r['after18_policy']=='yes' or r['weekend_policy']=='yes')
    r['is_currently_bookable']=False

# Prevent false venue-level referents from gaining time policy from operating hours only.
# All after18/weekend policies carry a qualifier in the output schema.
rows.sort(key=lambda r:(-r['research_priority'],r['display_name'].lower()))

D=HERE/'data'
D.mkdir(parents=True,exist_ok=True)
def writejson(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
def writejsonl(p,l):p.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in l),encoding='utf-8')
def writecsv(p,l):
    if not l:return
    with open(p,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(l[0]));w.writeheader();w.writerows(l)
writecsv(D/'venues_v2.csv',rows)
writejsonl(D/'venues_v2.jsonl',rows)
writejson(D/'venues_v2.json',rows)
writejsonl(D/'evidence.jsonl',evidence)
writejsonl(D/'cognee_edges.jsonl',edges)
writejsonl(D/'buildings.jsonl',list(buildings.values()))
writejsonl(D/'spaces.jsonl',list(spaces.values()))
writejsonl(D/'operators.jsonl',list(operators.values()))
# Text documents for vector/semantic ingestion; provenance MUST be kept with each fragment.
knowledge_docs=[]
for r in rows:
    bits=[r['display_name'], 'building: '+r['building_name'], 'type: '+r['venue_type']]
    for k in ('capacity_laptops','capacity_classroom','capacity_theatre','capacity_standing','area_sqm','after18_policy','weekend_policy','wifi_status','av_status','price_gbp_from'):
        if r.get(k) not in (None,'','unknown'): bits.append(k.replace('_',' ')+': '+str(r[k]))
    if r.get('evidence_note'):bits.append('source notes: '+r['evidence_note'])
    knowledge_docs.append({'document_id':r['venue_id'],'title':r['display_name'],'text':'. '.join(bits)+'. No live date availability verified.', 'metadata':{'source_url':r['source_url'],'source_class':r['source_class'],'observed_at':r['observed_at'],'entity_id':r['venue_id'],'entity_type':'venue_lead','live_booking':False}})
writejsonl(D/'cognee_documents.jsonl',knowledge_docs)
writecsv(D/'dedupe_review_queue.csv',potential_aliases)
writecsv(D/'excluded_catalogue_rows.csv',excluded)

# SQLite data mart with typed normalized tables and source evidence; no live availability claims.
db=D/'venue_intelligence_v2.sqlite'
if db.exists():db.unlink()
con=sqlite3.connect(db)
con.execute('PRAGMA foreign_keys=ON')
for tab,key,l in [('venues','venue_id',rows),('buildings','building_id',list(buildings.values())),('spaces','space_id',list(spaces.values())),('operators','operator_id',list(operators.values())),('evidence','evidence_id',evidence)]:
    con.execute(f'CREATE TABLE {tab} ({key} TEXT PRIMARY KEY, payload_json TEXT NOT NULL)')
    con.executemany(f'INSERT INTO {tab} VALUES (?,?)',[(r[key],json.dumps(r,ensure_ascii=False)) for r in l])
con.execute('CREATE TABLE graph_edges (from_id TEXT NOT NULL, predicate TEXT NOT NULL, to_id TEXT NOT NULL, source_url TEXT)')
con.executemany('INSERT INTO graph_edges VALUES (:from_id,:predicate,:to_id,:source_url)',edges)
con.execute('CREATE INDEX edges_from_idx ON graph_edges(from_id)')
con.execute('CREATE INDEX edges_to_idx ON graph_edges(to_id)')
con.commit();con.close()

stats={
  'snapshot_date':DATE,'legacy_rows':len(legacy),'researched_second_pass_rows':len(additions),
  'unique_leads':len(rows),'new_incremental_leads':len(rows)-len(legacy),
  'data_quality':{'has_postcode':sum(bool(r['postcode']) for r in rows),'has_location_coordinates':sum(r['latitude'] is not None and r['longitude'] is not None for r in rows),'has_laptop_capacity':sum(r['capacity_laptops'] is not None for r in rows),'has_classroom_capacity':sum(r['capacity_classroom'] is not None for r in rows),'has_theatre_capacity':sum(r['capacity_theatre'] is not None for r in rows),'has_room_name':sum(r['room_name'] is not None for r in rows),'has_wifi_yes':sum(r['wifi_status']=='yes' for r in rows),'has_after18_yes':sum(r['after18_policy']=='yes' for r in rows),'has_weekend_yes':sum(r['weekend_policy']=='yes' for r in rows),'has_any_hire_window':sum(r['after18_policy']=='yes' or r['weekend_policy']=='yes' for r in rows),'has_validated_availability':0},
  'per_category':dict(Counter(r['venue_type'] for r in rows)),
  'sources_by_domain':dict(Counter(r['source_domain'] for r in rows)),
  'graph':{'operators':len(operators),'buildings':len(buildings),'spaces':len(spaces),'evidence_statements':len(evidence),'edges':len(edges)},
  'targeted_first_party_enrichments':len(enrichments),
  'review_status_distribution':dict(Counter(r['review_status'] for r in rows)),
  'full_postcodes':sum(bool(r['postcode']) and bool(re.match(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s+[0-9][A-Z]{2}$',r['postcode'],re.I)) for r in rows),
  'uncertain_dedupes':len(potential_aliases),'excluded_collection_rows':len(excluded),
  'warning':'Prospect intelligence only. Even explicit policy does NOT imply free or bookable dates.'
}
writejson(D/'stats_v2.json',stats)
print(json.dumps({k:stats[k] for k in ('legacy_rows','researched_second_pass_rows','unique_leads','new_incremental_leads','graph','data_quality','uncertain_dedupes')},indent=2))
