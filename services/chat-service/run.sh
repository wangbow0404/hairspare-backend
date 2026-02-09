#!/bin/bash

# Chat Service 실행 스크립트

# PYTHONPATH 설정
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH

# DATABASE_URL 설정
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/hairspare"

# 서비스 실행
cd "$(dirname "$0")"
uvicorn app.main:app --host 0.0.0.0 --port 8105 --reload
