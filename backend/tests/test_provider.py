import unittest
from app.provider import _number, _flatten_records, _get_value, _sum_age_waits

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

if __name__ == "__main__":
    unittest.main()
