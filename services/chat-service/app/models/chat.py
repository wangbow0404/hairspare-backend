"""
Chat 및 Message 모델
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


class Chat(Base):
    __tablename__ = "Chat"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column("jobId", String, ForeignKey("Job.id", ondelete="CASCADE"), nullable=False)
    shop_id = Column("shopId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    spare_id = Column("spareId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    last_message_at = Column("lastMessageAt", DateTime, nullable=True)
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)
    updated_at = Column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("jobId", "shopId", "spareId", name="uq_chat_job_shop_spare"),
        Index("idx_chat_shop_id", "shopId"),
        Index("idx_chat_spare_id", "spareId"),
        Index("idx_chat_last_message_at", "lastMessageAt"),
    )


class Message(Base):
    __tablename__ = "Message"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column("chatId", String, ForeignKey("Chat.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column("senderId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    content = Column("content", String, nullable=False)
    is_read = Column("isRead", Boolean, default=False, nullable=False)
    is_filtered = Column("isFiltered", Boolean, default=False, nullable=False)
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_message_chat_id", "chatId"),
        Index("idx_message_sender_id", "senderId"),
        Index("idx_message_is_read", "isRead"),
        Index("idx_message_created_at", "createdAt"),
    )
