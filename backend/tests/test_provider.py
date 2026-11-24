import unittest
import sys
from pathlib import Path
import httpx
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.provider import (
    _number, _flatten_records, _get_value, _sum_age_waits,
    _validate_field_map, _validate_live_field_map, LIVE_WAIT_FIELDS,
    _safe_http_error, _wait_total_consistent, _mark_facility_id_quality,
    _normalize_provider_record, ProviderError,
)

class ProviderNormalizationTests(unittest.TestCase):
    def test_flatten_json_items(self):
        payload = {"response": {"body": {"items": {"item": [
            {"CRCODE": "A1", "CRNAME": "Facility 1"},
            {"CRCODE": "A2", "CRNAME": "Facility 2"}
        ]}}}}
        rows = _flatten_records(payload)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["CRCODE"], "A1")

    def test_single_record_payload(self):
        record = {"CRCODE": "A1", "CRNAME": "Facility 1"}
        self.assertEqual(_flatten_records(record), [record])

    def test_alias_mapping(self):
        record = {"CRNAME": "Facility 1"}
        self.assertEqual(_get_value(record, "name", {}), "Facility 1")

    def test_count_parsing(self):
        self.assertEqual(_number("1,200"), 1200)
        self.assertEqual(_number("4.0"), 4)
        self.assertIsNone(_number("4.5"))
        self.assertIsNone(_number("-3"))
        self.assertIsNone(_number("NaN"))

    def test_missing_values_stay_none(self):
        for value in (None, "", "-", "--"):
            self.assertIsNone(_number(value))

    def test_coordinates_allow_negative_float(self):
        self.assertEqual(_number("-128.5", floating=True), -128.5)

    def test_age_sum_requires_all_buckets(self):
        self.assertEqual(_sum_age_waits([1, 2, 0]), 3)
        self.assertIsNone(_sum_age_waits([1, None, 0]))

    def test_total_consistency_when_equal(self):
        self.assertTrue(_wait_total_consistent(12, 12))

    def test_total_consistency_when_mismatch(self):
        self.assertFalse(_wait_total_consistent(12, 10))

    def test_total_consistency_unknown_when_incomplete(self):
        self.assertIsNone(_wait_total_consistent(None, 12))
        self.assertIsNone(_wait_total_consistent(12, None))

    def test_field_map_validation(self):
        self.assertEqual(_validate_field_map({"name": "CRNAME"}), {"name": "CRNAME"})
        for invalid in ({"unknown_field": "X"}, {"name": ""}, {"name": ["CRNAME"]}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ProviderError):
                    _validate_field_map(invalid)

    def test_live_field_map_requires_identity_date_and_waitlist(self):
        invalid_maps = (
            {},
            {"name": "NAME", "data_date": "DATE", "wait_total": "TOTAL"},
            {"facility_id": "ID", "name": "NAME", "wait_0": "W0"},
            {"facility_id": "ID", "name": "NAME", "wait_total": "TOTAL"},
        )
        for invalid in invalid_maps:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ProviderError):
                    _validate_live_field_map(invalid)

    def test_live_field_map_accepts_total_or_complete_age_buckets(self):
        identity = {"facility_id": "ID", "name": "NAME", "data_date": "DATE"}
        total_map = {**identity, "wait_total": "TOTAL"}
        self.assertEqual(_validate_live_field_map(total_map), total_map)
        age_map = {**identity, **{field: field.upper() for field in LIVE_WAIT_FIELDS}}
        self.assertEqual(_validate_live_field_map(age_map), age_map)
    def test_field_map_trims_provider_field_names_and_rejects_duplicates(self):
        self.assertEqual(_validate_field_map({"name": " CRNAME "}), {"name": "CRNAME"})
        duplicate_maps = (
            {"facility_id": "ID", "name": "ID"},
            {"wait_0": "AGE", "wait_1": "AGE"},
        )
        for duplicate in duplicate_maps:
            with self.subTest(duplicate=duplicate):
                with self.assertRaisesRegex(ProviderError, "mapped to multiple normalized fields"):
                    _validate_field_map(duplicate)

    def test_live_field_map_rejects_duplicate_critical_provider_fields(self):
        duplicate_map = {
            "facility_id": "ID", "name": "ID", "data_date": "DATE",
            "wait_total": "TOTAL",
        }
        with self.assertRaisesRegex(ProviderError, "mapped to multiple normalized fields"):
            _validate_live_field_map(duplicate_map)


    def test_live_normalization_uses_only_explicit_field_mapping(self):
        record = {
            "facility_id": "F1", "name": "Mapped Name", "data_date": "2026-11-23",
            "wait_total": "7", "CRNAME": "Alias Name", "CRCODE": "Alias ID",
            "CRTNAME": "Alias Type",
        }
        mapping = {"facility_id": "facility_id", "name": "name", "data_date": "data_date", "wait_total": "wait_total"}
        row = _normalize_provider_record(record, mapping, allow_aliases=False)
        self.assertEqual(row["facility_id"], "F1")
        self.assertEqual(row["name"], "Mapped Name")
        self.assertEqual(row["wait_total"], 7)
        self.assertIsNone(row["type"])

    def test_secondary_schema_candidates_are_not_accepted_without_explicit_mapping(self):
        # These names have appeared in secondary schema listings, but the official
        # service-specific XML specification and a redacted payload are still unverified.
        record = {
            "stcode": "F1", "crname": "Candidate Name", "crtypename": "Candidate Type",
            "crstatusname": "Candidate Status", "craddr": "Candidate Address",
            "crcapat": "100", "Crchcnt": "80", "La": "37.5", "Lo": "127.0",
            "datastdrdt": "2026-11-24", "ew_cnt_00": "1", "ew_cnt_01": "2",
            "ew_cnt_02": "0", "ew_cnt_03": "0", "ew_cnt_04": "0",
            "ew_cnt_05": "0", "ew_cnt_m6": "0", "ew_cnt_tot": "3",
        }
        row = _normalize_provider_record(record, {}, allow_aliases=False)
        for field in ("facility_id", "name", "data_date", "wait_0", "wait_total"):
            with self.subTest(field=field):
                self.assertIsNone(row[field])

    def test_http_status_error_does_not_expose_key(self):
        request = httpx.Request("GET", "https://api.example.test/data?serviceKey=SECRET_KEY")
        response = httpx.Response(403, request=request)
        exc = httpx.HTTPStatusError("request failed", request=request, response=response)
        message = _safe_http_error(exc)
        self.assertEqual(message, "Official API returned HTTP 403.")
        self.assertNotIn("SECRET_KEY", message)

    def test_timeout_error_is_sanitized(self):
        request = httpx.Request("GET", "https://api.example.test/data?serviceKey=SECRET_KEY")
        exc = httpx.ReadTimeout("timed out", request=request)
        message = _safe_http_error(exc)
        self.assertEqual(message, "Official API request timed out.")
        self.assertNotIn("SECRET_KEY", message)

    def test_facility_ids_trimmed_and_duplicates_flagged(self):
        rows = [{"facility_id": " A001 "}, {"facility_id": "A001"}, {"facility_id": "B002"}]
        result = _mark_facility_id_quality(rows)
        self.assertEqual([row["facility_id"] for row in result], ["A001", "A001", "B002"])
        self.assertEqual([row["facility_id_duplicate"] for row in result], [True, True, False])
        self.assertEqual([row["facility_id_missing"] for row in result], [False, False, False])
        self.assertIn("facility_id_duplicate", result[0]["quality_flags"])
        self.assertNotIn("facility_id_duplicate", result[2]["quality_flags"])

    def test_missing_facility_id_flagged_without_dropping_named_row(self):
        rows = [{"facility_id": None, "name": "Unnamed code facility"}, {"facility_id": " "}]
        result = _mark_facility_id_quality(rows)
        self.assertEqual(result[0]["facility_id"], None)
        self.assertTrue(result[0]["facility_id_missing"])
        self.assertFalse(result[0]["facility_id_duplicate"])
        self.assertTrue(result[1]["facility_id_missing"])
        self.assertIn("facility_id_missing", result[0]["quality_flags"])

    def test_provider_total_provenance_preserved_when_derived(self):
        record = {
            "facility_id": "F1", "wait_0": 1, "wait_1": 2,
            "wait_2": 0, "wait_3": 0, "wait_4": 0, "wait_5": 0,
            "wait_6_plus": 0, "wait_total": None,
        }
        row = _normalize_provider_record(record, {})
        self.assertEqual(row["wait_total"], 3)
        self.assertIsNone(row["wait_total_reported"])
        self.assertEqual(row["wait_total_derived"], 3)
        self.assertIsNone(row["wait_total_consistent"])
        self.assertNotIn("wait_total_mismatch", row["quality_flags"])

    def test_reported_total_mismatch_is_quality_flagged(self):
        record = {
            "facility_id": "F1", "wait_0": 1, "wait_1": 2,
            "wait_2": 0, "wait_3": 0, "wait_4": 0, "wait_5": 0,
            "wait_6_plus": 0, "wait_total": 4,
        }
        row = _normalize_provider_record(record, {})
        self.assertEqual(row["wait_total_reported"], 4)
        self.assertEqual(row["wait_total_derived"], 3)
        self.assertEqual(row["wait_total"], 4)
        self.assertFalse(row["wait_total_consistent"])
        self.assertIn("wait_total_mismatch", row["quality_flags"])

    def test_invalid_numeric_value_is_null_and_flagged(self):
        row = _normalize_provider_record({"facility_id": "F1", "wait_0": "2.5"}, {})
        self.assertIsNone(row["wait_0"])
        self.assertIn("invalid_numeric:wait_0", row["quality_flags"])

    def test_geographic_coordinates_out_of_range_are_null_and_flagged(self):
        row = _normalize_provider_record({"facility_id": "F1", "latitude": "95", "longitude": "181"}, {})
        self.assertIsNone(row["latitude"])
        self.assertIsNone(row["longitude"])
        self.assertIn("coordinate_out_of_range:latitude", row["quality_flags"])
        self.assertIn("coordinate_out_of_range:longitude", row["quality_flags"])

    def test_incomplete_age_buckets_are_flagged_not_zero_filled(self):
        row = _normalize_provider_record({"facility_id": "F1", "wait_0": 0, "wait_1": None}, {})
        self.assertIsNone(row["wait_total_derived"])
        self.assertIsNone(row["wait_total"])
        self.assertIn("wait_age_buckets_incomplete", row["quality_flags"])

    def test_incomplete_coordinate_pair_is_flagged(self):
        row = _normalize_provider_record({"facility_id": "F1", "latitude": "37.5"}, {})
        self.assertEqual(row["latitude"], 37.5)
        self.assertIsNone(row["longitude"])
        self.assertIn("coordinate_pair_incomplete", row["quality_flags"])

    def test_missing_coordinate_pair_is_not_flagged(self):
        row = _normalize_provider_record({"facility_id": "F1"}, {})
        self.assertIsNone(row["latitude"])
        self.assertIsNone(row["longitude"])
        self.assertNotIn("coordinate_pair_incomplete", row["quality_flags"])

if __name__ == "__main__":
    unittest.main()
