# 문제 해결 가이드

## 포트 5432가 이미 사용 중인 경우

### 옵션 1: 기존 로컬 PostgreSQL 사용 (권장)

로컬에 PostgreSQL이 이미 실행 중이라면, Docker를 사용하지 않고 기존 PostgreSQL을 사용할 수 있습니다:

```bash
# 1. 데이터베이스 생성
createdb hairspare

# 2. .env 파일 수정 (현재 사용자명 사용)
cd backend/services/auth-service
cat > .env << 'EOF'
DATABASE_URL=postgresql://yoram@localhost:5432/hairspare
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SERVICE_PORT=8001
ENVIRONMENT=development
EOF

# 3. 마이그레이션 실행
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 옵션 2: Docker 포트 변경

docker-compose.yml에서 포트를 변경했습니다 (5433으로). 이 경우:

```bash
# 1. .env 파일 수정
cd backend/services/auth-service
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/hairspare
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SERVICE_PORT=8001
ENVIRONMENT=development
EOF

# 2. Docker Compose 실행
cd ../../backend
docker-compose up -d postgres

# 3. 마이그레이션 실행
cd services/auth-service
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 옵션 3: 기존 PostgreSQL 프로세스 종료

로컬 PostgreSQL을 종료하고 Docker를 사용하려면:

```bash
# PostgreSQL 프로세스 확인
lsof -i :5432

# 종료 (프로세스 ID 확인 후)
kill <PID>

# 또는 brew services 사용 중이라면
brew services stop postgresql@14
```

## 확인 방법

```bash
# 데이터베이스 연결 테스트
psql -d hairspare -c "SELECT 1;"

# 또는 Docker 사용 시
docker exec -it backend-postgres-1 psql -U postgres -d hairspare -c "SELECT 1;"
```
