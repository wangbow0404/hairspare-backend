# Job Service 재시작 필요

## 문제
shared 라이브러리의 DATABASE_URL 설정을 수정했지만, 변경사항이 아직 적용되지 않았습니다.

## 해결 방법

### 1. Job Service 재시작

Job Service를 실행한 터미널에서:
1. `Ctrl+C`로 서비스 중지
2. 다시 시작:

```bash
cd /Users/yoram/hairspare/backend/services/job-service
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8103 --reload
```

### 2. 테스트 재실행

다른 터미널에서:
```bash
cd /Users/yoram/hairspare/backend/services/job-service
BASE_URL="http://localhost:8103" ./test_api.sh
```

## 확인 사항

재시작 후에도 같은 오류가 발생하면:

1. **환경 변수 확인:**
```bash
echo $DATABASE_URL
```

2. **shared 라이브러리 확인:**
```bash
cd /Users/yoram/hairspare/backend
python3 -c "from shared.database.session import DATABASE_URL; print(DATABASE_URL)"
```

3. **직접 데이터베이스 연결 테스트:**
```bash
psql -U $(whoami) -d hairspare -c "SELECT 1;"
```
