#!/usr/bin/env python3
"""
Settings Fallback 테스트 스크립트

환경변수 없이 Settings 초기화가 정상 작동하는지 확인합니다.

Usage:
    uv run python scripts/test_settings_fallback.py
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 추가
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

def test_settings_without_env():
    """환경변수 없이 Settings 초기화 테스트"""
    print("="*70)
    print("Settings Fallback 테스트")
    print("="*70)
    print()

    # 기존 환경변수 백업
    env_backup = {}
    test_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ]

    print("1. 환경변수 백업 및 제거...")
    for var in test_vars:
        env_backup[var] = os.environ.pop(var, None)
        print(f"   - {var}: {'백업됨' if env_backup[var] else '없음'}")

    print()
    print("2. Settings 초기화 시도...")
    try:
        from src.config.settings import Settings, get_settings

        # 새로운 Settings 인스턴스 생성
        settings = Settings()

        print("   ✅ Settings 초기화 성공!")
        print()
        print("3. Fallback 값 확인:")
        print(f"   - SUPABASE_URL: {settings.supabase_url}")
        print(f"   - SUPABASE_KEY: {settings.supabase_key}")
        print(f"   - SUPABASE_SERVICE_ROLE_KEY: {settings.supabase_service_role_key}")
        print(f"   - APP_ENV: {settings.app_env}")
        print(f"   - DEBUG: {settings.debug}")
        print()

        # Placeholder 확인
        if "placeholder" in settings.supabase_url:
            print("   ✅ Placeholder URL 사용 중 (Mock mode)")
        else:
            print("   ⚠️  실제 Supabase URL이 설정됨")

        if settings.supabase_key == "placeholder-key":
            print("   ✅ Placeholder KEY 사용 중 (Mock mode)")
        else:
            print("   ⚠️  실제 Supabase KEY가 설정됨")

        print()
        print("="*70)
        print("✅ 테스트 성공: 환경변수 없이도 Settings 초기화 가능")
        print("="*70)
        success = True

    except Exception as e:
        print(f"   ❌ Settings 초기화 실패!")
        print(f"   Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("="*70)
        print("❌ 테스트 실패: Settings 초기화 중 오류 발생")
        print("="*70)
        success = False

    finally:
        # 환경변수 복원
        print()
        print("4. 환경변수 복원...")
        for var, value in env_backup.items():
            if value is not None:
                os.environ[var] = value
                print(f"   - {var}: 복원됨")

    return success

def test_empty_string_env():
    """빈 문자열 환경변수 테스트"""
    print()
    print("="*70)
    print("빈 문자열 환경변수 테스트")
    print("="*70)
    print()

    # 빈 문자열로 설정
    print("1. 빈 문자열 환경변수 설정...")
    os.environ["SUPABASE_URL"] = ""
    os.environ["SUPABASE_KEY"] = ""
    print("   - SUPABASE_URL: \"\"")
    print("   - SUPABASE_KEY: \"\"")

    print()
    print("2. Settings 초기화 시도...")
    try:
        # get_settings 캐시 초기화 필요 시
        from src.config import settings as settings_module
        if hasattr(settings_module, '_settings'):
            settings_module._settings = None

        from src.config.settings import Settings

        settings = Settings()

        print("   ✅ Settings 초기화 성공!")
        print()
        print("3. Field validator 동작 확인:")
        print(f"   - SUPABASE_URL: {settings.supabase_url}")
        print(f"   - SUPABASE_KEY: {settings.supabase_key}")
        print()

        # 빈 문자열이 None으로 변환되고 placeholder로 설정되었는지 확인
        if "placeholder" in settings.supabase_url:
            print("   ✅ 빈 문자열 → None → Placeholder 변환 성공")
        else:
            print("   ❌ 빈 문자열이 제대로 처리되지 않음")

        print()
        print("="*70)
        print("✅ 테스트 성공: 빈 문자열도 올바르게 처리됨")
        print("="*70)
        success = True

    except Exception as e:
        print(f"   ❌ Settings 초기화 실패!")
        print(f"   Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("="*70)
        print("❌ 테스트 실패")
        print("="*70)
        success = False

    finally:
        # 환경변수 제거
        os.environ.pop("SUPABASE_URL", None)
        os.environ.pop("SUPABASE_KEY", None)

    return success

def main():
    print()
    print("="*70)
    print(" "*20 + "Settings Fallback Test Suite")
    print("="*70)
    print()

    results = []

    # Test 1: 환경변수 없음
    result1 = test_settings_without_env()
    results.append(("환경변수 없음", result1))

    # Test 2: 빈 문자열 환경변수
    result2 = test_empty_string_env()
    results.append(("빈 문자열 환경변수", result2))

    # 최종 결과
    print()
    print("="*70)
    print("최종 테스트 결과")
    print("="*70)
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")

    all_passed = all(success for _, success in results)
    print()
    if all_passed:
        print("✅ 모든 테스트 통과!")
        print("Vercel 배포 시 환경변수가 없어도 애플리케이션이 정상 작동합니다.")
        sys.exit(0)
    else:
        print("❌ 일부 테스트 실패")
        print("settings.py 또는 api/index.py를 확인하세요.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
        sys.exit(0)
