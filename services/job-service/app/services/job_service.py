"""
Job Service 비즈니스 로직
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime
import sys
import os
import httpx
import httpx

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from shared.exceptions.app_exceptions import NotFoundException, ConflictException, AuthorizationException
from ..models.job import Job, Application, Region
from ..schemas.job import JobCreate, JobUpdate


def get_jobs(
    db: Session,
    region_ids: Optional[List[str]] = None,
    is_urgent: Optional[bool] = None,
    is_premium: Optional[bool] = None,
    status: str = "published",
    limit: int = 50,
    offset: int = 0
) -> List[Job]:
    """공고 목록 조회"""
    query = db.query(Job).filter(Job.status == status)
    
    if region_ids:
        query = query.filter(Job.region_id.in_(region_ids))
    
    if is_urgent is not None:
        query = query.filter(Job.is_urgent == is_urgent)
    
    if is_premium is not None:
        query = query.filter(Job.is_premium == is_premium)
    
    # 노출 시간 체크 (필드가 있는 경우에만)
    # Prisma 스키마에는 exposureTime이 있지만 SQLAlchemy 모델에는 exposure_time으로 매핑됨
    # 필드가 없을 수 있으므로 try-except로 처리
    try:
        query = query.filter(
            or_(
                Job.exposure_time <= datetime.now(),
                Job.exposure_time.is_(None)
            )
        )
    except Exception:
        # exposure_time 필드가 없으면 필터링하지 않음
        pass
    
    return query.order_by(Job.created_at.desc()).limit(limit).offset(offset).all()


def get_job_by_id(db: Session, job_id: str) -> Optional[Job]:
    """ID로 공고 조회"""
    return db.query(Job).filter(Job.id == job_id).first()


def create_job(db: Session, shop_id: str, job_data: JobCreate) -> Job:
    """공고 생성"""
    job = Job(
        shop_id=shop_id,
        title=job_data.title,
        date=job_data.date,
        time=job_data.time,
        # end_time=job_data.end_time,  # 데이터베이스에 없음
        amount=job_data.amount,
        energy=job_data.energy,
        required_count=job_data.required_count,
        region_id=job_data.region_id,
        # description=job_data.description,  # 데이터베이스에 없음
        # requirements=job_data.requirements,  # 데이터베이스에 없음
        # images=job_data.images or [],  # 데이터베이스에 없음
        is_urgent=job_data.is_urgent,
        is_premium=job_data.is_premium,
        status="published",
        exposure_time=datetime.now(),  # TODO: 노출 정책에 따라 설정
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job


def update_job(db: Session, job_id: str, shop_id: str, job_data: JobUpdate) -> Job:
    """공고 수정"""
    job = get_job_by_id(db, job_id)
    if not job:
        raise NotFoundException("공고를 찾을 수 없습니다")
    
    if job.shop_id != shop_id:
        raise AuthorizationException("공고를 수정할 권한이 없습니다")
    
    update_data = job_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
    
    db.commit()
    db.refresh(job)
    
    return job


def delete_job(db: Session, job_id: str, shop_id: str) -> None:
    """공고 삭제"""
    job = get_job_by_id(db, job_id)
    if not job:
        raise NotFoundException("공고를 찾을 수 없습니다")
    
    if job.shop_id != shop_id:
        raise AuthorizationException("공고를 삭제할 권한이 없습니다")
    
    db.delete(job)
    db.commit()


def apply_to_job(db: Session, job_id: str, spare_id: str, auth_header: Optional[str] = None) -> Application:
    """공고 지원 + 에너지 잠금"""
    job = get_job_by_id(db, job_id)
    if not job:
        raise NotFoundException("공고를 찾을 수 없습니다")
    
    # 중복 지원 체크
    existing = db.query(Application).filter(
        and_(Application.job_id == job_id, Application.spare_id == spare_id)
    ).first()
    
    if existing:
        raise ConflictException("이미 지원한 공고입니다")
    
    energy_locked = False
    if job.energy > 0 and auth_header:
        from ..config import ENERGY_SERVICE_URL
        try:
            resp = httpx.post(
                f"{ENERGY_SERVICE_URL}/api/energy/lock",
                params={"job_id": job_id, "amount": job.energy},
                headers={"Authorization": auth_header},
                timeout=10.0,
            )
            if resp.status_code in (200, 201):
                energy_locked = True
            elif resp.status_code == 409:
                raise ConflictException("에너지 잔액이 부족합니다")
            else:
                raise ConflictException("에너지 잠금에 실패했습니다")
        except ConflictException:
            raise
        except Exception as e:
            raise ConflictException(f"에너지 잠금 중 오류: {str(e)}")
    
    application = Application(
        job_id=job_id,
        spare_id=spare_id,
        status="pending",
        energy_locked=energy_locked,
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application


def get_applications_for_shop(db: Session, shop_id: str) -> List[Application]:
    """매장의 공고에 대한 지원 목록 (Application + Job join)"""
    return (
        db.query(Application)
        .join(Job, Application.job_id == Job.id)
        .filter(Job.shop_id == shop_id)
        .order_by(Application.created_at.desc())
        .all()
    )


def approve_application(
    db: Session,
    application_id: str,
    shop_id: str,
    auth_header: Optional[str] = None,
) -> Application:
    """지원 승인 + 스케줄 생성"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise NotFoundException("지원을 찾을 수 없습니다")
    
    job = get_job_by_id(db, application.job_id)
    if not job or job.shop_id != shop_id:
        raise AuthorizationException("해당 지원을 승인할 권한이 없습니다")
    
    if application.status != "pending":
        raise ConflictException("이미 처리된 지원입니다")
    
    application.status = "approved"
    db.commit()
    
    # Schedule Service에 스케줄 생성 요청
    from ..config import SCHEDULE_SERVICE_URL
    try:
        end_time = None
        if job.time:
            parts = job.time.split(":")
            if len(parts) >= 2:
                h, m = int(parts[0]), int(parts[1])
                end_h = (h + 1) % 24
                end_time = f"{end_h:02d}:{m:02d}"
        body = {
            "job_id": job.id,
            "spare_id": application.spare_id,
            "shop_id": job.shop_id,
            "date": job.date,
            "start_time": job.time,
            "end_time": end_time or job.time,
        }
        headers = {"Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header
        resp = httpx.post(
            f"{SCHEDULE_SERVICE_URL}/api/schedules",
            json=body,
            headers=headers,
            timeout=10.0,
        )
        if resp.status_code not in (200, 201):
            print(f"[Job] Schedule 생성 실패: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[Job] Schedule 생성 오류: {e}")
    
    db.refresh(application)
    return application


def reject_application(db: Session, application_id: str, shop_id: str) -> Application:
    """지원 거절 (에너지 잠금 시 반환은 Energy Service에서 처리 - 추후)"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise NotFoundException("지원을 찾을 수 없습니다")
    
    job = get_job_by_id(db, application.job_id)
    if not job or job.shop_id != shop_id:
        raise AuthorizationException("해당 지원을 거절할 권한이 없습니다")
    
    if application.status != "pending":
        raise ConflictException("이미 처리된 지원입니다")
    
    application.status = "rejected"
    db.commit()
    db.refresh(application)
    return application


def get_user_jobs(db: Session, shop_id: str) -> List[Job]:
    """사용자의 공고 목록"""
    return db.query(Job).filter(Job.shop_id == shop_id).order_by(Job.created_at.desc()).all()


def get_user_applications(db: Session, spare_id: str) -> List[Application]:
    """사용자의 지원 목록"""
    return db.query(Application).filter(Application.spare_id == spare_id).order_by(Application.created_at.desc()).all()
