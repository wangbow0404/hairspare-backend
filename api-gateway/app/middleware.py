"""
API Gateway 미들웨어
CORS 및 인증 처리
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import sys
import os

# shared 라이브러리 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))
from shared.auth.jwt import verify_token
from shared.exceptions.app_exceptions import AuthenticationException
from .config import CORS_ORIGINS


def setup_cors(app):
    """
    CORS 미들웨어 설정
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    인증 미들웨어
    특정 경로는 인증을 건너뛰고, 나머지는 토큰 검증
    """
    
    # 인증이 필요 없는 경로
    PUBLIC_PATHS = [
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/find-id",
        "/api/auth/reset-password",
        "/api/auth/send-verification-code",
        "/api/auth/verify-code",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # OPTIONS 요청은 통과
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # 공개 경로는 인증 건너뛰기
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)
        
        # Authorization 헤더 확인
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 필요합니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Bearer 토큰 추출
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 인증 형식입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 토큰 검증
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 유효하지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 사용자 정보를 요청 상태에 저장
        request.state.user = payload
        
        return await call_next(request)
