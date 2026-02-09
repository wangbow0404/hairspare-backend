"""
공통 예외 처리
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .app_exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException):
    """
    커스텀 AppException 핸들러
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "message": exc.message,
                "code": exc.code or "APP_ERROR"
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTPException 핸들러
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "message": exc.detail,
                "code": f"HTTP_{exc.status_code}"
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    요청 검증 오류 핸들러
    """
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "error": {
                "message": "; ".join(error_messages),
                "code": "VALIDATION_ERROR"
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    일반 예외 핸들러 (마지막 방어선)
    """
    import traceback
    import os
    
    # 개발 환경에서는 상세한 에러 정보 제공
    if os.getenv("ENVIRONMENT") == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": {
                    "message": str(exc),
                    "code": "INTERNAL_ERROR",
                    "traceback": traceback.format_exc()
                }
            }
        )
    
    # 프로덕션 환경에서는 일반적인 에러 메시지만 제공
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "error": {
                "message": "서버 오류가 발생했습니다",
                "code": "INTERNAL_ERROR"
            }
        }
    )
