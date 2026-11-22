import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.region_crosswalk import RegionCrosswalkValidationError, validate_region_crosswalk


def fixture_regions():
    return [
        {"region_id": "S1", "name": "서울", "region_type": "sido", "source_system": "test-admin", "source_code": "00011", "is_active": True},
        {"region_id": "G1", "name": "종로구", "region_type": "sigungu", "parent_region_id": "S1", "source_system": "test-admin", "source_code": "11110", "is_active": True},
        {"region_id": "D1", "name": "청운효자동", "region_type": "admin_dong", "parent_region_id": "G1", "source_system": "test-admin", "source_code": "D-01", "is_active": True},
        {"region_id": "D2", "name": "사직동", "region_type": "admin_dong", "parent_region_id": "G1", "source_system": "test-admin", "source_code": "D-02", "is_active": True},
        {"region_id": "L1", "name": "청운동", "region_type": "legal_dong", "parent_region_id": "G1", "source_system": "test-legal", "source_code": "L-01", "is_active": True},
        {"region_id": "L2", "name": "사직동", "region_type": "legal_dong", "parent_region_id": "G1", "source_system": "test-legal", "source_code": "L-02", "is_active": True},
    ]


def crosswalk_row(legal="L1", admin="D1", start="2026-01-01", end=None, version="v1"):
    return {
        "legal_region_id": legal,
        "admin_region_id": admin,
        "crosswalk_version": version,
        "valid_from": start,
        "valid_to": end,
        "source_system": "MOIS",
        "source_reference": "https://www.mois.go.kr/region-codes",
    }


class RegionCrosswalkTests(unittest.TestCase):
    def test_many_to_many_relationships_are_allowed(self):
        rows = [
            crosswalk_row("L1", "D1"),
            crosswalk_row("L1", "D2"),
            crosswalk_row("L2", "D1"),
            crosswalk_row("L2", "D2"),
        ]
        result = validate_region_crosswalk(rows, fixture_regions())
        pairs = {(row["legal_region_id"], row["admin_region_id"]) for row in result}
        self.assertEqual(len(result), 4)
        self.assertEqual(pairs, {("L1", "D1"), ("L1", "D2"), ("L2", "D1"), ("L2", "D2")})

    def test_empty_crosswalk_is_valid(self):
        self.assertEqual(validate_region_crosswalk([], fixture_regions()), [])

    def test_non_list_crosswalk_rejected(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk({}, fixture_regions())
        self.assertIn("crosswalk_not_list", {issue["code"] for issue in ctx.exception.issues})

    def test_invalid_region_records_are_reported(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([crosswalk_row()], [{"region_id": "bad"}])
        self.assertIn("region_records_invalid", {issue["code"] for issue in ctx.exception.issues})

    def test_missing_legal_region_rejected(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([crosswalk_row(legal="missing")], fixture_regions())
        self.assertIn("legal_region_not_found", {issue["code"] for issue in ctx.exception.issues})

    def test_missing_admin_region_rejected(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([crosswalk_row(admin="missing")], fixture_regions())
        self.assertIn("admin_region_not_found", {issue["code"] for issue in ctx.exception.issues})

    def test_source_must_be_legal_dong(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([crosswalk_row(legal="D1")], fixture_regions())
        self.assertIn("legal_region_type_invalid", {issue["code"] for issue in ctx.exception.issues})

    def test_target_must_be_administrative_dong(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([crosswalk_row(admin="L1")], fixture_regions())
        self.assertIn("admin_region_type_invalid", {issue["code"] for issue in ctx.exception.issues})

    def test_invalid_start_date_rejected(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([crosswalk_row(start="2026-1-1")], fixture_regions())
        self.assertIn("valid_from_invalid_date", {issue["code"] for issue in ctx.exception.issues})

    def test_end_before_start_rejected(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([crosswalk_row(start="2026-02-01", end="2026-01-31")], fixture_regions())
        self.assertIn("valid_to_before_valid_from", {issue["code"] for issue in ctx.exception.issues})

    def test_inclusive_overlap_rejected(self):
        rows = [
            crosswalk_row(start="2026-01-01", end="2026-06-30"),
            crosswalk_row(start="2026-06-30", end="2026-12-31"),
        ]
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk(rows, fixture_regions())
        self.assertIn("crosswalk_period_overlap", {issue["code"] for issue in ctx.exception.issues})

    def test_non_overlapping_periods_allowed(self):
        rows = [
            crosswalk_row(start="2026-01-01", end="2026-06-30"),
            crosswalk_row(start="2026-07-01", end=None),
        ]
        result = validate_region_crosswalk(rows, fixture_regions())
        self.assertEqual(len(result), 2)

    def test_source_reference_must_be_https_without_credentials(self):
        row = crosswalk_row()
        row["source_reference"] = "https://user:pass@mois.go.kr/codes"
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([row], fixture_regions())
        self.assertIn("source_reference_invalid_url", {issue["code"] for issue in ctx.exception.issues})

    def test_rows_are_not_mutated(self):
        rows = [crosswalk_row("L2", "D2"), crosswalk_row("L1", "D1")]
        before = copy.deepcopy(rows)
        validate_region_crosswalk(rows, fixture_regions())
        self.assertEqual(rows, before)

    def test_output_is_deterministically_sorted(self):
        rows = [crosswalk_row("L2", "D2"), crosswalk_row("L1", "D1")]
        result = validate_region_crosswalk(rows, fixture_regions())
        self.assertEqual([(row["legal_region_id"], row["admin_region_id"]) for row in result], [("L1", "D1"), ("L2", "D2")])


    def test_missing_fields_report_required_codes(self):
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk([{}], fixture_regions())
        codes = {issue["code"] for issue in ctx.exception.issues}
        self.assertIn("legal_region_id_required", codes)
        self.assertIn("admin_region_id_required", codes)
        self.assertIn("crosswalk_version_required", codes)
        self.assertIn("valid_from_required", codes)
        self.assertIn("source_system_required", codes)
        self.assertIn("source_reference_required", codes)

    def test_overlap_issue_uses_original_row_index(self):
        rows = [
            {"bad": "record"},
            crosswalk_row(start="2026-01-01", end="2026-06-30"),
            crosswalk_row(start="2026-06-30", end="2026-12-31"),
        ]
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk(rows, fixture_regions())
        overlap = next(issue for issue in ctx.exception.issues if issue["code"] == "crosswalk_period_overlap")
        self.assertEqual(overlap["row_index"], 2)

    def test_overlapping_periods_in_different_versions_allowed(self):
        rows = [
            crosswalk_row(start="2026-01-01", end="2026-12-31", version="v1"),
            crosswalk_row(start="2026-01-01", end="2026-12-31", version="v2"),
        ]
        result = validate_region_crosswalk(rows, fixture_regions())
        self.assertEqual(len(result), 2)

    def test_open_ended_period_overlaps_later_period(self):
        rows = [
            crosswalk_row(start="2026-01-01", end=None),
            crosswalk_row(start="2027-01-01", end="2027-12-31"),
        ]
        with self.assertRaises(RegionCrosswalkValidationError) as ctx:
            validate_region_crosswalk(rows, fixture_regions())
        self.assertIn("crosswalk_period_overlap", {issue["code"] for issue in ctx.exception.issues})


if __name__ == "__main__":
    unittest.main()
