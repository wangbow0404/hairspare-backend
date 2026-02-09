#!/bin/bash

# Chat Service API 테스트 스크립트

BASE_URL="${BASE_URL:-http://localhost:8105}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Chat Service API 테스트"
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
echo "참고: 대부분의 Chat Service 엔드포인트는 인증이 필요합니다."
echo "- GET /api/chats (채팅방 목록 조회)"
echo "- GET /api/chats/{chat_id} (채팅방 상세 조회)"
echo "- GET /api/chats/{chat_id}/messages (메시지 목록 조회)"
echo "- POST /api/chats/{chat_id}/messages (메시지 전송)"
echo "- POST /api/chats/{chat_id}/read (메시지 읽음 처리)"
echo "- DELETE /api/chats/{chat_id} (채팅방 삭제)"
