"""
Schedule 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
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


class ScheduleCreate(BaseSchema):
    """스케줄 생성 스키마"""
    job_id: str = Field(..., description="공고 ID")
    date: str = Field(..., description="YYYY-MM-DD 형식")
    start_time: str = Field(..., description="HH:mm 형식")
    end_time: Optional[str] = Field(None, description="HH:mm 형식")


class ScheduleUpdate(BaseSchema):
    """스케줄 수정 스키마"""
    date: Optional[str] = Field(None, description="YYYY-MM-DD 형식")
    start_time: Optional[str] = Field(None, description="HH:mm 형식")
    end_time: Optional[str] = Field(None, description="HH:mm 형식")
    status: Optional[str] = Field(None, description="scheduled | completed | cancelled")
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None


class ScheduleResponse(BaseSchema):
    """스케줄 응답 스키마"""
    id: str
    job_id: str
    spare_id: str
    shop_id: str
    date: str
    start_time: str
    end_time: Optional[str]
    status: str
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
