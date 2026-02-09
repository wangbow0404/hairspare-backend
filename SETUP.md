# HairSpare Backend 설정 가이드

## 데이터베이스 설정

### 옵션 1: Docker Compose 사용 (권장)

가장 쉬운 방법은 Docker Compose를 사용하는 것입니다:

```bash
cd backend
docker-compose up -d postgres
```

이렇게 하면 PostgreSQL이 자동으로 설정되고 `postgresql://postgres:postgres@localhost:5432/hairspare`로 연결할 수 있습니다.

### 옵션 2: 로컬 PostgreSQL 사용

로컬에 PostgreSQL이 설치되어 있다면:

1. 데이터베이스 생성:
```bash
createdb hairspare
```

2. 환경 변수 설정:
```bash
cd backend/services/auth-service
cp .env.example .env
```

`.env` 파일을 열어서 DATABASE_URL을 수정하세요:
- macOS의 경우: `postgresql://$(whoami)@localhost:5432/hairspare`
- 또는 PostgreSQL 사용자명 확인: `psql -U postgres -l`

### 옵션 3: 기존 Next.js 프로젝트의 데이터베이스 사용

기존 Next.js 프로젝트에서 Prisma를 사용하고 있다면, 같은 데이터베이스를 사용할 수 있습니다:

1. 기존 `.env` 파일에서 `DATABASE_URL` 확인
2. Auth Service의 `.env` 파일에 동일한 값 설정

## 환경 변수 설정

각 서비스 디렉토리에서:

```bash
cd backend/services/auth-service
cp .env.example .env
# .env 파일을 편집하여 실제 값으로 수정
```

## 마이그레이션 실행

데이터베이스가 설정된 후:

```bash
cd backend/services/auth-service

# 환경 변수 로드 (python-dotenv 사용)
export $(cat .env | xargs)

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

## 문제 해결

### "role postgres does not exist" 오류

이 오류는 PostgreSQL에 "postgres" 사용자가 없을 때 발생합니다.

**해결 방법:**

1. 현재 사용자로 데이터베이스 생성:
```bash
createdb hairspare
```

2. `.env` 파일에서 DATABASE_URL 수정:
```
DATABASE_URL=postgresql://yoram@localhost:5432/hairspare
```
(여기서 `yoram`은 현재 사용자명)

3. 또는 Docker Compose 사용:
```bash
docker-compose up -d postgres
```

### PostgreSQL이 실행되지 않는 경우

```bash
# PostgreSQL 시작 (macOS)
brew services start postgresql@14

# 또는
pg_ctl -D /usr/local/var/postgres start
```
