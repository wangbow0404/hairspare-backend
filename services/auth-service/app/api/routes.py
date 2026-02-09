"""
Auth Service API 라우트
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from shared.database.session import get_db
from shared.responses.formats import success_response, error_response
from shared.auth.dependencies import get_current_user_dependency
from shared.exceptions.app_exceptions import (
    AuthenticationException,
    NotFoundException,
    ConflictException,
)
from ..schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
    ChangePasswordRequest,
    FindIdRequest,
    ResetPasswordRequest,
)
from ..services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_id,
    update_user_password,
    get_user_by_identifier,
)
from ..models.user import User
from shared.auth.jwt import create_access_token

router = APIRouter()


@router.post("/api/auth/register", status_code=201)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    회원가입
    """
    try:
        user = create_user(db, request)
        
        # TODO: 에너지 지갑 생성 (spare만) - Energy Service 호출
        # TODO: 구독 생성 (shop만) - Payment Service 호출
        
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            name=user.name,
            phone=user.phone,
            profile_image=user.profile_image,
            created_at=user.created_at,
        )
        
        return success_response(
            {
                "user": user_response.model_dump(),
                "message": "회원가입이 완료되었습니다",
            },
            status_code=201
        )
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("회원가입 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/auth/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    로그인
    """
    user = authenticate_user(db, request.username, request.password)
    
    if not user:
        return error_response(
            "이메일 또는 비밀번호가 올바르지 않습니다",
            "INVALID_CREDENTIALS",
            status_code=401
        )
    
    # JWT 토큰 생성
    token_data = {
        "sub": user.id,
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
    }
    token = create_access_token(token_data)
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        name=user.name,
        phone=user.phone,
        profile_image=user.profile_image,
        created_at=user.created_at,
    )
    
    return success_response({
        "message": "로그인 성공",
        "user": user_response.model_dump(),
        "token": token,
    })


@router.get("/api/auth/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    현재 사용자 정보 조회
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    if not user_id:
        return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
    
    user = get_user_by_id(db, user_id)
    if not user:
        return error_response("사용자를 찾을 수 없습니다", "NOT_FOUND", status_code=404)
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        name=user.name,
        phone=user.phone,
        profile_image=user.profile_image,
        created_at=user.created_at,
    )
    
    return success_response(user_response.model_dump())


@router.post("/api/auth/logout")
async def logout():
    """
    로그아웃 (클라이언트에서 토큰 삭제)
    """
    return success_response({"message": "로그아웃되었습니다"})


@router.post("/api/auth/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    비밀번호 변경
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    user = get_user_by_id(db, user_id)
    
    if not user:
        return error_response("사용자를 찾을 수 없습니다", "NOT_FOUND", status_code=404)
    
    # 현재 비밀번호 확인
    from ..services.auth_service import verify_password
    if not verify_password(request.current_password, user.password):
        return error_response("현재 비밀번호가 올바르지 않습니다", "INVALID_PASSWORD", status_code=400)
    
    # 비밀번호 변경
    update_user_password(db, user_id, request.new_password)
    
    return success_response({"message": "비밀번호가 변경되었습니다"})


@router.post("/api/auth/find-id")
async def find_id(
    request: FindIdRequest,
    db: Session = Depends(get_db)
):
    """
    아이디 찾기
    """
    # TODO: 이메일 또는 전화번호로 사용자 조회 및 아이디 반환
    return error_response("아직 구현되지 않았습니다", "NOT_IMPLEMENTED", status_code=501)


@router.post("/api/auth/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    비밀번호 재설정
    """
    # TODO: 인증번호 확인 후 비밀번호 재설정
    return error_response("아직 구현되지 않았습니다", "NOT_IMPLEMENTED", status_code=501)


@router.post("/api/auth/send-verification-code")
async def send_verification_code(
    request: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    인증번호 발송
    """
    # TODO: 전화번호로 인증번호 발송
    return error_response("아직 구현되지 않았습니다", "NOT_IMPLEMENTED", status_code=501)


@router.post("/api/auth/verify-code")
async def verify_code(
    request: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    인증번호 확인
    """
    # TODO: 인증번호 확인
    return error_response("아직 구현되지 않았습니다", "NOT_IMPLEMENTED", status_code=501)


@router.get("/health")
async def health_check():
    """
    헬스 체크
    """
    return {"status": "ok", "service": "auth-service"}
