"""
API Gateway 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .middleware import setup_cors, AuthenticationMiddleware
from .routes import proxy
from .config import GATEWAY_PORT
import sys
import os

# shared 라이브러리 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))
from shared.exceptions.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from shared.exceptions.app_exceptions import AppException

# FastAPI 앱 생성
app = FastAPI(
    title="HairSpare API Gateway",
    description="HairSpare 마이크로서비스 API Gateway",
    version="1.0.0",
)

# CORS 설정
setup_cors(app)

# 인증 미들웨어 (선택적 - 필요시 활성화)
# app.add_middleware(AuthenticationMiddleware)

# 예외 핸들러 등록
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 라우터 등록
app.include_router(proxy.router)


@app.get("/")
async def root():
    """
    루트 엔드포인트
    """
    return {
        "service": "HairSpare API Gateway",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=GATEWAY_PORT)
