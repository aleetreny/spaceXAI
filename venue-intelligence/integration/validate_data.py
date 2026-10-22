"""Strict and deterministic validation for the static Night Office venue dataset."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
ID_PATTERN = re.compile(r'^(?:v|b|s|op|e)_[a-f0-9]{12,32}$')
EXPECTED = {'operators': 23, 'buildings': 337, 'venues': 381, 'spaces': 381, 'evidence': 699, 'edges_raw': 851, 'edges_unique': 819}
TABLE_ORDER = ('operators', 'buildings', 'venues', 'spaces', 'evidence', 'edges')

class DataIntegrityError(ValueError):
    pass

def jsonl(name):
    with (DATA_DIR / name).open(encoding='utf-8') as f:
        return [json.loads(row) for row in f if row.strip()]

def require(cond, message):
    if not cond:
        raise DataIntegrityError(message)

def distinct(rows, key, label):
    ids = [r[key] for r in rows]
    require(all(isinstance(v, str) and ID_PATTERN.fullmatch(v) for v in ids), f'invalid {label} identifier')
    require(len(set(ids)) == len(ids), f'nonunique {label} identifier')
    return set(ids)

def load_and_validate(check_expected=True):
    tables = {
        'operators': jsonl('operators.jsonl'),
        'buildings': jsonl('buildings.jsonl'),
        'venues': json.loads((DATA_DIR / 'venues_v2.json').read_text(encoding='utf-8')),
        'spaces': jsonl('spaces.jsonl'),
        'evidence': jsonl('evidence.jsonl'),
        'edges': jsonl('cognee_edges.jsonl'),
    }
    ids = {}
    for name, key in [('operators','operator_id'),('buildings','building_id'),('venues','venue_id'),('spaces','space_id'),('evidence','evidence_id')]:
        ids[name] = distinct(tables[name], key, name)
    for row in tables['venues']:
        require(row['building_id'] in ids['buildings'], 'orphan venue building')
        require(row.get('operator_id') is None or row['operator_id'] in ids['operators'], 'orphan venue operator')
        require(row.get('after18_policy') in ('yes','no','restricted','unknown'), 'invalid evening policy')
        require(row.get('weekend_policy') in ('yes','no','restricted','unknown'), 'invalid weekend policy')
        require(row.get('overnight_policy') in ('yes','no','restricted','unknown'), 'invalid overnight policy')
        require(row['availability_live'] is False and row['can_advertise_available'] is False and row['is_currently_bookable'] is False, 'false availability claim')
        require(row.get('lead_status') == 'research_lead', 'non-research lead status')
        require(row.get('latitude') is None and row.get('longitude') is None, 'unsourced geocoding detected')
        for capacity in ('capacity_laptops','capacity_classroom','capacity_theatre','capacity_standing'):
            require(row.get(capacity) is None or (type(row[capacity]) is int and row[capacity] > 0), f'invalid {capacity}')
    venues_by_id = {r['venue_id']: r for r in tables['venues']}
    for row in tables['spaces']:
        require(row['venue_id'] in ids['venues'], 'orphan space venue')
        require(row['building_id'] in ids['buildings'], 'orphan space building')
        require(venues_by_id[row['venue_id']]['building_id'] == row['building_id'], 'space building mismatch')
    for row in tables['evidence']:
        require(row['venue_id'] in ids['venues'], 'orphan evidence venue')
        require(row['source_url'].startswith('https://') or row['source_url'].startswith('http://'), 'invalid evidence URL')
    edges = tables['edges']; seen=set(); unique=[]
    all_ids=set().union(*ids.values())
    for row in edges:
        require(row['predicate'] in ('HAS_SPACE','DESCRIBED_BY','OPERATES'), 'unexpected graph predicate')
        require(row['from_id'] in all_ids and row['to_id'] in all_ids, 'orphan graph node')
        tup=(row['from_id'],row['predicate'],row['to_id'],row['source_url'])
        if tup not in seen:
            seen.add(tup);unique.append(row)
    tables['edges'] = unique
    counts={k:len(v) for k,v in tables.items()};counts['edges_raw']=len(edges); counts['edges_unique']=len(unique)
    if check_expected:
        for k,v in EXPECTED.items(): require(counts.get(k)==v,f'count mismatch {k}: {counts.get(k)} != {v}')
    return tables, counts

if __name__ == '__main__':
    _,counts=load_and_validate(); print(json.dumps(counts,indent=2,sort_keys=True))
