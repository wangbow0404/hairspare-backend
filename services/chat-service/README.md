# Chat Service

HairSpare의 채팅 서비스입니다.

## 기능

- 채팅방 목록 조회
- 채팅방 상세 조회
- 채팅방 생성 또는 조회
- 메시지 목록 조회
- 메시지 전송
- 메시지 읽음 처리
- 채팅방 삭제

## 실행 방법

### 방법 1: 실행 스크립트 사용

```bash
cd /Users/yoram/hairspare/backend/services/chat-service
chmod +x run.sh
./run.sh
```

### 방법 2: 직접 실행

```bash
cd /Users/yoram/hairspare/backend/services/chat-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/hairspare"
export PYTHONPATH=/Users/yoram/hairspare/backend:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8105 --reload
```

## API 엔드포인트

- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스 체크
- `GET /api/chats` - 채팅방 목록 조회 (인증 필요)
- `GET /api/chats/{chat_id}` - 채팅방 상세 조회
- `GET /api/chats/{chat_id}/messages` - 메시지 목록 조회 (인증 필요)
- `POST /api/chats/{chat_id}/messages` - 메시지 전송 (인증 필요)
- `POST /api/chats/{chat_id}/read` - 메시지 읽음 처리 (인증 필요)
- `DELETE /api/chats/{chat_id}` - 채팅방 삭제 (인증 필요)

## 포트

기본 포트: **8105**

환경 변수 `SERVICE_PORT`로 변경 가능합니다.

## 데이터베이스

- `Chat` 테이블: 채팅방 정보
- `Message` 테이블: 메시지 정보

## 의존성

- Auth Service (포트 8101): 사용자 인증 및 권한 확인
- Job Service (포트 8103): 공고 정보 확인 (향후 구현)
