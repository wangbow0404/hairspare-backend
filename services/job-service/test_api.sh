#!/bin/bash

# Job Service API 테스트 스크립트

BASE_URL="${BASE_URL:-http://localhost:8102}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Job Service API 테스트"
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

# 3. 공고 목록 조회 (인증 없이)
echo -e "${YELLOW}[3] 공고 목록 조회 (GET /api/jobs)${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/jobs?limit=5")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "HTTP Status: $http_code"
echo "Response: $body" | head -20
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ 공고 목록 조회 성공${NC}"
else
    echo -e "${RED}✗ 공고 목록 조회 실패${NC}"
fi
echo ""

# 4. 지역별 공고 조회
echo -e "${YELLOW}[4] 지역별 공고 조회 (region_ids=seoul)${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/jobs?region_ids=seoul&limit=5")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "HTTP Status: $http_code"
echo "Response: $body" | head -20
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ 지역별 공고 조회 성공${NC}"
else
    echo -e "${RED}✗ 지역별 공고 조회 실패${NC}"
fi
echo ""

# 5. 급구 공고 조회
echo -e "${YELLOW}[5] 급구 공고 조회 (is_urgent=true)${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/jobs?is_urgent=true&limit=5")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "HTTP Status: $http_code"
echo "Response: $body" | head -20
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ 급구 공고 조회 성공${NC}"
else
    echo -e "${RED}✗ 급구 공고 조회 실패${NC}"
fi
echo ""

echo "=========================================="
echo "테스트 완료"
echo "=========================================="
echo ""
echo "참고: 인증이 필요한 엔드포인트는 Auth Service와 연동 후 테스트해야 합니다."
echo "- POST /api/jobs (공고 생성)"
echo "- POST /api/jobs/{job_id}/apply (공고 지원)"
echo "- GET /api/jobs/my (내 공고 목록)"
echo "- GET /api/applications/my (내 지원 목록)"
