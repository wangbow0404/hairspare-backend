"""
Schedule Service API 라우트
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status, Request, Request
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
from shared.auth.dependencies import get_current_user_dependency, get_optional_user_dependency
from typing import Optional as TypingOptional
from shared.exceptions.app_exceptions import NotFoundException, ConflictException, AuthorizationException
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from ..services.schedule_service import (
    get_schedules as get_schedules_service,
    get_schedule_by_id,
    create_schedule as create_schedule_service,
    update_schedule,
    cancel_schedule,
    get_user_schedules,
    check_in_schedule,
    confirm_schedule,
    get_work_check_stats,
    get_shop_work_check_stats,
)

router = APIRouter()


@router.get("/api/schedules")
async def get_schedules(
    request: Request,
    spare_id: Optional[str] = Query(None),
    shop_id: Optional[str] = Query(None),
    owner_id: Optional[str] = Query(None),  # 'me'로 설정하면 현재 사용자의 스케줄만 조회
    status: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """스케줄 목록 조회"""
    try:
        # ownerId가 'me'인 경우 현재 사용자 정보 사용
        if owner_id == "me":
            # Authorization 헤더에서 토큰 추출
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return error_response("인증이 필요합니다", "UNAUTHORIZED", status_code=401)
            
            token = auth_header.split(" ")[1]
            from shared.auth.jwt import verify_token
            current_user = verify_token(token)
            
            if not current_user:
                return error_response("인증 토큰이 유효하지 않습니다", "UNAUTHORIZED", status_code=401)
            
            user_id = current_user.get("user_id") or current_user.get("sub")
            role = current_user.get("role")
            if role == "spare":
                spare_id = user_id
            elif role == "shop":
                shop_id = user_id
            else:
                return error_response("권한이 없습니다", "FORBIDDEN", status_code=403)
        
        schedules = get_schedules_service(
            db,
            spare_id=spare_id,
            shop_id=shop_id,
            status=status,
            date=date,
            limit=limit,
            offset=offset
        )
        
        # User 정보 조회를 위한 import
        try:
            from shared.database.models.user import User
            # spare_id 목록 수집
            spare_ids = list(set([s.spare_id for s in schedules]))
            # User 정보 조회
            users = db.query(User).filter(User.id.in_(spare_ids)).all()
            user_dict = {user.id: user for user in users}
        except:
            user_dict = {}
        
        schedules_data = []
        for schedule in schedules:
            # Flutter가 기대하는 camelCase 형식으로 변환
            schedule_dict = {
                "id": schedule.id,
                "jobId": schedule.job_id,
                "spareId": schedule.spare_id,
                "shopId": schedule.shop_id,
                "date": schedule.date,
                "startTime": schedule.start_time,
                "endTime": schedule.end_time,
                "status": schedule.status,
                "checkInTime": schedule.check_in_time.isoformat() if schedule.check_in_time else None,
                "checkOutTime": schedule.check_out_time.isoformat() if schedule.check_out_time else None,
                "createdAt": schedule.created_at.isoformat(),
                "updatedAt": schedule.updated_at.isoformat(),
            }
            
            # spare 정보 포함
            if schedule.spare_id in user_dict:
                user = user_dict[schedule.spare_id]
                schedule_dict["spare"] = {
                    "id": user.id,
                    "name": user.name or user.username or "스페어",
                }
            else:
                schedule_dict["spare"] = {
                    "id": schedule.spare_id,
                    "name": "스페어",
                }
            
            schedules_data.append(schedule_dict)
        
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
        
        shop_id = schedule_data.shop_id or (current_user.get("user_id") or current_user.get("sub"))
        spare_id = schedule_data.spare_id
        if not shop_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        if not spare_id:
            return error_response("spare_id가 필요합니다", "VALIDATION_ERROR", status_code=400)
        
        schedule = create_schedule_service(
            db,
            job_id=schedule_data.job_id,
            spare_id=spare_id,
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


@router.post("/api/schedules/{schedule_id}/check-in")
async def check_in_schedule_endpoint(
    schedule_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """스케줄 체크인 (Spare만, 출근 완료 시)"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        if current_user.get("role") != "spare":
            return error_response("체크인은 스페어만 가능합니다", "FORBIDDEN", status_code=403)
        auth_header = request.headers.get("Authorization")
        schedule = check_in_schedule(db, schedule_id, user_id, auth_header)
        schedule_data = {
            "id": schedule.id,
            "jobId": schedule.job_id,
            "spareId": schedule.spare_id,
            "shopId": schedule.shop_id,
            "date": schedule.date,
            "startTime": schedule.start_time,
            "endTime": schedule.end_time,
            "status": schedule.status,
            "checkInTime": schedule.check_in_time.isoformat() if schedule.check_in_time else None,
            "checkOutTime": schedule.check_out_time.isoformat() if schedule.check_out_time else None,
            "createdAt": schedule.created_at.isoformat(),
            "updatedAt": schedule.updated_at.isoformat(),
        }
        return success_response(schedule_data)
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("체크인 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/schedules/{schedule_id}/confirm")
async def confirm_schedule_endpoint(
    schedule_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """근무 확인/정산 (Shop만)"""
    try:
        thumbs_up = False
        try:
            body = await request.json()
            thumbs_up = body.get("thumbsUp", False) if isinstance(body, dict) else False
        except Exception:
            pass
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        if current_user.get("role") != "shop":
            return error_response("근무 확인은 매장만 가능합니다", "FORBIDDEN", status_code=403)
        schedule, result = confirm_schedule(db, schedule_id, user_id, thumbs_up)
        schedule_data = {
            "id": schedule.id,
            "status": schedule.status,
            "checkInTime": schedule.check_in_time.isoformat() if schedule.check_in_time else None,
        }
        return success_response({**schedule_data, **result})
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except ConflictException as e:
        return error_response(e.message, e.code or "CONFLICT", status_code=409)
    except Exception as e:
        return error_response("근무 확인 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/api/work-check/stats")
async def work_check_stats(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """출근 체크 통계 (Spare용)"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        stats = get_work_check_stats(db, user_id)
        return success_response(stats)
    except Exception as e:
        return error_response("통계 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/api/work-check/shop-stats")
async def shop_work_check_stats(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Shop VIP 등급 통계 (미용실용)"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        if current_user.get("role") != "shop":
            return error_response("미용실만 조회 가능합니다", "FORBIDDEN", status_code=403)
        stats = get_shop_work_check_stats(db, user_id)
        return success_response(stats)
    except Exception as e:
        return error_response("VIP 통계 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)
