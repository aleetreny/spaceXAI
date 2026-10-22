import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from validate_data import load_and_validate, DataIntegrityError
from supabase_import import map_rows
from cognee_sync import documents

class ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.tables,cls.counts=load_and_validate();cls.mapped=map_rows(cls.tables)
    def test_expected_counts(self):
        self.assertEqual([self.counts[k] for k in ('operators','buildings','venues','spaces','evidence','edges_raw','edges_unique')],[23,337,381,381,699,851,819])
    def test_foreign_keys(self):
        keys={r['node_id'] for r in self.mapped['vi_nodes']}
        self.assertEqual(len(keys),1821)
        self.assertTrue(all(r['from_id'] in keys and r['to_id'] in keys for r in self.mapped['vi_edges']))
    def test_unique_edge_key(self):
        rows=self.mapped['vi_edges'];self.assertEqual(len(set((r['from_id'],r['predicate'],r['to_id'],r['source_url']) for r in rows)),819)
    def test_payload_no_loss(self):
        src={x['venue_id']:x for x in self.tables['venues']}
        for row in self.mapped['vi_venues']:
            self.assertEqual(row['payload'],src[row['venue_id']]);self.assertEqual(row['lead_status'],'research_lead')
            self.assertFalse(row['payload']['availability_live'])
    def test_null_and_unknown(self):
        unknown=[r for r in self.mapped['vi_venues'] if r['capacity_laptops'] is None]
        self.assertEqual(len(unknown),380)
        self.assertTrue(any(r['after18_policy']=='unknown' for r in unknown))
    def test_cognee_documents_have_evidence(self):
        docs=list(documents(self.tables)); self.assertEqual(len(docs),381)
        for venue_id,body,sha in docs:
            self.assertIn('venue_id: '+venue_id,body)
            self.assertIn('bookable_dates: not_verified',body)
            self.assertIn('Evidence: evidence_id=',body)
            self.assertEqual(len(sha),64)
    def test_cognee_deterministic(self):
        self.assertEqual([(i,h) for i,_,h in documents(self.tables)],[(i,h) for i,_,h in documents(self.tables)])

if __name__=='__main__':unittest.main()
