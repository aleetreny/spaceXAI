"""Cognee REST adapter for the separate *research* dataset. No credentials in source.

Implemented against Cognee REST /api/v1/{add,cognify,search}. Raw cognee_edges.jsonl
is staging-only; graph relationships are *textual context* for Cognee extraction.
Requires the user's OWN Cognee endpoint and API key, never the teammate's instance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import defaultdict
from pathlib import Path
from validate_data import load_and_validate
from supabase_import import client_config

DATASET = 'nightoffice_venue_research_2026_10_22'

def documents(tables):
    evidence=defaultdict(list)
    for e in tables['evidence']: evidence[e['venue_id']].append(e)
    spaces={s['venue_id']:s for s in tables['spaces']}
    buildings={b['building_id']:b for b in tables['buildings']}
    operators={o['operator_id']:o for o in tables['operators']}
    for v in tables['venues']:
        lines=[
            f"venue_id: {v['venue_id']}",
            'status: research_lead; bookable_dates: not_verified; live_availability: false',
            f"venue_name: {v['display_name']}",
            f"source_url: {v['source_url']}",
            f"review_status: {v['review_status']}",
            f"venue_type: {v['venue_type']}",
            f"building_id: {v['building_id']}; building_name: {buildings[v['building_id']]['name']}",
            f"space_id: {spaces[v['venue_id']]['space_id']}; space_name: {spaces[v['venue_id']]['name']}",
        ]
        if v.get('operator_id'):
            op=operators[v['operator_id']];lines.append(f"operator_id: {op['operator_id']}; operator_name: {op['name']}")
        for key in ('postcode','borough','capacity_laptops','capacity_classroom','capacity_theatre','capacity_standing','after18_policy','weekend_policy','overnight_policy','wifi_status','av_status','price_gbp_from'):
            val=v.get(key)
            lines.append(f'{key}: {val if val is not None else "unknown"}')
        lines.append('Note: venue policies are NOT dates available to book. Theatre seating is NOT laptop capacity.')
        for e in evidence[v['venue_id']]:
            lines.append(f"Evidence: evidence_id={e['evidence_id']}; field={e['field']}; value={json.dumps(e['value'],ensure_ascii=False)}; source_url={e['source_url']}; observed_date={e['observed_date'] or 'unknown'}; caveat={e.get('caveat') or 'none'}; text={e.get('evidence_text') or ''}")
        body='\n'.join(lines)
        yield v['venue_id'],body,hashlib.sha256(body.encode()).hexdigest()

def request(url, headers, method='GET', payload=None, timeout=60):
    req=urllib.request.Request(url,headers=headers,data=payload,method=method)
    with urllib.request.urlopen(req,timeout=timeout) as resp:
        raw=resp.read()
        return json.loads(raw) if raw else None

def supa_state(base,key,venue_id):
    q=urllib.parse.urlencode({'venue_id':'eq.'+venue_id,'select':'document_sha256,dataset_name'})
    h={'apikey':key}
    if not key.startswith('sb_secret_'):h['Authorization']='Bearer '+key
    rows=request(base+'/rest/v1/vi_cognee_sync?'+q,h)
    return rows[0] if rows else None

def save_state(base,key,venue_id,digest):
    h={'apikey':key,'Content-Type':'application/json','Prefer':'resolution=merge-duplicates,return=minimal'}
    if not key.startswith('sb_secret_'):h['Authorization']='Bearer '+key
    body={'venue_id':venue_id,'dataset_name':DATASET,'document_sha256':digest}
    request(base+'/rest/v1/vi_cognee_sync?on_conflict=venue_id',h,'POST',json.dumps([body]).encode())

def cognee_config():
    url=os.environ.get('COGNEE_URL','').rstrip('/')
    token=os.environ.get('COGNEE_API_KEY','')
    if not token or not (url.startswith('https://') or url.startswith('http://localhost:')):
        raise RuntimeError('Configure server-only COGNEE_URL (HTTPS or localhost) and COGNEE_API_KEY using private environment')
    kind=os.environ.get('COGNEE_AUTH_MODE','api_key')
    if kind not in ('api_key','bearer'): raise RuntimeError('COGNEE_AUTH_MODE must be api_key or bearer')
    return url,({'X-Api-Key':token} if kind=='api_key' else {'Authorization':'Bearer '+token})

def add_document(url,headers,venue_id,body):
    boundary='venue-'+uuid.uuid4().hex
    data=(f'--{boundary}\r\nContent-Disposition: form-data; name="datasetName"\r\n\r\n{DATASET}\r\n'
          f'--{boundary}\r\nContent-Disposition: form-data; name="data"; filename="{venue_id}.txt"\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n{body}\r\n'
          f'--{boundary}--\r\n').encode()
    return request(url+'/api/v1/add',{**headers,'Content-Type':f'multipart/form-data; boundary={boundary}'},'POST',data,120)

def execute():
    a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True);g.add_argument('--dry-run',action='store_true');g.add_argument('--execute',action='store_true')
    a.add_argument('--limit',type=int,default=381);a.add_argument('--cognify',action='store_true')
    args=a.parse_args()
    tables,_=load_and_validate()
    docs=list(documents(tables));print(json.dumps({'dataset':DATASET,'documents_total':len(docs),'sample_venue_id':docs[0][0],'first_document_preview':docs[0][1][:380]},indent=2))
    if args.dry_run:return
    if args.limit<1 or args.limit>len(docs):raise RuntimeError('Invalid limit')
    sb,key=client_config();cg,headers=cognee_config()
    # Connectivity check before any expensive ingestion.
    request(cg+'/api/v1/datasets/',headers)
    added=skipped=0
    for venue_id,body,digest in docs[:args.limit]:
        status=supa_state(sb,key,venue_id)
        if status and status['document_sha256']==digest and status['dataset_name']==DATASET:
            skipped+=1;continue
        if status:raise RuntimeError('Changed document requires explicit versioned Cognee dataset / reindex policy: '+venue_id)
        add_document(cg,headers,venue_id,body)
        save_state(sb,key,venue_id,digest)
        added+=1
        if (added+skipped)%25==0:print('processed:',added+skipped,flush=True)
    if args.cognify:
        request(cg+'/api/v1/cognify',{**headers,'Content-Type':'application/json'},'POST',json.dumps({'datasets':[DATASET],'run_in_background':False}).encode(),600)
    print(json.dumps({'dataset':DATASET,'added':added,'skipped_unchanged':skipped,'cognify_requested':args.cognify,'total_scoped':args.limit}))

if __name__=='__main__':execute()
