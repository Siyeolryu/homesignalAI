"""
Supabase Agent 간단 테스트
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.shared.database import get_supabase_client
from src.shared.supabase_agent import SupabaseAgent


async def test_agent():
    """Agent 테스트"""
    print("=" * 80)
    print("Supabase Agent 테스트")
    print("=" * 80)
    print()

    # Supabase 클라이언트
    try:
        supabase_client = get_supabase_client(use_service_role=True)
        print("[OK] Supabase 클라이언트 초기화")
    except Exception as e:
        print(f"[FAIL] Supabase 연결 실패: {e}")
        print()
        print("Mock 모드로 계속...")
        from src.shared.database import MockSupabaseClient

        supabase_client = MockSupabaseClient()

    print()

    # Agent 초기화 (Dry-run)
    agent = SupabaseAgent(supabase_client=supabase_client, dry_run=True)
    print("[OK] Agent 초기화 (Dry-run 모드)")
    print()

    # 테스트 명령들
    test_commands = [
        "Migration 007 실행해줘",
        "conversation_sessions 테이블 확인해줘",
        "활성 세션 개수 알려줘",
    ]

    for i, command in enumerate(test_commands, 1):
        print(f"[테스트 {i}] {command}")
        print("-" * 80)

        response = await agent.execute(command)

        print(f"결과: {'[OK]' if response.success else '[FAIL]'}")
        print(response.message)
        print()

    # 실제 검증 테스트 (Dry-run 해제)
    print("[테스트 4] 실제 검증 테스트")
    print("-" * 80)

    agent.dry_run = False

    response = await agent.execute("Migration 목록 보여줘")
    print(f"결과: {'[OK]' if response.success else '[FAIL]'}")
    print(response.message)
    print()

    print("=" * 80)
    print("테스트 완료")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_agent())
