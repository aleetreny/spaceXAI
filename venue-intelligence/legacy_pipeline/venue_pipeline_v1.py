#!/usr/bin/env python3
"""Night Office: public-source venue discovery, enrichment, scoring, dedup & SQLite/CSV exports.

Principles: unknown != available; evidence source for every row; no Google Maps extraction;
no marketplace crawling; respect site robots/TOS; OSM data remains in separable attribution layer.
"""
import argparse, csv, hashlib, json, os, re, sqlite3, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from seed_data import get_seeds, EXISTING_NIGHTOFFICE_NAMES

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'; D.mkdir(parents=True,exist_ok=True)
DATE='2026-10-22'  # seed-source review date: do not re-label unless actually reverified
UA='HackathonVenueResearch/0.3 (+https://nightoffice.co/)'  # operator affiliation not asserted
FIELDS=['venue_id','name','venue_type','borough','postcode','latitude','longitude','source_url','source_type','evidence_level','hire_status','after18_status','weekend_status','overnight_status','laptop_seated_capacity','theatre_capacity','standing_capacity','price_from_gbp','price_unit','wifi_status','power_status','av_status','breakout_status','accessibility_status','catering_status','booking_url','official_website','phone_business','email_business','evidence_note','last_seen_date','last_checked_date','relevance_score','data_completeness','already_on_nightoffice','licence_bucket','external_id','source_terms_review','status']

# Listed on Night Office as of 2026-10-22; never count as new supply.
EXISTING_ALIAS=[('halkin','1-2 paris garden'),('kindling','white city'),('mainframe','euston'),('channel','kings cross'),('variouslabs','parkway'),('harewood','hanover square'),('lower thames','10 lower thames'),('68 king william','68 king william')]

def norm(s):
    return re.sub(r'[^a-z0-9]+','',re.sub(r'^(lambeth|tower hamlets|westminster)\s*[-:]\s*','',str(s).lower()).strip())

def identity(r):
    # postcode-based geographic identity and individual bookable room distinction
    name=norm(r.get('name') or '')
    p=norm(r.get('postcode') or '')
    return hashlib.sha1(f'{name}|{p}'.encode()).hexdigest()[:16]

def decode_seed(r):
    v={k:None for k in FIELDS}
    v.update(venue_id=identity(r),name=r['name'],venue_type=r.get('category'),borough=r.get('borough') or None,postcode=r.get('postcode') or None,source_url=r.get('source_url'),source_type=r.get('source_type'),hire_status=r.get('hire_status','unknown'),after18_status=r.get('after18','unknown'),weekend_status=r.get('weekend','unknown'),overnight_status='unknown',laptop_seated_capacity=r.get('laptop_capacity'),theatre_capacity=r.get('theatre_capacity'),standing_capacity=r.get('standing_capacity'),price_from_gbp=r.get('price_from_gbp'),price_unit=r.get('price_unit'),wifi_status='unknown',power_status='unknown',av_status='unknown',breakout_status='unknown',accessibility_status='unknown',catering_status='unknown',evidence_note=r.get('evidence_note'),last_seen_date=DATE,evidence_level=('first_party_specific' if r.get('source_type')=='official_venue_page' else 'directory_listing'),status='candidate',licence_bucket='official_web' if r.get('source_type')=='official_venue_page' else ('third_party_reference_only' if r.get('source_type')=='third_party_venue_listing' else 'council_reference'),source_terms_review='pending')
    if v['source_type']=='official_venue_page':v['official_website']=v['source_url']
    if 'ramenclub.com/' in (v['source_url'] or ''):
        v.update(wifi_status='unknown',power_status='yes')
    if 'civo.com/tech-junction' in (v['source_url'] or ''):
        v.update(wifi_status='yes',av_status='yes',breakout_status='yes',accessibility_status='yes',catering_status='yes',email_business='techjunction@civo.com')
    if 'plexal.com/event-hire/' in (v['source_url'] or ''):
        v.update(wifi_status='yes',av_status='yes',breakout_status='yes',catering_status='yes',phone_business='+44 20 3909 7763')
    if 'future' in v['name'].lower() or 'coming soon' in (v.get('evidence_note') or '').lower():
        v['status']='not_yet_operational'
    if v['name']=='Huckletree London - General Event Spaces':
        v['status']='source_directory_only'
    if v['name']=='Westminster - Victoria Library Large Events Room':
        v.update(wifi_status='yes',av_status='yes',catering_status='yes')
    if v['name']=='The Gallery - Techspace Goswell Road':v.update(av_status='yes',breakout_status='yes')
    if v['name']=='The Lightwell - Techspace Worship Street':v.update(av_status='yes')
    if 'Techspace' in v['name']: v['av_status']='yes'
    if 'Electra House' in v['name']:
        v.update(av_status='yes',phone_business='020 7307 2345',accessibility_status='unknown')
    if 'Second Home Spitalfields - The Rooftop'==v['name']:
        v.update(wifi_status='yes',av_status='yes',catering_status='yes')
    if v['name']=='Impact Hub London Euston Event Space':
        v.update(av_status='yes',breakout_status='yes',accessibility_status='yes',catering_status='yes')
    return v

