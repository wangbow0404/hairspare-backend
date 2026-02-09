"""
Auth Service 설정
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 URL
# 환경 변수가 없으면 현재 사용자명으로 시도
# macOS의 경우 일반적으로 현재 사용자명을 사용
import getpass
default_user = getpass.getuser()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{default_user}@localhost:5432/hairspare"
)

# JWT 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24시간

# 서비스 포트 (포트 충돌 시 다른 포트 사용 가능)
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8101"))

# 비밀번호 해싱
BCRYPT_ROUNDS = 12
