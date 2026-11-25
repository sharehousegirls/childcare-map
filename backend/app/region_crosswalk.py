"""Validate versioned many-to-many legal-dong/admin-dong crosswalk rows.

This is structural validation only. It does not establish geographic correctness,
boundary equivalence, or official provenance.
"""
from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import urlparse

from .regions import RegionValidationError, validate_region_records


class RegionCrosswalkValidationError(ValueError):
    """Raised when crosswalk rows violate the normalized validation contract."""

    def __init__(self, issues: list[dict[str, Any]]):
        self.issues = issues
        super().__init__(
            "Region crosswalk validation failed: "
            + "; ".join(issue["code"] for issue in issues)
        )


def _issue(code: str, row_index: int | None, message: str) -> dict[str, Any]:
    return {"code": code, "row_index": row_index, "message": message}


def _text(
    value: Any,
    field: str,
    row_index: int,
    issues: list[dict[str, Any]],
    max_length: int = 300,
) -> str | None:
    if value is None:
        issues.append(_issue(f"{field}_required", row_index, f"{field} is required."))
        return None
    if not isinstance(value, str):
        issues.append(_issue(f"{field}_must_be_string", row_index, f"{field} must be a string."))
        return None
    if any(127 <= ord(char) <= 159 for char in value):
        issues.append(_issue(f"{field}_contains_control_character", row_index, f"{field} contains a control character."))
        return None
    normalized = value.strip()
    if not normalized:
        issues.append(_issue(f"{field}_required", row_index, f"{field} is required."))
        return None
    if len(normalized) > max_length:
        issues.append(_issue(f"{field}_too_long", row_index, f"{field} exceeds {max_length} characters."))
        return None
    if any(ord(char) < 32 for char in normalized):
        issues.append(_issue(f"{field}_contains_control_character", row_index, f"{field} contains a control character."))
        return None
    return normalized


def _date(
    value: Any,
    field: str,
    row_index: int,
    issues: list[dict[str, Any]],
    *,
    required: bool = True,
) -> str | None:
    if value is None:
        if required:
            issues.append(_issue(f"{field}_required", row_index, f"{field} is required."))
        return None
    if not isinstance(value, str):
        issues.append(_issue(f"{field}_must_be_string", row_index, f"{field} must be a string."))
        return None
    if any(127 <= ord(char) <= 159 for char in value):
        issues.append(_issue(f"{field}_contains_control_character", row_index, f"{field} contains a control character."))
        return None
    normalized = value.strip()
    if any(ord(char) < 32 for char in normalized):
        issues.append(_issue(f"{field}_contains_control_character", row_index, f"{field} contains a control character."))
        return None
    try:
        parsed = date.fromisoformat(normalized)
    except ValueError:
        issues.append(_issue(f"{field}_invalid_date", row_index, f"{field} must be an ISO YYYY-MM-DD date."))
        return None
    if parsed.isoformat() != normalized:
        issues.append(_issue(f"{field}_invalid_date", row_index, f"{field} must use ISO YYYY-MM-DD format."))
        return None
    return normalized


def _https_reference(value: str, row_index: int, issues: list[dict[str, Any]]) -> str | None:
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        parsed = None
        hostname = None
        port = None
    if (
        parsed is None
        or parsed.scheme != "https"
        or not hostname
        or any(char.isspace() for char in hostname)
        or "\\" in hostname
        or (port is not None and not 1 <= port <= 65535)
        or parsed.username is not None
        or parsed.password is not None
    ):
        issues.append(
            _issue(
                "source_reference_invalid_url",
                row_index,
                "source_reference must be a valid HTTPS URL without credentials.",
            )
        )
        return None
    return value


