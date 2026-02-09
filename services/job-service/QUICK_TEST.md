# Job Service 빠른 테스트 가이드

## 빠른 시작

### 1단계: Job Service 실행

새 터미널 창을 열고:

```bash
cd /Users/yoram/hairspare/backend/services/job-service
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload
```

### 2단계: 기본 테스트 (인증 불필요)

다른 터미널에서:

```bash
cd /Users/yoram/hairspare/backend/services/job-service
./test_api.sh
```

또는 수동으로:

```bash
# Health check
curl http://localhost:8102/health

# 루트 엔드포인트
curl http://localhost:8102/

# 공고 목록 조회
curl http://localhost:8102/api/jobs?limit=5
```

### 3단계: 인증 테스트 (선택사항)

Auth Service가 실행 중이어야 합니다 (포트 8101).

```bash
cd /Users/yoram/hairspare/backend/services/job-service
./test_with_auth.sh
```

## 예상 결과

### 성공적인 응답 예시

**Health Check:**
```json
{"status": "ok", "service": "job-service"}
```

**공고 목록:**
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "...",
        "title": "...",
        "date": "2025-02-05",
        ...
      }
    ]
  }
}
```

## 문제 해결

### 서비스가 시작되지 않음
- PYTHONPATH 환경 변수 확인
- 포트 8102가 사용 중인지 확인: `lsof -i :8102`

### 데이터베이스 연결 오류
- PostgreSQL 실행 확인
- DATABASE_URL 환경 변수 확인

### 모듈을 찾을 수 없음
```bash
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
```
