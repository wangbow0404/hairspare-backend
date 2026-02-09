# Job Service 500 에러 디버깅 가이드

## 현재 상황
- Health check: ✅ 성공 (200)
- Root endpoint: ✅ 성공 (200)
- 공고 목록 조회: ❌ 실패 (500 Internal Server Error)

## 가능한 원인

### 1. 데이터베이스 테이블이 없음
Job, Application, Region 테이블이 데이터베이스에 존재하지 않을 수 있습니다.

### 2. 쿼리 오류
`exposure_time` 필드나 다른 필드가 데이터베이스 스키마와 일치하지 않을 수 있습니다.

### 3. 데이터베이스 연결 문제
데이터베이스 연결 설정이 잘못되었을 수 있습니다.

## 해결 방법

### 1단계: 서버 로그 확인

Job Service를 실행한 터미널에서 오류 메시지를 확인하세요. 
다음과 같은 오류가 보일 수 있습니다:
- `relation "Job" does not exist` → 테이블이 없음
- `column "exposure_time" does not exist` → 컬럼이 없음
- `syntax error` → SQL 쿼리 오류

### 2단계: 데이터베이스 테이블 확인

```bash
psql -U $(whoami) -d hairspare -c "\dt"
```

Job, Application, Region 테이블이 있는지 확인하세요.

### 3단계: Alembic 마이그레이션 설정

Job Service에 Alembic을 설정하고 마이그레이션을 생성/적용해야 합니다.

## 빠른 해결책

만약 테이블이 없다면, Alembic 마이그레이션을 설정하거나, 
Prisma 스키마를 사용 중이라면 Prisma 마이그레이션을 확인해야 합니다.
