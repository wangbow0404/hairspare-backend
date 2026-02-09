# Energy Service

HairSpare의 에너지(예약금) 서비스입니다.

## 기능

- 에너지 지갑 조회/생성
- 에너지 구매
- 에너지 잠금 (공고 지원 시)
- 에너지 반환 (근무 완료 시)
- 에너지 몰수 (노쇼 시)
- 거래 내역 조회
- 노쇼 이력 조회

## 실행 방법

### 방법 1: 실행 스크립트 사용

```bash
cd /Users/yoram/hairspare/backend/services/energy-service
chmod +x run.sh
./run.sh
```

### 방법 2: 직접 실행

```bash
cd /Users/yoram/hairspare/backend/services/energy-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/hairspare"
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8106 --reload
```

## API 엔드포인트

- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스 체크
- `GET /api/energy/wallet` - 에너지 지갑 조회 (인증 필요)
- `POST /api/energy/purchase` - 에너지 구매 (인증 필요)
- `POST /api/energy/lock` - 에너지 잠금 (인증 필요)
- `POST /api/energy/return` - 에너지 반환 (인증 필요)
- `POST /api/energy/forfeit` - 에너지 몰수 (인증 필요)

## 포트

기본 포트: **8106**

환경 변수 `SERVICE_PORT`로 변경 가능합니다.

## 데이터베이스

- `EnergyWallet` 테이블: 에너지 지갑 정보
- `EnergyTransaction` 테이블: 에너지 거래 내역
- `NoShowHistory` 테이블: 노쇼 이력

## 에너지 상태 머신

- `available`: 사용 가능한 에너지
- `locked`: 잠금된 에너지 (공고 지원 시)
- `returned`: 반환된 에너지 (근무 완료 시)
- `forfeited`: 몰수된 에너지 (노쇼 시)

## 의존성

- Auth Service (포트 8101): 사용자 인증 및 권한 확인
- Job Service (포트 8103): 공고 정보 확인 (향후 구현)
