# 어린이집 지도 (Childcare Map)

지역별 어린이집 입소 대기 정보 비교 서비스.

## 현재 상태
- 반응형 정적 웹 프로토타입: 지역 카드, 시설 검색, 유형/대기 0 필터
- 기존 화면은 **가상 데모 데이터**를 사용합니다. 실제 데이터 연결 성공 전에는 실제 현황으로 간주하지 마세요.
- FastAPI backend scaffold가 `backend/`에 추가되었습니다.
- Frontend는 backend `/api/facilities` 응답이 정상이고 `source=official_api`일 때 실제 데이터로 전환합니다. 연결 실패 시 가상 데이터로 돌아가며 화면 상단 상태 표시로 구분합니다.

## Frontend 실행
- 단순히 `index.html`을 `file://`로 열면 backend fetch가 브라우저 보안/CORS에 의해 제한될 수 있습니다.
- VS Code Live Server 등으로 `index.html`을 localhost에서 실행하세요.

## Backend 설정
`backend/README.md` 참조.
1. Python 3.11+ 설치 후 backend 디렉터리에서 가상환경 생성
2. `pip install -r requirements.txt`
3. `.env.example`을 `.env`로 복사
4. 공식 API 키, endpoint, 필수 query parameter와 응답 field mapping을 확인 후 입력
5. `uvicorn app.main:app --reload --port 8000`
6. `http://127.0.0.1:8000/health` 및 `/api/facilities` 확인

## Data integration status
- 공식 어린이집정보공개포털 Open API를 데이터 소스로 조사했습니다.
- API 개발계정 신청/심의 및 인증키 발급이 필요합니다.
- 정확한 endpoint/요청 parameters/response field mapping은 공식 문서와 샘플 응답으로 확인해야 합니다.
- 인증키는 frontend 코드에 넣거나 GitHub에 commit하지 않습니다.
- 대기 값이 누락된 시설을 대기 0으로 간주하지 않습니다.

## Next milestones
1. 개발 API access 신청 및 key 발급
2. 공식 endpoint, parameters, sample payload 확보
3. field mapping 확정 및 API collector 검증
4. 실제 데이터 연결 테스트
5. DB snapshot/history 및 행정구역 매핑
6. 전국 자동 수집, 품질검증, 지도/지역 상세 기능
7. SEO 및 배포 준비

## 원칙
- 무료 서비스로 시작, 초기 광고 없음
- Lock-in First: 저장한 지역, 비교, 변화 추적, 데이터 이력으로 재방문 가치 강화
- 데이터 출처와 기준일 표시
- 신고/위반 이력은 모든 기능 완료 후 별도 검토
- 사용자 승인 없이 배포하지 않음


## API application status (2026-11-21)
- Daegu-only development API application submitted; approval is pending.
- Credentials, actual response sample, and field mapping are not yet available.
- No live data is connected; demo figures remain fictional.
