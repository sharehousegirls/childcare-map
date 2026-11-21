# Real-data integration plan

## Confirmed source candidate
Official Childcare Disclosure Portal Open API: https://info.childcare.go.kr/info/oais/openapi/OpenApiInfoSl.jsp
The official portal requires signup/login, a development API application/review, and issued credentials. The development account has a 50-row response limit; production access requires a separate application/review and anticipated traffic registration. Review official use policy and restrictions before commercial reuse.

## Potential data fields
Facility code/name/type/status, address, capacity/enrollment, coordinates, age-based waitlist counts (0–6+), total waitlist count, and data date are listed in a catalog entry for the SSIS childcare-facility API. Exact official endpoint and response field names must be confirmed against official documentation/sample response before implementation.

## Integration blockers
- API credentials not yet issued.
- Exact API endpoint and request parameter names not verified.
- Official sample response not yet obtained; field mapping is unverified.
- Data reuse/redistribution and commercial-use terms require checking.

## Work completed
- Added FastAPI backend scaffold with configurable endpoint, API key kept server-side, JSON/XML parsing, normalized field mapping, and health/data routes.
- Existing demo remains available; it must not be represented as live data.

## Next actions
1. Apply for development API access at the official portal and obtain key.
2. Confirm exact API service/operation URL and query parameter names from official docs.
3. Capture a small sample response (up to development account limit) and configure mappings.
4. Test response handling and validate fields, missing values, IDs, waitlist sums, timestamps.
5. Replace demo mode only after successful source validation; then plan production account approval.
