"""
Schedule Service 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from shared.exceptions.handlers import app_exception_handler, general_exception_handler
from shared.exceptions.app_exceptions import AppException
from .api import routes
from .config import SERVICE_PORT

app = FastAPI(
    title="HairSpare Schedule Service",
    description="스케줄 관리 서비스",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "service": "HairSpare Schedule Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "schedule-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
