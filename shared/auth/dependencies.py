"""
FastAPI 인증 의존성
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from .jwt import verify_token

security = HTTPBearer()


def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI 의존성: 현재 사용자 정보 추출
    
    사용 예:
        @app.get("/api/users/me")
        def get_me(current_user: dict = Depends(get_current_user_dependency)):
            return current_user
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def get_optional_user_dependency(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    선택적 인증 의존성 (인증되지 않은 사용자도 허용)
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    return payload