def merge(a,b):
    # Merge sparse rows without ever upgrading unknown to confirmed; evidence links remain in sources table
    dst=dict(a)
    for field in FIELDS:
        if field in ('venue_id','name','source_url','source_type','evidence_level','last_seen_date','status'):continue
        new=b.get(field); old=dst.get(field)
        if (old in (None,'','unknown','pending') and new not in (None,'','unknown','pending')):
            dst[field]=new
    # Evidence URL from confirmed first-party result is preferred over directory URL
    if b.get('evidence_level')=='first_party_specific' and a.get('evidence_level')!='first_party_specific':
        for k in ['source_url','source_type','evidence_level','evidence_note','official_website','licence_bucket']:dst[k]=b.get(k)
    return dst

def dedupe(rows):
    seen={}; aliases={
        'thelondonacademyschooleventhire':'londonacademyeventhire',
        'londonacademyeveningandweekendacademyhire':'londonacademyeventhire',
        'space4eventhire':'space4eventhire',
        'space4techtechcommunityeventroom':'space4eventhire',
    }
    for r in rows:
        n=norm(r['name'])
        if n in ('towerhamletsidealcentre','sundialcentretowerhamlets'):
            key='idealcentre' if 'ideal' in n else 'sundialcentre'
        else:key=aliases.get(n,n)
        # Different named rooms remain distinct, even at same address.
        # 'Tower Hamlets Ideal Centre' and directory 'Ideal Centre' are a known building match.
        if key in seen:
            merged=merge(seen[key],r)
            merged['venue_id']=seen[key]['venue_id']
            seen[key]=merged
        else:seen[key]=r
    return list(seen.values())

def nightoffice_check(name):
    # Very conservative: exact names only; unresolved parent/room overlap is left for manual check.
    return 'yes' if norm(name) in {norm(n) for n in EXISTING_NIGHTOFFICE_NAMES} else 'unknown'

def score(r):
    t=r['venue_type']
    base={'tech_event':32,'innovation_hub':27,'coworking':23,'training_centre':24,'university':20,'conference':19,'library':13,'community':11,'school':13,'arts':11,'warehouse':9,'museum':7,'sports':3,'cinema':2,'hotel_event':13}.get(t,8)
    s=base
    a=r['after18_status']; w=r['weekend_status']
    if a=='yes':s+=22
    elif a=='restricted':s+=9
    elif a=='no':s-=5
    if w=='yes':s+=15
    elif w=='restricted':s+=7
    elif w=='no':s-=5
    if r['laptop_seated_capacity']:
        s+=min(18,int(float(r['laptop_seated_capacity'])/4))
    elif r['theatre_capacity']:
        s+=min(9,int(float(r['theatre_capacity'])/20))
    for k,b in [('wifi_status',5),('power_status',5),('av_status',4),('breakout_status',5)]:
        if r[k]=='yes':s+=b
    if r['hire_status']=='advertised':s+=4
    if r['evidence_level']=='directory_listing':s-=1
    if r['status'] in ('not_yet_operational','source_directory_only'):s-=40
    if r['venue_type']=='cinema':s-=8
    if r['venue_type']=='sports':s-=8
    return max(0,min(100,s))

