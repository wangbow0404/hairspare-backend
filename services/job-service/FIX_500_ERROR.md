# Job Service 500 에러 수정 가이드

## 수정 사항

1. **exposure_time 필드 처리 개선**: 필드가 없을 경우를 대비해 try-except 추가
2. **에러 로깅 개선**: 실제 오류 메시지를 서버 로그에 출력하도록 수정

## 다음 단계

### 1. Job Service 재시작

```bash
# Job Service를 중지하고 다시 시작
# 터미널에서 Ctrl+C로 중지 후
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8103 --reload
```

### 2. 테스트 재실행

```bash
BASE_URL="http://localhost:8103" ./test_api.sh
```

### 3. 서버 로그 확인

Job Service를 실행한 터미널에서 실제 오류 메시지를 확인하세요.
다음과 같은 메시지가 보일 것입니다:
- `공고 조회 오류: ...`
- `Traceback: ...`

이 정보를 바탕으로 정확한 원인을 파악할 수 있습니다.

## 가능한 원인

1. **테이블 이름 불일치**: Prisma는 `Job`이지만 SQLAlchemy는 `"Job"`로 찾을 수 있음
2. **컬럼 이름 불일치**: Prisma는 camelCase, SQLAlchemy는 snake_case
3. **데이터베이스 연결 문제**: DATABASE_URL 설정 확인 필요

## 추가 확인 사항

Prisma 스키마와 SQLAlchemy 모델의 필드명이 일치하는지 확인:
- Prisma: `exposureTime` → SQLAlchemy: `exposure_time`
- Prisma: `endTime` → SQLAlchemy: `end_time`
