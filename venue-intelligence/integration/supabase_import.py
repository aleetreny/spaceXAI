"""Idempotent, privileged, server-only import of static VI research rows using PostgREST.

Requires SUPABASE_URL and SUPABASE_SECRET_KEY (or legacy SUPABASE_SERVICE_ROLE_KEY).
Run --dry-run BEFORE --execute; refuses to use URLs outside the named target project.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path
from validate_data import load_and_validate, TABLE_ORDER, DataIntegrityError

BATCH = 75


def client_config():
    url = os.environ.get('SUPABASE_URL','').rstrip('/')
    key = os.environ.get('SUPABASE_SECRET_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    expected = os.environ.get('SUPABASE_PROJECT_REF','')
    if not url.startswith('https://') or not key or not expected or not url.startswith(f'https://{expected}.supabase.co'):
        raise RuntimeError('Require SUPABASE_URL=https://<SUPABASE_PROJECT_REF>.supabase.co, SUPABASE_PROJECT_REF and server-only SUPABASE_SECRET_KEY')
    return url,key


def rest(url, key, table, rows=None, count=False):
    query='?select=*&limit=1' if count else '?on_conflict='+urllib.parse.quote(('from_id,predicate,to_id,source_url' if table=='vi_edges' else {
      'vi_operators':'operator_id','vi_buildings':'building_id','vi_venues':'venue_id',
      'vi_spaces':'space_id','vi_evidence':'evidence_id','vi_nodes':'node_id'}[table]))
    headers={'apikey':key,'Accept':'application/json'}
    if not key.startswith('sb_secret_'):
        headers['Authorization']='Bearer '+key
    if count:
        headers['Prefer']='count=exact'
        req=urllib.request.Request(url+'/rest/v1/'+table+query,headers=headers,method='HEAD')
    else:
        headers.update({'Content-Type':'application/json','Prefer':'resolution=merge-duplicates,return=minimal'})
        req=urllib.request.Request(url+'/rest/v1/'+table+query,data=json.dumps(rows,ensure_ascii=False,allow_nan=False).encode(),headers=headers,method='POST')
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=45) as res:
                return int(res.headers.get('Content-Range','0/0').split('/')[-1]) if count else res.status
        except urllib.error.HTTPError as e:
            body=e.read(1200).decode(errors='replace')
            if e.code not in (429,500,502,503,504) or attempt==3:
                raise RuntimeError(f'{table}: HTTP {e.code}: {body}') from None
        except urllib.error.URLError:
            if attempt==3: raise
        time.sleep(2**attempt)


def map_rows(tables):
    result={}
    result['vi_operators']=[{'operator_id':r['operator_id'],'name':r['name'],'evidence_url':r.get('evidence_url')} for r in tables['operators']]
    result['vi_buildings']=[{'building_id':r['building_id'],'name':r['name'],'postcode':r.get('postcode'),'borough':r.get('borough'),'latitude':r.get('latitude'),'longitude':r.get('longitude')} for r in tables['buildings']]
    result['vi_venues']=[{
        'venue_id':r['venue_id'],'building_id':r['building_id'],'operator_id':r.get('operator_id'),
        'display_name':r['display_name'],'venue_type':r['venue_type'],'source_url':r['source_url'],
        'review_status':r['review_status'],'after18_policy':r['after18_policy'],
        'weekend_policy':r['weekend_policy'],'overnight_policy':r['overnight_policy'],
        'capacity_laptops':r.get('capacity_laptops'),'capacity_classroom':r.get('capacity_classroom'),
        'capacity_theatre':r.get('capacity_theatre'),'capacity_standing':r.get('capacity_standing'),
        'area_sqm':r.get('area_sqm'),'research_priority':r['research_priority'],
        'lead_status':'research_lead','payload':r} for r in tables['venues']]
    result['vi_spaces']=[{'space_id':r['space_id'],'building_id':r['building_id'],'venue_id':r['venue_id'],'name':r['name'],'granularity':r['granularity']} for r in tables['spaces']]
    result['vi_evidence']=[{'evidence_id':r['evidence_id'],'venue_id':r['venue_id'],'field':r['field'],'value':r['value'],'source_url':r['source_url'],'source_class':r['source_class'],'observed_date':r['observed_date'],'caveat':r['caveat'],'evidence_text':r['evidence_text']} for r in tables['evidence']]
    # Includes nodes for all references; vi_edges.from_id/to_id have actual FKs into vi_nodes.
    result['vi_nodes']=[{'node_id':r[k],'node_type':kind} for kind,t,k in [
        ('operator','operators','operator_id'),('building','buildings','building_id'),
        ('venue','venues','venue_id'),('space','spaces','space_id'),('evidence','evidence','evidence_id')]
        for r in tables[t]]
    result['vi_edges']=list(tables['edges'])
    return result


def execute():
    a=argparse.ArgumentParser()
    mode=a.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run',action='store_true');mode.add_argument('--execute',action='store_true')
    a.add_argument('--report',default=None,help='write only public counts/status, not secrets')
    args=a.parse_args()
    tables,counts=load_and_validate()
    mapped=map_rows(tables)
    summary={'source_counts':counts,'target_counts':{k:len(v) for k,v in mapped.items()},'executed':False}
    if args.execute:
        url,key=client_config()
        # Server-only; never echo env keys or request headers.
        for target in ('vi_operators','vi_buildings','vi_venues','vi_spaces','vi_evidence','vi_nodes','vi_edges'):
            for i in range(0,len(mapped[target]),BATCH):rest(url,key,target,mapped[target][i:i+BATCH])
            print(f'upserted {target}: {len(mapped[target])}',flush=True)
        summary['verified_counts']={t:rest(url,key,t,count=True) for t in mapped}
        for table,expected in summary['target_counts'].items():
            if summary['verified_counts'][table]!=expected:
                raise RuntimeError(f'verification FAILED for {table}: expected {expected}, got {summary["verified_counts"][table]}')
        summary['executed']=True
    if args.report:Path(args.report).write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':execute()
