#!/bin/bash

# 사용 가능한 포트 찾기

echo "=== 사용 가능한 포트 찾기 ==="

for port in 8102 8103 8104 8105 8201 8202; do
  if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✓ 포트 $port 사용 가능"
    echo ""
    echo "사용 방법:"
    echo "  export SERVICE_PORT=$port"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port $port --reload"
    echo ""
    echo "또는 .env 파일에 추가:"
    echo "  SERVICE_PORT=$port"
    exit 0
  else
    echo "✗ 포트 $port 사용 중"
  fi
done

echo "사용 가능한 포트를 찾지 못했습니다. 수동으로 포트를 선택하세요."
