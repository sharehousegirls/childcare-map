"""SQLite storage for normalized childcare facility metadata and immutable snapshots.

This module is intentionally independent from the unverified official API adapter.
It accepts already-normalized facility records and never makes network requests.
"""
from __future__ import annotations

import hashlib
from contextlib import contextmanager
import json
import math
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS ingestion_run (
    run_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_data_date TEXT,
    collected_at TEXT NOT NULL,
    batch_fingerprint TEXT NOT NULL,
    received_count INTEGER NOT NULL DEFAULT 0,
    stored_count INTEGER NOT NULL DEFAULT 0,
    flagged_count INTEGER NOT NULL DEFAULT 0,
    unresolved_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS facility (
    provider_facility_id TEXT PRIMARY KEY,
    name TEXT,
    type TEXT,
    status TEXT,
    address TEXT,
    sido TEXT,
    sigungu TEXT,
    latitude REAL,
    longitude REAL,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS facility_snapshot (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES ingestion_run(run_id),
    provider_facility_id TEXT NOT NULL REFERENCES facility(provider_facility_id),
    source_data_date TEXT,
    collected_at TEXT NOT NULL,
    capacity INTEGER,
    enrolled INTEGER,
    wait_0 INTEGER,
    wait_1 INTEGER,
    wait_2 INTEGER,
    wait_3 INTEGER,
    wait_4 INTEGER,
    wait_5 INTEGER,
    wait_6_plus INTEGER,
    wait_total_reported INTEGER,
    wait_total_derived INTEGER,
    wait_total_consistent INTEGER CHECK (wait_total_consistent IN (0, 1) OR wait_total_consistent IS NULL),
    quality_flags_json TEXT NOT NULL,
    UNIQUE (run_id, provider_facility_id)
);
CREATE INDEX IF NOT EXISTS idx_snapshot_facility_collected
    ON facility_snapshot(provider_facility_id, collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_snapshot_source_date
    ON facility_snapshot(source_data_date);
CREATE TRIGGER IF NOT EXISTS facility_snapshot_append_only
BEFORE UPDATE ON facility_snapshot
BEGIN
    SELECT RAISE(ABORT, 'facility snapshots are append-only');
END;
CREATE TABLE IF NOT EXISTS unresolved_record (
    unresolved_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES ingestion_run(run_id),
    record_index INTEGER NOT NULL,
    provider_facility_id TEXT,
    source_data_date TEXT,
    normalized_record_json TEXT NOT NULL,
    quality_flags_json TEXT NOT NULL,
    UNIQUE (run_id, record_index)
);
CREATE INDEX IF NOT EXISTS idx_unresolved_run ON unresolved_record(run_id);
"""

NORMALIZED_FIELDS = (
    "facility_id", "name", "type", "status", "address", "sido", "sigungu",
    "capacity", "enrolled", "latitude", "longitude", "data_date",
    "wait_0", "wait_1", "wait_2", "wait_3", "wait_4", "wait_5",
    "wait_6_plus", "wait_total",
)
COUNT_FIELDS = ("capacity", "enrolled", "wait_0", "wait_1", "wait_2", "wait_3", "wait_4", "wait_5", "wait_6_plus", "wait_total")
AGE_FIELDS = ("wait_0", "wait_1", "wait_2", "wait_3", "wait_4", "wait_5", "wait_6_plus")
TEXT_FIELDS = ("name", "type", "status", "address", "sido", "sigungu")
COORD_FIELDS = ("latitude", "longitude")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _safe_number(value: Any, field: str, flags: list[str], *, integer: bool = False) -> int | float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        flags.append(f"invalid_numeric:{field}")
        return None
    try:
        number = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        flags.append(f"invalid_numeric:{field}")
        return None
    if not math.isfinite(number) or (integer and (number < 0 or not number.is_integer())):
        flags.append(f"invalid_numeric:{field}")
        return None
    return int(number) if integer else number


def _normalize_record(record: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    flags: list[str] = []
    normalized = {field: record.get(field) for field in NORMALIZED_FIELDS}
    normalized["facility_id"] = _text(normalized["facility_id"])
    for field in TEXT_FIELDS:
        normalized[field] = _text(normalized[field])
    normalized["data_date"] = _text(normalized["data_date"])
    for field in COUNT_FIELDS:
        normalized[field] = _safe_number(normalized[field], field, flags, integer=True)
    for field in COORD_FIELDS:
        normalized[field] = _safe_number(normalized[field], field, flags)
    # Stored coordinates must be geographic latitude/longitude, not projected x/y.
    if normalized["latitude"] is not None and not -90 <= normalized["latitude"] <= 90:
        normalized["latitude"] = None
        flags.append("coordinate_out_of_range:latitude")
    if normalized["longitude"] is not None and not -180 <= normalized["longitude"] <= 180:
        normalized["longitude"] = None
        flags.append("coordinate_out_of_range:longitude")
    if (normalized["latitude"] is None) != (normalized["longitude"] is None):
        flags.append("coordinate_pair_incomplete")
    # Provider adapters may expose the display total derived from age buckets.
    # Persist the explicit source total separately instead of mislabeling a
    # derived value as provider-reported.
    if "wait_total_reported" in record:
        normalized["wait_total"] = _safe_number(
            record.get("wait_total_reported"), "wait_total", flags, integer=True
        )
    provider_flags = record.get("quality_flags")
    if isinstance(provider_flags, list):
        flags.extend(flag.strip() for flag in provider_flags if isinstance(flag, str) and flag.strip())
    if not normalized["facility_id"]:
        flags.append("facility_id_missing")
    if not normalized["data_date"]:
        flags.append("source_data_date_missing")
    age_values = [normalized[field] for field in AGE_FIELDS]
    derived_total = sum(age_values) if all(value is not None for value in age_values) else None
    if derived_total is None:
        flags.append("wait_age_buckets_incomplete")
    official_total = normalized["wait_total"]
    consistent = None if official_total is None or derived_total is None else official_total == derived_total
    if consistent is False:
        flags.append("wait_total_mismatch")
    normalized["wait_total_derived"] = derived_total
    normalized["wait_total_consistent"] = consistent
    return normalized, flags


def _connect(db_path: str | Path) -> sqlite3.Connection:
    path = str(db_path)
    if path == ":memory:":
        raise ValueError("Snapshot storage requires a file-backed SQLite path.")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def _database(db_path: str | Path):
    connection = _connect(db_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(db_path: str | Path) -> None:
    """Create storage tables and indexes. Safe to call repeatedly."""
    with _database(db_path) as connection:
        connection.executescript(SCHEMA)


def _record_summary(connection: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT run_id, source, received_count, stored_count, flagged_count, unresolved_count "
        "FROM ingestion_run WHERE run_id = ?", (run_id,)
    ).fetchone()
    if row is None:
        raise ValueError("Ingestion run not found.")
    return dict(row)


def ingest_snapshot_batch(
    db_path: str | Path,
    records: list[dict[str, Any]],
    *,
    source: str,
    source_data_date: str | None = None,
    collected_at: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Store normalized records in one transaction; repeat calls with the same run ID are idempotent.

    Missing/duplicate facility identifiers are kept in an unresolved audit table, not discarded.
    A duplicate ID within one batch is stored once as a snapshot; subsequent duplicate rows
    are retained as unresolved records with a diagnostic flag.
    """
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ValueError("records must be a list of dictionaries.")
    source = _text(source)
    if not source:
        raise ValueError("source must be a non-empty string.")
    run_id = _text(run_id) or str(uuid.uuid4())
    collected_at = _text(collected_at) or _utc_now()
    batch_date = _text(source_data_date)

    normalized_rows = []
    for record in records:
        normalized, flags = _normalize_record(record)
        if not normalized["data_date"] and batch_date:
            normalized["data_date"] = batch_date
            flags = [flag for flag in flags if flag != "source_data_date_missing"]
        normalized_rows.append((normalized, flags))
    id_counts: dict[str, int] = {}
    for normalized, _ in normalized_rows:
        facility_id = normalized["facility_id"]
        if facility_id:
            id_counts[facility_id] = id_counts.get(facility_id, 0) + 1
    for normalized, flags in normalized_rows:
        facility_id = normalized["facility_id"]
        if facility_id and id_counts.get(facility_id, 0) > 1 and "facility_id_duplicate_in_batch" not in flags:
            flags.append("facility_id_duplicate_in_batch")

    fingerprint_payload = {
        "source": source,
        "source_data_date": batch_date,
        "records": [normalized for normalized, _ in normalized_rows],
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    initialize_database(db_path)
    with _database(db_path) as connection:
        existing = connection.execute(
            "SELECT batch_fingerprint FROM ingestion_run WHERE run_id = ?", (run_id,)
        ).fetchone()
        if existing:
            if existing["batch_fingerprint"] != fingerprint:
                raise ValueError("run_id already exists with different batch content.")
            return _record_summary(connection, run_id)

        connection.execute(
            "INSERT INTO ingestion_run (run_id, source, source_data_date, collected_at, batch_fingerprint, received_count) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, source, batch_date, collected_at, fingerprint, len(records)),
        )
        stored_ids: set[str] = set()
        flagged_count = 0
        unresolved_count = 0
        for index, (row, flags) in enumerate(normalized_rows):
            facility_id = row["facility_id"]
            is_duplicate = bool(facility_id and id_counts.get(facility_id, 0) > 1 and facility_id in stored_ids)
            if is_duplicate and "duplicate_record_after_first" not in flags:
                flags.append("duplicate_record_after_first")
            flagged_count += bool(flags)
            if not facility_id or is_duplicate:
                unresolved_count += 1
                unresolved_json = {field: row.get(field) for field in NORMALIZED_FIELDS}
                unresolved_json.update({
                    "wait_total_derived": row.get("wait_total_derived"),
                    "wait_total_consistent": row.get("wait_total_consistent"),
                })
                connection.execute(
                    "INSERT INTO unresolved_record (run_id, record_index, provider_facility_id, source_data_date, normalized_record_json, quality_flags_json) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (run_id, index, facility_id, row["data_date"],
                     json.dumps(unresolved_json, ensure_ascii=False, sort_keys=True),
                     json.dumps(sorted(set(flags)), ensure_ascii=False)),
                )
                continue

            stored_ids.add(facility_id)
            connection.execute(
                "INSERT INTO facility (provider_facility_id, name, type, status, address, sido, sigungu, latitude, longitude, first_seen_at, last_seen_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(provider_facility_id) DO UPDATE SET "
                "name=excluded.name, type=excluded.type, status=excluded.status, address=excluded.address, "
                "sido=excluded.sido, sigungu=excluded.sigungu, latitude=excluded.latitude, longitude=excluded.longitude, "
                "last_seen_at=excluded.last_seen_at",
                (facility_id, row["name"], row["type"], row["status"], row["address"], row["sido"], row["sigungu"],
                 row["latitude"], row["longitude"], collected_at, collected_at),
            )
            connection.execute(
                "INSERT INTO facility_snapshot (run_id, provider_facility_id, source_data_date, collected_at, capacity, enrolled, "
                "wait_0, wait_1, wait_2, wait_3, wait_4, wait_5, wait_6_plus, wait_total_reported, wait_total_derived, "
                "wait_total_consistent, quality_flags_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, facility_id, row["data_date"], collected_at, row["capacity"], row["enrolled"],
                 row["wait_0"], row["wait_1"], row["wait_2"], row["wait_3"], row["wait_4"], row["wait_5"], row["wait_6_plus"],
                 row["wait_total"], row["wait_total_derived"],
                 None if row["wait_total_consistent"] is None else int(row["wait_total_consistent"]),
                 json.dumps(sorted(set(flags)), ensure_ascii=False)),
            )
        stored_count = connection.execute(
            "SELECT COUNT(*) FROM facility_snapshot WHERE run_id = ?", (run_id,)
        ).fetchone()[0]
        connection.execute(
            "UPDATE ingestion_run SET stored_count=?, flagged_count=?, unresolved_count=? WHERE run_id=?",
            (stored_count, flagged_count, unresolved_count, run_id),
        )
        return _record_summary(connection, run_id)
