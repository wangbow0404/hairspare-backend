"""
Energy 관련 모델
"""

import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index, UniqueConstraint
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


class EnergyWallet(Base):
    __tablename__ = "EnergyWallet"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column("userId", String, ForeignKey("User.id", ondelete="CASCADE"), unique=True, nullable=False)
    balance = Column("balance", Integer, default=0, nullable=False)
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)
    updated_at = Column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_energy_wallet_user_id", "userId"),
    )


class EnergyTransaction(Base):
    __tablename__ = "EnergyTransaction"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_id = Column("walletId", String, ForeignKey("EnergyWallet.id", ondelete="CASCADE"), nullable=False)
    job_id = Column("jobId", String, ForeignKey("Job.id", ondelete="SET NULL"), nullable=True)
    amount = Column("amount", Integer, nullable=False)
    state = Column("state", String, nullable=False)  # "available" | "locked" | "returned" | "forfeited"
    timestamp = Column("timestamp", DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_energy_transaction_wallet_id", "walletId"),
        Index("idx_energy_transaction_job_id", "jobId"),
        Index("idx_energy_transaction_state", "state"),
        Index("idx_energy_transaction_timestamp", "timestamp"),
    )


class NoShowHistory(Base):
    __tablename__ = "NoShowHistory"
    
    # Prisma는 camelCase를 사용하므로 컬럼명을 명시적으로 매핑
    id = Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_id = Column("walletId", String, ForeignKey("EnergyWallet.id", ondelete="CASCADE"), nullable=False)
    job_id = Column("jobId", String, nullable=False)
    created_at = Column("createdAt", DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_no_show_history_wallet_id", "walletId"),
        Index("idx_no_show_history_job_id", "jobId"),
    )