def completeness(r):
    keys=['postcode','latitude','laptop_seated_capacity','theatre_capacity','standing_capacity','price_from_gbp','wifi_status','power_status','av_status','breakout_status','accessibility_status','catering_status','phone_business','email_business','booking_url']
    return round(sum(r.get(k) not in (None,'','unknown') for k in keys)/len(keys),3)

def ingest_osm(endpoint='https://overpass.kumi.systems/api/interpreter',timeout=240):
    """Real OSM POI discovery. Run with external internet; not run in this notebook sandbox.

    ODbL requires attribution and potentially share-alike for a derivative database.
    Results should be stored in a segregated origin layer for legal review.
    Use a local London PBF / self-hosted Overpass for larger scale recurring jobs.
    """
    import requests
    query='''[out:json][timeout:180];
area["name"="Greater London"]["boundary"="administrative"]->.a;
(
  nwr["amenity"~"^(community_centre|conference_centre|events_venue|arts_centre|library|university|college)$"]["name"](area.a);
  nwr["office"="coworking"]["name"](area.a);
  nwr["leisure"="hackerspace"]["name"](area.a);
  nwr["club"="hackerspace"]["name"](area.a);
);
out center tags;'''
    resp=requests.post(endpoint,data={'data':query},timeout=timeout,headers={'User-Agent':UA});resp.raise_for_status()
    result=[]
    for el in resp.json().get('elements',[]):
        tags=el.get('tags',{}); name=tags.get('name')
        if not name:continue
        addr=', '.join(filter(None,[tags.get('addr:street'),tags.get('addr:housenumber')]))
        src=f'https://www.openstreetmap.org/{el["type"]}/{el["id"]}'
        lon=el.get('lon',el.get('center',{}).get('lon')); lat=el.get('lat',el.get('center',{}).get('lat'))
        tp='coworking' if tags.get('office')=='coworking' else 'community' if tags.get('amenity')=='community_centre' else 'university' if tags.get('amenity') in ('university','college') else 'arts' if tags.get('amenity')=='arts_centre' else 'conference' if tags.get('amenity')=='conference_centre' else 'library' if tags.get('amenity')=='library' else 'innovation_hub' if tags.get('club')=='hackerspace' else 'community'
        r=dict(name=name,category=tp,postcode=tags.get('addr:postcode'),borough=None,source_url=src,source_type='osm',hire_status='unknown',evidence_note=f'OSM location POI, tag category; {addr}'.strip('; '))
        v=decode_seed(r)
        v.update(latitude=lat,longitude=lon,external_id=f'osm:{el["type"]}:{el["id"]}',source_type='osm',evidence_level='map_poi_only',licence_bucket='ODbL_OSM_SEPARATE',official_website=tags.get('website') or tags.get('contact:website'),phone_business=tags.get('contact:phone') or tags.get('phone'),email_business=tags.get('contact:email'),last_seen_date=datetime.now(timezone.utc).date().isoformat())
        result.append(v)
    return result

def protected_get(url,session,cache,delay_s=1.5,timeout=15):
    """Robots-aware; first party only; fail closed. Not an anti-bot bypass."""
    from requests.exceptions import RequestException
    u=urlparse(url)
    if u.scheme!='https' or not u.hostname: return None
    if any(x in u.hostname for x in ('hirespace.com','tagvenue.com','headbox.com','venuescanner.com','schoolhire.co.uk','google.com','maps.google.com','peerspace.com')):return None
    domain=u.hostname
    if domain not in cache:
        rp=RobotFileParser()
        try:
            r=session.get(f'{u.scheme}://{domain}/robots.txt',timeout=timeout,headers={'User-Agent':UA})
            if r.status_code!=200: cache[domain]=(None,time.monotonic())
            else:
                rp.parse(r.text.splitlines());cache[domain]=(rp,time.monotonic())
        except RequestException:
            cache[domain]=(None,time.monotonic())
    rp,last=cache[domain]
    if rp is None or not rp.can_fetch(UA,url):return None
    wait=delay_s-(time.monotonic()-last)
    if wait>0:time.sleep(wait)
    try:
        response=session.get(url,timeout=timeout,headers={'User-Agent':UA},allow_redirects=True)
        cache[domain]=(rp,time.monotonic())
        if response.status_code!=200 or 'text/html' not in response.headers.get('content-type',''):return None
        if len(response.content)>1_000_000:return None
        return response.text
    except RequestException:return None

