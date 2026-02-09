# 마이크로서비스 상태

## 완료된 서비스 ✅

### 1. Auth Service (포트 8101)
- 상태: ✅ 실행 중
- 기능: 인증 및 사용자 관리
- 테스트: ✅ 성공

### 2. Job Service (포트 8103)
- 상태: ✅ 실행 중
- 기능: 공고 관리
- 테스트: ✅ 성공
- API:
  - ✅ `GET /health`
  - ✅ `GET /`
  - ✅ `GET /api/jobs`

## 다음 단계

### 우선순위 1: 핵심 서비스
1. **Schedule Service** - 스케줄 관리
2. **Chat Service** - 채팅 기능
3. **Energy Service** - 에너지(예약금) 관리

### 우선순위 2: 주문 관련 서비스
4. **Order Service** - 주문 관리
5. **Payment Service** - 결제 처리
6. **Cart Service** - 장바구니

### 우선순위 3: 기타 서비스
7. **Store Service** - 스토어 관리
8. **Notification Service** - 알림 서비스

### 우선순위 4: 통합
9. **API Gateway** - 모든 서비스 통합

## 실행 명령어

### Auth Service
```bash
cd /Users/yoram/hairspare/backend/services/auth-service
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8101 --reload
```

### Job Service
```bash
cd /Users/yoram/hairspare/backend/services/job-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/hairspare"
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8103 --reload
```

## 테스트

### Auth Service
```bash
curl http://localhost:8101/
```

### Job Service
```bash
curl http://localhost:8103/api/jobs?limit=5
```
