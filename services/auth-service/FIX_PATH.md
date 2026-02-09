# 경로 문제 해결

## 문제
`ModuleNotFoundError: No module named 'shared'` 오류 발생

## 원인
shared 라이브러리 경로가 올바르게 설정되지 않음

## 해결 방법

모든 파일의 경로 설정을 절대 경로로 변경했습니다.

### 테스트

```bash
cd /Users/yoram/hairspare/backend/services/auth-service

# Python에서 직접 테스트
python -c "import sys; import os; sys.path.insert(0, os.path.abspath('../..')); import shared; print('OK')"

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 8101 --reload
```

### 여전히 오류가 발생하면

1. 현재 디렉토리 확인:
```bash
pwd
# 반드시 /Users/yoram/hairspare/backend/services/auth-service 여야 함
```

2. shared 디렉토리 확인:
```bash
ls -la ../../shared/__init__.py
# 파일이 존재해야 함
```

3. PYTHONPATH 환경 변수 사용:
```bash
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8101 --reload
```
