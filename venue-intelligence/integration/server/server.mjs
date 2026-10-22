/** Night Office research query backend. Node >=20, no runtime dependencies.
 *
 * Same-origin server-side API. No privileged Supabase key or Cognee key in browser.
 * All venues are research leads; never return bookable=true.
 */
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.VENUE_PORT || 4343);
const DATASET = 'nightoffice_venue_research_2026_10_22';
const idPattern = /^v_[a-f0-9]{12,32}$/;
const evidencePattern = /^e_[a-f0-9]{12,32}$/;
const askHits = new Map();
function askAllowed(req) {
  const ip = req.socket.remoteAddress || 'unknown';
  const now = Date.now();
  const before = (askHits.get(ip) || []).filter(t => now - t < 3600_000);
  if (before.length >= 10) return false;
  before.push(now); askHits.set(ip,before);
  if (askHits.size > 5000) askHits.clear();
  return true;
}
const localHost = /^(localhost|127\.0\.0\.1)$/;
function config() {
  const sb = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_PUBLISHABLE_KEY || process.env.SUPABASE_ANON_KEY;
  if (!sb || !key || !/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/.test(sb)) {
    throw new Error('SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be set to the dedicated same-room project');
  }
  return { sb: sb.replace(/\/$/, ''), key };
}
function supabaseHeaders(key) {
  return key.startsWith('sb_publishable_') ? { apikey: key } : { apikey: key, Authorization: `Bearer ${key}` };
}
async function readTable(table, params) {
  const { sb, key } = config();
  const req = await fetch(`${sb}/rest/v1/${table}?${params.toString()}`, {
    headers: { ...supabaseHeaders(key), Accept: 'application/json' },
    signal: AbortSignal.timeout(14000),
  });
  if (!req.ok) throw new Error(`Supabase ${table}: HTTP ${req.status}`);
  return req.json();
}
const selectFields = 'venue_id,display_name,venue_type,review_status,after18_policy,weekend_policy,overnight_policy,capacity_laptops,capacity_classroom,capacity_theatre,capacity_standing,research_priority,lead_status,source_url,payload';
const venParams = new URLSearchParams({ select: selectFields, limit: '1000', order: 'research_priority.desc' });
async function venues() { return readTable('vi_venues',venParams); }
function renderVenue(v) {
  const p = v.payload || {};
  return {
    venue_id: v.venue_id, name: v.display_name, type: v.venue_type,
    source_url:v.source_url, review_status: v.review_status,
    building_id:p.building_id ?? null, space_id:p.space_id ?? null,
    postcode:p.postcode ?? null,borough:p.borough ?? null,
    after18_policy:v.after18_policy,weekend_policy:v.weekend_policy,overnight_policy:v.overnight_policy,
    capacity_laptops:v.capacity_laptops,capacity_classroom:v.capacity_classroom,
    capacity_theatre:v.capacity_theatre, capacity_standing:v.capacity_standing,
    wifi_status:p.wifi_status ?? 'unknown',accessibility_status:p.accessibility_status ?? 'unknown',
    price_gbp_from:p.price_gbp_from ?? null, price_unit:p.price_unit ?? null,
    research_priority:v.research_priority, lead_status:'research_lead',
    availability_live:false,is_currently_bookable:false,can_advertise_available:false,
    source_caveat:'Potential venue only — enquire with the operator. No date availability verified.',
  };
}
function json(res,status,data) {
  res.writeHead(status, {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
  res.end(JSON.stringify(data));
}
function searchFilter(all,q,params) {
  const term=(q||'').toLocaleLowerCase().trim();
  const type=params.get('type');const after18=params.get('after18');const weekend=params.get('weekend');
  const review=params.get('review_status');const minLaptops=Number(params.get('min_laptops')||0);
  return all.filter(v=>{
    const p=v.payload||{};
    return (!term || [v.display_name,v.venue_type,p.borough,p.postcode,p.street_address].some(x=>String(x||'').toLowerCase().includes(term))) &&
      (!type || v.venue_type===type) && (!after18 || v.after18_policy===after18) &&
      (!weekend || v.weekend_policy===weekend) && (!review || v.review_status===review) &&
      (!minLaptops || (v.capacity_laptops !== null && v.capacity_laptops>=minLaptops));
  });
}
async function evidenceFor(venueId) {
  const params=new URLSearchParams({venue_id:'eq.'+venueId,select:'evidence_id,venue_id,field,value,source_url,source_class,observed_date,caveat,evidence_text',order:'evidence_id.asc',limit:'1000'});
  return readTable('vi_evidence',params);
}
function cogneeConfig() {
  const base=process.env.COGNEE_URL?.replace(/\/$/,'');const key=process.env.COGNEE_API_KEY;
  if (!base || !key) return null;
  const uri=new URL(base);
  if (uri.protocol!=='https:' && !(uri.protocol==='http:' && localHost.test(uri.hostname))) throw new Error('Insecure Cognee URL rejected');
  const mode=process.env.COGNEE_AUTH_MODE||'api_key';
  if (!['api_key','bearer'].includes(mode)) throw new Error('COGNEE_AUTH_MODE must be api_key or bearer');
  return {base,headers:mode==='bearer'?{Authorization:`Bearer ${key}`}:{'X-Api-Key':key}};
}
async function cogneeSearch(question) {
  const c=cogneeConfig();if(!c) return {ready:false,results:[],detail:'Cognee endpoint not configured'};
  const resp=await fetch(c.base+'/api/v1/search',{
    method:'POST',headers:{...c.headers,'Content-Type':'application/json'},
    body:JSON.stringify({query:question,search_type:'CHUNKS',datasets:[DATASET],top_k:12}),
    signal:AbortSignal.timeout(45000),
  });
  if(!resp.ok)throw new Error('Cognee search HTTP '+resp.status);
  const body=await resp.json();
  return {ready:true,results:Array.isArray(body)?body:Array.isArray(body.results)?body.results:[body]};
}
function cogneeCitations(raw, venueIds){
  const all=JSON.stringify(raw).slice(0,80000);
  const venueIdsFound=new Set((all.match(/v_[a-f0-9]{12,32}/g)||[]).filter(x=>venueIds.has(x)));
  const evidenceIdsFound=new Set((all.match(/e_[a-f0-9]{12,32}/g)||[]).filter(x=>evidencePattern.test(x)));
  return {venueIds:[...venueIdsFound].slice(0,15),evidenceIds:[...evidenceIdsFound].slice(0,40)};
}
async function ask(question) {
  const v=await venues();const map=new Map(v.map(x=>[x.venue_id,x]));
  const cog=await cogneeSearch(question);
  const refs=cogneeCitations(cog.results,new Set(map.keys()));
  const matches=[];
  for (const id of refs.venueIds) {
    const doc=map.get(id);if(!doc)continue;
    const evidence=await evidenceFor(id);
    const eligible=evidence.filter(e=>refs.evidenceIds.includes(e.evidence_id));
    matches.push({venue:renderVenue(doc), evidence:eligible.length?eligible:evidence.slice(0,4)});
  }
  // No unverified LLM answer is returned. This is a retrieval response with grounded source links.
  return {query:question, dataset:DATASET, cognee_connected:cog.ready,
    status:cog.ready?(matches.length?'retrieved_with_sources':'retrieved_but_no_source_ids'):'not_configured',
    answer:matches.length?'Candidate matches found; verify capacity and dates with the operator.':'No source-backed venue answer available.',
    matches, warning:'No real-time booking data; unknown does not mean no.'};
}
const staticFiles=new Map([['/venues/','index.html'],['/venues/index.html','index.html'],['/venues/client.js','client.js']]);
export const server=createServer(async(req,res)=>{
  try {
    const url=new URL(req.url,'http://localhost');const path=url.pathname;
    if(req.method==='GET' && staticFiles.has(path)) {
      const ext=path.endsWith('.js')?'application/javascript':'text/html';
      const contents=await readFile(join(root,'..','ui',staticFiles.get(path)));
      res.writeHead(200,{'Content-Type':ext+'; charset=utf-8','X-Content-Type-Options':'nosniff'});res.end(contents);return;
    }
    if(req.method==='GET' && path==='/api/venues'){
      const n=Math.min(Math.max(Number(url.searchParams.get('limit')||50),1),200);
      const all=await venues();const filtered=searchFilter(all,url.searchParams.get('q'),url.searchParams);
      json(res,200,{total:filtered.length,items:filtered.slice(0,n).map(renderVenue)});return;
    }
    let m=path.match(/^\/api\/venues\/(v_[a-f0-9]{12,32})(\/evidence)?$/);
    if(req.method==='GET' && m){
      const v=await readTable('vi_venues',new URLSearchParams({venue_id:'eq.'+m[1],select:'*',limit:'1'}));
      if(!v.length){json(res,404,{error:'venue_not_found'});return;}
      if(m[2])json(res,200,{venue_id:m[1],evidence:await evidenceFor(m[1])});
      else json(res,200,{...renderVenue(v[0]),payload:v[0].payload,evidence:await evidenceFor(m[1])});
      return;
    }
    if(req.method==='POST' && path==='/api/venues/ask'){
      if(!askAllowed(req)){json(res,429,{error:'rate_limit',message:'Maximum 10 graph searches per hour.'});return;}
      let b='';for await(const chunk of req){b+=chunk;if(b.length>3000){json(res,413,{error:'too_large'});return;}}
      let data;try{data=JSON.parse(b);}catch{json(res,400,{error:'invalid_json'});return;}
      const question=typeof data.question==='string'?data.question.trim():'';
      if(!question || question.length>300){json(res,400,{error:'question_must_be_1_to_300_chars'});return;}
      json(res,200,await ask(question));return;
    }
    json(res,404,{error:'not_found'});
  } catch(err) {
    // No credentials, raw third-party data, or stack traces returned to browser.
    console.error('Venue API error:',err.message);
    json(res,503,{error:'backend_unavailable',message:'The venue backend is not configured or the requested provider failed.'});
  }
});
if(process.argv[1]===fileURLToPath(import.meta.url)){
  server.listen(PORT,'127.0.0.1',()=>console.log(`Venue backend http://127.0.0.1:${PORT}/venues/`));
}
