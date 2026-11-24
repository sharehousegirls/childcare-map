# 어린이집 지도 (Childcare Map)

지역별 어린이집 입소 대기 정보 비교 서비스.

## 현재 상태
- 반응형 정적 웹 프로토타입: 지역 카드, 시설 검색, 유형/대기 0 필터
- 기존 화면은 **가상 데모 데이터**를 사용합니다. 실제 데이터 연결 성공 전에는 실제 현황으로 간주하지 마세요.
- FastAPI backend scaffold가 backend/에 추가되었습니다.
- SQLite 스냅샷 저장 기반(backend/app/storage.py)이 추가됐습니다. 시설 메타데이터, append-only 스냅샷, 수집 배치 요약, 검토 대상 레코드를 저장하지만 아직 API와 연결하지 않았습니다.
- 브라우저에서 검색 조건 저장/불러오기/삭제 기능을 제공합니다. 저장 데이터는 해당 브라우저의 localStorage에만 보관됩니다.
- 지역 선택 목록은 현재 상위 지역 표시명별로 묶어 보여주며, 하위 옵션은 한국어 정렬합니다. 공식 행정구역 코드 기반 탐색이 아니라 화면 편의용 그룹입니다.
- Live regional summaries keep missing wait counts unknown, show partial totals and known/missing facility coverage; zero-wait only counts explicit zero values.
- Frontend는 backend /api/facilities 응답이 정상이고 source=official_api일 때 실제 데이터로 전환합니다. 연결 실패 시 가상 데이터로 돌아가며 화면 상단 상태 표시로 구분합니다.
- Backend API errors are sanitized to avoid exposing service keys in request URLs; field mapping configuration is validated.
- Provider and SQLite ingestion independently validate geographic coordinate ranges; a partial latitude/longitude pair is flagged and two missing coordinates remain unknown. These safeguards do not verify CRS or coordinate accuracy.
- 15 backend unit tests passed in an isolated harness using the exact provider and test blobs from commit ec14fb6a938820cb1181ada6e3e26101fa3201e4 (Git blob SHAs matched); GitHub Actions also passed for that commit. Direct local checkout execution remains unconfirmed because GitHub DNS is unavailable in this environment; however, the repository's GitHub Actions run #48 passed all 26 tests for commit 396e30762bb3776eadeddd1715b0574bf0049ce4: https://github.com/sharehousegirls/childcare-map/actions/runs/44947857967. See the security review.


**PASS — GitHub Actions run #217:** backend unit-test, JavaScript syntax-check, and frontend test steps completed successfully for commit `1f5cc34adc07e0a26949d67bbb36848a2b9d3640`. The connector confirms the run-level conclusion is success but does not expose exact test-count output. https://github.com/sharehousegirls/childcare-map/actions/runs/45281684930
## Frontend 실행
- 단순히 index.html을 file://로 열면 backend fetch가 브라우저 보안/CORS에 의해 제한될 수 있습니다.
- VS Code Live Server 등으로 index.html을 localhost에서 실행하세요.

## 관심 지역 저장
- 현재 선택한 개별 지역을 저장/불러오기/삭제할 수 있습니다. `전체 지역`은 저장할 수 없습니다.
- 최대 20개 지역을 브라우저 `localStorage`에 저장하며, 중복 지역은 허용하지 않습니다.
- 현재 저장 값은 지역명 문자열이며 공식 행정구역 코드가 아닙니다. 공식 코드 도입 시 ID 기반 저장과 마이그레이션이 필요합니다.
- 저장된 관심 지역의 현재 요약(시설 수, 대기 합계, 시설당 평균, 대기 0건 시설, 대기 확인률)을 비교합니다. 데모에서는 모든 숫자를 예시로 표시하고 시설별 대기 원자료가 없어 확인률은 제공하지 않습니다. 실제 데이터에서는 미확인 시설을 구분하고 부분 합계를 명시합니다.

