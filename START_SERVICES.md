# 서비스 실행 가이드

## 포트 설정

- **API Gateway**: 8000
- **Auth Service**: 8101 (포트 충돌로 변경)
- **Job Service**: 8002
- **PostgreSQL**: 5433 (Docker) 또는 5432 (로컬)

## 서비스 실행 순서

### 1. 데이터베이스 시작

```bash
cd /Users/yoram/hairspare/backend
docker-compose up -d postgres
```

### 2. Auth Service 실행

```bash
cd /Users/yoram/hairspare/backend/services/auth-service

# .env 파일 확인 (SERVICE_PORT=8101)
cat .env

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 8101 --reload
```

### 3. API Gateway 실행 (선택사항)

```bash
cd /Users/yoram/hairspare/backend/api-gateway

# .env 파일 확인 (AUTH_SERVICE_URL=http://localhost:8101)
cat .env

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 테스트

### Auth Service 직접 테스트

```bash
# 헬스 체크
curl http://localhost:8101/health

# 회원가입
curl -X POST http://localhost:8101/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "spare"
  }'
```

### API Gateway를 통한 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 회원가입 (API Gateway 경유)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "spare"
  }'
```

## 문제 해결

### 포트 충돌

포트가 이미 사용 중이면:
1. 다른 포트 사용 (예: 8101, 8102 등)
2. 사용 중인 프로세스 종료: `lsof -ti :8001 | xargs kill`

### 데이터베이스 연결 오류

`.env` 파일의 `DATABASE_URL` 확인:
- Docker 사용: `postgresql://postgres:postgres@localhost:5433/hairspare`
- 로컬 PostgreSQL: `postgresql://yoram@localhost:5432/hairspare`
