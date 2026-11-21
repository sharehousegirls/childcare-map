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


## Application and validation status (2026-11-21)
- Development API application submitted for Daegu only; review/approval pending. Credentials have not been issued.
- The application screen lists REST/XML and an API URL, but this is not yet confirmed by a successful request. Do not configure the provider or infer the response schema from the application form alone.
- The official service specification file shown on the application screen must be reviewed, along with a sample response, after access is approved.
- Before connecting, confirm: exact operation URL and required parameters; pagination and 50-row development limit; error envelope/status codes; facility ID stability; missing-value semantics; data-date semantics; terms and redistribution/commercial-use permission.

## Acceptance checklist for first API test
- [ ] Key remains only in local backend environment or approved secret storage; never in browser or repository.
- [ ] One successful request with a redacted sample response saved for mapping review.
- [ ] Provider errors and empty/error payloads are distinguished from valid empty datasets.
- [ ] Normalized records have stable IDs or are explicitly flagged when IDs are missing.
- [ ] Waitlist values are non-negative integers; blanks remain null; total is derived from age buckets only when every bucket is present.
- [ ] Coordinates and administrative region fields are validated before map display.
- [ ] Source and date are shown; date is not guessed when absent.
- [ ] Terms/reuse permission are documented before public display or redistribution.
- [ ] Unit tests run and results recorded before declaring the connection successful.
