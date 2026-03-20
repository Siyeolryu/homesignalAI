"""
Migration 007 직접 실행 (MigrationTool 사용)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.shared.supabase_agent.tools import MigrationTool


async def main():
    """Migration 007 실행"""
    print("=" * 80)
    print("Migration 007 실행 (MigrationTool 직접 사용)")
    print("=" * 80)
    print()

    # MigrationTool은 Supabase 클라이언트가 필요하지만
    # 실제로는 psycopg를 사용하므로 None으로 초기화
    tool = MigrationTool(supabase_client=None)

    # Migration 파일 찾기
    migration_file = await tool.find_migration("007")

    if not migration_file:
        print("[FAIL] Migration 007 파일을 찾을 수 없습니다.")
        print()
        print("사용 가능한 Migration:")
        migrations = await tool.list_migrations()
        for m in migrations:
            print(f"  - {Path(m).name}")
        return 1

    print(f"[OK] Migration 파일 발견: {migration_file}")
    print()

    # Migration 실행
    print("[실행 중...]")
    print()

    result = await tool.run_migration(migration_file)

    if result.success:
        print("=" * 80)
        print("[SUCCESS] Migration 007 실행 완료!")
        print("=" * 80)
        print()
        print(f"파일: {result.migration_file}")
        print(f"실행 시간: {result.execution_time:.2f}초")
        print()

        if result.tables_created:
            print(f"생성된 테이블 ({len(result.tables_created)}개):")
            for table in result.tables_created:
                print(f"  - {table}")
            print()

        if result.functions_created:
            print(f"생성된 함수 ({len(result.functions_created)}개):")
            for func in result.functions_created:
                print(f"  - {func}()")
            print()

        print("다음 단계:")
        print("  1. 검증: python verify_migration_007.py")
        print("  2. .env에서 FORCE_CONVERSATION_MOCK=false 설정")
        print("  3. 서버 재시작: uv run uvicorn src.main:app --host 127.0.0.1 --port 8000")
        print()

        return 0
    else:
        print("=" * 80)
        print("[FAIL] Migration 007 실행 실패")
        print("=" * 80)
        print()
        print("오류:")
        for error in result.errors:
            print(f"  - {error}")
        print()

        if "DATABASE_URL" in str(result.errors):
            print("해결 방법:")
            print("  1. .env 파일에 DATABASE_URL 설정 확인")
            print("  2. 또는 Supabase SQL Editor에서 수동 실행")
            print("     → MIGRATION_007_GUIDE.md 참고")
            print()

        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
