import unittest
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.provider import (
    _number, _flatten_records, _get_value, _sum_age_waits,
    _validate_field_map, _safe_http_error, _wait_total_consistent, ProviderError,
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

if __name__ == "__main__":
    unittest.main()
