# Docker Compose 가이드

HairSpare MSA 아키텍처의 모든 서비스를 Docker Compose로 한 번에 실행하는 방법입니다.

## 사전 요구사항

- Docker Desktop 설치 및 실행 중
- Docker Compose 설치 (Docker Desktop에 포함됨)

## 실행 방법

### 모든 서비스 시작

```bash
cd /Users/yoram/hairspare/backend
docker-compose up -d
```

### 로그 확인

```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f auth-service
docker-compose logs -f api-gateway
```

### 서비스 상태 확인

```bash
docker-compose ps
```

### 모든 서비스 중지

```bash
docker-compose down
```

### 데이터베이스 데이터 유지하며 중지

```bash
docker-compose down
```

데이터는 `postgres_data` 볼륨에 저장되므로 데이터가 유지됩니다.

### 데이터베이스 데이터까지 삭제하며 중지

```bash
docker-compose down -v
```

## 서비스 포트

| 서비스 | 포트 | URL |
|--------|------|-----|
| API Gateway | 8000 | http://localhost:8000 |
| Auth Service | 8101 | http://localhost:8101 |
| Job Service | 8103 | http://localhost:8103 |
| Schedule Service | 8104 | http://localhost:8104 |
| Chat Service | 8105 | http://localhost:8105 |
| Energy Service | 8106 | http://localhost:8106 |
| PostgreSQL | 5433 | localhost:5433 |

## 헬스 체크

각 서비스는 헬스 체크 엔드포인트를 제공합니다:

```bash
# API Gateway
curl http://localhost:8000/health

# Auth Service
curl http://localhost:8101/health

# Job Service
curl http://localhost:8103/health

# Schedule Service
curl http://localhost:8104/health

# Chat Service
curl http://localhost:8105/health

# Energy Service
curl http://localhost:8106/health
```

## 빌드

### 모든 서비스 빌드

```bash
docker-compose build
```

### 특정 서비스만 빌드

```bash
docker-compose build auth-service
```

### 빌드 캐시 없이 재빌드

```bash
docker-compose build --no-cache
```

## 환경 변수

환경 변수는 `docker-compose.yml` 파일에서 설정됩니다. 로컬 개발 환경에 맞게 수정할 수 있습니다.

### 주요 환경 변수

- `DATABASE_URL`: PostgreSQL 연결 문자열
- `JWT_SECRET_KEY`: JWT 토큰 서명 키
- `SERVICE_PORT`: 각 서비스의 포트
- `CORS_ORIGINS`: CORS 허용 origin 목록

## 문제 해결

### 포트 충돌

포트가 이미 사용 중인 경우:

1. 사용 중인 포트 확인:
   ```bash
   lsof -i :8000
   ```

2. `docker-compose.yml`에서 포트 변경

### 서비스가 시작되지 않음

1. 로그 확인:
   ```bash
   docker-compose logs [service-name]
   ```

2. 데이터베이스 연결 확인:
   ```bash
   docker-compose exec postgres psql -U postgres -d hairspare
   ```

### 데이터베이스 마이그레이션

서비스 시작 전에 데이터베이스 마이그레이션이 필요할 수 있습니다:

```bash
# Auth Service 마이그레이션
docker-compose exec auth-service alembic upgrade head
```

## 개발 모드

개발 중에는 로컬에서 직접 실행하는 것이 더 편리할 수 있습니다:

```bash
# 각 서비스 디렉토리에서
cd services/auth-service
./run.sh
```

Docker Compose는 프로덕션 환경이나 통합 테스트에 더 적합합니다.

## 볼륨

- `postgres_data`: PostgreSQL 데이터 저장소

볼륨 위치 확인:
```bash
docker volume inspect backend_postgres_data
```
