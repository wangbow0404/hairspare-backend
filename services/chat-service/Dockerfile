FROM python:3.11-slim

WORKDIR /app

# 공통 라이브러리 복사 (build context가 backend 디렉토리)
COPY shared /app/shared

# 의존성 설치
COPY services/chat-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY services/chat-service/app /app/app

# 포트 노출
EXPOSE 8105

# 실행 (환경 변수에서 포트를 읽거나 기본값 8105 사용)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8105}"]
