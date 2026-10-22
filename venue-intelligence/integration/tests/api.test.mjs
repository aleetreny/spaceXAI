import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import http from 'node:http';
process.env.SUPABASE_URL='https://example.supabase.co';
process.env.SUPABASE_PUBLISHABLE_KEY='sb_publishable_test';
process.env.COGNEE_URL='https://api.cognee.ai';
process.env.COGNEE_API_KEY='private-test-only-not-real';
const V={venue_id:'v_20788f6d9dad9722',display_name:'Ramen Space',venue_type:'coworking',source_url:'https://ramenclub.com/ramen-space/events/',review_status:'page_reviewed',after18_policy:'yes',weekend_policy:'yes',overnight_policy:'unknown',capacity_laptops:50,capacity_classroom:null,capacity_theatre:70,capacity_standing:100,research_priority:60,lead_status:'research_lead',payload:{building_id:'b_cb62d28fda98e79c',space_id:'s_6736d3af44249a44',capacity_laptops:50}};
const E={evidence_id:'e_fee8f5654104909f',venue_id:V.venue_id,field:'research_lead_mentioned',value:'Ramen Space',source_url:V.source_url,source_class:'first_party_enriched',observed_date:'2026-10-22',caveat:'Enquire; dates unknown'};
let urls=[];
globalThis.fetch=async (input,opts={})=>{
  const url=String(input);urls.push({url,headers:opts.headers||{}});
  if(url.includes('vi_venues'))return new Response(JSON.stringify([V]),{status:200});
  if(url.includes('vi_evidence'))return new Response(JSON.stringify([E]),{status:200});
  if(url.includes('/api/v1/search'))return new Response(JSON.stringify([{text:'venue_id: '+V.venue_id+' evidence_id: '+E.evidence_id}]),{status:200});
  return new Response('{}',{status:404});
};
const {server}=await import('../server/server.mjs');
let address;
before(async()=>{await new Promise(ok=>server.listen(0,'127.0.0.1',ok));address=server.address();});
after(async()=>{await new Promise(ok=>server.close(ok));});
async function call(path,body){return new Promise((resolve,reject)=>{const req=http.request({hostname:'127.0.0.1',port:address.port,path,method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{}},res=>{let output='';res.on('data',s=>output+=s);res.on('end',()=>resolve({status:res.statusCode,data:JSON.parse(output)}));});req.on('error',reject);req.end(body?JSON.stringify(body):undefined);});}
test('list only research not availability',async()=>{const r=await call('/api/venues?q=ramen&after18=yes');assert.equal(r.status,200);assert.equal(r.data.total,1);assert.equal(r.data.items[0].availability_live,false);assert.equal(r.data.items[0].capacity_laptops,50);});
test('details show ID, evidence and url',async()=>{const r=await call('/api/venues/'+V.venue_id);assert.equal(r.status,200);assert.equal(r.data.evidence[0].evidence_id,E.evidence_id);assert.equal(r.data.evidence[0].source_url,V.source_url)});
test('Cognee query only source-backed IDs',async()=>{const r=await call('/api/venues/ask',{question:'Which venues host evening events?'});assert.equal(r.status,200);assert.equal(r.data.matches[0].venue.venue_id,V.venue_id);assert.equal(r.data.matches[0].evidence[0].evidence_id,E.evidence_id);assert.equal(r.data.dataset,'nightoffice_venue_research_2026_10_22');});
test('reject invalid question',async()=>{const r=await call('/api/venues/ask',{question:''});assert.equal(r.status,400)});
test('no privileged secrets forwarded to Supabase',()=>{assert(urls.some(x=>x.url.includes('vi_venues')));for(const x of urls){if(x.url.includes('supabase.co')){assert.equal(x.headers.apikey,'sb_publishable_test');assert.equal(x.headers.Authorization,undefined);}}});
