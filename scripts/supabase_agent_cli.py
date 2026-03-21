#!/usr/bin/env python3
"""
Supabase Agent CLI

사용법:
  # 대화형 모드
  python scripts/supabase_agent_cli.py

  # 단일 명령
  python scripts/supabase_agent_cli.py "Migration 007 실행해줘"

  # Migration 특화 (단축)
  python scripts/supabase_agent_cli.py migrate 007

  # 검증
  python scripts/supabase_agent_cli.py verify

  # Dry-run 모드
  python scripts/supabase_agent_cli.py --dry-run "Migration 007 실행해줘"
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shared.ai_client import AIClient
from src.shared.database import get_supabase_client
from src.shared.supabase_agent import SupabaseAgent


def print_banner():
    """배너 출력"""
    print("=" * 80)
    print("Supabase Agent CLI")
    print("=" * 80)
    print()
    print("명령어 예시:")
    print("  - Migration 007 실행해줘")
    print("  - conversation_sessions 테이블 확인해줘")
    print("  - 활성 세션 개수 알려줘")
    print("  - exit (종료)")
    print()


async def interactive_mode(agent: SupabaseAgent):
    """대화형 모드"""
    print_banner()

    while True:
        try:
            command = input("\n> ").strip()

            if not command:
                continue

            if command.lower() in ["exit", "quit", "q"]:
                print("\n종료합니다.")
                break

            # 명령 실행
            response = await agent.execute(command)

            # 결과 출력
            print()
            print(response.message)

            if response.data:
                print(f"\n[디버그] 데이터: {response.data}")

        except KeyboardInterrupt:
            print("\n\n종료합니다.")
            break
        except Exception as e:
            print(f"\n오류: {e}")


async def single_command_mode(agent: SupabaseAgent, command: str):
    """단일 명령 모드"""
    print(f"명령: {command}")
    print("-" * 80)

    response = await agent.execute(command)

    print(response.message)

    if response.data:
        print(f"\n[데이터] {response.data}")

    return 0 if response.success else 1


async def main():
    """메인 함수"""
    # 인자 파싱
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        sys.argv.remove("--dry-run")

    # Supabase 클라이언트
    try:
        supabase_client = get_supabase_client(use_service_role=True)
        print(f"[OK] Supabase 연결 완료")
    except Exception as e:
        print(f"[FAIL] Supabase 연결 실패: {e}")
        return 1

    # AI 클라이언트 (선택사항)
    ai_client = None
    try:
        ai_client = AIClient()
        print(f"[OK] AI 클라이언트 초기화")
    except Exception:
        print(f"[INFO] AI 클라이언트 없음 (규칙 기반 모드)")

    # Agent 초기화
    agent = SupabaseAgent(
        supabase_client=supabase_client,
        ai_client=ai_client,
        dry_run=dry_run,
    )

    if dry_run:
        print("[INFO] Dry-run 모드 활성화 (실제 실행하지 않음)")

    print()

    # 명령 모드 결정
    if len(sys.argv) > 1:
        # 단축 명령어 처리
        if sys.argv[1] == "migrate" and len(sys.argv) > 2:
            # migrate 007 → "Migration 007 실행해줘"
            command = f"Migration {sys.argv[2]} 실행해줘"
        elif sys.argv[1] == "verify":
            # verify → "검증해줘"
            command = "Migration 007 검증해줘"
        else:
            # 일반 명령
            command = " ".join(sys.argv[1:])

        # 단일 명령 실행
        return await single_command_mode(agent, command)
    else:
        # 대화형 모드
        await interactive_mode(agent)
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
