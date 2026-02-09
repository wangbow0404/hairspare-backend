#!/bin/bash

# Schedule Service API 테스트 스크립트

BASE_URL="${BASE_URL:-http://localhost:8104}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Schedule Service API 테스트"
echo "=========================================="
echo ""

# 1. Health Check
echo -e "${YELLOW}[1] Health Check${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "HTTP Status: $http_code"
echo "Response: $body"
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ Health check 성공${NC}"
else
    echo -e "${RED}✗ Health check 실패${NC}"
fi
echo ""

# 2. Root Endpoint
echo -e "${YELLOW}[2] Root Endpoint${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "HTTP Status: $http_code"
echo "Response: $body"
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ Root endpoint 성공${NC}"
else
    echo -e "${RED}✗ Root endpoint 실패${NC}"
fi
echo ""

# 3. 스케줄 목록 조회 (인증 없이)
echo -e "${YELLOW}[3] 스케줄 목록 조회 (GET /api/schedules)${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/schedules?limit=5")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "HTTP Status: $http_code"
echo "Response: $body" | head -20
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ 스케줄 목록 조회 성공${NC}"
else
    echo -e "${RED}✗ 스케줄 목록 조회 실패${NC}"
fi
echo ""

echo "=========================================="
echo "테스트 완료"
echo "=========================================="
echo ""
echo "참고: 인증이 필요한 엔드포인트는 Auth Service와 연동 후 테스트해야 합니다."
echo "- POST /api/schedules (스케줄 생성)"
echo "- POST /api/schedules/{schedule_id}/cancel (스케줄 취소)"
echo "- GET /api/schedules/my (내 스케줄 목록)"
