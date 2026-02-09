"""
Chat Service 비즈니스 로직
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
from ..models.chat import Chat, Message
from ..schemas.chat import MessageCreate


def get_chats(
    db: Session,
    user_id: str,
    role: str,
    limit: int = 50,
    offset: int = 0
) -> List[Chat]:
    """채팅방 목록 조회"""
    query = db.query(Chat)
    
    if role == "spare":
        query = query.filter(Chat.spare_id == user_id)
    elif role == "shop":
        query = query.filter(Chat.shop_id == user_id)
    else:
        return []
    
    return query.order_by(Chat.last_message_at.desc().nulls_last(), Chat.created_at.desc()).limit(limit).offset(offset).all()


def get_chat_by_id(db: Session, chat_id: str) -> Optional[Chat]:
    """ID로 채팅방 조회"""
    return db.query(Chat).filter(Chat.id == chat_id).first()


def get_or_create_chat(db: Session, job_id: str, shop_id: str, spare_id: str) -> Chat:
    """채팅방 조회 또는 생성"""
    # 기존 채팅방 확인
    chat = db.query(Chat).filter(
        Chat.job_id == job_id,
        Chat.shop_id == shop_id,
        Chat.spare_id == spare_id
    ).first()
    
    if chat:
        return chat
    
    # 새 채팅방 생성
    chat = Chat(
        job_id=job_id,
        shop_id=shop_id,
        spare_id=spare_id,
    )
    
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    return chat


def get_messages(
    db: Session,
    chat_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[Message]:
    """메시지 목록 조회"""
    return db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).limit(limit).offset(offset).all()


def send_message(db: Session, chat_id: str, sender_id: str, message_data: MessageCreate) -> Message:
    """메시지 전송"""
    # 채팅방 확인
    chat = get_chat_by_id(db, chat_id)
    if not chat:
        raise NotFoundException("채팅방을 찾을 수 없습니다")
    
    # 권한 확인 (채팅방 참여자만 메시지 전송 가능)
    if chat.shop_id != sender_id and chat.spare_id != sender_id:
        raise AuthorizationException("메시지를 전송할 권한이 없습니다")
    
    # 메시지 생성
    message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        content=message_data.content,
        is_read=False,
        is_filtered=False,
    )
    
    db.add(message)
    
    # 채팅방의 마지막 메시지 시간 업데이트
    chat.last_message_at = datetime.now()
    
    db.commit()
    db.refresh(message)
    
    return message


def mark_messages_as_read(db: Session, chat_id: str, user_id: str) -> int:
    """메시지를 읽음으로 표시"""
    # 채팅방 확인
    chat = get_chat_by_id(db, chat_id)
    if not chat:
        raise NotFoundException("채팅방을 찾을 수 없습니다")
    
    # 권한 확인
    if chat.shop_id != user_id and chat.spare_id != user_id:
        raise AuthorizationException("메시지를 읽을 권한이 없습니다")
    
    # 자신이 보낸 메시지가 아닌 메시지만 읽음 처리
    updated = db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.sender_id != user_id,
        Message.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return updated


def delete_chat(db: Session, chat_id: str, user_id: str) -> None:
    """채팅방 삭제"""
    chat = get_chat_by_id(db, chat_id)
    if not chat:
        raise NotFoundException("채팅방을 찾을 수 없습니다")
    
    # 권한 확인 (채팅방 참여자만 삭제 가능)
    if chat.shop_id != user_id and chat.spare_id != user_id:
        raise AuthorizationException("채팅방을 삭제할 권한이 없습니다")
    
    db.delete(chat)
    db.commit()
