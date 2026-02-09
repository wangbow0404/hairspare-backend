"""
인증 서비스 비즈니스 로직
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from passlib.context import CryptContext
from typing import Optional
import secrets
import string
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from shared.auth.jwt import create_access_token
from shared.exceptions.app_exceptions import (
    AuthenticationException,
    NotFoundException,
    ConflictException,
    ValidationException,
)
from ..models.user import User
from ..schemas.auth import RegisterRequest, LoginRequest

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱
    """
    return pwd_context.hash(password)


def generate_referral_code() -> str:
    """
    고유 추천 코드 생성 (8자리 대문자+숫자)
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """
    사용자명 또는 이메일로 사용자 조회
    """
    # 먼저 username으로 검색
    user = db.query(User).filter(User.username == identifier).first()
    
    # username으로 찾지 못한 경우 email로 검색
    if not user:
        user = db.query(User).filter(User.email == identifier).first()
    
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    사용자 인증
    """
    user = get_user_by_identifier(db, username)
    
    if not user:
        return None
    
    if not verify_password(password, user.password):
        return None
    
    return user


def create_user(db: Session, user_data: RegisterRequest) -> User:
    """
    사용자 생성
    """
    # 아이디 중복 체크
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise ConflictException("이미 등록된 아이디입니다")
    
    # 이메일 중복 체크 (이메일이 제공된 경우)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise ConflictException("이미 사용 중인 이메일입니다")
    
    # 고유 추천 코드 생성
    referral_code = None
    max_attempts = 10
    for _ in range(max_attempts):
        code = generate_referral_code()
        existing_code = db.query(User).filter(User.referral_code == code).first()
        if not existing_code:
            referral_code = code
            break
    
    if not referral_code:
        raise ValidationException("추천 코드 생성에 실패했습니다")
    
    # 비밀번호 해싱
    hashed_password = get_password_hash(user_data.password)
    
    # 사용자 생성
    user = User(
        username=user_data.username,
        password=hashed_password,
        role=user_data.role,
        email=user_data.email,
        name=user_data.name,
        phone=user_data.phone,
        referral_code=referral_code,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    ID로 사용자 조회
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user_password(db: Session, user_id: str, new_password: str) -> User:
    """
    사용자 비밀번호 변경
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("사용자를 찾을 수 없습니다")
    
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    
    return user
