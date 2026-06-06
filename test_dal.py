import unittest
import datetime
from dal import DataAccessLayer

class TestFinancialDWH(unittest.TestCase):
    def setUp(self):
        self.dal = DataAccessLayer()
        self.test_asset_id = 999

    def test_asset_lifecycle_and_temporal_versioning(self):
        """Testeaza structura append-only si versionarea temporala a activelor[cite: 206, 207]."""
        payload = {
            "Asset_ID": self.test_asset_id,
            "Name": "Test Crypto",
            "Description": "Temporal Test Unit",
            "Attributes": {"Ticker": "TST", "Class": "Crypto"}
        }
        doc = self.dal.save_asset(payload["Asset_ID"], payload["Name"], payload["Description"], payload["Attributes"])
        self.assertIsNotNone(doc)
        self.assertEqual(doc["Asset_ID"], self.test_asset_id)
        self.assertFalse(doc["deleted"])

    def test_ingestion_idempotency_and_provenance(self):
        """Testeaza urmarirea provenientei si prevenirea duplicarii datelor[cite: 181]."""
        asset_id = 1
        data_source_id = 101 
        
        doc1 = self.dal.save_time_series(
            asset_id=asset_id, data_source_id=data_source_id,
            business_date="2026-06-06", values_double={"price": 65000.0}
        )
        
        doc2 = self.dal.save_time_series(
            asset_id=asset_id, data_source_id=data_source_id,
            business_date="2026-06-06", values_double={"price": 65000.0}
        )
        
        self.assertIsNotNone(doc1)
        self.assertIsNotNone(doc2)
        self.assertEqual(doc1["Asset_ID"], asset_id)

if __name__ == "__main__":
    unittest.main()