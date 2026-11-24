# Official childcare API account and schema gate — 2026-11-25

## Scope

This is a documentation-only recheck of the public nationwide waitlist dataset catalog and the official Childcare Information Disclosure Portal's Open API workflow. No credentials were used, no live API request was made, and no schema mapping was changed.

## Evidence checked

- Nationwide candidate dataset 15101154: https://www.data.go.kr/data/15101154/openapi.do
- Official Childcare Portal Open API list: https://info.childcare.go.kr/info/oais/openapi/OpenApiSlL.jsp
- Official development guide: https://info.childcare.go.kr/info/oais/guide/Development.jsp
- Official account/use policy: https://info.childcare.go.kr/info/oais/introduction/Policy.jsp

## What the public pages confirm

### Catalog-level dataset description

The public catalog describes facility metadata and waitlist counts for ages 0–5, age 6+, and a total. It labels the dataset XML/LINK, free, real-time catalog metadata, and unrestricted reuse.

These are catalog descriptions. They do **not** verify the exact XML element/tag names, operation, response nesting, paging, ID stability, blanks/nulls, coordinate reference system, or a working endpoint. The catalog's reuse label is not a blanket conclusion about service-specific commercial use, caching, attribution, or redistribution.

### Official portal service list and technical specification

The official portal's public Open API list displays **어린이집별 기본정보 조회** and **전국 어린이집 정보 조회** as Open API services. The public list does not expose enough detail here to confirm the exact operation/schema correspondence to catalog ID 15101154.

The official development guide states that a developer must register and sign in, request a development account, and complete its review/key issuance before building and testing against the service. The service detail's technical document is the authoritative next schema artifact. It is described as including service information, provider information, technology, service URL, operations, request/response specifications, and examples.

Guide: https://info.childcare.go.kr/info/oais/guide/Development.jsp

### Official account policy

The public policy page confirms:

- **Development account:** testing stage; responses are limited to 50 rows; no stated time limit.
- **Operating account:** a separate application/review step for actual service operation; expected traffic must be entered.
- **Operating-account term:** 12 months, with renewal application needed for continued use.
- **Key issuance:** issued per service account after approval.
- **Usage restrictions:** the guide describes restriction for commercial use of APIs that do not permit commercial use, excessive traffic causing load, and improper/private or illegal use.

Policy: https://info.childcare.go.kr/info/oais/introduction/Policy.jsp

This policy is a portal-wide workflow description. It does not independently resolve the terms of dataset 15101154.

## Gate before live integration

1. Confirm the user is registered/logged in to the official portal and the development account application is approved for the exact service.
2. Download the exact service technical document from the service-detail page and record its version/date if available.
3. Obtain a redacted successful response sample; remove keys and personal information.
4. Confirm the service/operation is the waitlist dataset (15101154), rather than a facility-metadata-only service.
5. Verify URL, operation, parameters, response envelope, pagination, row limits, errors, exact field names, ID semantics, date semantics, null/blank behavior, total vs age-bucket meaning, and coordinate CRS/axis order.
6. Review the exact service's attribution, display, caching, commercial-use, and redistribution conditions.
7. Keep credentials server-side. Do not commit or share API keys in chat/email.
8. Run an offline mapping validation with the redacted sample before enabling any live request or public real-data display.

## Current blocker and work that can continue

The required account approval, service specification, redacted response, and service-specific terms remain unavailable in this repository context. The existing API-approval request has already been emailed; this recheck does not send a duplicate request.

Until evidence is supplied, keep live ingestion and public real-data display disabled. Independent work can continue on UI, saved-region/search behavior, validation, tests, documentation, and fictional demo data.

## Verification result

- Official catalog opened: **PASS** (catalog-level field groups and metadata only).
- Official portal API list opened: **PASS** (service names visible; exact schema/operation not established).
- Official development guide opened: **PASS** (account workflow and specification contents verified).
- Official policy opened: **PASS** (development/operating account limits and key workflow verified).
- Exact dataset-to-portal operation/schema mapping: **BLOCKED**.
- Live API request and credential validation: **NOT RUN**.
- License/commercial/cache/redistribution clearance for this exact service: **BLOCKED**.
