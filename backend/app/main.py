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

@app.get("/health")
def health():
    return {"status": "ok", "data_source_configured": bool(__import__('os')..getenv('API_BASE_URL') and __import__('os').getenv('API_SERVICE_KEY'))}


@app.get("/api/facilities")
async def facilities():
    try:
        records = await get_facilities()
        return {"source": "official_api", "count": len(records), "facilities": records}
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
