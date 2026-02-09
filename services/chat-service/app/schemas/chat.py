"""
Chat 관련 Pydantic 스키마
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


class ChatResponse(BaseSchema):
    """채팅방 응답 스키마"""
    id: str
    job_id: str
    shop_id: str
    spare_id: str
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseSchema):
    """메시지 생성 스키마"""
    content: str = Field(..., min_length=1, max_length=1000)


class MessageResponse(BaseSchema):
    """메시지 응답 스키마"""
    id: str
    chat_id: str
    sender_id: str
    content: str
    is_read: bool
    is_filtered: bool
    created_at: datetime
