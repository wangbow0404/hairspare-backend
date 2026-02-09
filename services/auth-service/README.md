# Auth Service

인증 및 사용자 관리 마이크로서비스

## 실행 방법

### 1. 환경 변수 설정

`.env` 파일이 이미 생성되어 있습니다. 필요시 수정하세요:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/hairspare
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SERVICE_PORT=8001
ENVIRONMENT=development
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션 (이미 완료됨)

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "Migration name"

# 마이그레이션 적용
alembic upgrade head
```

### 4. 서비스 실행

```bash
# 방법 1: 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 방법 2: 스크립트 사용
./run.sh
```

## API 엔드포인트

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/me` - 현재 사용자 정보
- `POST /api/auth/logout` - 로그아웃
- `POST /api/auth/change-password` - 비밀번호 변경
- `GET /health` - 헬스 체크

## 테스트

```bash
# API 테스트 스크립트 실행
./test_api.sh
```

## 문제 해결

### shared 라이브러리 import 오류

서비스를 실행할 때는 반드시 `backend/services/auth-service` 디렉토리에서 실행해야 합니다:

```bash
cd /Users/yoram/hairspare/backend/services/auth-service
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 데이터베이스 연결 오류

`.env` 파일의 `DATABASE_URL`이 올바른지 확인하세요:
- Docker 사용 시: `postgresql://postgres:postgres@localhost:5433/hairspare`
- 로컬 PostgreSQL 사용 시: `postgresql://yoram@localhost:5432/hairspare`
