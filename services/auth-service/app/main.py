"""
Auth Service 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# shared 라이브러리 경로 추가
# 현재 파일 위치: backend/services/auth-service/app/main.py
# shared 위치: backend/shared/
# 절대 경로로 backend 디렉토리 찾기
current_file = os.path.abspath(__file__)
# app/main.py -> services/auth-service/app/main.py -> backend/
backend_dir = os.path.abspath(os.path.join(current_file, "../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from shared.database.session import engine, get_db
from shared.exceptions.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from shared.exceptions.app_exceptions import AppException
from .api import routes
from .config import SERVICE_PORT

# FastAPI 앱 생성
app = FastAPI(
    title="HairSpare Auth Service",
    description="인증 및 사용자 관리 서비스",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 예외 핸들러 등록
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 라우터 등록
app.include_router(routes.router)


@app.get("/")
async def root():
    """
    루트 엔드포인트
    """
    return {
        "service": "HairSpare Auth Service",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
