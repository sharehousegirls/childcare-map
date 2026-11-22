"""Validate and assemble normalized administrative-region records.

No official codes or datasets are embedded here. Callers must map verified source
rows into this schema and preserve source codes as strings.
"""
from __future__ import annotations

from typing import Any

REGION_TYPES = frozenset({"sido", "sigungu", "admin_dong", "legal_dong", "eup", "myeon", "ri"})
REGION_TYPE_ORDER = ("sido", "sigungu", "admin_dong", "legal_dong", "eup", "myeon", "ri")
PARENT_TYPES = {
    "sido": frozenset(),
    "sigungu": frozenset({"sido"}),
    "admin_dong": frozenset({"sigungu"}),
    "legal_dong": frozenset({"sigungu"}),
    "eup": frozenset({"sigungu"}),
    "myeon": frozenset({"sigungu"}),
    "ri": frozenset({"eup", "myeon"}),
}

class RegionValidationError(ValueError):
    """Raised when normalized region rows violate the initial hierarchy contract."""

def _issue(code: str, region_id: str | None, message: str) -> dict[str, str | None]:
    return {"code": code, "region_id": region_id, "message": message}

def _optional_text(value: Any, field: str, region_id: str | None, issues: list[dict]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        issues.append(_issue(f"invalid_{field}", region_id, f"{field} must be a string."))
        return None
    value = value.strip()
    if not value:
        return None
    if len(value) > 100:
        issues.append(_issue(f"{field}_too_long", region_id, f"{field} exceeds 100 characters."))
        return None
    return value

def validate_region_records(records: Any) -> list[dict[str, Any]]:
    """Return normalized records or raise with aggregated structural issues.

    Records are not mutated. Official source-code formats/lengths are deliberately
    not assumed; source code strings are retained exactly after trimming.
    """
    if not isinstance(records, list):
        error = RegionValidationError("regions_not_list")
        error.issues = [_issue("regions_not_list", None, "Expected a list of region records.")]
        raise error

    issues: list[dict[str, str | None]] = []
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(records):
        row_issue_start = len(issues)
        if not isinstance(raw, dict):
            issues.append(_issue("invalid_record", None, f"Record {index} must be an object."))
            continue
        region_id = _optional_text(raw.get("region_id"), "region_id", None, issues)
        name = _optional_text(raw.get("name"), "name", region_id, issues)
        region_type = _optional_text(raw.get("region_type"), "region_type", region_id, issues)
        parent_id = _optional_text(raw.get("parent_region_id"), "parent_region_id", region_id, issues)
        source_system = _optional_text(raw.get("source_system"), "source_system", region_id, issues)
        source_code = _optional_text(raw.get("source_code"), "source_code", region_id, issues)
        is_active = raw.get("is_active")
        if is_active is not None and not isinstance(is_active, bool):
            issues.append(_issue("invalid_is_active", region_id, "is_active must be true, false, or null."))
            is_active = None
        if not region_id:
            issues.append(_issue("region_id_required", None, f"Record {index} requires region_id."))
        if not name:
            issues.append(_issue("name_required", region_id, f"Record {index} requires name."))
        if region_type not in REGION_TYPES:
            issues.append(_issue("invalid_region_type", region_id, f"Unknown region_type: {region_type!r}."))
        if (source_system is None) != (source_code is None):
            issues.append(_issue("source_identity_incomplete", region_id, "source_system and source_code must be supplied together."))
        if len(issues) == row_issue_start and region_id and name and region_type in REGION_TYPES:
            normalized.append({
                "region_id": region_id,
                "name": name,
                "region_type": region_type,
                "parent_region_id": parent_id,
                "source_system": source_system,
                "source_code": source_code,
                "is_active": is_active,
            })

    by_id: dict[str, dict[str, Any]] = {}
    for record in normalized:
        region_id = record["region_id"]
        if region_id in by_id:
            issues.append(_issue("duplicate_region_id", region_id, f"Duplicate region_id: {region_id}."))
        else:
            by_id[region_id] = record

    source_keys: dict[tuple[str, str], str] = {}
    for record in normalized:
        system, code = record["source_system"], record["source_code"]
        if system is not None and code is not None:
            key = (system, code)
            if key in source_keys:
                issues.append(_issue("duplicate_source_code", record["region_id"], f"Source code {code} duplicates region {source_keys[key]} in {system}."))
            else:
                source_keys[key] = record["region_id"]

    for record in normalized:
        region_id, region_type, parent_id = record["region_id"], record["region_type"], record["parent_region_id"]
        if region_type == "sido":
            if parent_id is not None:
                issues.append(_issue("sido_parent_forbidden", region_id, "sido records must be roots."))
        elif parent_id is None:
            issues.append(_issue("parent_required", region_id, f"{region_type} requires a parent."))
        elif parent_id not in by_id:
            issues.append(_issue("parent_not_found", region_id, f"Parent region {parent_id} was not found."))
        else:
            parent = by_id[parent_id]
            if parent["region_type"] not in PARENT_TYPES[region_type]:
                issues.append(_issue("invalid_parent_type", region_id, f"{region_type} cannot have parent type {parent['region_type']}."))
            if record["is_active"] is True and parent["is_active"] is False:
                issues.append(_issue("active_child_of_inactive_parent", region_id, "An active region cannot have an inactive parent."))

    # Detect cycles iteratively so malformed deep input cannot exhaust Python's
    # recursion limit. Every traversal is finalized before the next one begins.
    state: dict[str, int] = {}  # 0/unseen, 1/visiting, 2/complete
    cycle_ids: set[str] = set()
    for start_id in by_id:
        if state.get(start_id) == 2:
            continue
        path: list[str] = []
        position: dict[str, int] = {}
        current_id: str | None = start_id
        while current_id in by_id:
            current_state = state.get(current_id, 0)
            if current_state == 2:
                break
            if current_state == 1:
                cycle_start = position.get(current_id)
                if cycle_start is not None:
                    cycle_ids.update(path[cycle_start:])
                break
            state[current_id] = 1
            position[current_id] = len(path)
            path.append(current_id)
            current_id = by_id[current_id].get("parent_region_id")
        for region_id in path:
            state[region_id] = 2
    for region_id in sorted(cycle_ids):
        issues.append(_issue("parent_cycle", region_id, "Region parent links contain a cycle."))

    if issues:
        error = RegionValidationError("Region validation failed: " + "; ".join(issue["code"] for issue in issues))
        error.issues = issues
        raise error
    return normalized

def build_region_tree(records: Any) -> list[dict[str, Any]]:
    """Build deterministic root/child lists from validated records."""
    normalized = validate_region_records(records)
    nodes = {record["region_id"]: {**record, "children": []} for record in normalized}
    roots: list[dict[str, Any]] = []
    for node in nodes.values():
        parent_id = node["parent_region_id"]
        if parent_id is None:
            roots.append(node)
        else:
            nodes[parent_id]["children"].append(node)
    order = {region_type: index for index, region_type in enumerate(REGION_TYPE_ORDER)}
    pending = list(roots)
    while pending:
        items = pending.pop()
        items.sort(key=lambda item: (order[item["region_type"]], item["name"], item["region_id"]))
        pending.extend(item["children"] for item in items)
    return roots
