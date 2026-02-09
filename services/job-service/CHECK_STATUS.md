# Job Service 상태 확인

## 문제
HTTP Status 000은 서비스에 연결할 수 없다는 의미입니다.

## 해결 방법

### 1. Job Service 터미널 확인

Job Service를 실행한 터미널(Top-Right)을 확인하세요:
- 서비스가 실행 중이어야 합니다
- "Application startup complete" 메시지가 있어야 합니다
- 오류 메시지가 없는지 확인하세요

### 2. 서비스 재시작

서비스가 종료되었거나 오류가 발생했다면:

```bash
cd /Users/yoram/hairspare/backend/services/job-service
./quick_restart.sh
```

또는 수동으로:

```bash
cd /Users/yoram/hairspare/backend/services/job-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/hairspare"
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8103 --reload
```

### 3. 연결 테스트

서비스가 시작되면:

```bash
curl http://localhost:8103/health
```

예상 응답:
```json
{"status":"ok","service":"job-service"}
```

## 가능한 원인

1. 서비스가 재로드 중에 오류로 종료됨
2. 포트 충돌
3. 모델 로드 오류

Job Service 터미널의 최신 로그를 확인하세요.
