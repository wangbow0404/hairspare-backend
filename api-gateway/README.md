# API Gateway

HairSpare의 마이크로서비스 API Gateway입니다. 모든 클라이언트 요청의 단일 진입점 역할을 합니다.

## 기능

- 모든 마이크로서비스로의 요청 라우팅
- CORS 처리
- 인증 토큰 검증 (선택적)
- 요청/응답 프록시
- 서비스 헬스 체크

## 실행 방법

### 방법 1: 실행 스크립트 사용

```bash
cd /Users/yoram/hairspare/backend/api-gateway
chmod +x run.sh
./run.sh
```

### 방법 2: 직접 실행

```bash
cd /Users/yoram/hairspare/backend/api-gateway
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 포트

기본 포트: **8000**

환경 변수 `GATEWAY_PORT`로 변경 가능합니다.

## 서비스 URL 설정

각 서비스의 URL은 `app/config.py`에서 설정됩니다:

- Auth Service: `http://localhost:8101`
- Job Service: `http://localhost:8103`
- Schedule Service: `http://localhost:8104`
- Chat Service: `http://localhost:8105`
- Energy Service: `http://localhost:8106`

환경 변수로도 설정 가능합니다:
- `AUTH_SERVICE_URL`
- `JOB_SERVICE_URL`
- `SCHEDULE_SERVICE_URL`
- `CHAT_SERVICE_URL`
- `ENERGY_SERVICE_URL`

## API 엔드포인트

### 공통
- `GET /` - API Gateway 상태 확인
- `GET /health` - 헬스 체크

### Auth Service
- `/api/auth/*` → Auth Service로 프록시

### Job Service
- `/api/jobs/*` → Job Service로 프록시
- `/api/applications/*` → Job Service로 프록시

### Schedule Service
- `/api/schedules/*` → Schedule Service로 프록시

### Chat Service
- `/api/chats/*` → Chat Service로 프록시
- `/api/messages/*` → Chat Service로 프록시

### Energy Service
- `/api/energy/*` → Energy Service로 프록시

## 인증

인증 미들웨어는 기본적으로 비활성화되어 있습니다. 활성화하려면 `app/main.py`에서 주석을 해제하세요:

```python
app.add_middleware(AuthenticationMiddleware)
```

인증이 필요 없는 공개 경로는 `app/middleware.py`의 `PUBLIC_PATHS`에 정의되어 있습니다.

## CORS

CORS는 기본적으로 활성화되어 있으며, 다음 origin을 허용합니다:
- `http://localhost:3000` (Next.js 개발 서버)
- `http://localhost:8080` (Flutter 웹)

환경 변수 `CORS_ORIGINS`로 변경 가능합니다.

## 테스트

```bash
cd /Users/yoram/hairspare/backend/api-gateway
chmod +x test_api.sh
BASE_URL="http://localhost:8000" ./test_api.sh
```

## 의존성

- FastAPI
- httpx (HTTP 클라이언트)
- python-jose (JWT 토큰 검증)
- python-dotenv (환경 변수 관리)
