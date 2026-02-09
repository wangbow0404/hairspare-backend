"""
Job Service 설정
"""

import os
from dotenv import load_dotenv
import getpass

# .env 파일 로드
load_dotenv()

# 데이터베이스 URL
default_user = getpass.getuser()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{default_user}@localhost:5432/hairspare"
)

# 서비스 포트
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8102"))

# Auth Service URL (로컬 개발용)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8101")