def enrich_official(rows,max_pages=50):
    """Conservative extractor. No invented capacity or availability. Run only after checking TOS."""
    import requests
    from bs4 import BeautifulSoup
    sess=requests.Session();cache={}; done=0
    for r in rows:
        if done>=max_pages:break
        if r['source_type']!='official_venue_page':continue
        url=r['source_url'];html=protected_get(url,sess,cache)
        if not html:continue
        soup=BeautifulSoup(html,'html.parser');done+=1
        # Standard JSON-LD entity extraction; keep only direct operator site info.
        ld=[]
        for s in soup.select('script[type="application/ld+json"]'):
            try:ld.append(json.loads(s.string or '{}'))
            except:pass
        candidates=[]
        def walk(z):
            if isinstance(z,list):
                for q in z:walk(q)
            if isinstance(z,dict):
                if '@graph' in z:walk(z['@graph'])
                if any(q in str(z.get('@type','')).lower() for q in ('localbusiness','eventvenue','organization','place')):candidates.append(z)
        for ldj in ld:walk(ldj)
        for z in candidates:
            ad=z.get('address') if isinstance(z.get('address'),dict) else {}
            if not r.get('postcode') and ad.get('postalCode'):r['postcode']=ad['postalCode']
            if not r.get('phone_business') and z.get('telephone'):r['phone_business']=z['telephone']
            geo=z.get('geo') if isinstance(z.get('geo'),dict) else {}
            if r.get('latitude') is None and geo.get('latitude'):r['latitude']=geo['latitude']
            if r.get('longitude') is None and geo.get('longitude'):r['longitude']=geo['longitude']
        text=soup.get_text(' ',strip=True)
        lower=text.lower()
        if re.search(r'\b(free wi-?fi|high.speed wi-?fi|fast wi-?fi|dedicated fibre|1gb fibre)\b',lower):r['wifi_status']='yes'
        if re.search(r'\b(a/v equipment|av equipment|projector|large screen|microphones)\b',lower):r['av_status']='yes'
        if re.search(r'\b(power at every desk|power outlets at every|sockets at every desk)\b',lower):r['power_status']='yes'
        if re.search(r'\b(breakout space|breakout rooms|breakout areas)\b',lower):r['breakout_status']='yes'
        if re.search(r'\b(wheelchair accessible|step.free access|disabled access)\b',lower):r['accessibility_status']='yes'
        # Do not infer weekend hire from normal opening hours! Only explicit venue hire wording.
        if re.search(r'(evening|out.of.hours|after.hours|weekday[s]? 18:00).{0,80}(hire|book|event)',lower) or re.search(r'(hire|book|event).{0,80}(evening|out.of.hours|after.hours)',lower):
            if r['after18_status']=='unknown':r['after18_status']='possibly'
        if re.search(r'(weekend|saturday|sunday).{0,70}(hire|book)',lower) or re.search(r'(hire|book).{0,70}weekend',lower):
            if r['weekend_status']=='unknown':r['weekend_status']='possibly'
        r['last_checked_date']=datetime.now(timezone.utc).date().isoformat()
        r['evidence_note']=(r.get('evidence_note') or '')+' [Machine-reviewed operator page; manually verify inferred attributes.]'
    return done

