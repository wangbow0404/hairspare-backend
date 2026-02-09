"""
User 모델
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from shared.database.base import Base


class User(Base):
    """
    사용자 모델
    """
    __tablename__ = "User"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "spare" | "shop" | "seller"
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    birth_year = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # "M" | "F"
    profile_image = Column(String, nullable=True)
    referral_code = Column(String, unique=True, nullable=True)
    contact_warning_count = Column(Integer, nullable=True, default=0)
    contact_warning_updated_at = Column(DateTime, nullable=True)
    is_banned = Column(Boolean, nullable=True, default=False)
    banned_at = Column(DateTime, nullable=True)
    ban_reason = Column(String, nullable=True)
    notification_settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # 인덱스
    __table_args__ = (
        Index("idx_user_username", "username"),
        Index("idx_user_email", "email"),
        Index("idx_user_role", "role"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
