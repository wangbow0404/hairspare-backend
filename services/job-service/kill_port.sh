#!/bin/bash

# 포트 8102를 사용하는 프로세스 종료

PORT=8102

echo "포트 $PORT를 사용하는 프로세스 확인 중..."
PIDS=$(lsof -ti :$PORT)

if [ -z "$PIDS" ]; then
    echo "포트 $PORT를 사용하는 프로세스가 없습니다."
    exit 0
fi

echo "다음 프로세스들이 포트 $PORT를 사용 중입니다:"
lsof -i :$PORT

echo ""
read -p "이 프로세스들을 종료하시겠습니까? (y/N): " CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "프로세스 종료 중..."
    kill -9 $PIDS
    sleep 1
    
    # 확인
    if lsof -ti :$PORT >/dev/null 2>&1; then
        echo "경고: 일부 프로세스가 아직 실행 중일 수 있습니다."
    else
        echo "포트 $PORT가 해제되었습니다."
    fi
else
    echo "취소되었습니다."
fi
