"""
API Gateway 설정
"""

import os
from typing import Dict
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 서비스 URL 설정 (환경변수에서 가져오거나 기본값 사용)
SERVICE_URLS: Dict[str, str] = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8101"),
    "job": os.getenv("JOB_SERVICE_URL", "http://localhost:8103"),
    "schedule": os.getenv("SCHEDULE_SERVICE_URL", "http://localhost:8104"),
    "chat": os.getenv("CHAT_SERVICE_URL", "http://localhost:8105"),
    "energy": os.getenv("ENERGY_SERVICE_URL", "http://localhost:8106"),
    "store": os.getenv("STORE_SERVICE_URL", "http://localhost:8107"),
    "cart": os.getenv("CART_SERVICE_URL", "http://localhost:8108"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://localhost:8109"),
    "payment": os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8110"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8111"),
}

# API Gateway 포트
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))

# CORS 설정
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8080"
).split(",")

# JWT 시크릿 키 (토큰 검증용)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
