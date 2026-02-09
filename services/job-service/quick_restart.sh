#!/bin/bash

# Job Service 빠른 재시작 스크립트

PORT=8103

echo "포트 $PORT를 사용하는 프로세스 종료 중..."
PIDS=$(lsof -ti :$PORT 2>/dev/null)

if [ -n "$PIDS" ]; then
    echo "프로세스 ID: $PIDS"
    kill -9 $PIDS 2>/dev/null
    sleep 1
    echo "포트 $PORT 해제 완료"
else
    echo "포트 $PORT를 사용하는 프로세스가 없습니다."
fi

echo ""
echo "Job Service 시작 중..."
cd "$(dirname "$0")"
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/hairspare"
uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
