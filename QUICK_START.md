# 빠른 시작 가이드

## 데이터베이스 설정 (필수)

### 방법 1: Docker Compose 사용 (가장 쉬움)

```bash
cd backend
docker-compose up -d postgres
```

이렇게 하면 PostgreSQL이 자동으로 설정되고 `postgresql://postgres:postgres@localhost:5432/hairspare`로 연결됩니다.

그런 다음 `.env` 파일을 수정:
```bash
cd services/auth-service
# .env 파일에서 DATABASE_URL을 다음으로 변경:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hairspare
```

### 방법 2: 로컬 PostgreSQL 사용

1. **PostgreSQL 시작:**
```bash
# macOS (Homebrew)
brew services start postgresql@14

# 또는
pg_ctl -D /usr/local/var/postgres start
```

2. **데이터베이스 생성:**
```bash
createdb hairspare
```

3. **환경 변수 확인:**
```bash
cd backend/services/auth-service
# .env 파일이 이미 생성되어 있습니다
# DATABASE_URL=postgresql://yoram@localhost:5432/hairspare
```

## 마이그레이션 실행

데이터베이스가 준비된 후:

```bash
cd backend/services/auth-service

# 의존성 설치 (처음 한 번만)
pip install -r requirements.txt

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

## 서비스 실행

```bash
# Auth Service 실행
cd backend/services/auth-service
uvicorn app.main:app --host 0.0.0.0 --port 8001

# 다른 터미널에서 Job Service 실행
cd backend/services/job-service
uvicorn app.main:app --host 0.0.0.0 --port 8002

# API Gateway 실행
cd backend/api-gateway
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 테스트

```bash
# API Gateway 헬스 체크
curl http://localhost:8000/health

# Auth Service 헬스 체크
curl http://localhost:8001/health

# 회원가입 테스트
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "spare"
  }'
```
