"""
Energy Service 비즈니스 로직
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from shared.exceptions.app_exceptions import NotFoundException, ConflictException, AuthorizationException
from ..models.energy import EnergyWallet, EnergyTransaction, NoShowHistory


def get_energy_wallet(db: Session, user_id: str) -> EnergyWallet:
    """에너지 지갑 조회 또는 생성"""
    wallet = db.query(EnergyWallet).filter(EnergyWallet.user_id == user_id).first()
    
    if not wallet:
        # 지갑이 없으면 생성
        wallet = EnergyWallet(
            user_id=user_id,
            balance=0,
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    return wallet


def get_energy_transactions(
    db: Session,
    wallet_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[EnergyTransaction]:
    """에너지 거래 내역 조회"""
    return db.query(EnergyTransaction).filter(
        EnergyTransaction.wallet_id == wallet_id
    ).order_by(EnergyTransaction.timestamp.desc()).limit(limit).offset(offset).all()


def purchase_energy(db: Session, wallet_id: str, amount: int) -> EnergyTransaction:
    """에너지 구매"""
    wallet = db.query(EnergyWallet).filter(EnergyWallet.id == wallet_id).first()
    if not wallet:
        raise NotFoundException("에너지 지갑을 찾을 수 없습니다")
    
    # 에너지 거래 생성
    transaction = EnergyTransaction(
        wallet_id=wallet_id,
        amount=amount,
        state="available",
    )
    
    db.add(transaction)
    
    # 지갑 잔액 증가
    wallet.balance += amount
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


def lock_energy_for_job(db: Session, wallet_id: str, job_id: str, amount: int) -> EnergyTransaction:
    """공고 지원 시 에너지 잠금"""
    wallet = db.query(EnergyWallet).filter(EnergyWallet.id == wallet_id).first()
    if not wallet:
        raise NotFoundException("에너지 지갑을 찾을 수 없습니다")
    
    if wallet.balance < amount:
        raise ConflictException(f"에너지가 부족합니다. (필요: {amount}개, 보유: {wallet.balance}개)")
    
    # 에너지 거래 생성
    transaction = EnergyTransaction(
        wallet_id=wallet_id,
        job_id=job_id,
        amount=amount,
        state="locked",
    )
    
    db.add(transaction)
    
    # 지갑 잔액 차감
    wallet.balance -= amount
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


def return_energy_for_job(db: Session, wallet_id: str, job_id: str, amount: int) -> Optional[EnergyTransaction]:
    """근무 완료 시 에너지 반환"""
    wallet = db.query(EnergyWallet).filter(EnergyWallet.id == wallet_id).first()
    if not wallet:
        raise NotFoundException("에너지 지갑을 찾을 수 없습니다")
    
    # 잠금된 거래 찾기
    locked_transaction = db.query(EnergyTransaction).filter(
        EnergyTransaction.wallet_id == wallet_id,
        EnergyTransaction.job_id == job_id,
        EnergyTransaction.state == "locked"
    ).first()
    
    if locked_transaction:
        # 잠금 상태를 반환 상태로 변경
        locked_transaction.state = "returned"
    
    # 반환 거래 생성
    transaction = EnergyTransaction(
        wallet_id=wallet_id,
        job_id=job_id,
        amount=amount,
        state="returned",
    )
    
    db.add(transaction)
    
    # 지갑 잔액 증가
    wallet.balance += amount
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


def forfeit_energy_for_job(db: Session, wallet_id: str, job_id: str, amount: int) -> Optional[EnergyTransaction]:
    """노쇼 시 에너지 몰수"""
    wallet = db.query(EnergyWallet).filter(EnergyWallet.id == wallet_id).first()
    if not wallet:
        raise NotFoundException("에너지 지갑을 찾을 수 없습니다")
    
    # 잠금된 거래 찾기
    locked_transaction = db.query(EnergyTransaction).filter(
        EnergyTransaction.wallet_id == wallet_id,
        EnergyTransaction.job_id == job_id,
        EnergyTransaction.state == "locked"
    ).first()
    
    if locked_transaction:
        # 잠금 상태를 몰수 상태로 변경
        locked_transaction.state = "forfeited"
    
    # 몰수 거래 생성
    transaction = EnergyTransaction(
        wallet_id=wallet_id,
        job_id=job_id,
        amount=amount,
        state="forfeited",
    )
    
    db.add(transaction)
    
    # 노쇼 이력 추가
    no_show = NoShowHistory(
        wallet_id=wallet_id,
        job_id=job_id,
    )
    db.add(no_show)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


def get_no_show_history(
    db: Session,
    wallet_id: str,
    limit: int = 10
) -> List[NoShowHistory]:
    """노쇼 이력 조회"""
    return db.query(NoShowHistory).filter(
        NoShowHistory.wallet_id == wallet_id
    ).order_by(NoShowHistory.created_at.desc()).limit(limit).all()
