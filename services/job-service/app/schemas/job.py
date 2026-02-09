"""
Job 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from shared.schemas.base import BaseSchema


class JobCreate(BaseSchema):
    """공고 생성 스키마"""
    title: str = Field(..., min_length=1, max_length=200)
    date: str = Field(..., description="YYYY-MM-DD 형식")
    time: str = Field(..., description="HH:mm 형식")
    end_time: Optional[str] = Field(None, description="HH:mm 형식")
    amount: int = Field(..., ge=0)
    energy: int = Field(..., ge=0)
    required_count: int = Field(..., ge=1)
    region_id: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    images: Optional[List[str]] = Field(default_factory=list, max_items=5)
    is_urgent: bool = False
    is_premium: bool = False


class JobUpdate(BaseSchema):
    """공고 수정 스키마"""
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    end_time: Optional[str] = None
    amount: Optional[int] = None
    energy: Optional[int] = None
    required_count: Optional[int] = None
    region_id: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    images: Optional[List[str]] = None
    is_urgent: Optional[bool] = None
    is_premium: Optional[bool] = None
    status: Optional[str] = None


class JobResponse(BaseSchema):
    """공고 응답 스키마"""
    id: str
    shop_id: str
    shop_name: Optional[str] = None
    title: str
    date: str
    time: str
    end_time: Optional[str] = None
    amount: int
    energy: int
    required_count: int
    region_id: str
    region_name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    images: Optional[List[str]] = None
    is_urgent: bool
    is_premium: bool
    status: str
    created_at: datetime
    updated_at: datetime


class ApplicationResponse(BaseSchema):
    """지원 응답 스키마"""
    id: str
    job_id: str
    spare_id: str
    spare_name: Optional[str] = None
    status: str
    energy_locked: bool
    created_at: datetime
