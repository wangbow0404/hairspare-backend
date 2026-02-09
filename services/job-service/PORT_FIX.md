# 포트 충돌 해결 방법

## 현재 상황
포트 8102가 이미 사용 중입니다. 프로세스 ID: 27475, 27477

## 해결 방법

### 방법 1: 기존 프로세스 종료 (권장)

```bash
cd /Users/yoram/hairspare/backend/services/job-service
./kill_port.sh
```

또는 수동으로:
```bash
kill -9 27475 27477
```

그 다음 다시 실행:
```bash
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload
```

### 방법 2: 다른 포트 사용

포트 8103 사용:
```bash
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
SERVICE_PORT=8103 uvicorn app.main:app --host 0.0.0.0 --port 8103 --reload
```

또는 환경 변수로:
```bash
export SERVICE_PORT=8103
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8103 --reload
```

### 방법 3: 사용 가능한 포트 자동 찾기

```bash
./find_free_port.sh
```

## 확인

서비스가 정상적으로 실행되었는지 확인:
```bash
curl http://localhost:8102/health
# 또는 다른 포트를 사용한 경우
curl http://localhost:8103/health
```
