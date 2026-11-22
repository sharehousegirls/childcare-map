import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import build_facility_meta


class FacilityMetaTests(unittest.TestCase):
    def test_single_source_date_and_collection_timestamp_are_separate(self):
        collected_at = datetime(2026, 11, 22, 12, 34, 56, tzinfo=timezone.utc)
        records = [{"data_date": "2026-11-21"}, {"data_date": "2026-11-21"}]
        meta = build_facility_meta(records, collected_at)
        self.assertEqual(meta["source_data_date"], "2026-11-21")
        self.assertEqual(meta["source_data_dates"], ["2026-11-21"])
        self.assertFalse(meta["mixed_source_data_dates"])
        self.assertEqual(meta["records_with_source_data_date"], 2)
        self.assertEqual(meta["records_without_source_data_date"], 0)
        self.assertEqual(meta["collected_at"], "2026-11-22T12:34:56+00:00")

    def test_mixed_source_dates_do_not_claim_a_single_date(self):
        records = [{"data_date": "2026-11-20"}, {"data_date": "2026-11-22"}]
        meta = build_facility_meta(records)
        self.assertIsNone(meta["source_data_date"])
        self.assertEqual(meta["source_data_dates"], ["2026-11-20", "2026-11-22"])
        self.assertTrue(meta["mixed_source_data_dates"])

    def test_missing_source_dates_are_counted_not_filled(self):
        records = [{"data_date": None}, {}, {"data_date": "  "}]
        meta = build_facility_meta(records)
        self.assertEqual(meta["source_data_dates"], [])
        self.assertIsNone(meta["source_data_date"])
        self.assertEqual(meta["records_with_source_data_date"], 0)
        self.assertEqual(meta["records_without_source_data_date"], 3)

    def test_collection_timestamp_is_normalized_to_utc(self):
        collected_at = datetime(2026, 11, 22, 21, 40, 0, tzinfo=timezone(timedelta(hours=9)))
        meta = build_facility_meta([], collected_at)
        self.assertEqual(meta["collected_at"], "2026-11-22T12:40:00+00:00")

    def test_naive_collection_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            build_facility_meta([], datetime(2026, 11, 22, 12, 0, 0))


if __name__ == "__main__":
    unittest.main()
