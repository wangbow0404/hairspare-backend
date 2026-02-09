# Job Service 500 에러 해결 가이드

## 현재 상황
- Health check: ✅ 성공
- Root endpoint: ✅ 성공  
- 공고 목록 조회: ❌ 500 에러

## 해결 단계

### 1단계: 에러 로깅 확인

Job Service를 실행한 터미널에서 실제 오류 메시지를 확인하세요.

**Job Service 재시작:**
```bash
cd /Users/yoram/hairspare/backend/services/job-service
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8103 --reload
```

**테스트 재실행:**
```bash
BASE_URL="http://localhost:8103" ./test_api.sh
```

**서버 로그 확인:**
Job Service 터미널에서 다음과 같은 형식의 오류 메시지가 출력됩니다:
```
============================================================
[공고 목록 조회 오류] ...
============================================================
[Traceback]
...
============================================================
```

### 2단계: 데이터베이스 테이블 확인

```bash
cd /Users/yoram/hairspare/backend/services/job-service
./check_tables.sh
```

또는 직접 확인:
```bash
psql -U $(whoami) -d hairspare -c "\dt"
```

### 3단계: 가능한 원인별 해결

#### 원인 1: 테이블이 없음
**증상:** `relation "Job" does not exist`

**해결:**
```bash
# Prisma 마이그레이션 확인
cd /Users/yoram/hairspare
npx prisma migrate status

# 마이그레이션 적용
npx prisma migrate deploy
```

#### 원인 2: 테이블 이름 불일치
**증상:** Prisma는 소문자 `job`, SQLAlchemy는 대문자 `Job`

**해결:** SQLAlchemy 모델의 `__tablename__` 수정:
```python
# app/models/job.py
class Job(Base):
    __tablename__ = "job"  # 소문자로 변경
```

#### 원인 3: 컬럼 이름 불일치
**증상:** `column "exposure_time" does not exist`

**해결:** Prisma는 camelCase (`exposureTime`), SQLAlchemy는 snake_case (`exposure_time`)
- Prisma 스키마 확인: `prisma/schema.prisma`
- SQLAlchemy 모델과 일치시키기

### 4단계: 테이블 생성 (필요한 경우)

Prisma 마이그레이션이 적용되지 않았다면:

```bash
cd /Users/yoram/hairspare
npx prisma migrate dev --name init_job_tables
```

또는 Alembic 사용 (Job Service 전용):
```bash
cd /Users/yoram/hairspare/backend/services/job-service
# Alembic 설정 후
alembic revision --autogenerate -m "create job tables"
alembic upgrade head
```

## 빠른 확인 명령어

```bash
# 1. 테이블 존재 확인
psql -U $(whoami) -d hairspare -c "SELECT COUNT(*) FROM \"Job\";"

# 2. Job 테이블 구조 확인
psql -U $(whoami) -d hairspare -c "\d \"Job\""

# 3. 데이터 개수 확인
psql -U $(whoami) -d hairspare -c "SELECT COUNT(*) FROM \"Job\";"
```

## 다음 단계

서버 로그의 실제 오류 메시지를 확인한 후, 해당 오류에 맞는 해결 방법을 적용하세요.
