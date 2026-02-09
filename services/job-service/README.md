# Job Service

HairSpare의 공고(Job) 관리 마이크로서비스입니다.

## 기능

- 공고 목록 조회 (필터링: 지역, 급구 여부, 프리미엄 여부)
- 공고 상세 조회
- 공고 생성 (매장만 가능)
- 공고 지원 (스페어만 가능)
- 내 공고 목록 조회
- 내 지원 목록 조회

## 실행 방법

### 방법 1: 실행 스크립트 사용

```bash
cd /Users/yoram/hairspare/backend/services/job-service
./run.sh
```

### 방법 2: 직접 실행

```bash
cd /Users/yoram/hairspare/backend/services/job-service
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload
```

## API 엔드포인트

- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스 체크
- `GET /api/jobs` - 공고 목록 조회
- `GET /api/jobs/{job_id}` - 공고 상세 조회
- `POST /api/jobs` - 공고 생성 (인증 필요, shop 역할만)
- `POST /api/jobs/{job_id}/apply` - 공고 지원 (인증 필요, spare 역할만)
- `GET /api/jobs/my` - 내 공고 목록 (인증 필요, shop 역할만)
- `GET /api/applications/my` - 내 지원 목록 (인증 필요, spare 역할만)

## 포트

기본 포트: **8102**

환경 변수 `SERVICE_PORT`로 변경 가능합니다.

## 데이터베이스

- `Job` 테이블: 공고 정보
- `Application` 테이블: 지원 정보
- `Region` 테이블: 지역 정보

## 의존성

- Auth Service (포트 8101): 사용자 인증 및 권한 확인
