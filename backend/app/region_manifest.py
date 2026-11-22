"""Validate provenance and reuse-review metadata before importing region archives."""
from __future__ import annotations

from datetime import date, datetime
import hashlib
import hmac
import re
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

DATASET_KINDS = frozenset({"administrative_dong", "legal_dong", "admin_legal_crosswalk"})
REVIEW_STATUSES = frozenset({"pending", "verified"})
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class RegionSourceManifestError(ValueError):
    """Raised when a region-source manifest is malformed or inconsistent."""

    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__("Region source manifest invalid: " + "; ".join(issues))


def _text(
    value: Any,
    field: str,
    issues: list[str],
    *,
    required: bool = True,
    max_length: int = 500,
) -> str | None:
    if value is None:
        if required:
            issues.append(f"{field}_required")
        return None
    if not isinstance(value, str):
        issues.append(f"{field}_must_be_string")
        return None
    normalized = value.strip()
    if required and not normalized:
        issues.append(f"{field}_required")
        return None
    if len(normalized) > max_length:
        issues.append(f"{field}_too_long")
        return None
    if any(ord(char) < 32 for char in normalized):
        issues.append(f"{field}_contains_control_character")
        return None
    return normalized or None


def _https_url(value: str | None, field: str, issues: list[str]) -> str | None:
    if not value:
        return None
    try:
        parsed = urlparse(value)
    except ValueError:
        issues.append(f"{field}_invalid_url")
        return None
    if parsed.scheme != "https" or not parsed.hostname:
        issues.append(f"{field}_must_be_https_url")
        return None
    if parsed.username is not None or parsed.password is not None:
        issues.append(f"{field}_must_not_contain_credentials")
        return None
    return value


def _iso_date(value: str | None, field: str, issues: list[str]) -> str | None:
    if not value:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        issues.append(f"{field}_invalid_date")
        return None
    if parsed.isoformat() != value:
        issues.append(f"{field}_must_be_yyyy_mm_dd")
        return None
    return value


def _timezone_datetime(value: str | None, field: str, issues: list[str]) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        issues.append(f"{field}_invalid_datetime")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        issues.append(f"{field}_timezone_required")
        return None
    return value


def validate_region_source_manifest(manifest: Any) -> dict[str, Any]:
    """Normalize a manifest and expose fail-closed public/commercial import gates.

    This does not fetch files, verify a digest, authenticate the source, or
    interpret legal terms. Those checks must be performed independently.
    """
    if not isinstance(manifest, dict):
        raise RegionSourceManifestError(["manifest_must_be_object"])
    issues: list[str] = []
    version = manifest.get("manifest_version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        issues.append("manifest_version_unsupported")
    kind = _text(manifest.get("dataset_kind"), "dataset_kind", issues)
    if kind and kind not in DATASET_KINDS:
        issues.append("dataset_kind_unsupported")
    source_system = _text(manifest.get("source_system"), "source_system", issues, max_length=100)
    dataset_id = _text(manifest.get("dataset_id"), "dataset_id", issues, max_length=100)
    source_url = _https_url(_text(manifest.get("source_url"), "source_url", issues), "source_url", issues)
    terms_url = _https_url(_text(manifest.get("terms_url"), "terms_url", issues), "terms_url", issues)
    file_name = _text(manifest.get("file_name"), "file_name", issues, max_length=255)
    if file_name and (file_name in {".", ".."} or "/" in file_name or "\\' in file_name):
        issues.append("file_name_must_be_basename")
    digest = _text(manifest.get("sha256"), "sha256", issues, max_length=64)
    if digest and not SHA256_RE.fullmatch(digest):
        issues.append("sha256_invalid")
    effective_date = _iso_date(
        _text(manifest.get("effective_date"), "effective_date", issues, max_length=10),
        "effective_date", issues,
    )
    downloaded_at = _timezone_datetime(
        _text(manifest.get("downloaded_at"), "downloaded_at", issues, max_length=50),
        "downloaded_at", issues,
    )
    attribution = _text(manifest.get("attribution"), "attribution", issues, max_length=300)
    review_status = _text(manifest.get("reuse_review_status"), "reuse_review_status", issues, max_length=20)
    if review_status and review_status not in REVIEW_STATUSES:
        issues.append("reuse_review_status_unsupported")
    reviewed_at = _iso_date(
        _text(manifest.get("license_reviewed_at"), "license_reviewed_at", issues, required=False, max_length=10),
        "license_reviewed_at", issues,
    )
    redistribution_allowed = manifest.get("redistribution_allowed")
    commercial_use_allowed = manifest.get("commercial_use_allowed")
    if redistribution_allowed is not None and not isinstance(redistribution_allowed, bool):
        issues.append("redistribution_allowed_must_be_boolean_or_null")
        redistribution_allowed = None
    if commercial_use_allowed is not None and not isinstance(commercial_use_allowed, bool):
        issues.append("commercial_use_allowed_must_be_boolean_or_null")
        commercial_use_allowed = None
    if review_status == "verified" and not reviewed_at:
        issues.append("verified_review_date_required")
    if issues:
        raise RegionSourceManifestError(issues)
    public_ready = review_status == "verified" and redistribution_allowed is True
    commercial_ready = public_ready and commercial_use_allowed is True
    return {
        "manifest_version": version,
        "source_system": source_system,
        "dataset_id": dataset_id,
        "dataset_kind": kind,
        "source_url": source_url,
        "terms_url": terms_url,
        "file_name": file_name,
        "sha256": digest.lower(),
        "effective_date": effective_date,
        "downloaded_at": downloaded_at,
        "attribution": attribution,
        "reuse_review_status": review_status,
        "license_reviewed_at": reviewed_at,
        "redistribution_allowed": redistribution_allowed,
        "commercial_use_allowed": commercial_use_allowed,
        "public_import_ready": public_ready,
        "commercial_use_ready": commercial_ready,
    }


def verify_file_sha256(file_path: str | Path, expected_sha256: str) -> bool:
    """Compare a file digest with a manifest value using bounded-memory reads."""
    if not isinstance(expected_sha256, str) or not SHA256_RE.fullmatch(expected_sha256):
        raise ValueError("expected_sha256 must be a 64-character hexadecimal digest")
    digest = hashlib.sha256()
    with Path(file_path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return hmac.compare_digest(digest.hexdigest(), expected_sha256.lower())
