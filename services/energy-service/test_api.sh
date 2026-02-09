#!/bin/bash

# Energy Service API 테스트 스크립트

BASE_URL="${BASE_URL:-http://localhost:8106}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Energy Service API 테스트"
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

echo "=========================================="
echo "테스트 완료"
echo "=========================================="
echo ""
echo "참고: Energy Service 엔드포인트는 모두 인증이 필요합니다."
echo "- GET /api/energy/wallet (에너지 지갑 조회)"
echo "- POST /api/energy/purchase (에너지 구매)"
echo "- POST /api/energy/lock (에너지 잠금)"
echo "- POST /api/energy/return (에너지 반환)"
echo "- POST /api/energy/forfeit (에너지 몰수)"
