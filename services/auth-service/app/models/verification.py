"""
Verification 모델 (인증 정보)
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index, UniqueConstraint
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


class Verification(Base):
    """
    인증 정보 모델
    """
    __tablename__ = "Verification"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("User.id", ondelete="CASCADE"), unique=True, nullable=False)
    identity_verified = Column(Boolean, default=False, nullable=False)
    license_verified = Column(Boolean, default=False, nullable=False)
    verification_documents = Column(String, nullable=True)
    
    # PASS 본인인증 정보
    identity_name = Column(String, nullable=True)
    identity_phone = Column(String, nullable=True)
    identity_birth_date = Column(String, nullable=True)  # YYYYMMDD
    identity_gender = Column(String, nullable=True)  # "M" | "F"
    identity_verified_at = Column(DateTime, nullable=True)
    pass_transaction_id = Column(String, unique=True, nullable=True)
    
    # 면허 인증 정보
    license_number = Column(String, nullable=True)
    license_name = Column(String, nullable=True)
    license_image_url = Column(String, nullable=True)
    license_submitted_at = Column(DateTime, nullable=True)
    license_status = Column(String, nullable=True)  # "pending" | "approved" | "rejected" | "under_review"
    license_rejection_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # 관계
    user = relationship("User", backref="verification", uselist=False)

    # 인덱스
    __table_args__ = (
        Index("idx_verification_user_id", "user_id"),
        Index("idx_verification_pass_transaction_id", "pass_transaction_id"),
    )

    def __repr__(self):
        return f"<Verification(user_id={self.user_id}, identity_verified={self.identity_verified})>"
