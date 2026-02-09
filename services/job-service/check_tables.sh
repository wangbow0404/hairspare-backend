#!/bin/bash

# 데이터베이스 테이블 확인 스크립트

echo "=========================================="
echo "데이터베이스 테이블 확인"
echo "=========================================="
echo ""

# 사용자명 가져오기
USER=$(whoami)

echo "데이터베이스 연결 정보:"
echo "  사용자: $USER"
echo "  데이터베이스: hairspare"
echo ""

# 모든 테이블 목록
echo "[1] 모든 테이블 목록:"
psql -U "$USER" -d hairspare -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
" 2>&1

echo ""
echo "[2] Job 관련 테이블:"
psql -U "$USER" -d hairspare -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND (table_name ILIKE '%job%' OR table_name ILIKE '%Job%')
ORDER BY table_name;
" 2>&1

echo ""
echo "[3] Job 테이블 컬럼 (존재하는 경우):"
psql -U "$USER" -d hairspare -c "
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name IN ('Job', 'job')
ORDER BY ordinal_position;
" 2>&1

echo ""
echo "=========================================="
echo "확인 완료"
echo "=========================================="
