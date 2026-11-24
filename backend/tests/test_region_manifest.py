import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.region_manifest import (
    RegionSourceManifestError,
    validate_region_source_manifest,
    verify_file_sha256,
    evaluate_region_archive_preflight,
)


def manifest(**overrides):
    data = {
        "manifest_version": 1,
        "source_system": "MOIS",
        "dataset_id": "KiKmix.20261111",
        "dataset_kind": "admin_legal_crosswalk",
        "source_url": "https://www.mois.go.kr/source.zip",
        "terms_url": "https://www.mois.go.kr/terms",
        "file_name": "KiKmix.20261111.zip",
        "sha256": "a" * 64,
        "effective_date": "2026-10-23",
        "downloaded_at": "2026-11-22T08:00:00Z",
        "attribution": "Source: Ministry of the Interior and Safety",
        "reuse_review_status": "pending",
        "license_reviewed_at": None,
        "redistribution_allowed": None,
        "commercial_use_allowed": None,
    }
    data.update(overrides)
    return data


class RegionManifestTests(unittest.TestCase):
    def test_pending_review_valid_but_not_import_ready(self):
        result = validate_region_source_manifest(manifest())
        self.assertFalse(result["public_import_ready"])
        self.assertFalse(result["commercial_use_ready"])
        self.assertEqual(result["sha256"], "a" * 64)

    def test_verified_redistribution_allowed_unlocks_public_import(self):
        result = validate_region_source_manifest(manifest(
            reuse_review_status="verified",
            license_reviewed_at="2026-11-22",
            redistribution_allowed=True,
            commercial_use_allowed=True,
        ))
        self.assertTrue(result["public_import_ready"])
        self.assertTrue(result["commercial_use_ready"])

    def test_noncommercial_permission_does_not_unlock_commercial_use(self):
        result = validate_region_source_manifest(manifest(
            reuse_review_status="verified",
            license_reviewed_at="2026-11-22",
            redistribution_allowed=True,
            commercial_use_allowed=False,
        ))
        self.assertTrue(result["public_import_ready"])
        self.assertFalse(result["commercial_use_ready"])

    def test_commercial_readiness_requires_redistribution(self):
        result = validate_region_source_manifest(manifest(
            reuse_review_status="verified",
            license_reviewed_at="2026-11-22",
            redistribution_allowed=False,
            commercial_use_allowed=True,
        ))
        self.assertFalse(result["public_import_ready"])
        self.assertFalse(result["commercial_use_ready"])

    def test_verified_without_review_date_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(
                reuse_review_status="verified",
                redistribution_allowed=True,
            ))
        self.assertIn("verified_review_date_required", ctx.exception.issues)

    def test_unsupported_version_rejected(self):
        with self.assertRaises(RegionSourceManifestError):
            validate_region_source_manifest(manifest(manifest_version=2))

    def test_float_version_rejected(self):
        with self.assertRaises(RegionSourceManifestError):
            validate_region_source_manifest(manifest(manifest_version=1.0))

    def test_unknown_dataset_kind_rejected(self):
        with self.assertRaises(RegionSourceManifestError):
            validate_region_source_manifest(manifest(dataset_kind="facility"))

    def test_source_url_rejects_whitespace_hostname(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(source_url="https://bad host/source.zip"))
        self.assertIn("source_url_invalid_url", ctx.exception.issues)

    def test_terms_url_rejects_out_of_range_port(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(terms_url="https://mois.go.kr:99999/terms"))
        self.assertIn("terms_url_invalid_url", ctx.exception.issues)

    def test_http_source_url_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(source_url="http://example.test/file.zip"))
        self.assertIn("source_url_must_be_https_url", ctx.exception.issues)

    def test_http_terms_url_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(terms_url="http://example.test/terms"))
        self.assertIn("terms_url_must_be_https_url", ctx.exception.issues)

    def test_url_credentials_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(
                source_url="https://user:secret@example.test/file.zip"))
        self.assertIn("source_url_must_not_contain_credentials", ctx.exception.issues)

    def test_malformed_url_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(source_url="https://[broken"))
        self.assertIn("source_url_invalid_url", ctx.exception.issues)

    def test_path_traversal_filename_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(file_name="../secret.zip"))
        self.assertIn("file_name_must_be_basename", ctx.exception.issues)

    def test_windows_path_filename_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(file_name="folder\\archive.zip"))
        self.assertIn("file_name_must_be_basename", ctx.exception.issues)

    def test_invalid_digest_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(sha256="not-a-hash"))
        self.assertIn("sha256_invalid", ctx.exception.issues)

    def test_invalid_effective_date_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(effective_date="2026-02-30"))
        self.assertIn("effective_date_invalid_date", ctx.exception.issues)

    def test_timezone_required_for_download_timestamp(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(
                downloaded_at="2026-11-22T08:00:00"))
        self.assertIn("downloaded_at_timezone_required", ctx.exception.issues)

    def test_bad_permission_types_rejected(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(manifest(redistribution_allowed="yes"))
        self.assertIn("redistribution_allowed_must_be_boolean_or_null", ctx.exception.issues)

    def test_manifest_must_be_object(self):
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest([])
        self.assertEqual(ctx.exception.issues, ["manifest_must_be_object"])

    def test_required_metadata_missing_rejected(self):
        data = manifest()
        del data["source_system"]
        with self.assertRaises(RegionSourceManifestError) as ctx:
            validate_region_source_manifest(data)
        self.assertIn("source_system_required", ctx.exception.issues)

    def test_digest_normalized_to_lowercase(self):
        result = validate_region_source_manifest(manifest(sha256="B" * 64))
        self.assertEqual(result["sha256"], "b" * 64)

    def test_sha256_file_verification_matches_and_mismatches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "archive.bin"
            path.write_bytes(b"verified test archive")
            expected = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertTrue(verify_file_sha256(path, expected))
            self.assertFalse(verify_file_sha256(path, "b" * 64))

    def test_sha256_verifier_rejects_malformed_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "archive.bin"
            path.write_bytes(b"test")
            with self.assertRaises(ValueError):
                verify_file_sha256(path, "bad")




    def test_preflight_hash_match_does_not_bypass_pending_reuse_review(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "jscode20261111.zip"
            payload = b"archive preflight test"
            path.write_bytes(payload)
            data = manifest(file_name=path.name, sha256=hashlib.sha256(payload).hexdigest())
            result = evaluate_region_archive_preflight(data, path)
            self.assertTrue(result["archive_integrity_verified"])
            self.assertIsNone(result["archive_integrity_issue"])
            self.assertFalse(result["public_archive_import_ready"])
            self.assertFalse(result["commercial_archive_import_ready"])

    def test_preflight_requires_reuse_review_and_integrity_for_public_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "jscode20261111.zip"
            payload = b"archive preflight test"
            path.write_bytes(payload)
            data = manifest(
                file_name=path.name,
                sha256=hashlib.sha256(payload).hexdigest(),
                reuse_review_status="verified",
                license_reviewed_at="2026-11-24",
                redistribution_allowed=True,
                commercial_use_allowed=True,
            )
            result = evaluate_region_archive_preflight(data, path)
            self.assertTrue(result["public_archive_import_ready"])
            self.assertTrue(result["commercial_archive_import_ready"])

    def test_preflight_digest_mismatch_blocks_both_import_gates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "jscode20261111.zip"
            path.write_bytes(b"actual archive")
            data = manifest(
                file_name=path.name,
                sha256=hashlib.sha256(b"expected archive").hexdigest(),
                reuse_review_status="verified",
                license_reviewed_at="2026-11-24",
                redistribution_allowed=True,
                commercial_use_allowed=True,
            )
            result = evaluate_region_archive_preflight(data, path)
            self.assertFalse(result["archive_integrity_verified"])
            self.assertEqual(result["archive_integrity_issue"], "archive_sha256_mismatch")
            self.assertFalse(result["public_archive_import_ready"])
            self.assertFalse(result["commercial_archive_import_ready"])

    def test_preflight_filename_mismatch_blocks_integrity_check(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "actual.zip"
            payload = b"archive preflight test"
            path.write_bytes(payload)
            data = manifest(
                file_name="expected.zip",
                sha256=hashlib.sha256(payload).hexdigest(),
                reuse_review_status="verified",
                license_reviewed_at="2026-11-24",
                redistribution_allowed=True,
                commercial_use_allowed=True,
            )
            result = evaluate_region_archive_preflight(data, path)
            self.assertFalse(result["archive_integrity_verified"])
            self.assertEqual(result["archive_integrity_issue"], "archive_filename_mismatch")
            self.assertFalse(result["public_archive_import_ready"])

    def test_preflight_missing_archive_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "jscode20261111.zip"
            data = manifest(
                file_name=path.name,
                reuse_review_status="verified",
                license_reviewed_at="2026-11-24",
                redistribution_allowed=True,
                commercial_use_allowed=True,
            )
            result = evaluate_region_archive_preflight(data, path)
            self.assertFalse(result["archive_integrity_verified"])
            self.assertEqual(result["archive_integrity_issue"], "archive_file_not_found")
            self.assertFalse(result["public_archive_import_ready"])
            self.assertFalse(result["commercial_archive_import_ready"])

    def test_preflight_keeps_commercial_gate_closed_when_permission_denied(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "jscode20261111.zip"
            payload = b"archive preflight test"
            path.write_bytes(payload)
            data = manifest(
                file_name=path.name,
                sha256=hashlib.sha256(payload).hexdigest(),
                reuse_review_status="verified",
                license_reviewed_at="2026-11-24",
                redistribution_allowed=True,
                commercial_use_allowed=False,
            )
            result = evaluate_region_archive_preflight(data, path)
            self.assertTrue(result["archive_integrity_verified"])
            self.assertTrue(result["public_archive_import_ready"])
            self.assertFalse(result["commercial_archive_import_ready"])


if __name__ == "__main__":
    unittest.main()
