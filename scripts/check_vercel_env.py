#!/usr/bin/env python3
"""
Vercel 환경변수 확인 스크립트

Vercel 프로젝트에 설정된 환경변수를 확인하고 누락된 것을 식별합니다.

Usage:
    uv run python scripts/check_vercel_env.py
    uv run python scripts/check_vercel_env.py --project homesignal-ai
"""

import argparse
import json
import subprocess
import sys


def run_command(cmd: list[str]) -> tuple[bool, str]:
    """명령어 실행"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, "Vercel CLI not found"


def main():
    parser = argparse.ArgumentParser(
        description="Vercel 환경변수 확인"
    )
    parser.add_argument(
        "--project",
        "-p",
        help="Vercel 프로젝트 이름",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Vercel 환경변수 확인")
    print("=" * 60)

    # Vercel CLI 확인
    print("\n[1] Vercel CLI 확인...")
    success, output = run_command(["vercel", "--version"])
    if not success:
        print("❌ Vercel CLI가 설치되지 않았습니다.")
        print("\n설치 방법:")
        print("  npm i -g vercel")
        print("  vercel login")
        sys.exit(1)
    print(f"✅ Vercel CLI: {output.strip()}")

    # 환경변수 목록 조회
    print("\n[2] Production 환경변수 조회...")
    cmd = ["vercel", "env", "ls", "production"]
    if args.project:
        cmd.extend(["--project", args.project])

    success, output = run_command(cmd)
    if not success:
        print(f"❌ 환경변수 조회 실패: {output}")
        print("\n확인 사항:")
        print("  1. Vercel에 로그인했는지 확인: vercel login")
        print("  2. 프로젝트가 연결되었는지 확인: vercel link")
        sys.exit(1)

    print("✅ 환경변수 목록:")
    print(output)

    # 필수 환경변수 확인
    print("\n[3] 필수 환경변수 확인...")
    required_vars = {
        "SUPABASE_URL": "Supabase 프로젝트 URL",
        "SUPABASE_KEY": "Supabase anon/public key",
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase service_role key",
        "OPENAI_API_KEY": "OpenAI API key (또는 ANTHROPIC_API_KEY)",
    }

    missing_vars = []
    for var, description in required_vars.items():
        if var in output:
            print(f"  ✅ {var}: 설정됨")
        else:
            print(f"  ❌ {var}: 누락 ({description})")
            missing_vars.append(var)

    # 결과 및 조치 사항
    print("\n" + "=" * 60)
    if missing_vars:
        print("❌ 누락된 환경변수 발견")
        print("=" * 60)
        print("\n다음 환경변수를 설정해야 합니다:")
        for var in missing_vars:
            print(f"  - {var}: {required_vars[var]}")

        print("\n설정 방법:")
        print("  방법 1: Vercel CLI")
        for var in missing_vars:
            print(f"    vercel env add {var} production")

        print("\n  방법 2: 자동 설정 스크립트")
        print("    uv run python scripts/setup_vercel_env.py")

        print("\n  방법 3: Vercel Dashboard")
        print("    https://vercel.com/dashboard → 프로젝트 → Settings → Environment Variables")

        sys.exit(1)
    else:
        print("✅ 모든 필수 환경변수가 설정되었습니다")
        print("=" * 60)

        print("\n다음 단계:")
        print("  1. 재배포: vercel --prod")
        print("  2. 배포 확인: curl https://your-app.vercel.app/health")

        sys.exit(0)


if __name__ == "__main__":
    main()
