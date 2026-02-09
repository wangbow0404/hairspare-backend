"""
데이터베이스 세션 관리
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# 데이터베이스 URL (환경변수에서 가져오거나 기본값 사용)
# 환경 변수가 없으면 현재 사용자명으로 시도 (macOS의 경우)
import getpass
default_user = getpass.getuser()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{default_user}@localhost:5432/hairspare"
)

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 검사
    pool_size=10,
    max_overflow=20,
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성
    FastAPI에서 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