## 저장 지역 비교
- 저장한 관심 지역의 현재 요약을 비교 카드로 표시합니다. 지역 이름이 현재 데이터에서 사라졌거나 중복되어 매칭이 모호하면 수치를 추정하지 않고 비교 불가 상태를 표시합니다.
- 실제 데이터의 대기 합계는 모든 시설이 확인된 경우에만 완전 합계로 표시하며, 그 외에는 확인된 시설 기준 부분 합계로 구분합니다. 시설별 대기 수는 동일 아동이 여러 시설에 중복될 수 있어 고유 아동 수를 의미하지 않습니다.
- 비교는 현재 브라우저에 저장된 지역 이름과 현재 데이터에 대한 비교입니다. 과거 스냅샷/추세 비교, 서버 동기화 및 공식 지역 코드 기반 매칭은 아직 지원하지 않습니다.
- 브라우저 데이터 삭제 또는 저장소 제한 시 저장 내용이 사라지거나 저장되지 않을 수 있습니다. 계정/서버/기기 간 동기화는 제공하지 않습니다.

## 상위 지역 그룹 선택

지역 선택 목록은 기존 상위 지역 표시명(`district`)을 기준으로 그룹화하고, 하위 옵션을 한국어로 정렬합니다. 상위 지역명이 지역 이름에 반복되는 경우 표시 텍스트에서만 접두어를 줄이며, 선택 값과 저장 기능에는 전체 지역명 문자열을 유지합니다.

이는 현재 데이터에 대한 화면 표시 그룹일 뿐 공식 행정구역 코드나 전국 계층 구조가 아닙니다. 공식 코드 import와 재사용 조건 검토 후 코드 기반 시도→시군구→읍면동 계층 및 저장 지역 마이그레이션을 구현할 예정입니다.

## 검색 조건 저장
- 현재 선택 지역, 시설명 검색어, 시설 유형, 대기 0명 필터를 저장/불러오기/삭제할 수 있습니다.
- 최대 20개까지 브라우저 localStorage에 저장하며 계정/서버 동기화는 제공하지 않습니다.
- 브라우저 데이터 삭제 또는 저장소 제한 시 저장 내용이 사라지거나 저장되지 않을 수 있습니다.
- 저장 조건은 데모/실제 데이터 상태와 무관하게 필터만 기억합니다. 실제 데이터의 정확성이나 가용성을 보장하지 않습니다.

