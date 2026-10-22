import csv,json,unittest
from pathlib import Path
D=Path(__file__).resolve().parents[1]/'data'
class VenueResearchTests(unittest.TestCase):
 def setUp(self):
  self.venues=json.loads((D/'venues_v2.json').read_text());
  self.evidence=[json.loads(x) for x in (D/'evidence.jsonl').read_text().splitlines()]
 def test_id_unique(self):self.assertEqual(len({r['venue_id'] for r in self.venues}),len(self.venues))
 def test_all_provenance(self):self.assertTrue(all(r['source_url'].startswith('http') for r in self.venues))
 def test_no_fake_booking(self):self.assertTrue(all(r['availability_live'] is False and r['can_advertise_available'] is False and r['is_currently_bookable'] is False for r in self.venues))
 def test_no_capacity_inflation(self):
  self.assertEqual(sum(r['capacity_laptops'] is not None for r in self.venues),1)
 def test_valid_policy(self):
  for r in self.venues:
   for k in ('after18_policy','weekend_policy','overnight_policy'):
    self.assertIn(r[k],{'yes','no','restricted','unknown'})
 def test_evidence_links(self):
  ids={r['venue_id'] for r in self.venues}
  self.assertTrue(all(e['venue_id'] in ids for e in self.evidence))
 def test_missing_op_not_pretend(self):
  for r in self.venues:
   if r['acquisition_batch']=='legacy':self.assertIsNone(r['operator_id'])
 def test_no_bogus_coordinates(self):
  self.assertTrue(all(r['latitude'] is None and r['longitude'] is None for r in self.venues))
 def test_source_link_and_granularity(self):
  self.assertTrue(all(r['listing_granularity'] in ('space','building_or_unspecified') for r in self.venues))
if __name__=='__main__':unittest.main()
