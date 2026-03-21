"""
Migration 007 검증 스크립트
Conversation 테이블과 RPC 함수가 제대로 생성되었는지 확인
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.shared.database import get_supabase_client

print("=" * 80)
print("Migration 007 검증")
print("=" * 80)
print()

try:
    client = get_supabase_client(use_service_role=True)
    print("[OK] Supabase 클라이언트 연결")
except Exception as e:
    print(f"[FAIL] Supabase 연결 실패: {e}")
    sys.exit(1)

print()
print("[1] 테이블 존재 확인")
print("-" * 80)

tables_to_check = [
    "conversation_sessions",
    "conversation_messages"
]

tables_found = []
for table_name in tables_to_check:
    try:
        # 테이블에 SELECT 권한이 있는지 확인 (limit 0으로 실제 데이터 조회 X)
        result = client.table(table_name).select("*").limit(0).execute()
        print(f"[OK] {table_name}")
        tables_found.append(table_name)
    except Exception as e:
        print(f"[FAIL] {table_name} - {str(e)[:100]}")

print()
print(f"테이블 생성: {len(tables_found)}/{len(tables_to_check)}")
print()

print("[2] RPC 함수 존재 확인")
print("-" * 80)

rpc_functions = [
    ("get_or_create_conversation_session", {
        "p_session_id": "verify-test-session",
        "p_region": "청량리동"
    }),
    ("get_conversation_history", {
        "p_session_id": "verify-test-session",
        "p_limit": 1
    }),
]

rpcs_found = []
for func_name, params in rpc_functions:
    try:
        # RPC 함수 호출 (실제 데이터 생성/조회)
        result = client.rpc(func_name, params).execute()
        print(f"[OK] {func_name}()")
        rpcs_found.append(func_name)
    except Exception as e:
        error_msg = str(e)
        if "Could not find the function" in error_msg:
            print(f"[FAIL] {func_name}() - 함수가 존재하지 않음")
        else:
            print(f"[FAIL] {func_name}() - {error_msg[:100]}")

print()
print(f"RPC 함수 생성: {len(rpcs_found)}/{len(rpc_functions)}")
print()

# save_conversation_message 테스트
print("[3] save_conversation_message 테스트")
print("-" * 80)

try:
    # 세션이 존재하는지 확인
    session_result = client.rpc("get_or_create_conversation_session", {
        "p_session_id": "verify-test-session-save",
        "p_region": "청량리동"
    }).execute()

    if session_result.data:
        print(f"[OK] 세션 생성/조회 성공")

        # 메시지 저장
        message_id = client.rpc("save_conversation_message", {
            "p_session_id": "verify-test-session-save",
            "p_role": "user",
            "p_content": "테스트 메시지입니다",
        }).execute()

        print(f"[OK] save_conversation_message() - Message ID: {message_id.data}")
        rpcs_found.append("save_conversation_message")
    else:
        print(f"[FAIL] 세션 생성 실패")
except Exception as e:
    print(f"[FAIL] save_conversation_message() - {str(e)[:150]}")

print()

print("=" * 80)
print("검증 결과")
print("=" * 80)
print()

all_passed = (
    len(tables_found) == len(tables_to_check) and
    len(rpcs_found) >= 3  # 최소 3개 RPC 함수
)

if all_passed:
    print("[SUCCESS] Migration 007이 성공적으로 적용되었습니다!")
    print()
    print("생성된 테이블:")
    for table in tables_found:
        print(f"  - {table}")
    print()
    print("생성된 RPC 함수:")
    for rpc in rpcs_found:
        print(f"  - {rpc}()")
    print()
    print("다음 단계:")
    print("  1. .env에서 FORCE_CONVERSATION_MOCK=false 설정")
    print("  2. 서버 재시작")
    print("  3. python test_local_chat.py 실행")
    print("  4. 로그에서 'Production mode: ConversationManager' 확인")
    print()
else:
    print("[FAIL] Migration 007이 완전히 적용되지 않았습니다.")
    print()
    print(f"테이블: {len(tables_found)}/{len(tables_to_check)}")
    print(f"RPC 함수: {len(rpcs_found)}/5 (예상)")
    print()
    print("해결 방법:")
    print("  1. Supabase SQL Editor에서 migrations/007_add_conversation_tables.sql 실행")
    print("  2. MIGRATION_007_GUIDE.md 참고")
    print("  3. 이 스크립트 다시 실행: python verify_migration_007.py")
    print()

    sys.exit(1)
