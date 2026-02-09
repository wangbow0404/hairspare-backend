"""
Job 및 Application 모델
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ARRAY, ForeignKey, Index, UniqueConstraint
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


class Region(Base):
    __tablename__ = "Region"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column("name", String, nullable=False)
    code = Column("code", String, unique=True, nullable=True)
    parent_id = Column("parentId", String, ForeignKey("Region.id"), nullable=True)
    type = Column("type", String, nullable=False)  # "province" | "city" | "district"
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)


class Job(Base):
    __tablename__ = "Job"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    # 실제 데이터베이스에 존재하는 컬럼만 정의
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = Column("shopId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    title = Column("title", String, nullable=False)
    date = Column("date", String, nullable=False)  # YYYY-MM-DD
    time = Column("time", String, nullable=False)  # HH:mm
    # endTime, description, requirements, images 컬럼은 데이터베이스에 없으므로 제외
    amount = Column("amount", Integer, nullable=False)
    energy = Column("energy", Integer, nullable=False)
    required_count = Column("requiredCount", Integer, nullable=False)
    region_id = Column("regionId", String, ForeignKey("Region.id"), nullable=False)
    is_urgent = Column("isUrgent", Boolean, default=False, nullable=False)
    is_premium = Column("isPremium", Boolean, default=False, nullable=False)
    status = Column("status", String, default="draft", nullable=False)  # "draft" | "published" | "closed"
    exposure_policy = Column("exposurePolicy", String, nullable=True)
    exposure_time = Column("exposureTime", DateTime, nullable=True)
    countdown = Column("countdown", Integer, nullable=True)
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)
    updated_at = Column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_job_shop_id", "shopId"),
        Index("idx_job_region_id", "regionId"),
        Index("idx_job_is_urgent", "isUrgent"),
        Index("idx_job_is_premium", "isPremium"),
        Index("idx_job_status", "status"),
        Index("idx_job_exposure_time", "exposureTime"),
        Index("idx_job_created_at", "createdAt"),
    )


class Application(Base):
    __tablename__ = "Application"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column("jobId", String, ForeignKey("Job.id", ondelete="CASCADE"), nullable=False)
    spare_id = Column("spareId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    status = Column("status", String, default="pending", nullable=False)  # "pending" | "approved" | "rejected"
    energy_locked = Column("energyLocked", Boolean, default=False, nullable=False)
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)
    updated_at = Column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("jobId", "spareId", name="uq_job_spare"),
        Index("idx_application_job_id", "jobId"),
        Index("idx_application_spare_id", "spareId"),
        Index("idx_application_status", "status"),
    )
