"""
User 모델 (공통)
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON
from sqlalchemy.sql import func
from datetime import datetime
from ..base import Base


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

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
