"""
Job Service API 라우트
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List
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
from ..schemas.job import JobCreate, JobUpdate, JobResponse, ApplicationResponse
from ..services.job_service import (
    get_jobs as get_jobs_service,
    get_job_by_id,
    create_job as create_job_service,
    update_job,
    delete_job,
    apply_to_job as apply_to_job_service,
    get_user_jobs,
    get_user_applications,
    get_applications_for_shop,
    approve_application as approve_application_service,
    reject_application as reject_application_service,
)

router = APIRouter()


@router.get("/api/jobs")
async def get_jobs(
    region_ids: Optional[List[str]] = Query(None),
    is_urgent: Optional[bool] = None,
    is_premium: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """공고 목록 조회"""
    try:
        jobs = get_jobs_service(
            db,
            region_ids=region_ids,
            is_urgent=is_urgent,
            is_premium=is_premium,
            limit=limit,
            offset=offset
        )
        
        jobs_data = []
        for job in jobs:
            job_dict = {
                "id": job.id,
                "shop_id": job.shop_id,
                "title": job.title,
                "date": job.date,
                "time": job.time,
                # "end_time": getattr(job, 'end_time', None),  # 데이터베이스에 없음
                "amount": job.amount,
                "energy": job.energy,
                "required_count": job.required_count,
                "region_id": job.region_id,
                # "description": getattr(job, 'description', None),  # 데이터베이스에 없음
                # "requirements": getattr(job, 'requirements', None),  # 데이터베이스에 없음
                # "images": getattr(job, 'images', None) or [],  # 데이터베이스에 없음
                "is_urgent": job.is_urgent,
                "is_premium": job.is_premium,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
            }
            jobs_data.append(job_dict)
        
        return success_response({"jobs": jobs_data})
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"\n{'='*60}")
        print(f"[공고 목록 조회 오류] {error_detail}")
        print(f"{'='*60}")
        print(f"[Traceback]\n{traceback_str}")
        print(f"{'='*60}\n")
        return error_response(
            f"공고 조회 중 오류가 발생했습니다: {error_detail}", 
            "INTERNAL_ERROR", 
            status_code=500
        )


@router.get("/api/jobs/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """공고 상세 조회"""
    try:
        job = get_job_by_id(db, job_id)
        if not job:
            return error_response("공고를 찾을 수 없습니다", "NOT_FOUND", status_code=404)
        
        job_data = {
            "id": job.id,
            "shop_id": job.shop_id,
            "title": job.title,
            "date": job.date,
            "time": job.time,
            # "end_time": getattr(job, 'end_time', None),  # 데이터베이스에 없음
            "amount": job.amount,
            "energy": job.energy,
            "required_count": job.required_count,
            "region_id": job.region_id,
            # "description": getattr(job, 'description', None),  # 데이터베이스에 없음
            # "requirements": getattr(job, 'requirements', None),  # 데이터베이스에 없음
            # "images": getattr(job, 'images', None) or [],  # 데이터베이스에 없음
            "is_urgent": job.is_urgent,
            "is_premium": job.is_premium,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }
        
        return success_response(job_data)
    except Exception as e:
        return error_response("공고 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/jobs")
async def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """공고 생성"""
    try:
        shop_id = current_user.get("user_id") or current_user.get("sub")
        if not shop_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        # shop 역할만 공고 생성 가능
        if current_user.get("role") != "shop":
            return error_response("공고는 매장만 생성할 수 있습니다", "FORBIDDEN", status_code=403)
        
        job = create_job_service(db, shop_id, job_data)
        
        job_response = {
            "id": job.id,
            "shop_id": job.shop_id,
            "title": job.title,
            "date": job.date,
            "time": job.time,
            # "end_time": getattr(job, 'end_time', None),  # 데이터베이스에 없음
            "amount": job.amount,
            "energy": job.energy,
            "required_count": job.required_count,
            "region_id": job.region_id,
            # "description": getattr(job, 'description', None),  # 데이터베이스에 없음
            # "requirements": getattr(job, 'requirements', None),  # 데이터베이스에 없음
            # "images": getattr(job, 'images', None) or [],  # 데이터베이스에 없음
            "is_urgent": job.is_urgent,
            "is_premium": job.is_premium,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }
        
        return success_response(job_response, status_code=201)
    except Exception as e:
        return error_response("공고 생성 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


def _job_to_dict(db, job, shop_name=None):
    """Job 응답 생성 (shopName 포함)"""
    if not shop_name:
        try:
            from shared.database.models.user import User
            shop_user = db.query(User).filter(User.id == job.shop_id).first()
            shop_name = (shop_user.name or shop_user.username or "매장") if shop_user else "매장"
        except Exception:
            shop_name = "매장"
    return {
        "id": job.id,
        "title": job.title,
        "shopId": job.shop_id,
        "shopName": shop_name,
        "date": job.date,
        "time": job.time,
        "amount": job.amount,
        "energy": job.energy,
        "requiredCount": job.required_count,
        "regionId": job.region_id,
        "isUrgent": job.is_urgent,
        "isPremium": job.is_premium,
        "status": job.status,
        "createdAt": job.created_at.isoformat(),
    }


def _application_to_dict(app, job=None, spare_user=None, db=None):
    """Application 응답 생성 (Job, spare 포함)"""
    d = {
        "id": app.id,
        "jobId": app.job_id,
        "spareId": app.spare_id,
        "status": app.status,
        "energyLocked": app.energy_locked,
        "createdAt": app.created_at.isoformat(),
    }
    if job and db:
        d["job"] = _job_to_dict(db, job)
    if spare_user:
        d["spare"] = {
            "id": spare_user.id,
            "username": getattr(spare_user, "username", None) or "",
            "name": getattr(spare_user, "name", None) or getattr(spare_user, "username", None) or "스페어",
            "role": getattr(spare_user, "role", None) or "spare",
            "createdAt": getattr(spare_user, "created_at", None).isoformat() if hasattr(spare_user, "created_at") and getattr(spare_user, "created_at", None) else None,
        }
    return d


def _build_applications_response(db, applications):
    """Application 목록을 Job, spare 포함하여 빌드"""
    from shared.database.models.user import User
    applications_data = []
    user_ids = list(set([a.spare_id for a in applications]))
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}
    for app in applications:
        job = get_job_by_id(db, app.job_id)
        spare_user = users.get(app.spare_id)
        applications_data.append(_application_to_dict(app, job, spare_user, db))
    return applications_data


@router.post("/api/jobs/{job_id}/apply")
async def apply_to_job(
    job_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """공고 지원"""
    try:
        spare_id = current_user.get("user_id") or current_user.get("sub")
        if not spare_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        # spare 역할만 지원 가능
        if current_user.get("role") != "spare":
            return error_response("스페어만 공고에 지원할 수 있습니다", "FORBIDDEN", status_code=403)
        
        auth_header = request.headers.get("Authorization")
        application = apply_to_job_service(db, job_id, spare_id, auth_header)
        job = get_job_by_id(db, application.job_id)
        spare_user = None
        try:
            from shared.database.models.user import User
            spare_user = db.query(User).filter(User.id == application.spare_id).first()
        except Exception:
            pass
        return success_response(_application_to_dict(application, job, spare_user, db), status_code=201)
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("공고 지원 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/api/jobs/my")
async def get_my_jobs(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """내 공고 목록"""
    try:
        shop_id = current_user.get("user_id") or current_user.get("sub")
        if not shop_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        jobs = get_user_jobs(db, shop_id)
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                "id": job.id,
                "shop_id": job.shop_id,
                "title": job.title,
                "date": job.date,
                "time": job.time,
                # "end_time": getattr(job, 'end_time', None),  # 데이터베이스에 없음
                "amount": job.amount,
                "energy": job.energy,
                "required_count": job.required_count,
                "region_id": job.region_id,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
            })
        
        return success_response({"jobs": jobs_data})
    except Exception as e:
        return error_response("공고 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/api/applications/my")
async def get_my_applications(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """내 지원 목록 (Spare용)"""
    try:
        spare_id = current_user.get("user_id") or current_user.get("sub")
        if not spare_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        applications = get_user_applications(db, spare_id)
        applications_data = _build_applications_response(db, applications)
        return success_response({"applications": applications_data})
    except Exception as e:
        return error_response("지원 목록 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/api/applications/shop")
async def get_shop_applications(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """매장 지원자 목록 (Shop용)"""
    try:
        shop_id = current_user.get("user_id") or current_user.get("sub")
        if not shop_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        if current_user.get("role") != "shop":
            return error_response("매장만 조회할 수 있습니다", "FORBIDDEN", status_code=403)
        
        applications = get_applications_for_shop(db, shop_id)
        applications_data = _build_applications_response(db, applications)
        return success_response({"applications": applications_data})
    except Exception as e:
        return error_response("지원 목록 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/applications/{application_id}/approve")
async def approve_application(
    application_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """지원 승인 (Shop만)"""
    try:
        shop_id = current_user.get("user_id") or current_user.get("sub")
        if not shop_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        if current_user.get("role") != "shop":
            return error_response("매장만 승인할 수 있습니다", "FORBIDDEN", status_code=403)
        
        auth_header = request.headers.get("Authorization")
        application = approve_application_service(db, application_id, shop_id, auth_header)
        applications_data = _build_applications_response(db, [application])
        return success_response(applications_data[0] if applications_data else {})
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("승인 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/applications/{application_id}/reject")
async def reject_application(
    application_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """지원 거절 (Shop만)"""
    try:
        shop_id = current_user.get("user_id") or current_user.get("sub")
        if not shop_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        if current_user.get("role") != "shop":
            return error_response("매장만 거절할 수 있습니다", "FORBIDDEN", status_code=403)
        
        application = reject_application_service(db, application_id, shop_id)
        applications_data = _build_applications_response(db, [application])
        return success_response(applications_data[0] if applications_data else {})
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("거절 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "job-service"}