def discover_public():
    """Refresh discovery on a small explicit allow-list; no marketplaces, no anti-bot workarounds.

    Website structure changes may reduce results. All discovered rows remain UNVERIFIED candidates,
    pending licence review and manual approval. Previously found leads persist across outages.
    """
    import requests
    from bs4 import BeautifulSoup
    listing_pages=[
      ('Hackney','https://communityhalls.hackney.gov.uk/venues','/venues/','community'),
      ('Lambeth','https://hire.lambeth.gov.uk/venues','/venues/','community'),
      ('Brent','https://spacehire.brent.gov.uk/spaces','/spaces/','community'),
      ('Tower Hamlets','https://www.towerhamlets.gov.uk/lgnl/community_and_living/halls_for_hire/halls_for_hire.aspx','/halls_for_hire/','community'),
      ('Huckletree','https://www.huckletree.com/hubs/hire-event-spaces/london','/hubs/','coworking'),
      ('Techspace','https://www.techspace.co/workspaces/events','/locations/','coworking'),
      ('Second Home','https://secondhome.io/venues/','/space/','coworking'),
      ('x+why','https://www.xandwhy.co.uk/memberships-type/event-spaces','/','coworking'),
    ]
    sess=requests.Session();cache={};found=[]
    banned={'our venues','venues','events','venue hire','meet the team','hire our spaces','contact us','view more','explore','learn more','book now','home','see all','enquire','find out more'}
    for borough,url,hint,category in listing_pages:
        html=protected_get(url,sess,cache)
        if not html:continue
        page=BeautifulSoup(html,'html.parser')
        for a in page.select('a[href]'):
            text=a.get_text(' ',strip=True)
            href=urljoin(url,a.get('href',''))
            if (len(text)<7 or len(text)>105 or text.lower() in banned or not hint in urlparse(href).path):continue
            if urlparse(href).hostname!=urlparse(url).hostname:continue
            if href.rstrip('/')==url.rstrip('/'):continue
            if not re.search(r'[a-zA-Z]{3}',text):continue
            if re.search(r'^(cookie|privacy|policy|social|community|venues for hire|meeting rooms|terms|read more)',text,re.I):continue
            found.append(dict(name=text,source_url=href,source_type='first_party_discovered',category=category,borough=borough if borough in {'Hackney','Lambeth','Brent','Tower Hamlets'} else '',hire_status='unknown',evidence_note='Automatically extracted hyperlink from an approved, public operator/council listing. Needs independent venue and suitability review.'))
    stored=D/'discovered_candidates.json'
    prev=[]
    if stored.exists():
        try:prev=json.loads(stored.read_text())
        except (ValueError,OSError):pass
    bykey={norm(r['name'])+'|'+r['source_url']:r for r in prev}
    for r in found:bykey[norm(r['name'])+'|'+r['source_url']]=r
    collected=list(bykey.values())
    stored.write_text(json.dumps(collected,ensure_ascii=False,indent=2)+'\n')
    return collected,len(found)

def to_database(rows,db_path=D/'venues.sqlite'):
    con=sqlite3.connect(db_path)
    con.execute('''CREATE TABLE IF NOT EXISTS venues ('''+','.join(f'"{k}" '+('REAL' if k in ('latitude','longitude','laptop_seated_capacity','theatre_capacity','standing_capacity','price_from_gbp','relevance_score','data_completeness') else 'TEXT') for k in FIELDS)+',PRIMARY KEY (venue_id))')
    con.execute('''CREATE TABLE IF NOT EXISTS venue_sources(venue_id TEXT NOT NULL,source_url TEXT NOT NULL,source_type TEXT,seen_date TEXT,PRIMARY KEY(venue_id,source_url))''')
    con.execute('''CREATE TABLE IF NOT EXISTS sync_audit (run_at TEXT, venue_id TEXT, event TEXT, detail TEXT)''')
    prev={x['venue_id']:dict(x) for x in [dict(zip([c[1] for c in con.execute('PRAGMA table_info(venues)').fetchall()],row)) for row in con.execute('SELECT * FROM venues').fetchall()]}
    now=datetime.now(timezone.utc).isoformat()
    with con:
        for r in rows:
            con.execute('INSERT OR REPLACE INTO venues ('+','.join('"'+k+'"' for k in FIELDS)+') VALUES ('+','.join('?' for k in FIELDS)+')',[r.get(k) for k in FIELDS])
            con.execute('INSERT OR IGNORE INTO venue_sources VALUES (?,?,?,?)',(r['venue_id'],r['source_url'],r['source_type'],r['last_seen_date']))
    incoming={r['venue_id'] for r in rows}
    with con:
        for k in prev.keys()-incoming:
            con.execute('INSERT INTO sync_audit VALUES (?,?,?,?)',(now,k,'no_longer_detected','not in this run; review before treating as closed'))
            con.execute('DELETE FROM venues WHERE venue_id=?',(k,))
    con.execute('CREATE INDEX IF NOT EXISTS ix_venues_score ON venues(relevance_score DESC)')
    con.execute('CREATE INDEX IF NOT EXISTS ix_venues_type ON venues(venue_type)')
    con.commit();con.close()

