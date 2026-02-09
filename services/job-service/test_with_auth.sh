#!/bin/bash

# Job Service 인증이 필요한 API 테스트 스크립트

AUTH_URL="http://localhost:8101"
JOB_URL="http://localhost:8102"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Job Service 인증 API 테스트"
echo "=========================================="
echo ""

# 1. Auth Service에서 로그인
echo -e "${YELLOW}[1] Auth Service 로그인${NC}"
echo "테스트용 사용자가 필요합니다. 먼저 회원가입을 진행하세요."
echo ""
echo "회원가입 예시:"
echo "curl -X POST $AUTH_URL/api/auth/register \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"username\":\"test_shop\",\"password\":\"password123\",\"role\":\"shop\"}'"
echo ""
read -p "사용자명을 입력하세요 (기본: test_shop): " USERNAME
USERNAME=${USERNAME:-test_shop}
read -p "비밀번호를 입력하세요 (기본: password123): " PASSWORD
PASSWORD=${PASSWORD:-password123}
read -p "역할을 입력하세요 (shop/spare, 기본: shop): " ROLE
ROLE=${ROLE:-shop}

echo ""
echo "로그인 시도 중..."
response=$(curl -s -w "\n%{http_code}" -X POST "$AUTH_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\",\"role\":\"$ROLE\"}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" == "200" ]; then
    TOKEN=$(echo "$body" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    if [ -z "$TOKEN" ]; then
        # 다른 형식 시도
        TOKEN=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('token', ''))" 2>/dev/null)
    fi
    
    if [ -n "$TOKEN" ]; then
        echo -e "${GREEN}✓ 로그인 성공${NC}"
        echo "Token: ${TOKEN:0:50}..."
        echo ""
    else
        echo -e "${RED}✗ 토큰을 찾을 수 없습니다${NC}"
        echo "Response: $body"
        exit 1
    fi
else
    echo -e "${RED}✗ 로그인 실패${NC}"
    echo "HTTP Status: $http_code"
    echo "Response: $body"
    exit 1
fi

# 2. 공고 생성 (shop 역할만)
if [ "$ROLE" == "shop" ]; then
    echo -e "${YELLOW}[2] 공고 생성 (POST /api/jobs)${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST "$JOB_URL/api/jobs" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{
        "title": "테스트 공고",
        "date": "2025-02-05",
        "time": "09:00",
        "end_time": "18:00",
        "amount": 50000,
        "energy": 10,
        "required_count": 1,
        "region_id": "seoul",
        "description": "테스트 공고 설명입니다",
        "is_urgent": false,
        "is_premium": false
      }')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    echo "HTTP Status: $http_code"
    echo "Response: $body" | head -20
    
    if [ "$http_code" == "201" ] || [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ 공고 생성 성공${NC}"
        JOB_ID=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('id', ''))" 2>/dev/null)
        if [ -n "$JOB_ID" ]; then
            echo "생성된 공고 ID: $JOB_ID"
        fi
    else
        echo -e "${RED}✗ 공고 생성 실패${NC}"
    fi
    echo ""
    
    # 3. 내 공고 목록 조회
    echo -e "${YELLOW}[3] 내 공고 목록 조회 (GET /api/jobs/my)${NC}"
    response=$(curl -s -w "\n%{http_code}" "$JOB_URL/api/jobs/my" \
      -H "Authorization: Bearer $TOKEN")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    echo "HTTP Status: $http_code"
    echo "Response: $body" | head -20
    
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ 내 공고 목록 조회 성공${NC}"
    else
        echo -e "${RED}✗ 내 공고 목록 조회 실패${NC}"
    fi
    echo ""
fi

# 4. 내 지원 목록 조회 (spare 역할만)
if [ "$ROLE" == "spare" ]; then
    echo -e "${YELLOW}[4] 내 지원 목록 조회 (GET /api/applications/my)${NC}"
    response=$(curl -s -w "\n%{http_code}" "$JOB_URL/api/applications/my" \
      -H "Authorization: Bearer $TOKEN")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    echo "HTTP Status: $http_code"
    echo "Response: $body" | head -20
    
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ 내 지원 목록 조회 성공${NC}"
    else
        echo -e "${RED}✗ 내 지원 목록 조회 실패${NC}"
    fi
    echo ""
fi

echo "=========================================="
echo "테스트 완료"
echo "=========================================="
