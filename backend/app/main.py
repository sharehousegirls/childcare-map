import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .provider import get_facilities, ProviderNotConfigured, ProviderError

app = FastAPI(title="Childcare Map API", version="0.1.0")

# During local development the static frontend may run from file:// or another port.
# Restrict this list before production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def build_facility_meta(records, collected_at=None):
    """Describe source-record dates separately from this API collection timestamp."""
    collected_at = collected_at or datetime.now(timezone.utc)
    if collected_at.tzinfo is None or collected_at.utcoffset() is None:
        raise ValueError("collected_at must be timezone-aware.")
    dates = sorted({
        str(record.get("data_date")).strip()
        for record in records
        if record.get("data_date") is not None and str(record.get("data_date")).strip()
    })
    dated_records = sum(
        1 for record in records
        if record.get("data_date") is not None and str(record.get("data_date")).strip()
    )
    return {
        "collected_at": collected_at.astimezone(timezone.utc).isoformat(),
        "source_data_date": dates[0] if len(dates) == 1 else None,
        "source_data_dates": dates,
        "mixed_source_data_dates": len(dates) > 1,
        "records_with_source_data_date": dated_records,
        "records_without_source_data_date": len(records) - dated_records,
    }


@app.get("/health")
def health():
    configured = bool(os.getenv("API_BASE_URL") and os.getenv("API_SERVICE_KEY"))
    return {"status": "ok", "data_source_configured": configured}


@app.get("/api/facilities")
async def facilities():
    try:
        records = await get_facilities()
        return {
            "source": "official_api",
            "count": len(records),
            "meta": build_facility_meta(records),
            "facilities": records,
        }
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
