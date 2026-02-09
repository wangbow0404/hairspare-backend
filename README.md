# HairSpare Backend - MSA Architecture

FastAPI 기반 마이크로서비스 아키텍처 백엔드

## 구조

- `shared/`: 공통 라이브러리 패키지
- `api-gateway/`: API Gateway 서비스
- `services/`: 각 마이크로서비스
  - `auth-service/`: 인증 서비스 (완전 구현됨)
  - `job-service/`: 공고 관리 서비스 (완전 구현됨)
  - 기타 서비스들...

## 실행 방법

### 로컬 개발 환경

```bash
# Docker Compose로 전체 스택 실행
cd backend
docker-compose up -d

# 특정 서비스만 실행
docker-compose up auth-service job-service api-gateway
```

### 개별 서비스 실행

```bash
# Auth Service
cd services/auth-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Job Service
cd services/job-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## 데이터베이스 마이그레이션

### Auth Service 마이그레이션

```bash
cd services/auth-service

# 초기 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

## API 엔드포인트

- API Gateway: http://localhost:8000
- Auth Service: http://localhost:8001
  - `POST /api/auth/register` - 회원가입
  - `POST /api/auth/login` - 로그인
  - `GET /api/auth/me` - 현재 사용자 정보
- Job Service: http://localhost:8002
  - `GET /api/jobs` - 공고 목록 조회
  - `GET /api/jobs/{id}` - 공고 상세 조회
  - `POST /api/jobs` - 공고 생성
  - `POST /api/jobs/{id}/apply` - 공고 지원

## 환경 변수

각 서비스의 `.env.example` 파일을 참고하여 `.env` 파일을 생성하세요.

## 다음 단계

1. 데이터베이스 마이그레이션 실행
2. 나머지 서비스들의 비즈니스 로직 구현
3. Flutter 앱 연동 테스트
