"""
Schedule 모델
"""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from shared.database.base import Base


class Schedule(Base):
    __tablename__ = "Schedule"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column("jobId", String, ForeignKey("Job.id", ondelete="CASCADE"), nullable=False)
    spare_id = Column("spareId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    shop_id = Column("shopId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    date = Column("date", String, nullable=False)  # YYYY-MM-DD
    start_time = Column("startTime", String, nullable=False)  # HH:mm
    end_time = Column("endTime", String, nullable=True)  # HH:mm
    status = Column("status", String, default="scheduled", nullable=False)  # "scheduled" | "completed" | "cancelled"
    check_in_time = Column("checkInTime", DateTime, nullable=True)
    check_out_time = Column("checkOutTime", DateTime, nullable=True)
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)
    updated_at = Column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_schedule_job_id", "jobId"),
        Index("idx_schedule_spare_id", "spareId"),
        Index("idx_schedule_shop_id", "shopId"),
        Index("idx_schedule_date", "date"),
        Index("idx_schedule_status", "status"),
    )
