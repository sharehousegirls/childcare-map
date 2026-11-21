# 어린이집 지도 (Childcare Map)

지역별 어린이집 입소 대기 정보 비교 서비스.

## 현재 상태
- 정적 웹 프로토타입: 지역 선택, 지역 카드, 시설 검색, 유형/대기 0명 필터, 반응형 UI
- **현재 화면의 데이터는 모두 가상 데모 데이터**이며 실제 시설/대기현황과 무관합니다.
- 공식 데이터 연결을 위한 FastAPI backend scaffold가 `backend/`에 추가되었습니다. 아직 실제 API endpoint, credentials, response field mapping이 설정되지 않아 live data 연결 상태가 아닙니다.

## 실행
- Frontend: `index.html`을 브라우저로 열어 UI를 확인합니다.
- Backend: `backend/README.md` 참고. Python 3.11+, FastAPI, httpx 기반으로 설정합니다.
- Frontend가 backend API를 직접 연결하는 작업은 provider endpoint와 실제 응답 샘플 검증 이후 이어집니다.

## 데이터 연결 상태
1. 공식 어린이집정보공개포털 Open API 후보를 조사했습니다.
2. API 신청/심의와 인증키가 필요합니다.
3. API endpoint, query parameter, response schema 및 정확한 field mapping은 공식 문서와 실제 샘플 응답으로 검증해야 합니다.
4. API credential은 frontend에 노출하지 않고 backend 환경변수로 보관합니다.
5. 대기 수치가 빈 값이면 0으로 단정하지 않습니다.
6. 실제 데이터와 가상 데이터는 명확하게 구분합니다.

## 다음 개발 단계
1. 개발계정 API 신청 및 인증키 발급
2. 공식 endpoint와 request parameter 확인
3. 샘플 응답(개발계정 제한 범위) 받아 field mapping 구성
4. backend 수집/정규화 테스트
5. UI에서 API data loading/error/empty states 처리 후 실제 데이터 연결
6. DB, snapshot/history, 행정구역 매핑
7. 전국 수집/업데이트, 통합 검증
8. SEO 및 배포 준비

## 원칙
- 무료 서비스로 시작, 초기 광고 없음
- Lock-in First: 지역 저장, 비교, 변화 추적, 데이터 이력으로 재방문 가치 강화
- 데이터 출처와 갱신일 표시
- 신고/위반 이력은 모든 기능 완료 후 별도 검토
- 사용자 승인 없이 배포하지 않음
