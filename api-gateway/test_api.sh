#!/bin/bash

# API Gateway 테스트 스크립트

BASE_URL="${BASE_URL:-http://localhost:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "API Gateway 테스트"
echo "=========================================="
echo ""

# 1. Health Check
echo -e "${YELLOW}[1] API Gateway Health Check${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "HTTP Status: $http_code"
echo "Response: $body"
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ API Gateway health check 성공${NC}"
else
    echo -e "${RED}✗ API Gateway health check 실패${NC}"
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

# 3. Auth Service 프록시 테스트 (헬스 체크)
echo -e "${YELLOW}[3] Auth Service 프록시 테스트${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/auth/health" 2>/dev/null || echo -e "\n000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
    echo -e "${GREEN}✓ Auth Service 프록시 연결 확인${NC}"
else
    echo -e "${YELLOW}⚠ Auth Service가 실행 중이지 않을 수 있습니다${NC}"
fi
echo ""

# 4. Job Service 프록시 테스트
echo -e "${YELLOW}[4] Job Service 프록시 테스트${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/jobs" 2>/dev/null || echo -e "\n000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
    echo -e "${GREEN}✓ Job Service 프록시 연결 확인${NC}"
else
    echo -e "${YELLOW}⚠ Job Service가 실행 중이지 않을 수 있습니다${NC}"
fi
echo ""

# 5. Schedule Service 프록시 테스트
echo -e "${YELLOW}[5] Schedule Service 프록시 테스트${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/schedules" 2>/dev/null || echo -e "\n000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
    echo -e "${GREEN}✓ Schedule Service 프록시 연결 확인${NC}"
else
    echo -e "${YELLOW}⚠ Schedule Service가 실행 중이지 않을 수 있습니다${NC}"
fi
echo ""

# 6. Chat Service 프록시 테스트
echo -e "${YELLOW}[6] Chat Service 프록시 테스트${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/chats" 2>/dev/null || echo -e "\n000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ] || [ "$http_code" == "401" ] || [ "$http_code" == "404" ]; then
    echo -e "${GREEN}✓ Chat Service 프록시 연결 확인${NC}"
else
    echo -e "${YELLOW}⚠ Chat Service가 실행 중이지 않을 수 있습니다${NC}"
fi
echo ""

# 7. Energy Service 프록시 테스트
echo -e "${YELLOW}[7] Energy Service 프록시 테스트${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/energy/wallet" 2>/dev/null || echo -e "\n000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ] || [ "$http_code" == "401" ] || [ "$http_code" == "404" ]; then
    echo -e "${GREEN}✓ Energy Service 프록시 연결 확인${NC}"
else
    echo -e "${YELLOW}⚠ Energy Service가 실행 중이지 않을 수 있습니다${NC}"
fi
echo ""

echo "=========================================="
echo "테스트 완료"
echo "=========================================="
echo ""
echo "참고:"
echo "- 모든 서비스가 실행 중이어야 정상적으로 작동합니다"
echo "- 인증이 필요한 엔드포인트는 401 응답이 정상입니다"
echo "- 서비스가 실행 중이지 않으면 503 또는 502 오류가 발생합니다"
