#!/usr/bin/env python3
"""
Vercel 환경변수 검증 스크립트

Vercel 배포 전/후에 환경변수 설정 상태를 확인합니다.

Requirements:
    - Vercel CLI 설치: npm i -g vercel
    - Vercel 로그인: vercel login

Usage:
    # 로컬 환경변수 검증
    uv run python scripts/verify_vercel_env.py --local

    # Vercel Production 환경변수 검증
    uv run python scripts/verify_vercel_env.py --vercel production

    # 모두 검증
    uv run python scripts/verify_vercel_env.py --all
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 색상 코드
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    OKBLUE = '\033[94m'

def print_header(text: str):
    """헤더 출력"""
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{'='*70}\n")

def print_success(text: str):
    """성공 메시지"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    """경고 메시지"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """에러 메시지"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """정보 메시지"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

# 필수 및 선택적 환경변수 정의
REQUIRED_VARS = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
]

RECOMMENDED_VARS = [
    "SUPABASE_SERVICE_ROLE_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
]

OPTIONAL_VARS = [
    "AI_PROVIDER",
    "APP_ENV",
    "DEBUG",
    "REDIS_URL",
    "DATABASE_URL",
    "ALLOWED_ORIGINS",
]

def check_local_env() -> Tuple[bool, List[str]]:
    """
    로컬 환경변수 확인

    Returns:
        (success, missing_required_vars)
    """
    print_header("로컬 환경변수 검증")

    missing_required = []
    missing_recommended = []
    found_vars = []

    print(f"{Colors.BOLD}필수 환경변수:{Colors.ENDC}")
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if value and value.strip() != "":
            # placeholder 체크
            if "placeholder" in value.lower():
                print_warning(f"  {var}: PLACEHOLDER (mock mode)")
            else:
                masked = value[:20] + "..." if len(value) > 20 else value
                print_success(f"  {var}: {masked}")
            found_vars.append(var)
        else:
            print_error(f"  {var}: NOT SET")
            missing_required.append(var)

    print(f"\n{Colors.BOLD}권장 환경변수:{Colors.ENDC}")
    for var in RECOMMENDED_VARS:
        value = os.getenv(var)
        if value and value.strip() != "":
            masked = value[:20] + "..." if len(value) > 20 else value
            print_success(f"  {var}: {masked}")
            found_vars.append(var)
        else:
            print_warning(f"  {var}: NOT SET (optional but recommended)")
            missing_recommended.append(var)

    print(f"\n{Colors.BOLD}선택적 환경변수:{Colors.ENDC}")
    for var in OPTIONAL_VARS:
        value = os.getenv(var)
        if value and value.strip() != "":
            print_info(f"  {var}: {value}")
            found_vars.append(var)
        else:
            print_info(f"  {var}: NOT SET (optional)")

    # 결과 요약
    print_header("로컬 검증 결과")
    if not missing_required:
        print_success("모든 필수 환경변수가 설정되어 있습니다.")
        return True, []
    else:
        print_error(f"필수 환경변수 {len(missing_required)}개 누락")
        print("\n누락된 환경변수:")
        for var in missing_required:
            print(f"  - {var}")
        print("\n.env 파일에 추가하거나 시스템 환경변수로 설정하세요.")
        return False, missing_required