## Frontend 검증
저장 검색/관심 지역 모듈 및 앱 스크립트 문법 확인:

    node --check app.js
    node --check saved-searches.mjs
    node --check saved-regions.mjs
    node --check regional-summary.mjs
    node --check saved-facilities.mjs
    node --check region-selector.mjs
    node --check saved-region-comparison.mjs
    node --test tests/*.test.mjs

**PASS — GitHub Actions run #167 (coordinate validation follow-up):** 108 backend tests, 40 frontend tests (8 regional summary, 11 saved-region, 9 saved-search, 12 saved-facility), and all JavaScript syntax checks passed. Provider and SQLite storage-boundary tests cover out-of-range coordinates, incomplete coordinate pairs, and the no-coordinate case. https://github.com/sharehousegirls/childcare-map/actions/runs/45112984412

관심 지역 기능 상세: `docs/saved-regions-implementation-2026-11-22.md`

## Backend 설정
backend/README.md 참조. 아래 명령은 저장소 루트에서 시작합니다.
1. Python 3.11+ 설치
2. cd backend
3. python -m venv .venv
4. 가상환경 활성화 (Windows PowerShell: .\.venv\Scripts\Activate.ps1; macOS/Linux: source .venv/bin/activate)
5. pip install -r requirements.txt
6. .env.example을 .env로 복사 (Windows PowerShell: Copy-Item .env.example .env; macOS/Linux: cp .env.example .env)
7. 공식 API 키, endpoint, 필수 query parameter와 응답 field mapping을 확인 후 입력
8. uvicorn app.main:app --reload --port 8000
9. http://127.0.0.1:8000/health 및 /api/facilities 확인

## Region source manifest

`backend/app/region_manifest.py` validates source provenance, archive metadata, dates, HTTPS source/terms URLs, SHA-256 format, and reuse-review flags before a future region-code importer can proceed. It exposes separate public-import and commercial-use gates; pending review or unknown permission never unlocks either gate. The local SHA-256 verifier streams files in 1 MiB chunks. It does not download or parse the official archive, and it does not replace a human reuse-terms review.

Implementation and manifest example: `docs/region-source-manifest-2026-11-22.md`.

Normalized region records reject embedded C0/C1 control characters in identifiers, names, type labels, parent IDs, and source metadata. This is input-quality validation only; official region codes and source files remain unimported. See `docs/region-code-control-character-validation-2026-11-24.md`.

## Region granularity and coordinate constraints

The Childcare Information Disclosure Portal FAQ (reviewed 2026-11-22) says its regional facility type/count query supports 시·군·구, not dong-level query (FAQ 12). This is scoped to that query and does not rule out deriving dong aggregates from facility-level records; any such aggregation requires validated facility coordinates, a reviewed/versioned boundary source, deduplication, and coverage disclosure. The FAQ reports EPSG:5181 TM coordinates for its childcare map data (FAQ 13), so verify the exact API field/CRS and transform before mapping. It also warns that legal-dong and administrative-dong lookup may differ (FAQ 10).

Official FAQ: https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp  
Review note and acceptance criteria: `docs/region-granularity-coordinate-review-2026-11-22.md`

## Data sources and status

**Official catalog rechecked 2026-11-24:** dataset 15101154 lists facility-level waitlist counts by age 0–5, age 6+, and total, plus facility metadata, as XML/LINK, free, real-time catalog metadata, and unrestricted reuse. Exact operation/request/response schema and service-specific commercial/redistribution conditions are still unverified; see `docs/official-api-catalog-recheck-2026-11-24.md`.
- **Nationwide waitlist candidate:** SSIS 한국사회보장정보원_어린이집별 기본정보 조회 (15101154). Official catalog lists age waitlist buckets 0–5, 6+ and total: https://www.data.go.kr/data/15101154/openapi.do. XML, real-time metadata, and unrestricted reuse are listed; request schema/sample and service-specific terms remain unverified.
- **Existing Daegu application:** 한국사회보장정보원_대구광역시 어린이집 정보조회 (15101186), submitted for development account on 2026-11-21. Catalog lists facility metadata (name/code/address/contact/homepage/capacity), not waitlist counts: https://www.data.go.kr/data/15101186/openapi.do. Review/credentials pending.
- **Administrative region codes:** As checked 2026-11-23, the MOIS notice posted 2026-11-18 lists `jscode20261111.zip` and its layout for the 2026-10-23 effective changes. The archive's filename suffix is not the effective date. The attachment notice does not show a reuse license; do not assume terms from the separate legal-dong API catalog apply to this ZIP. Reuse review remains pending. See `docs/region-code-validation-2026-11-22.md`.
- **MOIS legal-dong code API:** dataset 15077871 is legal-dong data, not administrative-dong: https://www.data.go.kr/data/15077871/openapi.do.
- **Regional aggregate comparator:** Incheon Namdong waitlist dataset 15119081 is annual district-level aggregate, not facility-level/nationwide: https://www.data.go.kr/data/15119081/fileData.do.
- Catalog-level unrestricted reuse is not blanket commercial clearance. Verify service-specific API terms, attribution, caching, redistribution, and commercial/advertising conditions before launch or monetization. Portal API policy limits development account to 50 rows and separately reviews operation access.
- Credentials must stay server-side and never be committed.
- Missing waitlist values are unknown, not zero. Waitlist/application counts are not necessarily unique children; no admission-date prediction.
- Real-time catalog metadata is not a row-level freshness guarantee; preserve provider data date and retrieval timestamp separately.
- Dong-level mapping and map coordinates require verified source granularity, boundary provenance, and CRS/axis-order validation.

## Official references
- Nationwide waitlist candidate: https://www.data.go.kr/data/15101154/openapi.do
- Daegu facility metadata: https://www.data.go.kr/data/15101186/openapi.do
- Incheon Namdong aggregate: https://www.data.go.kr/data/15119081/fileData.do
- Childcare API policy: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp
- Childcare API development guide: https://info.childcare.go.kr/info_html5/oais/guide/Development.jsp
- Childcare API overview: https://info.childcare.go.kr/info_html5/oais/introduction/Intro.jsp
- Childcare FAQ (region granularity/coordinates): https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp
- MOIS administrative/legal-dong changes (current source starting point): https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=131063
- MOIS code-change board: https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardList.do?bbsId=BBSMSTR_000000000052
- Statistics Korea/SIGIS administrative-region classification guide: https://sgis.mods.go.kr/html/attachFiles/%ED%95%9C%EA%B5%AD%ED%96%89%EC%A0%95%EA%B5%AC%EC%97%AD%EB%B6%84%EB%A5%98%20%ED%95%B4%EC%84%A4%EC%84%9C%282021.12.28.%29.pdf
- Region validator implementation and source review: `docs/region-code-validation-2026-11-22.md`
- Security review and test evidence: docs/backend-security-review-2026-11-21.md
- Draft/implemented data model: docs/data-model-draft.md
- SQLite storage scaffold and limitations: backend/README.md
- Snapshot-storage implementation notes: docs/storage-implementation-2026-11-22.md
- Saved-search feature notes: docs/saved-search-implementation-2026-11-22.md
- Current status, blockers, verification and next priorities: docs/project-status.md

## Next milestones
1. Apply for development API access for nationwide waitlist dataset 15101154; review the existing Daegu application separately.
2. Obtain official service guide/sample and verify URL, request parameters, response schema, pagination, coordinate system, error envelope and row limit.
3. Validate source terms, data date, facility IDs and waitlist totals.
4. Validate current MOIS region-code files, establish canonical identifiers, and implement a separate versioned M:N administrative-dong/legal-dong crosswalk; see `docs/region-code-validation-2026-11-22.md`.
5. Integrate the SQLite snapshot-storage scaffold with verified API ingestion, then add migrations and failure/retry audit.
6. Nationwide ingestion, quality checks, map and regional/facility views.
7. Saved regions/facilities/filters/comparisons and historical trends.
8. SEO, accessibility, security and deploy-readiness review (no deployment without user approval).

## Project principles
- Free first; no ads initially.
- Lock-in first: saved regions, comparisons, snapshots/history and filters should create return value.
- Source and date labels, data quality, and clear unknown values.
- No admission-date predictions.
- Defer violation/complaint/administrative history until all other features are complete and ask for review then.
- Do not deploy without user approval.

## 관심 시설 저장
- 시설 카드에서 고유 ID가 확인된 시설을 관심 시설로 저장하고, 목록에서 정확한 ID로 다시 찾거나 삭제할 수 있습니다.
- 최대 50개까지 브라우저 `localStorage`에 저장하며 계정/서버/기기 동기화는 제공하지 않습니다.
- 현재 데모 시설에는 명시적인 가상 ID를 사용합니다. 실 API 데이터에 시설 ID가 없으면 저장 버튼이 비활성화됩니다.
- 저장된 시설을 불러올 때 ID가 현재 데이터에서 확인되지 않으면 이름이 비슷한 시설로 임의 대체하지 않습니다.
- 구현: `saved-facilities.mjs`; 테스트: `tests/saved-facilities.test.mjs`

관심 시설 기능 상세: `docs/saved-facilities-implementation-2026-11-22.md`

## API source-date and collection-time metadata

The backend `GET /api/facilities` response includes additive `meta` fields for the UTC collection timestamp, provider source-date coverage, distinct source dates, and whether records have mixed dates. The UI displays source-date status and collection time separately. This timestamp is not a freshness guarantee; the official API's update frequency and date semantics still require verification. See `docs/api-freshness-metadata-2026-11-22.md`.


## Versioned region crosswalk validation scaffold

A backend-only validator now checks normalized legal-dong to administrative-dong links, allowing many-to-many relationships while enforcing region-type references, source provenance, strict effective dates and non-overlapping periods per pair/version. It is synthetic-data-only and does not import official rows or validate spatial boundaries.

See [crosswalk validation notes](docs/region-crosswalk-validation-2026-11-23.md).

## Nationwide waitlist API schema verification (2026-11-23)

The official catalog for dataset 15101154 lists facility identifiers, location, capacity/enrollment, provider data date, and waitlist buckets for ages 0–5, 6+, and total. The listed fields are catalog descriptions only; the exact XML tags, request/response envelope, pagination, null semantics, and coordinate CRS/axis order have not been verified from the authenticated service specification or a redacted sample. No live API request was made.

The official API guide says the service specification is available from the API detail page's technical documents and includes URLs, operations, request/response definitions, and examples. The development account is limited to 50 rows; the operating account requires separate approval and an expected-traffic estimate, and has a 12-month validity period.

See [schema verification and integration acceptance gate](docs/api-schema-verification-2026-11-23.md) before configuring live integration.


**Latest verification — GitHub Actions run #201:** 116 backend tests, 40 frontend tests, and all JavaScript syntax checks passed, including the record-level source-date ratio regression test. Earlier provider-quality safeguards are documented in [provider data-quality notes](docs/provider-data-quality-2026-11-23.md). https://github.com/sharehousegirls/childcare-map/actions/runs/45196215022

## Source-date parseability diagnostics (2026-11-23)

The facilities API metadata adds strict date parseability counts and the earliest/latest valid `YYYY-MM-DD` source dates. Non-empty source-date values in other formats or with invalid calendar dates are retained in the raw distinct-date list and counted as unparseable; blank values remain missing. These diagnostics do not define freshness or a stale threshold. Source-date semantics and the provider update cadence must be verified before any freshness SLA is configured.

See [API freshness metadata](docs/api-freshness-metadata-2026-11-22.md).


Source-date coverage and parseability ratios are **record-level**, not unique-facility metrics. Duplicate facility IDs are not deduplicated by these calculations and should be reviewed separately before interpreting coverage as facility-level. See the detailed ratio semantics in `docs/api-freshness-metadata-2026-11-22.md`.


## Frontend source-date quality details

When live backend metadata is present, the status panel reports source-date coverage and parseability using row counts, including separate missing and unparseable counts. In demo mode it explicitly states that no real date diagnostics are available. Counts are per response row (not unique facilities), and these ratios do not establish freshness. See `docs/frontend-data-quality-display-2026-11-24.md`.


## Frontend source-date freshness display

When live API metadata is present, the frontend displays the newest valid source-record date, a date range when records have mixed dates, and the elapsed calendar days between the latest source date and the API collection timestamp. It flags invalid or inconsistent date metadata. Time elapsed is computed only from a calendar-valid, timezone-qualified collection timestamp with valid clock and offset values. This is descriptive only: it does not define a freshness threshold, SLA, or provider update cadence. Collection time is not the source-record date. In demo mode, the UI explicitly states that real freshness information is unavailable.


See [frontend source-date freshness display](docs/frontend-data-freshness-display-2026-11-24.md).

## Official data-source recheck — 2026-11-24

The official catalog page for nationwide facility-level dataset 15101154 was rechecked. It lists XML/LINK delivery, free access, an unrestricted-reuse catalog label, real-time update metadata, and facility-level waitlist counts for ages 0–5, 6+, and total. These are catalog descriptions; the exact service schema, response, pagination, date semantics, and service-specific reuse conditions are not yet verified. See [data-source research](docs/data-source-research.md).
