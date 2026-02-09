# Schedule Service

HairSpare의 스케줄 관리 마이크로서비스입니다.

## 기능

- 스케줄 목록 조회 (필터링: spare_id, shop_id, status, date)
- 스케줄 상세 조회
- 스케줄 생성 (매장만 가능)
- 스케줄 수정
- 스케줄 취소 (스페어만 가능)
- 내 스케줄 목록 조회

## 실행 방법

### 방법 1: 실행 스크립트 사용

```bash
cd /Users/yoram/hairspare/backend/services/schedule-service
./run.sh
```

### 방법 2: 직접 실행

```bash
cd /Users/yoram/hairspare/backend/services/schedule-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/hairspare"
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8104 --reload
```

## API 엔드포인트

- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스 체크
- `GET /api/schedules` - 스케줄 목록 조회
- `GET /api/schedules/{schedule_id}` - 스케줄 상세 조회
- `POST /api/schedules` - 스케줄 생성 (인증 필요, shop 역할만)
- `POST /api/schedules/{schedule_id}/cancel` - 스케줄 취소 (인증 필요, spare 역할만)
- `GET /api/schedules/my` - 내 스케줄 목록 (인증 필요)

## 포트

기본 포트: **8104**

환경 변수 `SERVICE_PORT`로 변경 가능합니다.

## 데이터베이스

- `Schedule` 테이블: 스케줄 정보

## 의존성

- Auth Service (포트 8101): 사용자 인증 및 권한 확인
- Job Service (포트 8103): 공고 정보 확인 (향후 구현)
