"""
공통 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BaseSchema(BaseModel):
    """
    기본 스키마 클래스
    """
    class Config:
        from_attributes = True  # SQLAlchemy 모델과 호환
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseSchema):
    """
    성공 응답 스키마
    """
    success: bool = Field(default=True)
    data: Optional[dict] = None
    error: Optional[dict] = None


class ErrorResponse(BaseSchema):
    """
    에러 응답 스키마
    """
    success: bool = Field(default=False)
    data: Optional[dict] = None
    error: dict = Field(..., description="에러 정보")


class PaginationParams(BaseSchema):
    """
    페이지네이션 파라미터
    """
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseSchema):
    """
    페이지네이션 응답 스키마
    """
    items: list = Field(..., description="항목 목록")
    total: int = Field(..., description="전체 항목 수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지당 항목 수")
    pages: int = Field(..., description="전체 페이지 수")
    
    @classmethod
    def create(cls, items: list, total: int, page: int, limit: int):
        pages = (total + limit - 1) // limit if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
