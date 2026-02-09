#!/bin/bash

# 데이터베이스 설정 스크립트

echo "=== HairSpare 데이터베이스 설정 ==="

# PostgreSQL 서버 시작
echo "1. PostgreSQL 서버 시작 중..."
brew services start postgresql@14 2>/dev/null || pg_ctl -D /usr/local/var/postgres start 2>/dev/null || echo "PostgreSQL 서버를 수동으로 시작해주세요"

# 잠시 대기
sleep 2

# 데이터베이스 생성
echo "2. 데이터베이스 생성 중..."
createdb hairspare 2>/dev/null && echo "✓ 데이터베이스 'hairspare' 생성 완료" || echo "⚠ 데이터베이스가 이미 존재하거나 생성 실패"

# 연결 테스트
echo "3. 데이터베이스 연결 테스트..."
psql -d hairspare -c "SELECT version();" > /dev/null 2>&1 && echo "✓ 데이터베이스 연결 성공!" || echo "✗ 데이터베이스 연결 실패"

echo ""
echo "=== 설정 완료 ==="
echo "다음 명령어로 마이그레이션을 실행하세요:"
echo "  alembic revision --autogenerate -m 'Initial migration'"
echo "  alembic upgrade head"
