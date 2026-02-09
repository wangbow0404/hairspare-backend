# 다음 단계 가이드

## 완료된 작업 ✅

1. ✅ 공통 라이브러리 패키지 생성 (`shared/`)
2. ✅ API Gateway 구축
3. ✅ Auth Service 구현 및 마이그레이션 완료
4. ✅ Job Service 기본 구조 완성
5. ✅ Docker Compose 설정

## 현재 상태

- **데이터베이스**: 마이그레이션 완료 (User, Account, Verification 테이블 생성됨)
- **Auth Service**: 구현 완료, 실행 준비됨
- **Job Service**: 기본 구조 완성, 비즈니스 로직 구현 필요

## 다음 작업

### 1. Auth Service 실행 및 테스트

```bash
cd backend/services/auth-service

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 다른 터미널에서 테스트
./test_api.sh
```

### 2. Job Service 마이그레이션

```bash
cd backend/services/job-service

# Alembic 설정 (Auth Service와 유사하게)
# 마이그레이션 생성 및 적용
```

### 3. 나머지 서비스 구현

- Schedule Service
- Chat Service  
- Energy Service
- Store Service
- Cart Service
- Order Service
- Payment Service
- Notification Service

### 4. 서비스 간 통신 구현

서비스 간 HTTP 통신을 위한 클라이언트 구현:
- Job Service → Auth Service (사용자 정보 확인)
- Order Service → Store Service, Cart Service, Payment Service

### 5. Flutter 앱 연동

```dart
// lib/utils/api_config.dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000'; // API Gateway
}
```

## 우선순위

1. **즉시**: Auth Service 실행 및 테스트
2. **단기**: Job Service 마이그레이션 및 완전 구현
3. **중기**: 나머지 핵심 서비스 구현
4. **장기**: 스토어 서비스 및 Flutter 연동
