# 어린이집 지도 (Childcare Map)

지역별 어린이집 입소 대기 정보 비교 서비스.

## 현재 상태
- 반응형 정적 웹 프로토타입: 지역 카드, 시설 검색, 유형/대기 0 필터
- 기존 화면은 **가상 데모 데이터**를 사용합니다. 실제 데이터 연결 성공 전에는 실제 현황으로 간주하지 마세요.
- FastAPI backend scaffold가 backend/에 추가되었습니다.
- Frontend는 backend /api/facilities 응답이 정상이고 source=official_api일 때 실제 데이터로 전환합니다. 연결 실패 시 가상 데이터로 돌아가며 화면 상단 상태 표시로 구분합니다.
- Backend API errors are sanitized to avoid exposing service keys in request URLs; field mapping configuration is validated.
- 15 backend unit tests passed in an isolated harness using the exact provider and test blobs from commit ec14fb6a938820cb1185ada6e3e26101fa3201e4 (Git blob SHAs matched); GitHub Actions also passed for that commit. Direct repository-checkout execution remains unconfirmed because GitHub DNS is unavailable in this environment; see the security review.

## Frontend 실행
- 단순히 index.html을 file://로 열면 backend fetch가 브라우저 보안/CORS에 의해 제한될 수 있습니다.
- VS Code Live Server 등으로 index.html을 localhost에서 실행하세요.

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

## Data sources and status
- **Nationwide waitlist candidate:** SSIS 한국사회보장정보원_어린이집별 기본정보 조회 (15101154). Official catalog lists age waitlist buckets 0–5, 6+ and total: https://www.data.go.kr/data/15101154/openapi.do. XML, real-time metadata, and unrestricted reuse are listed; request schema/sample and service-specific terms remain unverified.
- **Existing Daegu application:** 한국사회보장정보원_대구광역시 어린이집 정보조회 (15101186), submitted for development account on 2026-11-21. Catalog lists facility metadata (name/code/address/contact/homepage/capacity), not waitlist counts: https://www.data.go.kr/data/15101186/openapi.do. Review/credentials pending.
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
- Security review and test evidence: docs/backend-security-review-2026-11-21.md
- Draft data model: docs/data-model-draft.md

## Next milestones
1. Apply for development API access for nationwide waitlist dataset 15101154; review the existing Daegu application separately.
2. Obtain official service guide/sample and verify URL, request parameters, response schema, pagination, coordinate system, error envelope and row limit.
3. Validate source terms, data date, facility IDs and waitlist totals.
4. Establish canonical region/facility identifiers and versioned region mapping; see draft model.
5. Design snapshot/history and idempotent ingestion.
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
