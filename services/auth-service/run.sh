#!/bin/bash

# Auth Service 실행 스크립트

echo "=== Auth Service 시작 ==="

# PYTHONPATH 설정 (shared 모듈을 찾기 위해)
export PYTHONPATH=/Users/yoram/backend-new:$PYTHONPATH

# 환경 변수 로드
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# 의존성 확인 (선택사항 - 경고만 표시)
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
  echo "⚠️  가상 환경이 없습니다. (선택사항 - 시스템 Python 사용)"
  echo "   가상 환경을 만들려면: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi

# 서비스 실행
echo "서비스 시작 중... (포트: ${SERVICE_PORT:-8101})"
cd "$(dirname "$0")"
uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8101} --reload
