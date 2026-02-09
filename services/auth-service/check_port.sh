#!/bin/bash

# 포트 사용 확인 및 해결 스크립트

PORT=8001

echo "=== 포트 $PORT 사용 확인 ==="

# 포트 사용 프로세스 확인
PROCESS=$(lsof -ti :$PORT 2>/dev/null)

if [ -z "$PROCESS" ]; then
  echo "✓ 포트 $PORT는 사용 가능합니다"
  exit 0
fi

echo "⚠ 포트 $PORT가 사용 중입니다"
echo ""
echo "사용 중인 프로세스:"
lsof -i :$PORT

echo ""
echo "해결 방법:"
echo "1. 프로세스 종료: kill $PROCESS"
echo "2. 다른 포트 사용: SERVICE_PORT=8101 uvicorn app.main:app --host 0.0.0.0 --port 8101 --reload"
echo ""

read -p "프로세스를 종료하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  kill $PROCESS
  echo "프로세스 종료됨"
  sleep 2
  echo "이제 서비스를 실행할 수 있습니다:"
  echo "  uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload"
fi
