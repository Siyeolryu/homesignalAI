#!/usr/bin/env python3
"""
Vercel 환경변수 자동 설정 스크립트

로컬 .env 파일을 읽어 Vercel 프로젝트에 환경변수를 자동으로 설정합니다.

Requirements:
    - Vercel CLI 설치: npm i -g vercel
    - Vercel 로그인: vercel login

Usage:
    uv run python scripts/setup_vercel_env.py
    uv run python scripts/setup_vercel_env.py --environment production
    uv run python scripts/setup_vercel_env.py --dry-run  # 테스트 실행
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

# 색상 코드 (Windows 호환)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """헤더 출력"""
    print(f"\n{'='*50}")
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{'='*50}\n")

def print_success(text: str):
    """성공 메시지 출력"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text: str):
    """정보 메시지 출력"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    """경고 메시지 출력"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def run_command(cmd: List[str], input_text: str = None) -> bool:
    """명령어 실행"""
    try:
        if input_text:
            result = subprocess.run(
                cmd,
                input=input_text,
                text=True,
                capture_output=True,
                check=True
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                check=True
            )
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ 오류: {e}{Colors.ENDC}")
        if e.stderr:
            print(f"상세: {e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr}")
        return False
    except FileNotFoundError:
        print(f"{Colors.FAIL}❌ Vercel CLI가 설치되지 않았습니다.{Colors.ENDC}")
        print(f"{Colors.WARNING}설치: npm i -g vercel{Colors.ENDC}")
        return False

def load_env_file(env_file: Path) -> dict[str, str]:
    """
    .env 파일을 파싱하여 환경변수 딕셔너리 반환

    Args:
        env_file: .env 파일 경로

    Returns:
        환경변수 딕셔너리 {key: value}
    """
    env_vars = {}
    if not env_file.exists():
        print_warning(f"{env_file} 파일을 찾을 수 없습니다.")
        return env_vars

    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 주석이나 빈 줄 무시
            if not line or line.startswith("#"):
                continue

            # key=value 파싱
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # 따옴표 제거
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # placeholder 값 스킵
                if "placeholder" not in value.lower() and value:
                    env_vars[key] = value

    return env_vars


def check_vercel_cli():
    """Vercel CLI 설치 확인"""
    print_info("Vercel CLI 확인 중...")
    try:
        result = subprocess.run(
            ["vercel", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print_success(f"Vercel CLI 버전: {version}")
        return True
    except:
        print_warning("Vercel CLI가 설치되지 않았습니다.")
        print("설치: npm i -g vercel")
        return False


def set_vercel_env(
    key: str, value: str, environment: str, dry_run: bool = False
) -> bool:
    """
    Vercel 환경변수 설정

    Args:
        key: 환경변수 키
        value: 환경변수 값
        environment: 환경 (production, preview, development)
        dry_run: 테스트 모드 (실제로 설정하지 않음)

    Returns:
        성공 여부
    """
    if dry_run:
        print(f"  [DRY-RUN] vercel env add {key} {environment}")
        return True

    try:
        # vercel env add 명령 실행
        process = subprocess.Popen(
            ["vercel", "env", "add", key, environment],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 값 입력
        stdout, stderr = process.communicate(input=value)

        if process.returncode == 0:
            return True
        else:
            print(f"{Colors.FAIL}  ✗ 설정 실패: {stderr}{Colors.ENDC}")
            return False

    except Exception as e:
        print(f"{Colors.FAIL}  ✗ 오류: {e}{Colors.ENDC}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Vercel 환경변수 자동 설정"
    )
    parser.add_argument(
        "--environment",
        "-e",
        choices=["production", "preview", "development"],
        default="production",
        help="Vercel 환경 (기본: production)",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help=".env 파일 경로 (기본: .env)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="테스트 실행 (실제로 설정하지 않음)",
    )
    parser.add_argument(
        "--skip-optional",
        action="store_true",
        help="선택적 환경변수 건너뛰기",
    )
    args = parser.parse_args()

    print_header("Vercel 환경변수 설정 스크립트")

    # Vercel CLI 확인
    if not args.dry_run and not check_vercel_cli():
        sys.exit(1)

    # .env 파일 로드
    print_info(f".env 파일 로드: {args.env_file}")
    env_vars = load_env_file(args.env_file)

    if not env_vars:
        print_warning("유효한 환경변수가 없습니다.")
        sys.exit(1)

    print_success(f"{len(env_vars)}개의 환경변수 발견")

    # 필수 환경변수 확인
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if var not in env_vars]

    if missing_vars:
        print_warning(f"필수 환경변수 누락: {', '.join(missing_vars)}")
        print("계속하려면 .env 파일에 추가하세요.")
        sys.exit(1)

    # Vercel에 환경변수 설정
    print_header(f"Vercel에 환경변수 설정 (Environment: {args.environment})")

    if args.dry_run:
        print_warning("DRY-RUN 모드: 실제로 설정하지 않습니다.\n")

    success_count = 0
    fail_count = 0

    # 선택적 환경변수 목록
    optional_vars = [
        "REDIS_URL",
        "DATABASE_URL",
        "ANTHROPIC_API_KEY",
        "CRAWLER_REQUESTS_PER_MINUTE",
    ]

    for key, value in env_vars.items():
        # 선택적 변수 스킵 옵션
        if args.skip_optional and key in optional_vars:
            print(f"  ⏭️  {key} 건너뜀 (선택적 변수)")
            continue

        # 민감한 정보 마스킹 출력
        masked_value = value[:8] + "..." if len(value) > 8 else "***"
        print(f"\n{Colors.OKCYAN}설정 중: {key}={masked_value}{Colors.ENDC}")

        if set_vercel_env(key, value, args.environment, args.dry_run):
            print_success(f"  ✓ {key} 설정 완료")
            success_count += 1
        else:
            fail_count += 1

    # 결과 출력
    print_header("설정 완료")
    print_success(f"성공: {success_count}개")
    if fail_count > 0:
        print(f"{Colors.FAIL}실패: {fail_count}개{Colors.ENDC}")

    if not args.dry_run:
        print_header("다음 단계")
        print("1. Vercel Dashboard에서 환경변수 확인")
        print("   https://vercel.com/dashboard")
        print("2. 재배포하여 환경변수 적용")
        print("   vercel --prod")

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단됨")
        sys.exit(0)
