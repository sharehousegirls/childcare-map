"""Configurable official API adapter. Verify endpoint/schema before configuring."""
import json
import math
import os
import xml.etree.ElementTree as ET
from typing import Any
import httpx

class ProviderNotConfigured(RuntimeError):
    pass

class ProviderError(RuntimeError):
    pass

FIELD_ALIASES = {
    "facility_id": ["facility_id", "childcare_code", "어린이집코드", "어린이집 코드", "crcode", "CRCODE"],
    "name": ["name", "facility_name", "어린이집명", "crname", "CRNAME"],
    "type": ["type", "facility_type", "어린이집유형", "어린이집유형구분", "crtname", "CRTNAME"],
    "status": ["status", "operating_status", "운영현황", "crstatusname", "CRSTATUSNAME"],
    "address": ["address", "full_address", "상세주소", "주소", "craddr", "CRADDR"],
    "sido": ["sido", "시도명", "시도"],
    "sigungu": ["sigungu", "시군구명", "시군구"],
    "capacity": ["capacity", "정원", "crcapacity", "CRCAPACITY"],
    "enrolled": ["enrolled", "현원", "아동수-총계", "아동수총계"],
    "latitude": ["latitude", "위도", "시설 위도(좌표값)"],
    "longitude": ["longitude", "경도", "시설 경도(좌표값)"],
    "wait_0": ["wait_0", "입소대기아동수 0세", "입소대기아동수-0세"],
    "wait_1": ["wait_1", "입소대기아동수 1세", "입소대기아동수-1세"],
    "wait_2": ["wait_2", "입소대기아동수 2세", "입소대기아동수-2세"],
    "wait_3": ["wait_3", "입소대기아동수 3세", "입소대기아동수-3세"],
    "wait_4": ["wait_4", "입소대기아동수 4세", "입소대기아동수-4세"],
    "wait_5": ["wait_5", "입소대기아동수 5세", "입소대기아동수-5세"],
    "wait_6_plus": ["wait_6_plus", "입소대기아동수 6세 이상", "입소대기아동수-6세 이상"],
    "wait_total": ["wait_total", "입소대기아동수-총계", "입소대기아동수 총계"],
    "data_date": ["data_date", "데이터기준일자", "기준일", "데이터수집일"],
}
NUMERIC_FIELDS = {"capacity", "enrolled", "latitude", "longitude", "wait_0", "wait_1", "wait_2", "wait_3", "wait_4", "wait_5", "wait_6_plus", "wait_total"}

def _parse_xml(node: ET.Element) -> Any:
    children = list(node)
    if not children:
        return node.text
    result = {}
    for child in children:
        val = _parse_xml(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(val)
        else:
            result[child.tag] = val
    return result

def _looks_like_record(payload: dict) -> bool:
    known = set(sum(FIELD_ALIASES.values(), []))
    return bool(set(payload.keys()) & known)

def _flatten_records(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        if payload and all(isinstance(x, dict) for x in payload):
            return payload
        for x in payload:
            found = _flatten_records(x)
            if found:
                return found
    elif isinstance(payload, dict):
        if _looks_like_record(payload):
            return [payload]
        for key in ("facilities", "items", "item", "rows", "data", "list"):
            if key in payload:
                found = _flatten_records(payload[key])
                if found:
                    return found
        for value in payload.values():
            found = _flatten_records(value)
            if found:
                return found
    return []

def _get_value(record: dict, field: str, field_map: dict) -> Any:
    configured = field_map.get(field)
    candidates = [configured] if configured else FIELD_ALIASES.get(field, [])
    for candidate in candidates:
        if candidate and candidate in record and record[candidate] not in (None, ""):
            return record[candidate]
    return None

def _validate_field_map(field_map: Any) -> dict:
    if not isinstance(field_map, dict):
        raise ProviderError("API_FIELD_MAP must be a JSON object.")
    for normalized, provider_field in field_map.items():
        if normalized not in FIELD_ALIASES or not isinstance(provider_field, str) or not provider_field.strip():
            raise ProviderError("API_FIELD_MAP must map known normalized fields to non-empty provider field names.")
    return field_map

def _safe_http_error(exc: httpx.HTTPError) -> str:
    # Never return the raw HTTP exception: it may contain the request URL and API key.
    if isinstance(exc, httpx.HTTPStatusError):
        return f"Official API returned HTTP {exc.response.status_code}."
    if isinstance(exc, httpx.TimeoutException):
        return "Official API request timed out."
    return "Official API connection failed. Verify endpoint and network configuration."

def _number(value, floating=False):
    if value in (None, "", "-", "--"):
        return None
    try:
        n = float(str(value).replace(",", "").strip())
        if not math.isfinite(n):
            return None
        if floating:
            return n
        if n < 0 or not n.is_integer():
            return None
        return int(n)
    except (TypeError, ValueError):
        return None

def _sum_age_waits(age_values):
    return sum(age_values) if all(value is not None for value in age_values) else None

async def get_facilities() -> list[dict]:
    base_url = os.getenv("API_BASE_URL", "").strip()
    api_key = os.getenv("API_SERVICE_KEY", "").strip()
    if not base_url or not api_key:
        raise ProviderNotConfigured("Official API is not configured. Set API_BASE_URL and API_SERVICE_KEY in backend/.env after obtaining the API key.")
    key_param = os.getenv("API_KEY_PARAM", "serviceKey").strip()
    if not key_param:
        raise ProviderError("API_KEY_PARAM must be a non-empty parameter name.")
    try:
        extra = json.loads(os.getenv("API_EXTRA_PARAMS", "{}"))
        field_map = _validate_field_map(json.loads(os.getenv("API_FIELD_MAP", "{}")))
        if not isinstance(extra, dict):
            raise ValueError("API_EXTRA_PARAMS must be a JSON object")
    except ValueError as exc:
        raise ProviderError(f"Invalid environment JSON configuration: {exc}")
    params = dict(extra)
    params[key_param] = api_key
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        # Sanitize: request URL may contain the service key.
        raise ProviderError(_safe_http_error(exc)) from None
    try:
        ctype = response.headers.get("content-type", "").lower()
        if "json" in ctype or response.text.lstrip().startswith(("{", "[")):
            payload = response.json()
        else:
            payload = _parse_xml(ET.fromstring(response.text))
    except Exception as exc:
        raise ProviderError(f"Could not parse official API response: {exc}")
    records = _flatten_records(payload)
    if not records:
        raise ProviderError("No facility records found. Inspect a sample official response and configure field mapping.")
    normalized = []
    for record in records:
        row = {field: _get_value(record, field, field_map) for field in FIELD_ALIASES}
        for field in NUMERIC_FIELDS:
            row[field] = _number(row[field], floating=field in {"latitude", "longitude"})
        age_values = [row[f"wait_{age}"] for age in range(6)] + [row["wait_6_plus"]]
        if row["wait_total"] is None and all(v is not None for v in age_values):
            row["wait_total"] = sum(age_values)
        row["wait_age_sum"] = _sum_age_waits(age_values)
        if row.get("facility_id") or row.get("name"):
            normalized.append(row)
    return normalized
