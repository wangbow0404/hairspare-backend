"""
인증 관련 Pydantic 스키마
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from shared.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    """
    로그인 요청 스키마
    """
    username: str = Field(..., description="사용자명 또는 이메일")
    password: str = Field(..., min_length=1, description="비밀번호")
    role: Optional[str] = Field(None, description="역할 (선택사항)")


class RegisterRequest(BaseSchema):
    """
    회원가입 요청 스키마
    """
    username: str = Field(..., min_length=3, max_length=50, description="사용자명")
    password: str = Field(..., min_length=8, description="비밀번호")
    role: str = Field(..., description="역할: spare, shop, seller")
    email: Optional[EmailStr] = Field(None, description="이메일")
    name: Optional[str] = Field(None, max_length=100, description="이름")
    phone: Optional[str] = Field(None, description="전화번호")
    referral_code: Optional[str] = Field(None, description="추천 코드")

    @validator("role")
    def validate_role(cls, v):
        if v not in ["spare", "shop", "seller"]:
            raise ValueError("역할은 spare, shop, seller 중 하나여야 합니다")
        return v


class UserResponse(BaseSchema):
    """
    사용자 응답 스키마
    """
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    role: str
    name: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime


class LoginResponse(BaseSchema):
    """
    로그인 응답 스키마
    """
    message: str
    user: UserResponse
    token: Optional[str] = None


class RegisterResponse(BaseSchema):
    """
    회원가입 응답 스키마
    """
    user: UserResponse
    message: str


class ChangePasswordRequest(BaseSchema):
    """
    비밀번호 변경 요청 스키마
    """
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., min_length=8, description="새 비밀번호")


class FindIdRequest(BaseSchema):
    """
    아이디 찾기 요청 스키마
    """
    email: EmailStr = Field(..., description="이메일")
    phone: Optional[str] = Field(None, description="전화번호")


class ResetPasswordRequest(BaseSchema):
    """
    비밀번호 재설정 요청 스키마
    """
    username: str = Field(..., description="사용자명")
    email: EmailStr = Field(..., description="이메일")
    new_password: str = Field(..., min_length=8, description="새 비밀번호")
    verification_code: str = Field(..., description="인증번호")


class SendVerificationCodeRequest(BaseSchema):
    """
    인증번호 발송 요청 스키마
    """
    phone: str = Field(..., description="전화번호")


class VerifyCodeRequest(BaseSchema):
    """
    인증번호 확인 요청 스키마
    """
    phone: str = Field(..., description="전화번호")
    code: str = Field(..., description="인증번호")
