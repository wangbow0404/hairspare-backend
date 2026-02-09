#!/bin/bash

# Auth Service 실행 스크립트

echo "=== Auth Service 시작 ==="

# 환경 변수 로드
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# 의존성 확인
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
  echo "가상 환경이 없습니다. 의존성을 설치하세요:"
  echo "  pip install -r requirements.txt"
fi

# 서비스 실행
echo "서비스 시작 중... (포트: ${SERVICE_PORT:-8001})"
uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8001} --reload
