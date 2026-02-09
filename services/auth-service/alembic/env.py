from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import sys
import os
from dotenv import load_dotenv

# .env 파일 로드 (alembic 실행 시)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# 프로젝트 루트를 Python 경로에 추가
# alembic/env.py 위치: backend/services/auth-service/alembic/env.py
# backend 디렉토리 찾기
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 앱의 모델들을 import (Base를 통해 모든 모델이 등록됨)
from app.models import User, Account, Verification
from app.config import DATABASE_URL

# Alembic Config 객체
config = context.config

# 데이터베이스 URL 설정
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData 객체 (모든 모델의 Base에서 가져옴)
from shared.database.base import Base
target_metadata = Base.metadata

# 다른 값들은 config에서 가져옴
# ... (기타 설정)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
