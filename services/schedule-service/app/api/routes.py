"""
Schedule Service API 라우트
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
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
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from ..services.schedule_service import (
    get_schedules as get_schedules_service,
    get_schedule_by_id,
    create_schedule as create_schedule_service,
    update_schedule,
    cancel_schedule,
    get_user_schedules,
)

router = APIRouter()


@router.get("/api/schedules")
async def get_schedules(
    spare_id: Optional[str] = Query(None),
    shop_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """스케줄 목록 조회"""
    try:
        schedules = get_schedules_service(
            db,
            spare_id=spare_id,
            shop_id=shop_id,
            status=status,
            date=date,
            limit=limit,
            offset=offset
        )
        
        schedules_data = []
        for schedule in schedules:
            schedules_data.append({
                "id": schedule.id,
                "job_id": schedule.job_id,
                "spare_id": schedule.spare_id,
                "shop_id": schedule.shop_id,
                "date": schedule.date,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "status": schedule.status,
                "check_in_time": schedule.check_in_time.isoformat() if schedule.check_in_time else None,
                "check_out_time": schedule.check_out_time.isoformat() if schedule.check_out_time else None,
                "created_at": schedule.created_at.isoformat(),
                "updated_at": schedule.updated_at.isoformat(),
            })
        
        return success_response({"schedules": schedules_data})
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"\n{'='*60}")
        print(f"[스케줄 목록 조회 오류] {error_detail}")
        print(f"{'='*60}")
        print(f"[Traceback]\n{traceback_str}")
        print(f"{'='*60}\n")
        return error_response(
            f"스케줄 조회 중 오류가 발생했습니다: {error_detail}",
            "INTERNAL_ERROR",
            status_code=500
        )


@router.get("/api/schedules/{schedule_id}")
async def get_schedule(schedule_id: str, db: Session = Depends(get_db)):
    """스케줄 상세 조회"""
    try:
        schedule = get_schedule_by_id(db, schedule_id)
        if not schedule:
            return error_response("스케줄을 찾을 수 없습니다", "NOT_FOUND", status_code=404)
        
        schedule_data = {
            "id": schedule.id,
            "job_id": schedule.job_id,
            "spare_id": schedule.spare_id,
            "shop_id": schedule.shop_id,
            "date": schedule.date,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "status": schedule.status,
            "check_in_time": schedule.check_in_time.isoformat() if schedule.check_in_time else None,
            "check_out_time": schedule.check_out_time.isoformat() if schedule.check_out_time else None,
            "created_at": schedule.created_at.isoformat(),
            "updated_at": schedule.updated_at.isoformat(),
        }
        
        return success_response(schedule_data)
    except Exception as e:
        return error_response("스케줄 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/schedules")
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """스케줄 생성"""
    try:
        # shop 역할만 스케줄 생성 가능
        if current_user.get("role") != "shop":
            return error_response("스케줄은 매장만 생성할 수 있습니다", "FORBIDDEN", status_code=403)
        
        shop_id = current_user.get("user_id") or current_user.get("sub")
        if not shop_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        # TODO: Job Service에서 공고 정보 확인 및 spare_id 가져오기
        # 임시로 spare_id는 요청에서 받거나, 공고에서 가져와야 함
        # 여기서는 간단히 job_id만 사용
        
        schedule = create_schedule_service(
            db,
            job_id=schedule_data.job_id,
            spare_id="",  # TODO: Job Service에서 가져오기
            shop_id=shop_id,
            schedule_data=schedule_data
        )
        
        schedule_response = {
            "id": schedule.id,
            "job_id": schedule.job_id,
            "spare_id": schedule.spare_id,
            "shop_id": schedule.shop_id,
            "date": schedule.date,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "status": schedule.status,
            "created_at": schedule.created_at.isoformat(),
            "updated_at": schedule.updated_at.isoformat(),
        }
        
        return success_response(schedule_response, status_code=201)
    except Exception as e:
        return error_response("스케줄 생성 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/schedules/{schedule_id}/cancel")
async def cancel_schedule_endpoint(
    schedule_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """스케줄 취소"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        schedule = cancel_schedule(db, schedule_id, user_id)
        
        schedule_response = {
            "id": schedule.id,
            "status": schedule.status,
            "updated_at": schedule.updated_at.isoformat(),
        }
        
        return success_response(schedule_response)
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("스케줄 취소 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/api/schedules/my")
async def get_my_schedules(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """내 스케줄 목록"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        role = current_user.get("role")
        if not user_id or not role:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        schedules = get_user_schedules(db, user_id, role)
        
        schedules_data = []
        for schedule in schedules:
            schedules_data.append({
                "id": schedule.id,
                "job_id": schedule.job_id,
                "spare_id": schedule.spare_id,
                "shop_id": schedule.shop_id,
                "date": schedule.date,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "status": schedule.status,
                "created_at": schedule.created_at.isoformat(),
            })
        
        return success_response({"schedules": schedules_data})
    except Exception as e:
        return error_response("스케줄 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)
