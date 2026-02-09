"""
Energy 관련 Pydantic 스키마
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


class EnergyWalletResponse(BaseSchema):
    """에너지 지갑 응답 스키마"""
    id: str
    user_id: str
    balance: int
    created_at: datetime
    updated_at: datetime


class EnergyTransactionResponse(BaseSchema):
    """에너지 거래 응답 스키마"""
    id: str
    wallet_id: str
    job_id: Optional[str]
    amount: int
    state: str  # "available" | "locked" | "returned" | "forfeited"
    timestamp: datetime


class EnergyPurchaseRequest(BaseSchema):
    """에너지 구매 요청 스키마"""
    amount: int = Field(..., gt=0, description="구매할 에너지 개수")


class NoShowHistoryResponse(BaseSchema):
    """노쇼 이력 응답 스키마"""
    id: str
    wallet_id: str
    job_id: str
    created_at: datetime
