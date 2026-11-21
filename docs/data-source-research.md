# Data Source Research — Initial Findings

**Research date:** 2026-11-21  
**Status:** Initial investigation; no live API integration performed.

## Findings

### 1. Childcare Disclosure Portal API
- Official portal provides childcare disclosure data via file downloads and REST/SOAP APIs.
- API use requires application and issued key.
- Developer account responses are limited to 50 rows.
- Production account requires a separate review/application and anticipated traffic information; approval is required.
- API use may be restricted for commercial use depending on API policy. Verify the specific endpoint's terms before use.

Official references:
- API overview: https://info.childcare.go.kr/info_html5/oais/introduction/Intro.jsp
- API use policy / account process: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp
- Open API listing: https://info.childcare.go.kr/info/oais/openapi/OpenApiInfoSl.jsp

### 2. Geographic granularity risk
- The portal FAQ states that its Open API can query childcare facility types/counts by city/county/district, but not by administrative dong.
- The FAQ also warns that legal-dong and administrative-dong naming can differ, causing search/matching issues.
- Dong-level analysis therefore needs an additional validated address/geocoding and administrative-boundary mapping strategy; it cannot be assumed from the portal API alone.

Official reference:
- FAQ: https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp

### 3. Waitlist data availability
- The initial research confirms public childcare facility disclosure APIs, but does **not** yet confirm an openly reusable endpoint that provides facility-level, current waitlist counts and age-specific waitlist counts nationwide.
- This is the critical data-source blocker to validate next. Do not substitute facility counts, enrollment, or capacity for waitlist counts.

### 4. General annual statistics
- Ministry of Health and Welfare annual childcare facility data exists through the Public Data Portal, with annual update cadence and reuse terms listed on the dataset page.
- This can be a baseline source for facility-level/region-level context, but it is not a substitute for live waitlist data.

Reference:
- https://www.data.go.kr/data/15128034/fileData.do

## Recommended next steps
1. Inspect API documentation and available fields for facility IDs, location, coordinates, type, capacity/enrollment, and freshness.
2. Determine whether facility-level waitlist and age-specific counts are available from an official public source and whether reuse/redistribution is permitted.
3. If waitlist data is not public or not reusable, stop before scraping authenticated/private child or guardian data; assess lawful alternative public aggregates.
4. Validate data on a small geographic sample, including legal-dong vs administrative-dong mapping.
5. Only after schema, licensing, and source freshness are verified, design ingestion and snapshot tables.

## Current conclusion
Nationwide facility mapping is technically feasible. Nationwide dong-level waitlist analytics remain **unverified** because the public API's documented granularity and available waitlist fields have not yet been confirmed. No real data has been connected and no API credentials have been requested or stored.
