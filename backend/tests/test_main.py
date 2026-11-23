import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import build_facility_meta


class FacilityMetaTests(unittest.TestCase):
    def test_empty_batch_has_unknown_date_coverage_ratios(self):
        meta = build_facility_meta([])
        self.assertIsNone(meta["source_data_date_coverage_ratio"])
        self.assertIsNone(meta["source_data_date_parseability_ratio"])

    def test_single_source_date_and_collection_timestamp_are_separate(self):
        collected_at = datetime(2026, 11, 22, 12, 34, 56, tzinfo=timezone.utc)
        records = [{"data_date": "2026-11-21"}, {"data_date": "2026-11-21"}]
        meta = build_facility_meta(records, collected_at)
        self.assertEqual(meta["source_data_date"], "2026-11-21")
        self.assertEqual(meta["source_data_dates"], ["2026-11-21"])
        self.assertFalse(meta["mixed_source_data_dates"])
        self.assertEqual(meta["records_with_source_data_date"], 2)
        self.assertEqual(meta["records_without_source_data_date"], 0)
        self.assertEqual(meta["records_with_parseable_source_data_date"], 2)
        self.assertEqual(meta["records_with_unparseable_source_data_date"], 0)
        self.assertEqual(meta["source_data_date_coverage_ratio"], 1.0)
        self.assertEqual(meta["source_data_date_parseability_ratio"], 1.0)
        self.assertEqual(meta["source_data_date_earliest"], "2026-11-21")
        self.assertEqual(meta["source_data_date_latest"], "2026-11-21")
        self.assertEqual(meta["collected_at"], "2026-11-22T12:34:56+00:00")

    def test_mixed_source_dates_do_not_claim_a_single_date(self):
        records = [{"data_date": "2026-11-20"}, {"data_date": "2026-11-22"}]
        meta = build_facility_meta(records)
        self.assertIsNone(meta["source_data_date"])
        self.assertEqual(meta["source_data_dates"], ["2026-11-20", "2026-11-22"])
        self.assertTrue(meta["mixed_source_data_dates"])
        self.assertEqual(meta["source_data_date_coverage_ratio"], 1.0)
        self.assertEqual(meta["source_data_date_parseability_ratio"], 1.0)
        self.assertEqual(meta["source_data_date_earliest"], "2026-11-20")
        self.assertEqual(meta["source_data_date_latest"], "2026-11-22")

    def test_iso_date_range_and_unparseable_values_are_diagnosed(self):
        records = [
            {"data_date": "2026-11-20"},
            {"data_date": "2026-11-23"},
            {"data_date": "2026/11/21"},
            {"data_date": "2026-02-30"},
            {"data_date": ""},
        ]
        meta = build_facility_meta(records)
        self.assertEqual(meta["records_with_source_data_date"], 4)
        self.assertEqual(meta["records_without_source_data_date"], 1)
        self.assertEqual(meta["records_with_parseable_source_data_date"], 2)
        self.assertEqual(meta["records_with_unparseable_source_data_date"], 2)
        self.assertEqual(meta["source_data_date_earliest"], "2026-11-20")
        self.assertEqual(meta["source_data_date_latest"], "2026-11-23")
        self.assertEqual(meta["source_data_date_coverage_ratio"], 0.8)
        self.assertEqual(meta["source_data_date_parseability_ratio"], 0.5)
        # Raw non-ISO and invalid calendar strings are preserved for source review.
        self.assertIn("2026/11/21", meta["source_data_dates"])
        self.assertIn("2026-02-30", meta["source_data_dates"])

    def test_missing_source_dates_are_counted_not_filled(self):
        records = [{"data_date": None}, {}, {"data_date": "  "}]
        meta = build_facility_meta(records)
        self.assertEqual(meta["source_data_dates"], [])
        self.assertIsNone(meta["source_data_date"])
        self.assertEqual(meta["records_with_source_data_date"], 0)
        self.assertEqual(meta["records_without_source_data_date"], 3)
        self.assertEqual(meta["records_with_parseable_source_data_date"], 0)
        self.assertEqual(meta["records_with_unparseable_source_data_date"], 0)
        self.assertEqual(meta["source_data_date_coverage_ratio"], 0.0)
        self.assertIsNone(meta["source_data_date_parseability_ratio"])
        self.assertIsNone(meta["source_data_date_earliest"])
        self.assertIsNone(meta["source_data_date_latest"])

    def test_source_date_ratios_are_record_level_not_unique_facility_level(self):
        records = [
            {"facility_id": "F-001", "data_date": "2026-11-20"},
            {"facility_id": "F-001", "data_date": None},
            {"facility_id": "F-002", "data_date": "2026-11-21"},
        ]
        meta = build_facility_meta(records)
        # Ratios use response rows, not deduplicated facility IDs.
        self.assertEqual(meta["records_with_source_data_date"], 2)
        self.assertEqual(meta["records_without_source_data_date"], 1)
        self.assertEqual(meta["source_data_date_coverage_ratio"], 0.6667)
        self.assertEqual(meta["source_data_date_parseability_ratio"], 1.0)

    def test_collection_timestamp_is_normalized_to_utc(self):
        collected_at = datetime(2026, 11, 22, 21, 40, 0, tzinfo=timezone(timedelta(hours=9)))
        meta = build_facility_meta([], collected_at)
        self.assertEqual(meta["collected_at"], "2026-11-22T12:40:00+00:00")

    def test_naive_collection_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            build_facility_meta([], datetime(2026, 11, 22, 12, 0, 0))


if __name__ == "__main__":
    unittest.main()
