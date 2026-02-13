"""
Schedule Service 비즈니스 로직
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Tuple
from datetime import datetime
import sys
import os
import httpx

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


def _get_job_energy(db: Session, job_id: str) -> int:
    """Job의 energy 수량 조회 (공유 DB)"""
    result = db.execute(text('SELECT energy FROM "Job" WHERE id = :job_id'), {"job_id": job_id})
    row = result.fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def check_in_schedule(
    db: Session,
    schedule_id: str,
    user_id: str,
    auth_header: Optional[str] = None,
) -> Schedule:
    """
    스케줄 체크인 (Spare만 가능)
    - check_in_time 설정, status=completed
    - Energy Service에 에너지 반환 요청
    """
    schedule = get_schedule_by_id(db, schedule_id)
    if not schedule:
        raise NotFoundException("스케줄을 찾을 수 없습니다")

    if schedule.spare_id != user_id:
        raise AuthorizationException("체크인은 해당 스케줄의 스페어만 가능합니다")

    if schedule.status != "scheduled":
        raise ConflictException("이미 완료되었거나 취소된 스케줄입니다")

    energy_amount = _get_job_energy(db, schedule.job_id)

    # Energy Service에 반환 요청 (스페어의 에너지 잠금 해제)
    if energy_amount > 0 and auth_header:
        from ..config import ENERGY_SERVICE_URL
        try:
            resp = httpx.post(
                f"{ENERGY_SERVICE_URL}/api/energy/return",
                params={"job_id": schedule.job_id, "amount": energy_amount},
                headers={"Authorization": auth_header},
                timeout=10.0,
            )
            if resp.status_code >= 400:
                print(f"[Schedule] Energy return 실패: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"[Schedule] Energy return 호출 실패: {e}")

    schedule.check_in_time = datetime.now()
    schedule.status = "completed"
    db.commit()
    db.refresh(schedule)
    return schedule


def confirm_schedule(
    db: Session,
    schedule_id: str,
    user_id: str,
    thumbs_up: bool = False,
) -> Tuple[Schedule, dict]:
    """
    근무 확인/정산 (Shop만 가능)
    - Shop이 스페어 근무 확인 시
    - thumbs_up: 따봉 (추후 ThumbsUp 테이블에 저장)
    - 에너지 반환은 Spare 체크인 시에만 처리 (Shop 확인은 완료 표시만)
    """
    schedule = get_schedule_by_id(db, schedule_id)
    if not schedule:
        raise NotFoundException("스케줄을 찾을 수 없습니다")

    if schedule.shop_id != user_id:
        raise AuthorizationException("근무 확인은 해당 스케줄의 매장만 가능합니다")

    if schedule.status == "cancelled":
        raise ConflictException("취소된 스케줄입니다")

    if schedule.status == "scheduled":
        schedule.check_in_time = schedule.check_in_time or datetime.now()
        schedule.status = "completed"

    db.commit()
    db.refresh(schedule)

    energy_amount = _get_job_energy(db, schedule.job_id)
    return schedule, {"amount": 0, "returnedEnergy": energy_amount if schedule.status == "completed" else 0}


def get_work_check_stats(db: Session, user_id: str) -> dict:
    """
    출근 체크 통계 (Spare용)
    - consecutiveDays: 최근 연속 출근 일수
    - energyFromWork: 근무로 받은 에너지 (체크인 완료 건 수 * 평균 등, 또는 별도 집계)
    """
    from datetime import timedelta
    from sqlalchemy import func

    schedules = (
        db.query(Schedule)
        .filter(Schedule.spare_id == user_id)
        .filter(Schedule.status == "completed")
        .filter(Schedule.check_in_time.isnot(None))
        .order_by(Schedule.check_in_time.desc())
        .all()
    )

    # 체크인 날짜별로 그룹화 (하루에 여러 건이어도 1일로)
    check_dates = set()
    for s in schedules:
        if s.check_in_time:
            check_dates.add(s.check_in_time.date())

    sorted_dates = sorted(check_dates, reverse=True)

    consecutive_days = 0
    today = datetime.now().date()
    expected = today
    for d in sorted_dates:
        if d == expected:
            consecutive_days += 1
            expected = expected - timedelta(days=1)
        else:
            break

    # energyFromWork: 체크인 완료한 일수 (1일 1에너지 가정, 또는 Job.energy 합계)
    energy_from_work = len(check_dates)

    return {"consecutiveDays": consecutive_days, "energyFromWork": energy_from_work}


def get_shop_work_check_stats(db: Session, shop_id: str) -> dict:
    """
    Shop VIP 등급 통계
    - totalCompleted: 완료한 스케줄 수
    - thumbsUpReceived: 받은 따봉 수 (추후 ThumbsUp 테이블 연동)
    - vipLevel: bronze | silver | gold | platinum | vip
    """
    from sqlalchemy import func

    total_completed = (
        db.query(func.count(Schedule.id))
        .filter(Schedule.shop_id == shop_id)
        .filter(Schedule.status == "completed")
        .scalar()
        or 0
    )

    # TODO: ThumbsUp 테이블 연동 시 thumbs_up_received 집계
    thumbs_up_received = 0

    # 등급 계산 (완료 스케줄 수 기준)
    tier = "bronze"
    if total_completed >= 500 or thumbs_up_received >= 1000:
        tier = "vip"
    elif total_completed >= 200 or thumbs_up_received >= 500:
        tier = "platinum"
    elif total_completed >= 50 or thumbs_up_received >= 100:
        tier = "gold"
    elif total_completed >= 10 or thumbs_up_received >= 20:
        tier = "silver"

    return {
        "totalCompleted": total_completed,
        "thumbsUpReceived": thumbs_up_received,
        "vipLevel": tier,
        "tier": tier,
        "nextCount": max(1, 10 - total_completed) if tier == "bronze" else 1,
        "progress": min(1.0, total_completed / 500.0) if tier != "vip" else 1.0,
    }
