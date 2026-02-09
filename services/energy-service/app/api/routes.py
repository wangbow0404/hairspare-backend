"""
Energy Service API 라우트
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from shared.database.session import get_db
from shared.responses.formats import success_response, error_response
from shared.auth.dependencies import get_current_user_dependency
from shared.exceptions.app_exceptions import NotFoundException, ConflictException, AuthorizationException
from ..schemas.energy import EnergyPurchaseRequest
from ..services.energy_service import (
    get_energy_wallet as get_energy_wallet_service,
    get_energy_transactions as get_energy_transactions_service,
    purchase_energy,
    lock_energy_for_job,
    return_energy_for_job,
    forfeit_energy_for_job,
    get_no_show_history,
)

router = APIRouter()


@router.get("/api/energy/wallet")
async def get_wallet(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """에너지 지갑 조회"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        wallet = get_energy_wallet_service(db, user_id)
        
        # 거래 내역 조회
        transactions = get_energy_transactions_service(db, wallet.id, limit=50)
        
        # 노쇼 이력 조회
        no_show_history = get_no_show_history(db, wallet.id, limit=10)
        
        wallet_data = {
            "id": wallet.id,
            "user_id": wallet.user_id,
            "balance": wallet.balance,
            "created_at": wallet.created_at.isoformat(),
            "updated_at": wallet.updated_at.isoformat(),
            "transactions": [
                {
                    "id": tx.id,
                    "wallet_id": tx.wallet_id,
                    "job_id": tx.job_id,
                    "amount": tx.amount,
                    "state": tx.state,
                    "timestamp": tx.timestamp.isoformat(),
                }
                for tx in transactions
            ],
            "no_show_history": [
                {
                    "id": ns.id,
                    "wallet_id": ns.wallet_id,
                    "job_id": ns.job_id,
                    "created_at": ns.created_at.isoformat(),
                }
                for ns in no_show_history
            ],
        }
        
        return success_response(wallet_data)
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"\n{'='*60}")
        print(f"[에너지 지갑 조회 오류] {error_detail}")
        print(f"{'='*60}")
        print(f"[Traceback]\n{traceback_str}")
        print(f"{'='*60}\n")
        return error_response(
            f"에너지 지갑 조회 중 오류가 발생했습니다: {error_detail}",
            "INTERNAL_ERROR",
            status_code=500
        )


@router.post("/api/energy/purchase")
async def purchase(
    request: EnergyPurchaseRequest,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """에너지 구매"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        wallet = get_energy_wallet_service(db, user_id)
        transaction = purchase_energy(db, wallet.id, request.amount)
        
        transaction_data = {
            "id": transaction.id,
            "wallet_id": transaction.wallet_id,
            "job_id": transaction.job_id,
            "amount": transaction.amount,
            "state": transaction.state,
            "timestamp": transaction.timestamp.isoformat(),
        }
        
        return success_response(transaction_data, status_code=201)
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except Exception as e:
        return error_response("에너지 구매 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/energy/lock")
async def lock(
    job_id: str,
    amount: int,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """에너지 잠금 (공고 지원 시)"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        wallet = get_energy_wallet_service(db, user_id)
        transaction = lock_energy_for_job(db, wallet.id, job_id, amount)
        
        transaction_data = {
            "id": transaction.id,
            "wallet_id": transaction.wallet_id,
            "job_id": transaction.job_id,
            "amount": transaction.amount,
            "state": transaction.state,
            "timestamp": transaction.timestamp.isoformat(),
        }
        
        return success_response(transaction_data, status_code=201)
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("에너지 잠금 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/energy/return")
async def return_energy(
    job_id: str,
    amount: int,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """에너지 반환 (근무 완료 시)"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        wallet = get_energy_wallet_service(db, user_id)
        transaction = return_energy_for_job(db, wallet.id, job_id, amount)
        
        if transaction:
            transaction_data = {
                "id": transaction.id,
                "wallet_id": transaction.wallet_id,
                "job_id": transaction.job_id,
                "amount": transaction.amount,
                "state": transaction.state,
                "timestamp": transaction.timestamp.isoformat(),
            }
            return success_response(transaction_data)
        else:
            return success_response({"message": "에너지가 반환되었습니다"})
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except Exception as e:
        return error_response("에너지 반환 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/energy/forfeit")
async def forfeit(
    job_id: str,
    amount: int,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """에너지 몰수 (노쇼 시)"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        wallet = get_energy_wallet_service(db, user_id)
        transaction = forfeit_energy_for_job(db, wallet.id, job_id, amount)
        
        if transaction:
            transaction_data = {
                "id": transaction.id,
                "wallet_id": transaction.wallet_id,
                "job_id": transaction.job_id,
                "amount": transaction.amount,
                "state": transaction.state,
                "timestamp": transaction.timestamp.isoformat(),
            }
            return success_response(transaction_data)
        else:
            return success_response({"message": "에너지가 몰수되었습니다"})
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except Exception as e:
        return error_response("에너지 몰수 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)
