#!/bin/bash

# Auth Service API 테스트 스크립트

echo "=== Auth Service API 테스트 ==="

BASE_URL="http://localhost:8001"

echo ""
echo "1. 헬스 체크..."
curl -s "$BASE_URL/health" | jq '.' || curl -s "$BASE_URL/health"

echo ""
echo ""
echo "2. 회원가입 테스트..."
curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "spare",
    "email": "test@example.com",
    "name": "테스트 사용자"
  }' | jq '.' || curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "spare",
    "email": "test@example.com",
    "name": "테스트 사용자"
  }'

echo ""
echo ""
echo "3. 로그인 테스트..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')

echo "$LOGIN_RESPONSE" | jq '.' || echo "$LOGIN_RESPONSE"

# 토큰 추출 (jq가 있는 경우)
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.token' 2>/dev/null || echo "")

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
  echo ""
  echo ""
  echo "4. 현재 사용자 정보 조회 (토큰 사용)..."
  curl -s "$BASE_URL/api/auth/me" \
    -H "Authorization: Bearer $TOKEN" | jq '.' || curl -s "$BASE_URL/api/auth/me" \
    -H "Authorization: Bearer $TOKEN"
fi

echo ""
echo ""
echo "=== 테스트 완료 ==="
