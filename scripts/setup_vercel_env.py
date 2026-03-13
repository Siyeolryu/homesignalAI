#!/usr/bin/env python3
"""
Vercel 환경변수 설정 스크립트 (Python)
사용법: python scripts/setup_vercel_env.py
"""

import subprocess
import sys
from typing import List, Tuple

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

def set_env_var(name: str, value: str, environments: List[str] = None):
    """환경변수 설정"""
    if environments is None:
        environments = ["production", "preview", "development"]

    print(f"\n{Colors.OKCYAN}Setting {name}...{Colors.ENDC}")

    for env in environments:
        cmd = ["vercel", "env", "add", name, env]
        if run_command(cmd, input_text=value):
            print(f"  ✓ {env} 환경 설정 완료")
        else:
            print(f"  ✗ {env} 환경 설정 실패")

    print_success(f"{name} 설정 완료")

def main():
    """메인 함수"""
    print_header("Vercel 환경변수 자동 설정")

    # 1. Vercel CLI 확인
    if not check_vercel_cli():
        sys.exit(1)

    # 2. Supabase 환경변수 설정
    print_header("1. Supabase 환경변수 설정")

    supabase_vars = {
        "SUPABASE_URL": "https://yietqoikdaqpwmmvamtv.supabase.co",
        "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpZXRxb2lrZGFxcHdtbXZhbXR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMjMyNjksImV4cCI6MjA4NzU5OTI2OX0.cnGFGUsn05TpVIvZyk6Sn6jEUdkTPzqc9YHOLnPr6NY",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpZXRxb2lrZGFxcHdtbXZhbXR2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAyMzI2OSwiZXhwIjoyMDg3NTk5MjY5fQ.F4HvWwUiFMysGP06DW45v5RbxG7UoW38q8JI2z1MIDM"
    }

    for name, value in supabase_vars.items():
        set_env_var(name, value)

    # 3. App 설정 환경변수
    print_header("2. App 설정 환경변수")

    # APP_ENV (환경별로 다르게)
    print(f"\n{Colors.OKCYAN}Setting APP_ENV...{Colors.ENDC}")
    set_env_var("APP_ENV", "production", ["production"])
    set_env_var("APP_ENV", "preview", ["preview"])
    set_env_var("APP_ENV", "development", ["development"])

    # DEBUG (환경별로 다르게)
    print(f"\n{Colors.OKCYAN}Setting DEBUG...{Colors.ENDC}")
    set_env_var("DEBUG", "false", ["production", "preview"])
    set_env_var("DEBUG", "true", ["development"])

    # AI_PROVIDER
    set_env_var("AI_PROVIDER", "openai")

    # 4. OPENAI_API_KEY (사용자 입력)
    print_header("3. OPENAI_API_KEY 설정")

    print_warning("OPENAI_API_KEY를 입력해주세요.")
    print("(OpenAI API 키가 없다면 Enter를 눌러 건너뛰세요)")
    print("")

    try:
        openai_key = input("OPENAI_API_KEY (선택사항): ").strip()

        if openai_key:
            set_env_var("OPENAI_API_KEY", openai_key)
        else:
            print_warning("OPENAI_API_KEY 건너뛰기 (나중에 설정 가능)")
    except KeyboardInterrupt:
        print("\n\n중단됨")
        sys.exit(0)

    # 5. 완료
    print_header("✅ 환경변수 설정 완료!")

    print_info("설정된 환경변수 확인:")
    subprocess.run(["vercel", "env", "ls"])

    print("\n")
    print_header("🚀 다음 단계")
    print("1. vercel --prod (프로덕션 배포)")
    print("2. curl https://your-backend.vercel.app/health (검증)")
    print("")
    print("💡 OPENAI_API_KEY를 나중에 설정하려면:")
    print("   vercel env add OPENAI_API_KEY production")
    print("")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단됨")
        sys.exit(0)
