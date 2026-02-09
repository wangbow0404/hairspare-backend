"""
Chat Service API 라우트
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
from ..schemas.chat import ChatResponse, MessageCreate, MessageResponse
from ..services.chat_service import (
    get_chats as get_chats_service,
    get_chat_by_id,
    get_or_create_chat,
    get_messages as get_messages_service,
    send_message as send_message_service,
    mark_messages_as_read,
    delete_chat as delete_chat_service,
)

router = APIRouter()


@router.get("/api/chats")
async def get_chats(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """채팅방 목록 조회"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        role = current_user.get("role")
        if not user_id or not role:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        chats = get_chats_service(db, user_id, role, limit=limit, offset=offset)
        
        chats_data = []
        for chat in chats:
            chats_data.append({
                "id": chat.id,
                "job_id": chat.job_id,
                "shop_id": chat.shop_id,
                "spare_id": chat.spare_id,
                "last_message_at": chat.last_message_at.isoformat() if chat.last_message_at else None,
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat(),
            })
        
        return success_response({"chats": chats_data})
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"\n{'='*60}")
        print(f"[채팅방 목록 조회 오류] {error_detail}")
        print(f"{'='*60}")
        print(f"[Traceback]\n{traceback_str}")
        print(f"{'='*60}\n")
        return error_response(
            f"채팅방 조회 중 오류가 발생했습니다: {error_detail}",
            "INTERNAL_ERROR",
            status_code=500
        )


@router.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str, db: Session = Depends(get_db)):
    """채팅방 상세 조회"""
    try:
        chat = get_chat_by_id(db, chat_id)
        if not chat:
            return error_response("채팅방을 찾을 수 없습니다", "NOT_FOUND", status_code=404)
        
        chat_data = {
            "id": chat.id,
            "job_id": chat.job_id,
            "shop_id": chat.shop_id,
            "spare_id": chat.spare_id,
            "last_message_at": chat.last_message_at.isoformat() if chat.last_message_at else None,
            "created_at": chat.created_at.isoformat(),
            "updated_at": chat.updated_at.isoformat(),
        }
        
        return success_response(chat_data)
    except Exception as e:
        return error_response("채팅방 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.get("/api/chats/{chat_id}/messages")
async def get_messages(
    chat_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """메시지 목록 조회"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        # 채팅방 권한 확인
        chat = get_chat_by_id(db, chat_id)
        if not chat:
            return error_response("채팅방을 찾을 수 없습니다", "NOT_FOUND", status_code=404)
        
        if chat.shop_id != user_id and chat.spare_id != user_id:
            return error_response("채팅방에 접근할 권한이 없습니다", "FORBIDDEN", status_code=403)
        
        messages = get_messages_service(db, chat_id, limit=limit, offset=offset)
        
        messages_data = []
        for message in messages:
            messages_data.append({
                "id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "is_read": message.is_read,
                "is_filtered": message.is_filtered,
                "created_at": message.created_at.isoformat(),
            })
        
        return success_response({"messages": messages_data})
    except Exception as e:
        return error_response("메시지 조회 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/chats/{chat_id}/messages")
async def send_message(
    chat_id: str,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """메시지 전송"""
    try:
        sender_id = current_user.get("user_id") or current_user.get("sub")
        if not sender_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        message = send_message_service(db, chat_id, sender_id, message_data)
        
        message_response = {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "is_read": message.is_read,
            "is_filtered": message.is_filtered,
            "created_at": message.created_at.isoformat(),
        }
        
        return success_response(message_response, status_code=201)
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except Exception as e:
        return error_response("메시지 전송 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.post("/api/chats/{chat_id}/read")
async def mark_read(
    chat_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """메시지 읽음 처리"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        count = mark_messages_as_read(db, chat_id, user_id)
        
        return success_response({"read_count": count})
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except Exception as e:
        return error_response("메시지 읽음 처리 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)


@router.delete("/api/chats/{chat_id}")
async def delete_chat_endpoint(
    chat_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """채팅방 삭제"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다", "UNAUTHORIZED", status_code=401)
        
        delete_chat_service(db, chat_id, user_id)
        
        return success_response({"message": "채팅방이 삭제되었습니다"})
    except NotFoundException as e:
        return error_response(e.message, e.code or "NOT_FOUND", status_code=404)
    except AuthorizationException as e:
        return error_response(e.message, e.code or "FORBIDDEN", status_code=403)
    except Exception as e:
        return error_response("채팅방 삭제 중 오류가 발생했습니다", "INTERNAL_ERROR", status_code=500)
