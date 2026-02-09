"""
Schedule Service 비즈니스 로직
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
from ..models.schedule import Schedule
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate


def get_schedules(
    db: Session,
    spare_id: Optional[str] = None,
    shop_id: Optional[str] = None,
    status: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Schedule]:
    """스케줄 목록 조회"""
    query = db.query(Schedule)
    
    if spare_id:
        query = query.filter(Schedule.spare_id == spare_id)
    
    if shop_id:
        query = query.filter(Schedule.shop_id == shop_id)
    
    if status:
        query = query.filter(Schedule.status == status)
    
    if date:
        query = query.filter(Schedule.date == date)
    
    return query.order_by(Schedule.date.desc(), Schedule.start_time.desc()).limit(limit).offset(offset).all()


def get_schedule_by_id(db: Session, schedule_id: str) -> Optional[Schedule]:
    """ID로 스케줄 조회"""
    return db.query(Schedule).filter(Schedule.id == schedule_id).first()


def create_schedule(db: Session, job_id: str, spare_id: str, shop_id: str, schedule_data: ScheduleCreate) -> Schedule:
    """스케줄 생성"""
    schedule = Schedule(
        job_id=job_id,
        spare_id=spare_id,
        shop_id=shop_id,
        date=schedule_data.date,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        status="scheduled",
    )
    
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    return schedule


def update_schedule(db: Session, schedule_id: str, user_id: str, schedule_data: ScheduleUpdate) -> Schedule:
    """스케줄 수정"""
    schedule = get_schedule_by_id(db, schedule_id)
    if not schedule:
        raise NotFoundException("스케줄을 찾을 수 없습니다")
    
    # 권한 확인 (spare 또는 shop만 수정 가능)
    if schedule.spare_id != user_id and schedule.shop_id != user_id:
        raise AuthorizationException("스케줄을 수정할 권한이 없습니다")
    
    update_data = schedule_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


def cancel_schedule(db: Session, schedule_id: str, user_id: str) -> Schedule:
    """스케줄 취소"""
    schedule = get_schedule_by_id(db, schedule_id)
    if not schedule:
        raise NotFoundException("스케줄을 찾을 수 없습니다")
    
    # 권한 확인 (spare만 취소 가능)
    if schedule.spare_id != user_id:
        raise AuthorizationException("스케줄을 취소할 권한이 없습니다")
    
    # 이미 완료되거나 취소된 스케줄은 취소 불가
    if schedule.status == "completed" or schedule.status == "cancelled":
        raise ConflictException("이미 완료되거나 취소된 스케줄입니다")
    
    schedule.status = "cancelled"
    db.commit()
    db.refresh(schedule)
    
    return schedule


def get_user_schedules(db: Session, user_id: str, role: str) -> List[Schedule]:
    """사용자의 스케줄 목록"""
    if role == "spare":
        return db.query(Schedule).filter(Schedule.spare_id == user_id).order_by(Schedule.date.desc(), Schedule.start_time.desc()).all()
    elif role == "shop":
        return db.query(Schedule).filter(Schedule.shop_id == user_id).order_by(Schedule.date.desc(), Schedule.start_time.desc()).all()
    else:
        return []
