#!/bin/bash

# 사용 가능한 포트 찾기

START_PORT=8102
MAX_PORT=8200

for port in $(seq $START_PORT $MAX_PORT); do
    if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "사용 가능한 포트: $port"
        exit 0
    fi
done

echo "8102-8200 범위에서 사용 가능한 포트를 찾을 수 없습니다."
exit 1