def check_vercel_env(environment: str = "production") -> Tuple[bool, List[str]]:
    """
    Vercel 환경변수 확인 (CLI 사용)

    Args:
        environment: production, preview, development

    Returns:
        (success, missing_required_vars)
    """
    print_header(f"Vercel 환경변수 검증 (Environment: {environment})")

    # Vercel CLI 확인
    try:
        result = subprocess.run(
            ["vercel", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print_info(f"Vercel CLI 버전: {result.stdout.strip()}")
    except FileNotFoundError:
        print_error("Vercel CLI가 설치되지 않았습니다.")
        print("설치: npm i -g vercel")
        return False, []
    except subprocess.CalledProcessError:
        print_error("Vercel CLI 실행 실패")
        return False, []

    # Vercel 환경변수 목록 조회
    print_info(f"Vercel {environment} 환경변수 조회 중...")
    try:
        result = subprocess.run(
            ["vercel", "env", "ls", environment],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout

        # 환경변수 파싱 (간단한 파싱)
        found_vars = []
        for line in output.split("\n"):
            for var in REQUIRED_VARS + RECOMMENDED_VARS + OPTIONAL_VARS:
                if var in line:
                    found_vars.append(var)

        # 결과 출력
        missing_required = []
        missing_recommended = []

        print(f"\n{Colors.BOLD}필수 환경변수:{Colors.ENDC}")
        for var in REQUIRED_VARS:
            if var in found_vars:
                print_success(f"  {var}: SET")
            else:
                print_error(f"  {var}: NOT SET")
                missing_required.append(var)

        print(f"\n{Colors.BOLD}권장 환경변수:{Colors.ENDC}")
        for var in RECOMMENDED_VARS:
            if var in found_vars:
                print_success(f"  {var}: SET")
            else:
                print_warning(f"  {var}: NOT SET")
                missing_recommended.append(var)

        print(f"\n{Colors.BOLD}선택적 환경변수:{Colors.ENDC}")
        for var in OPTIONAL_VARS:
            if var in found_vars:
                print_info(f"  {var}: SET")
            else:
                print_info(f"  {var}: NOT SET")

        # 결과 요약
        print_header(f"Vercel {environment} 검증 결과")
        if not missing_required:
            print_success("모든 필수 환경변수가 설정되어 있습니다.")
            if missing_recommended:
                print_warning(f"권장 환경변수 {len(missing_recommended)}개 누락 (선택적)")
            return True, []
        else:
            print_error(f"필수 환경변수 {len(missing_required)}개 누락")
            print("\n누락된 환경변수:")
            for var in missing_required:
                print(f"  - {var}")
            print(f"\n설정 방법:")
            print(f"  vercel env add {missing_required[0]} {environment}")
            return False, missing_required

    except subprocess.CalledProcessError as e:
        print_error(f"Vercel CLI 실행 실패: {e}")
        print("Vercel에 로그인하세요: vercel login")
        return False, []

def load_env_file(env_file: Path) -> Dict[str, str]:
    """
    .env 파일 로드

    Args:
        env_file: .env 파일 경로

    Returns:
        환경변수 딕셔너리
    """
    env_vars = {}
    if not env_file.exists():
        return env_vars

    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # 따옴표 제거
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                env_vars[key] = value

    return env_vars

def check_env_file() -> Tuple[bool, List[str]]:
    """
    .env 파일 검증

    Returns:
        (success, missing_required_vars)
    """
    print_header(".env 파일 검증")

    env_file = Path(".env")
    if not env_file.exists():
        print_error(".env 파일을 찾을 수 없습니다.")
        print("프로젝트 루트에 .env 파일을 생성하세요.")
        return False, REQUIRED_VARS

    env_vars = load_env_file(env_file)
    print_success(f".env 파일 발견: {len(env_vars)}개 환경변수")

    missing_required = []
    missing_recommended = []

    print(f"\n{Colors.BOLD}필수 환경변수:{Colors.ENDC}")
    for var in REQUIRED_VARS:
        value = env_vars.get(var, "")
        if value and "placeholder" not in value.lower():
            masked = value[:20] + "..." if len(value) > 20 else value
            print_success(f"  {var}: {masked}")
        elif value and "placeholder" in value.lower():
            print_warning(f"  {var}: PLACEHOLDER (mock mode)")
        else:
            print_error(f"  {var}: NOT SET")
            missing_required.append(var)

    print(f"\n{Colors.BOLD}권장 환경변수:{Colors.ENDC}")
    for var in RECOMMENDED_VARS:
        value = env_vars.get(var, "")
        if value:
            masked = value[:20] + "..." if len(value) > 20 else value
            print_success(f"  {var}: {masked}")
        else:
            print_warning(f"  {var}: NOT SET")
            missing_recommended.append(var)

    # 결과 요약
    print_header(".env 파일 검증 결과")
    if not missing_required:
        print_success("모든 필수 환경변수가 .env 파일에 설정되어 있습니다.")
        return True, []
    else:
        print_error(f"필수 환경변수 {len(missing_required)}개 누락")
        return False, missing_required

def main():
    parser = argparse.ArgumentParser(
        description="Vercel 환경변수 검증 스크립트"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="로컬 환경변수 확인"
    )
    parser.add_argument(
        "--vercel",
        choices=["production", "preview", "development"],
        help="Vercel 환경변수 확인"
    )
    parser.add_argument(
        "--env-file",
        action="store_true",
        help=".env 파일 확인"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 검증 실행 (local + vercel + env-file)"
    )

    args = parser.parse_args()

    # 아무 옵션도 없으면 local 검증
    if not any([args.local, args.vercel, args.env_file, args.all]):
        args.local = True

    results = []

    # .env 파일 검증
    if args.env_file or args.all:
        success, missing = check_env_file()
        results.append(("env_file", success))

    # 로컬 환경변수 검증
    if args.local or args.all:
        success, missing = check_local_env()
        results.append(("local", success))

    # Vercel 환경변수 검증
    if args.vercel or args.all:
        env = args.vercel if args.vercel else "production"
        success, missing = check_vercel_env(env)
        results.append((f"vercel_{env}", success))

    # 최종 결과 요약
    print_header("최종 검증 결과")

    all_passed = all(success for _, success in results)

    for name, success in results:
        if success:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")

    if all_passed:
        print_header("✅ 모든 검증 통과")
        print("Vercel 배포를 진행해도 좋습니다.")
        sys.exit(0)
    else:
        print_header("❌ 검증 실패")
        print("누락된 환경변수를 설정한 후 다시 시도하세요.")
        print("\n참고 문서:")
        print("  - docs/VERCEL_ENV_SETUP.md")
        print("  - docs/08_Vercel_Architecture_Guide.md")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단됨")
        sys.exit(0)