def validate_region_crosswalk(records: Any, regions: Any) -> list[dict[str, Any]]:
    """Normalize legal-dong -> administrative-dong links or raise aggregated issues.

    A legal dong may map to multiple administrative dongs, and an administrative
    dong may receive multiple legal dongs. Effective dates are inclusive. An
    omitted valid_to is an open-ended interval. Repeated links for the same pair
    and version may exist only when their effective intervals do not overlap.
    """
    if not isinstance(records, list):
        raise RegionCrosswalkValidationError(
            [_issue("crosswalk_not_list", None, "Expected a list of crosswalk records.")]
        )

    try:
        normalized_regions = validate_region_records(regions)
    except RegionValidationError as exc:
        raise RegionCrosswalkValidationError(
            [_issue("region_records_invalid", None, str(exc))]
        ) from exc

    regions_by_id = {region["region_id"]: region for region in normalized_regions}
    issues: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []

    for index, raw in enumerate(records):
        if not isinstance(raw, dict):
            issues.append(_issue("invalid_record", index, "Crosswalk row must be an object."))
            continue
        row_issue_start = len(issues)
        legal_id = _text(raw.get("legal_region_id"), "legal_region_id", index, issues, 100)
        admin_id = _text(raw.get("admin_region_id"), "admin_region_id", index, issues, 100)
        version = _text(raw.get("crosswalk_version"), "crosswalk_version", index, issues, 100)
        valid_from = _date(raw.get("valid_from"), "valid_from", index, issues)
        valid_to = _date(raw.get("valid_to"), "valid_to", index, issues, required=False)
        source_system = _text(raw.get("source_system"), "source_system", index, issues, 100)
        reference = _text(raw.get("source_reference"), "source_reference", index, issues, 500)
        if reference is not None:
            reference = _https_reference(reference, index, issues)

        if valid_from and valid_to and date.fromisoformat(valid_to) < date.fromisoformat(valid_from):
            issues.append(
                _issue("valid_to_before_valid_from", index, "valid_to cannot be earlier than valid_from.")
            )

        if legal_id and legal_id not in regions_by_id:
            issues.append(_issue("legal_region_not_found", index, f"Legal region {legal_id} is not in the validated region set."))
        elif legal_id and regions_by_id[legal_id]["region_type"] != "legal_dong":
            issues.append(_issue("legal_region_type_invalid", index, f"Source region {legal_id} must be legal_dong."))

        if admin_id and admin_id not in regions_by_id:
            issues.append(_issue("admin_region_not_found", index, f"Administrative region {admin_id} is not in the validated region set."))
        elif admin_id and regions_by_id[admin_id]["region_type"] != "admin_dong":
            issues.append(_issue("admin_region_type_invalid", index, f"Target region {admin_id} must be admin_dong."))

        if len(issues) == row_issue_start and legal_id and admin_id and version and valid_from and source_system and reference:
            normalized.append(
                (index, {
                    "legal_region_id": legal_id,
                    "admin_region_id": admin_id,
                    "crosswalk_version": version,
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                    "source_system": source_system,
                    "source_reference": reference,
                })
            )

    # Inclusive date intervals: a link ending on a day overlaps another link
    # starting that day. An open end is treated as date.max.
    grouped: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = {}
    for original_index, row in normalized:
        key = (row["crosswalk_version"], row["legal_region_id"], row["admin_region_id"])
        grouped.setdefault(key, []).append((original_index, row))

    for group in grouped.values():
        group.sort(key=lambda item: item[1]["valid_from"])
        previous_end: date | None = None
        for row_index, row in group:
            current_start = date.fromisoformat(row["valid_from"])
            if previous_end is not None and current_start <= previous_end:
                issues.append(
                    _issue(
                        "crosswalk_period_overlap",
                        row_index,
                        "The same pair has overlapping effective dates within a version.",
                    )
                )
            current_end = date.fromisoformat(row["valid_to"]) if row["valid_to"] else date.max
            if previous_end is None or current_end > previous_end:
                previous_end = current_end

    if issues:
        raise RegionCrosswalkValidationError(issues)

    rows = [row for _, row in normalized]
    return sorted(
        rows,
        key=lambda row: (
            row["crosswalk_version"],
            row["legal_region_id"],
            row["admin_region_id"],
            row["valid_from"],
        ),
    )
