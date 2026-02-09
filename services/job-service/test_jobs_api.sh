#!/bin/bash

# 공고 목록 조회 테스트

BASE_URL="http://localhost:8103"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "공고 목록 조회 테스트"
echo "=========================================="
echo ""

# 1. 공고 목록 조회
echo -e "${YELLOW}[1] 공고 목록 조회 (GET /api/jobs)${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/jobs?limit=5")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo "Response:"
echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"

if [ "$http_code" == "200" ]; then
    # jobs 배열 확인
    job_count=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('jobs', [])))" 2>/dev/null || echo "0")
    
    if [ "$job_count" == "0" ]; then
        echo -e "${YELLOW}⚠ 공고 목록 조회 성공했지만 데이터가 없습니다 (빈 배열)${NC}"
        echo "이는 정상입니다. 데이터베이스에 공고가 없을 수 있습니다."
    else
        echo -e "${GREEN}✓ 공고 목록 조회 성공 (공고 개수: $job_count)${NC}"
    fi
else
    echo -e "${RED}✗ 공고 목록 조회 실패${NC}"
fi
echo ""

# 2. 데이터베이스 확인
echo -e "${YELLOW}[2] 데이터베이스 공고 개수 확인${NC}"
echo "데이터베이스에서 직접 확인하려면:"
echo "psql -U \$(whoami) -d hairspare -c 'SELECT COUNT(*) FROM \"Job\";'"
echo ""

echo "=========================================="
echo "테스트 완료"
echo "=========================================="
