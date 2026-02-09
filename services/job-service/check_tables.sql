-- 데이터베이스 테이블 확인 SQL

-- 모든 테이블 목록 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Job 관련 테이블 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND (table_name ILIKE '%job%' OR table_name ILIKE '%Job%')
ORDER BY table_name;

-- Job 테이블 컬럼 확인 (테이블이 존재하는 경우)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name IN ('Job', 'job')
ORDER BY ordinal_position;
