# Job Service 테스트 실행

## 현재 상태
✅ Job Service가 포트 8103에서 실행 중입니다.

## 테스트 실행

다른 터미널에서 다음 명령어를 실행하세요:

```bash
cd /Users/yoram/hairspare/backend/services/job-service
BASE_URL="http://localhost:8103" ./test_api.sh
```

## 예상 결과

### 성공 시:
- Health check: ✅ 200
- Root endpoint: ✅ 200
- 공고 목록 조회: ✅ 200 (빈 배열 또는 공고 목록)

### 실패 시:
Job Service를 실행한 터미널에서 실제 오류 메시지를 확인하세요:
```
============================================================
[공고 목록 조회 오류] ...
============================================================
```

## 수정 사항

컬럼명 매핑을 Prisma의 camelCase 형식에 맞게 수정했습니다:
- `shop_id` → `shopId`
- `end_time` → `endTime`
- `required_count` → `requiredCount`
- `region_id` → `regionId`
- `is_urgent` → `isUrgent`
- `is_premium` → `isPremium`
- `exposure_time` → `exposureTime`
- `created_at` → `createdAt`
- `updated_at` → `updatedAt`

## 다음 단계

테스트 결과를 확인한 후:
1. 성공하면 → 다음 서비스 설정으로 진행
2. 실패하면 → 서버 로그의 오류 메시지를 확인하고 추가 수정
