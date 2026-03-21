#!/usr/bin/env python3
"""
환경변수 검증 스크립트

로컬 또는 Vercel 환경에서 필수 환경변수가 올바르게 설정되었는지 확인합니다.

Usage:
    uv run python scripts/validate_env.py
    uv run python scripts/validate_env.py --strict  # 프로덕션 모드
"""

import os
import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))


def validate_environment_variables(strict: bool = False):
    """환경변수 검증"""
    print("=" * 60)
    print("환경변수 검증 시작")
    print("=" * 60)

    errors = []
    warnings = []
    info = []

    # 1. 필수 환경변수 확인
    required_vars = {
        "SUPABASE_URL": "Supabase 프로젝트 URL",
        "SUPABASE_KEY": "Supabase anon/public key",
    }

    print("\n[1] 필수 환경변수 확인")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var}: 설정되지 않음 ({description})")
        elif value.startswith("placeholder") or value == "":
            warnings.append(
                f"⚠️  {var}: placeholder 값 사용 중 ({description})"
            )
        else:
            info.append(f"✅ {var}: 설정됨")

    # 2. 선택적 환경변수 확인
    optional_vars = {
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase service_role key (Ingest API 필수)",
        "OPENAI_API_KEY": "OpenAI API key (Chat 기능 필수)",
        "ANTHROPIC_API_KEY": "Anthropic API key (Chat 기능 선택)",
        "REDIS_URL": "Redis URL (캐싱 기능)",
    }

    print("\n[2] 선택적 환경변수 확인")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value:
            warnings.append(f"⚠️  {var}: 설정되지 않음 ({description})")
        else:
            info.append(f"✅ {var}: 설정됨")

    # 3. AI Provider 확인
    print("\n[3] AI Provider 확인")
    ai_provider = os.getenv("AI_PROVIDER", "openai")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if ai_provider == "openai" and not openai_key:
        errors.append(
            "❌ AI_PROVIDER=openai인데 OPENAI_API_KEY가 설정되지 않음"
        )
    elif ai_provider == "anthropic" and not anthropic_key:
        errors.append(
            "❌ AI_PROVIDER=anthropic인데 ANTHROPIC_API_KEY가 설정되지 않음"
        )
    else:
        info.append(f"✅ AI_PROVIDER={ai_provider} (적절한 키 설정됨)")

    # 4. 프로덕션 환경 체크 (strict 모드)
    if strict:
        print("\n[4] 프로덕션 환경 검증 (Strict 모드)")
        app_env = os.getenv("APP_ENV", "development")
        debug = os.getenv("DEBUG", "true").lower() == "true"

        if app_env != "production":
            warnings.append(
                f"⚠️  APP_ENV={app_env} (프로덕션에서는 'production' 권장)"
            )
        if debug:
            warnings.append(
                "⚠️  DEBUG=true (프로덕션에서는 'false' 권장)"
            )

        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
        if not allowed_origins:
            errors.append(
                "❌ ALLOWED_ORIGINS 미설정 (프로덕션 CORS 보안 필수)"
            )
        else:
            info.append(f"✅ ALLOWED_ORIGINS={allowed_origins}")

    # 5. Settings 클래스 로드 테스트
    print("\n[5] Settings 클래스 로드 테스트")
    try:
        from src.config.settings import settings

        info.append("✅ Settings 클래스 로드 성공")
        info.append(f"   - supabase_url: {settings.supabase_url}")
        info.append(f"   - ai_provider: {settings.ai_provider}")
        info.append(f"   - app_env: {settings.app_env}")
    except Exception as e:
        errors.append(f"❌ Settings 클래스 로드 실패: {e}")

    # 결과 출력
    print("\n" + "=" * 60)
    print("검증 결과")
    print("=" * 60)

    if errors:
        print("\n🔴 오류:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print("\n🟡 경고:")
        for warning in warnings:
            print(f"  {warning}")

    if info:
        print("\n🟢 정상:")
        for item in info:
            print(f"  {item}")

    # 종료 코드
    if errors:
        print("\n❌ 환경변수 검증 실패")
        print("\n해결 방법:")
        print("  1. .env 파일을 생성하거나 수정하세요")
        print("  2. Vercel 환경에서는 Dashboard에서 환경변수를 설정하세요")
        print("  3. 가이드: docs/VERCEL_ENV_SETUP.md 참조")
        return False
    elif warnings and strict:
        print("\n⚠️  경고가 있지만 실행 가능 (프로덕션에서는 수정 권장)")
        return True
    else:
        print("\n✅ 환경변수 검증 성공")
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="환경변수 검증 스크립트"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="프로덕션 모드 검증 (ALLOWED_ORIGINS, DEBUG 등 엄격 체크)",
    )
    args = parser.parse_args()

    success = validate_environment_variables(strict=args.strict)
    sys.exit(0 if success else 1)
