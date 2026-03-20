"""
DATABASE_URL 연결 테스트
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import settings

print("=" * 80)
print("DATABASE_URL 연결 테스트")
print("=" * 80)
print()

# 1. DATABASE_URL 확인
if settings.database_url:
    # 비밀번호 마스킹
    url = settings.database_url
    if "@" in url:
        parts = url.split("@")
        masked_auth = parts[0].split("://")[1].split(":")[0] + ":****"
        masked_url = url.split("://")[0] + "://" + masked_auth + "@" + parts[1]
    else:
        masked_url = url

    print(f"[OK] DATABASE_URL 설정됨")
    print(f"     {masked_url}")
    print()
else:
    print("[FAIL] DATABASE_URL이 설정되지 않았습니다.")
    print()
    print("해결 방법:")
    print("  1. .env 파일 확인")
    print("  2. DATABASE_URL 추가:")
    print("     DATABASE_URL=postgresql://postgres.xxx:[PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres")
    print()
    sys.exit(1)

# 2. psycopg 설치 확인
try:
    import psycopg
    print("[OK] psycopg 설치됨")
except ImportError:
    print("[FAIL] psycopg 미설치")
    print("     실행: uv pip install psycopg")
    sys.exit(1)

print()

# 3. 연결 테스트
print("[테스트] PostgreSQL 연결 시도...")
print()

try:
    with psycopg.connect(settings.database_url, connect_timeout=10) as conn:
        with conn.cursor() as cur:
            # 간단한 쿼리 실행
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]

            print("[SUCCESS] 연결 성공!")
            print()
            print(f"PostgreSQL 버전: {version[:80]}...")
            print()

            # 테이블 개수 확인
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            table_count = cur.fetchone()[0]

            print(f"Public 스키마 테이블 개수: {table_count}개")
            print()

            print("=" * 80)
            print("Agent가 Supabase에 자동 접속 가능합니다!")
            print("=" * 80)
            print()
            print("다음 명령 실행:")
            print("  python scripts/supabase_agent_cli.py migrate 007")
            print()

except psycopg.OperationalError as e:
    error_msg = str(e)
    print("[FAIL] 연결 실패")
    print()
    print(f"오류: {error_msg}")
    print()

    if "could not translate host name" in error_msg or "getaddrinfo failed" in error_msg:
        print("문제: DNS 해석 실패")
        print()
        print("해결 방법:")
        print("  1. 인터넷 연결 확인")
        print("  2. VPN 연결 (회사/학교 네트워크인 경우)")
        print("  3. 다른 네트워크로 전환 (모바일 핫스팟 등)")
        print("  4. 방화벽 확인")
        print()
    elif "password authentication failed" in error_msg:
        print("문제: 비밀번호 오류")
        print()
        print("해결 방법:")
        print("  1. Supabase Dashboard → Settings → Database")
        print("  2. Database password 확인 또는 재설정")
        print("  3. .env의 DATABASE_URL 업데이트")
        print()
    elif "timeout" in error_msg:
        print("문제: 연결 타임아웃")
        print()
        print("해결 방법:")
        print("  1. Supabase 프로젝트 활성 상태 확인")
        print("  2. 방화벽에서 PostgreSQL 포트 허용 (5432, 6543)")
        print("  3. IP 제한 확인 (Supabase Dashboard)")
        print()
    else:
        print("해결 방법:")
        print("  1. DATABASE_URL 형식 확인")
        print("  2. Supabase Dashboard에서 Connection string 다시 복사")
        print("  3. 또는 Supabase SQL Editor에서 수동 실행")
        print()

    sys.exit(1)

except Exception as e:
    print(f"[ERROR] 예상치 못한 오류: {e}")
    sys.exit(1)
