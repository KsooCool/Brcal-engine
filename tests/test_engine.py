"""
Comprehensive unit and integration test suite for the BRCAL Analytics Engine.
CMPS 201B Honors Project - Milestone 10
"""
import os
import tempfile
import unittest
from datetime import datetime
from src.models import CivicRecord
from src.ingest import load_and_clean_csv
from src.structures import CivicDataEngine
from src.bst import BinarySearchTree
from src.parallel import single_process_category_counts, parallel_category_counts


class TestBRCALEngine(unittest.TestCase):
    def setUp(self):
        """Set up reusable sample records before each test."""
        self.sample_records = [
            CivicRecord("1", datetime(2026, 3, 10, 12, 0), "Drainage", "PLANK RD", "North BR", "OPEN", {}),
            CivicRecord("2", datetime(2026, 3, 4, 10, 0), "Blight", "FLORIDA ST", "Downtown", "CLOSED", {}),
            CivicRecord("3", datetime(2026, 3, 18, 14, 0), "Traffic", "SCENIC HWY", "North BR", "PENDING", {}),
            CivicRecord("4", datetime(2026, 3, 7, 9, 30), "Drainage", "EVANGELINE ST", "Scotlandville", "OPEN", {}),
            CivicRecord("5", datetime(2026, 3, 10, 12, 0), "Blight", "GOVERNMENT ST", "Mid City", "OPEN", {}),  # Duplicate timestamp
        ]

    # --- 1. Data Ingestion & Edge Cases ---
    def test_csv_ingestion_and_cleaning(self):
        csv_data = (
            "ID,Date,Category,Street,Neighborhood,Status\n"
            "101,2026-03-04 10:15:00,  blight , florida st , downtown , closed\n"
            "102,invalid-date,DRAINAGE,plank rd,,\n"
            "103,,,,,\n"  # Missing category -> should be skipped
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp.write(csv_data)
            tmp_path = tmp.name

        try:
            records, skipped = load_and_clean_csv(tmp_path)
            self.assertEqual(len(records), 2)
            self.assertEqual(skipped, 1)

            # Check normalization
            self.assertEqual(records[0].category, "Blight")
            self.assertEqual(records[0].street, "FLORIDA ST")
            self.assertEqual(records[0].neighborhood, "Downtown")
            self.assertEqual(records[0].status, "CLOSED")

            # Check fallback defaults on missing/invalid fields
            self.assertEqual(records[1].incident_date, datetime(1970, 1, 1))
            self.assertEqual(records[1].neighborhood, "Unknown")
            self.assertEqual(records[1].status, "OPEN")
        finally:
            os.remove(tmp_path)

    def test_empty_csv(self):
        csv_data = "ID,Date,Category,Street,Neighborhood,Status\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp.write(csv_data)
            tmp_path = tmp.name

        try:
            records, skipped = load_and_clean_csv(tmp_path)
            self.assertEqual(records, [])
            self.assertEqual(skipped, 0)
        finally:
            os.remove(tmp_path)

    # --- 2. Core Data Structures (Dict & Set) ---
    def test_dictionary_and_set_indexes(self):
        engine = CivicDataEngine(self.sample_records)

        # O(1) ID lookup
        rec = engine.find_by_id("3")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.category, "Traffic")
        self.assertIsNone(engine.find_by_id("NON-EXISTENT"))

        # Category grouping
        drainage = engine.find_by_category("drainage")
        self.assertEqual(len(drainage), 2)

        # Set membership
        self.assertTrue(engine.has_neighborhood("Downtown"))
        self.assertTrue(engine.has_neighborhood("north br"))
        self.assertFalse(engine.has_neighborhood("Gardere"))

        # Street scan
        florida_matches = engine.find_by_street("florida")
        self.assertEqual(len(florida_matches), 1)
        self.assertEqual(florida_matches[0].record_id, "2")

    # --- 3. Custom Binary Search Tree ---
    def test_bst_insert_search_and_height(self):
        bst = BinarySearchTree()
        self.assertEqual(bst.get_height(), 0)

        for r in self.sample_records:
            bst.insert(r.incident_date, r)

        self.assertEqual(len(bst), 5)
        self.assertGreaterEqual(bst.get_height(), 3)

        # Exact match with duplicate keys (March 10 at 12:00 has IDs 1 and 5)
        exact_matches = bst.search(datetime(2026, 3, 10, 12, 0))
        self.assertEqual(len(exact_matches), 2)
        self.assertEqual({r.record_id for r in exact_matches}, {"1", "5"})

    def test_bst_range_query(self):
        bst = BinarySearchTree()
        for r in self.sample_records:
            bst.insert(r.incident_date, r)

        # Query March 5 through March 15 -> should return IDs 4 (Mar 7), 1 (Mar 10), and 5 (Mar 10)
        results = bst.range_search(datetime(2026, 3, 5), datetime(2026, 3, 15))
        matched_ids = {r.record_id for r in results}
        self.assertEqual(matched_ids, {"1", "4", "5"})

        # Out-of-bounds range
        empty_results = bst.range_search(datetime(2025, 1, 1), datetime(2025, 12, 31))
        self.assertEqual(empty_results, [])

    # --- 4. Multiprocessing Equivalence ---
    def test_multiprocessing_matches_single_process(self):
        # Scale up dataset to test chunking across 4 workers
        large_dataset = self.sample_records * 500  # 2,500 records
        single_counts = single_process_category_counts(large_dataset)
        parallel_counts = parallel_category_counts(large_dataset, num_workers=4)

        self.assertEqual(single_counts, parallel_counts)
        self.assertEqual(single_counts["Drainage"], 1000)
        self.assertEqual(single_counts["Blight"], 1000)
        self.assertEqual(single_counts["Traffic"], 500)


if __name__ == "__main__":
    unittest.main()