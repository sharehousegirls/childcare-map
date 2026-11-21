import json
import sqlite3
from contextlib import contextmanager
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.storage import initialize_database, ingest_snapshot_batch


class SnapshotStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "snapshots.sqlite3"
        initialize_database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def record(self, **overrides):
        record = {
            "facility_id": "F001", "name": "Test facility", "type": "국공립",
            "status": "운영", "address": "Test address", "sido": "Test province",
            "sigungu": "Test district", "capacity": 20, "enrolled": 10,
            "latitude": None, "longitude": None, "data_date": "2026-11-21",
            "wait_0": 1, "wait_1": 0, "wait_2": 1, "wait_3": 0,
            "wait_4": 0, "wait_5": 0, "wait_6_plus": 0, "wait_total": 2,
        }
        record.update(overrides)
        return record

    def test_schema_initialization_is_repeatable(self):
        initialize_database(self.db_path)
        initialize_database(self.db_path)
        result = ingest_snapshot_batch(self.db_path, [], source="test", run_id="empty-run")
        self.assertEqual(result["received_count"], 0)
        self.assertEqual(result["stored_count"], 0)

    def test_memory_database_is_rejected_to_prevent_nonpersistent_success(self):
        with self.assertRaises(ValueError):
            initialize_database(":memory:")

    def test_batch_date_fallback_removes_missing_date_flag(self):
        record = self.record(data_date=None)
        result = ingest_snapshot_batch(self.db_path, [record], source="test", source_data_date="2026-11-20", run_id="run-date")
        self.assertEqual(result["flagged_count"], 0)
        with sqlite3_connection(self.db_path) as conn:
            snapshot = conn.execute("SELECT source_data_date, quality_flags_json FROM facility_snapshot").fetchone()
            self.assertEqual(snapshot["source_data_date"], "2026-11-20")
            self.assertNotIn("source_data_date_missing", json.loads(snapshot["quality_flags_json"]))

    def test_snapshot_persists_and_reports_complete_age_sum(self):
        result = ingest_snapshot_batch(self.db_path, [self.record()], source="test", run_id="run-1")
        self.assertEqual(result["stored_count"], 1)
        with sqlite3_connection(self.db_path) as conn:
            snapshot = conn.execute("SELECT * FROM facility_snapshot").fetchone()
            self.assertEqual(snapshot["wait_total_reported"], 2)
            self.assertEqual(snapshot["wait_total_derived"], 2)
            self.assertEqual(snapshot["wait_total_consistent"], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM facility").fetchone()[0], 1)

    def test_snapshot_rows_are_append_only(self):
        ingest_snapshot_batch(self.db_path, [self.record()], source="test", run_id="run-immutable")
        with sqlite3_connection(self.db_path) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE facility_snapshot SET wait_total_reported=999")

    def test_missing_values_are_not_coerced_to_zero(self):
        record = self.record(wait_0=0, wait_1=None, wait_total=None)
        ingest_snapshot_batch(self.db_path, [record], source="test", run_id="run-2")
        with sqlite3_connection(self.db_path) as conn:
            snapshot = conn.execute("SELECT wait_0, wait_1, wait_total_reported, wait_total_derived FROM facility_snapshot").fetchone()
            self.assertEqual(snapshot["wait_0"], 0)
            self.assertIsNone(snapshot["wait_1"])
            self.assertIsNone(snapshot["wait_total_reported"])
            self.assertIsNone(snapshot["wait_total_derived")

    def test_missing_id_record_is_retained_for_review(self):
        result = ingest_snapshot_batch(self.db_path, [self.record(facility_id=" ")], source="test", run_id="run-3")
        self.assertEqual(result["stored_count"], 0)
        self.assertEqual(result["unresolved_count"], 1)
        with sqlite3_connection(self.db_path) as conn:
            row = conn.execute("SELECT normalized_record_json, quality_flags_json FROM unresolved_record").fetchone()
            self.assertIsNone(json.loads(row["normalized_record_json"])["facility_id"])
            self.assertIn("facility_id_missing", json.loads(row["quality_flags_json"]))

    def test_duplicate_id_keeps_first_snapshot_and_duplicate_audit_record(self):
        result = ingest_snapshot_batch(self.db_path, [self.record(), self.record(name="Duplicate row")], source="test", run_id="run-4")
        self.assertEqual(result["stored_count"], 1)
        self.assertEqual(result["unresolved_count"], 1)
        self.assertEqual(result["flagged_count"], 2)
        with sqlite3_connection(self.db_path) as conn:
            snapshot_flags = json.loads(conn.execute("SELECT quality_flags_json FROM facility_snapshot").fetchone()[0])
            unresolved = conn.execute("SELECT normalized_record_json, quality_flags_json FROM unresolved_record").fetchone()
            self.assertIn("facility_id_duplicate_in_batch", snapshot_flags)
            self.assertIn("duplicate_record_after_first", json.loads(unresolved["quality_flags_json"]))
            self.assertEqual(json.loads(unresolved["normalized_record_json"])["name"], "Duplicate row")

    def test_total_mismatch_is_flagged_without_overwriting_reported_value(self):
        ingest_snapshot_batch(self.db_path, [self.record(wait_total=8)], source="test", run_id="run-5")
        with sqlite3_connection(self.db_path) as conn:
            snapshot = conn.execute("SELECT wait_total_reported, wait_total_derived, wait_total_consistent, quality_flags_json FROM facility_snapshot").fetchone()
            self.assertEqual(snapshot["wait_total_reported"], 8)
            self.assertEqual(snapshot["wait_total_derived"], 2)
            self.assertEqual(snapshot["wait_total_consistent"], 0)
            self.assertIn("wait_total_mismatch", json.loads(snapshot["quality_flags_json"]))

    def test_invalid_count_is_null_and_flagged(self):
        ingest_snapshot_batch(self.db_path, [self.record(wait_0="2.5")], source="test", run_id="run-6")
        with sqlite3_connection(self.db_path) as conn:
            snapshot = conn.execute("SELECT wait_0, quality_flags_json FROM facility_snapshot").fetchone()
            self.assertIsNone(snapshot["wait_0"])
            self.assertIn("invalid_numeric:wait_0", json.loads(snapshot["quality_flags_json"]))

    def test_same_run_is_idempotent_and_conflicting_reuse_is_rejected(self):
        first = ingest_snapshot_batch(self.db_path, [self.record()], source="test", run_id="run-7")
        second = ingest_snapshot_batch(self.db_path, [self.record()], source="test", run_id="run-7")
        self.assertEqual(first, second)
        with sqlite3_connection(self.db_path) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM facility_snapshot").fetchone()[0], 1)
        with self.assertRaises(ValueError):
            ingest_snapshot_batch(self.db_path, [self.record(name="Changed")], source="test", run_id="run-7")


@contextmanager
def sqlite3_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


if __name__ == "__main__":
    unittest.main()
