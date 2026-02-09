#!/usr/bin/env python3
"""
데이터베이스 테이블 존재 여부 확인 스크립트
"""

import sys
import os

# shared 라이브러리 경로 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.abspath(os.path.join(current_file, "../../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from shared.database.session import engine, get_db
from sqlalchemy import inspect, text

def check_tables():
    """데이터베이스 테이블 확인"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("=" * 50)
    print("데이터베이스 테이블 목록")
    print("=" * 50)
    
    required_tables = ["Job", "Application", "Region", "User"]
    
    for table in sorted(tables):
        marker = "✓" if table in required_tables else " "
        print(f"{marker} {table}")
    
    print("\n필수 테이블 확인:")
    for table in required_tables:
        if table in tables:
            print(f"  ✓ {table} 존재")
        else:
            print(f"  ✗ {table} 없음")
    
    # Job 테이블 상세 정보
    if "Job" in tables:
        print("\nJob 테이블 컬럼:")
        columns = inspector.get_columns("Job")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    # 데이터 개수 확인
    print("\n데이터 개수:")
    with engine.connect() as conn:
        for table in required_tables:
            if table in tables:
                try:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                except Exception as e:
                    print(f"  {table}: 확인 실패 - {e}")

if __name__ == "__main__":
    try:
        check_tables()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