def write_csv(path,rows,fields=FIELDS):
    with path.open('w',newline='',encoding='utf-8-sig') as out:
        w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--discover',action='store_true',help='Discover additional named leads from allow-listed council/operator pages; needs internet')
    ap.add_argument('--osm',action='store_true',help='Fetch London POIs from public Overpass; needs internet and is ODbL-separated')
    ap.add_argument('--enrich',action='store_true',help='Enrich first-party pages robots-aware; verify site TOS beforehand')
    ap.add_argument('--max-pages',type=int,default=50)
    args=ap.parse_args()
    raw=get_seeds()
    discovered_count=0
    if args.discover:
        try:
            candidates,discovered_count=discover_public()
            raw.extend(candidates)
            print(f'Discovery links seen on source sites this run: {discovered_count}; persisted: {len(candidates)}',file=sys.stderr)
        except Exception as e:print(f'Discovery skipped: {e}',file=sys.stderr)
    seeds=[decode_seed(r) for r in raw]
    if args.osm:
        try:
            other=ingest_osm();print(f'OSM elements: {len(other)}',file=sys.stderr)
            # OSM is never silently merged into the proprietary-origin seeds.
            for r in other:r['relevance_score']=score(r);r['data_completeness']=completeness(r)
            write_csv(D/'venues_osm_odbl.csv',other)
            to_database(other,D/'venues_osm_odbl.sqlite')
        except Exception as e:print(f'OSM skipped: {e}',file=sys.stderr)
    rows=dedupe(seeds)
    if args.enrich:print(f'Official pages enriched: {enrich_official(rows,args.max_pages)}',file=sys.stderr)
    for r in rows:
        r['relevance_score']=score(r)
        r['data_completeness']=completeness(r)
        r['already_on_nightoffice']=nightoffice_check(r['name'])
    rows.sort(key=lambda x:(-x['relevance_score'],x['name']))
    to_database(rows)
    write_csv(D/'venues.csv',rows)
    write_csv(D/'priority_shortlist.csv',[r for r in rows if r['relevance_score']>=50 and r['already_on_nightoffice']!='yes' and r['status']=='candidate'])
    write_csv(D/'nightoffice_existing_reference.csv',[{'name':n,'source_url':'https://nightoffice.co/venues','reviewed_at':DATE} for n in EXISTING_NIGHTOFFICE_NAMES],['name','source_url','reviewed_at'])
    summary={'new_discovery_links_this_run':discovered_count,'generated_utc':datetime.now(timezone.utc).isoformat(),'seed_evidence_reviewed_at':DATE,'distinct_records':len(rows),'source_type':dict(Counter(r['source_type'] for r in rows)),'venue_type':dict(Counter(r['venue_type'] for r in rows)),'evening_yes':sum(r['after18_status']=='yes' for r in rows),'weekend_yes':sum(r['weekend_status']=='yes' for r in rows),'evening_or_weekend_yes':sum(r['after18_status']=='yes' or r['weekend_status']=='yes' for r in rows),'shortlist_ge50':sum(r['relevance_score']>=50 and r['status']=='candidate' for r in rows),'with_postcode':sum(bool(r['postcode']) for r in rows),'with_lat_lon':sum(r['latitude'] is not None and r['longitude'] is not None for r in rows),'actual_live_calendar_confirmations':0,'warning':'Venue inventory is a candidate discovery dataset, NOT proof of date-specific availability, exclusive hire or laptop-ready capacity.'}
    (D/'stats.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
