# Job Service 테스트 가이드

## 1. 서비스 실행

### 터미널 1: Job Service 실행

```bash
cd /Users/yoram/hairspare/backend/services/job-service

# 방법 1: 실행 스크립트 사용
./run.sh

# 방법 2: 직접 실행
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload
```

서비스가 정상적으로 시작되면 다음과 같은 메시지가 표시됩니다:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8102
```

## 2. 기본 API 테스트

### 터미널 2: 테스트 스크립트 실행

```bash
cd /Users/yoram/hairspare/backend/services/job-service
./test_api.sh
```

### 수동 테스트

#### 1. Health Check
```bash
curl http://localhost:8102/health
```

예상 응답:
```json
{"status": "ok", "service": "job-service"}
```

#### 2. Root Endpoint
```bash
curl http://localhost:8102/
```

예상 응답:
```json
{
  "service": "HairSpare Job Service",
  "version": "1.0.0",
  "status": "running"
}
```

#### 3. 공고 목록 조회
```bash
curl http://localhost:8102/api/jobs?limit=5
```

#### 4. 지역별 공고 조회
```bash
curl "http://localhost:8102/api/jobs?region_ids=seoul&limit=5"
```

#### 5. 급구 공고 조회
```bash
curl "http://localhost:8102/api/jobs?is_urgent=true&limit=5"
```

## 3. 인증이 필요한 엔드포인트 테스트

인증이 필요한 엔드포인트를 테스트하려면 먼저 Auth Service에서 토큰을 받아야 합니다.

### 3.1 Auth Service에서 로그인

```bash
# Auth Service가 실행 중이어야 합니다 (포트 8101)
curl -X POST http://localhost:8101/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_shop",
    "password": "password123",
    "role": "shop"
  }'
```

응답에서 `token`을 받습니다:
```json
{
  "data": {
    "user": {...},
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 3.2 공고 생성 (인증 필요)

```bash
TOKEN="여기에_받은_토큰_입력"

curl -X POST http://localhost:8102/api/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "테스트 공고",
    "date": "2025-02-05",
    "time": "09:00",
    "end_time": "18:00",
    "amount": 50000,
    "energy": 10,
    "required_count": 1,
    "region_id": "seoul",
    "description": "테스트 공고 설명",
    "is_urgent": false,
    "is_premium": false
  }'
```

### 3.3 내 공고 목록 조회

```bash
curl http://localhost:8102/api/jobs/my \
  -H "Authorization: Bearer $TOKEN"
```

## 4. 예상 오류 및 해결 방법

### 오류: "ModuleNotFoundError: No module named 'shared'"
**해결**: PYTHONPATH 환경 변수 설정
```bash
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
```

### 오류: "Connection refused"
**해결**: Job Service가 실행 중인지 확인
```bash
curl http://localhost:8102/health
```

### 오류: "Database connection failed"
**해결**: 데이터베이스가 실행 중인지 확인하고, DATABASE_URL 환경 변수 확인
```bash
# PostgreSQL 실행 확인
psql -U $(whoami) -d hairspare -c "SELECT 1;"
```

### 오류: "401 Unauthorized"
**해결**: 인증 토큰이 올바른지 확인하고, Auth Service가 실행 중인지 확인

## 5. 데이터베이스 확인

공고 데이터가 있는지 확인:
```bash
psql -U $(whoami) -d hairspare -c "SELECT COUNT(*) FROM \"Job\";"
```

지역 데이터가 있는지 확인:
```bash
psql -U $(whoami) -d hairspare -c "SELECT COUNT(*) FROM \"Region\";"
```
