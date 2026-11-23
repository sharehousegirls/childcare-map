import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.regions import RegionValidationError, build_region_tree, validate_region_records


def fixture_regions():
    return [
        {"region_id": "S1", "name": "서울", "region_type": "sido", "source_system": "test-admin", "source_code": "00011", "is_active": True},
        {"region_id": "G1", "name": "종로구", "region_type": "sigungu", "parent_region_id": "S1", "source_system": "test-admin", "source_code": "11110", "is_active": True},
        {"region_id": "D1", "name": "청운효자동", "region_type": "admin_dong", "parent_region_id": "G1", "source_system": "test-admin", "source_code": "D-01", "is_active": True},
        {"region_id": "L1", "name": "청운동", "region_type": "legal_dong", "parent_region_id": "G1", "source_system": "test-legal", "source_code": "L-01", "is_active": True},
        {"region_id": "E1", "name": "청운읍", "region_type": "eup", "parent_region_id": "G1", "source_system": "test-admin", "source_code": "E-01", "is_active": True},
        {"region_id": "M1", "name": "청운면", "region_type": "myeon", "parent_region_id": "G1", "source_system": "test-admin", "source_code": "M-01", "is_active": True},
        {"region_id": "R1", "name": "청운리", "region_type": "ri", "parent_region_id": "E1", "source_system": "test-legal", "source_code": "R-01", "is_active": True},
    ]


class RegionValidationTests(unittest.TestCase):
    def test_valid_hierarchy_with_distinct_dong_systems(self):
        normalized = validate_region_records(fixture_regions())
        self.assertEqual(len(normalized), 7)
        self.assertEqual(normalized[0]["source_code"], "00011")
        self.assertEqual(normalized[2]["region_type"], "admin_dong")
        self.assertEqual(normalized[3]["region_type"], "legal_dong")

    def test_empty_list_is_valid(self):
        self.assertEqual(validate_region_records([]), [])
        self.assertEqual(build_region_tree([]), [])

    def test_tree_is_nested_and_deterministically_sorted(self):
        tree = build_region_tree(fixture_regions())
        self.assertEqual([item["region_id"] for item in tree], ["S1"])
        district = tree[0]["children"][0]
        self.assertEqual(district["region_id"], "G1")
        self.assertEqual([item["region_type"] for item in district["children"]], ["admin_dong", "legal_dong", "eup", "myeon"])
        eup = next(item for item in district["children"] if item["region_type"] == "eup")
        self.assertEqual(eup["children"][0]["region_id"], "R1")

    def test_duplicate_region_id_rejected(self):
        records = fixture_regions() + [dict(fixture_regions()[0])]
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("duplicate_region_id", {issue["code"] for issue in context.exception.issues})

    def test_unknown_region_type_rejected(self):
        records = fixture_regions()
        records[1]["region_type"] = "district_guess"
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("invalid_region_type", {issue["code"] for issue in context.exception.issues})

    def test_missing_parent_rejected(self):
        records = fixture_regions()
        records[1]["parent_region_id"] = "missing"
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("parent_not_found", {issue["code"] for issue in context.exception.issues})

    def test_parent_type_must_match_initial_contract(self):
        records = fixture_regions()
        records[2]["parent_region_id"] = "S1"
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("invalid_parent_type", {issue["code"] for issue in context.exception.issues})

    def test_source_codes_unique_per_source_system(self):
        records = fixture_regions()
        records[2]["source_code"] = records[3]["source_code"]
        records[2]["source_system"] = records[3]["source_system"]
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("duplicate_source_code", {issue["code"] for issue in context.exception.issues})

    def test_source_identity_requires_both_fields(self):
        records = fixture_regions()
        records[2].pop("source_system")
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("source_identity_incomplete", {issue["code"] for issue in context.exception.issues})

    def test_parent_cycle_rejected(self):
        records = fixture_regions()
        records[0]["parent_region_id"] = "G1"
        records[1]["parent_region_id"] = "S1"
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("parent_cycle", {issue["code"] for issue in context.exception.issues})

    def test_active_child_of_inactive_parent_rejected(self):
        records = fixture_regions()
        records[1]["is_active"] = False
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("active_child_of_inactive_parent", {issue["code"] for issue in context.exception.issues})

    def test_sido_must_be_root(self):
        records = fixture_regions()
        records[0]["parent_region_id"] = "G1"
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("sido_parent_forbidden", {issue["code"] for issue in context.exception.issues})

    def test_source_code_preserves_leading_zeroes(self):
        records = fixture_regions()
        normalized = validate_region_records(records)
        self.assertEqual(normalized[0]["source_code"], "00011")

    def test_c0_control_characters_rejected_in_region_text_fields(self):
        fields = ("region_id", "name", "region_type", "parent_region_id", "source_system", "source_code")
        for field in fields:
            with self.subTest(field=field):
                records = fixture_regions()
                records[1][field] = records[1][field] + chr(31)
                with self.assertRaises(RegionValidationError) as context:
                    validate_region_records(records)
                self.assertIn(f"{field}_contains_control_character", {issue["code"] for issue in context.exception.issues})

    def test_c1_control_characters_rejected_in_region_text_fields(self):
        fields = ("region_id", "name", "region_type", "parent_region_id", "source_system", "source_code")
        for field in fields:
            with self.subTest(field=field):
                records = fixture_regions()
                records[1][field] = records[1][field] + chr(133)
                with self.assertRaises(RegionValidationError) as context:
                    validate_region_records(records)
                self.assertIn(f"{field}_contains_control_character", {issue["code"] for issue in context.exception.issues})
    def test_records_are_not_mutated(self):
        records = fixture_regions()
        before = copy.deepcopy(records)
        validate_region_records(records)
        self.assertEqual(records, before)

    def test_same_code_is_allowed_across_source_systems(self):
        records = fixture_regions()
        records[2]["source_code"] = records[3]["source_code"]
        self.assertEqual(len(validate_region_records(records)), 7)

    def test_tree_is_independent_of_input_order(self):
        records = fixture_regions()
        self.assertEqual(build_region_tree(records), build_region_tree(list(reversed(records))))

    def test_non_boolean_active_status_rejected(self):
        records = fixture_regions()
        records[1]["is_active"] = "active"
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        self.assertIn("invalid_is_active", {issue["code"] for issue in context.exception.issues})

    def test_non_list_input_rejected(self):
        with self.assertRaises(RegionValidationError):
            validate_region_records({"region_id": "S1"})

    def test_cycle_detection_handles_deep_malformed_hierarchy_without_recursion(self):
        count = 1500
        records = [
            {
                "region_id": f"R{index:04d}",
                "name": f"Region {index}",
                "region_type": "sigungu",
                "parent_region_id": f"R{(index - 1) % count:04d}",
                "source_system": "deep-test",
                "source_code": f"C{index:04d}",
                "is_active": True,
            }
            for index in range(count)
        ]
        with self.assertRaises(RegionValidationError) as context:
            validate_region_records(records)
        issue_codes = {issue["code"] for issue in context.exception.issues}
        self.assertIn("parent_cycle", issue_codes)
        self.assertIn("invalid_parent_type", issue_codes)


if __name__ == "__main__":
    unittest.main()
