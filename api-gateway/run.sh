#!/bin/bash

# API Gateway 실행 스크립트

# PYTHONPATH 설정
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH

# 서비스 실행
cd "$(dirname "$0")"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
