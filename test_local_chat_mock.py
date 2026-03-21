"""
로컬호스트 대화형 챗봇 테스트 스크립트 (Mock 모드)

이 스크립트는 서버를 Mock 모드로 시작하고 3턴 대화를 테스트합니다.
"""

import httpx
import json
import time
import subprocess
import sys
import os
from pathlib import Path

# Force Mock mode by setting SUPABASE_URL to empty
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_KEY"] = ""

# Start server in subprocess
print("=" * 80)
print("Starting server in Mock mode...")
print("=" * 80)

server_process = subprocess.Popen(
    [
        sys.executable, "-m", "uvicorn",
        "src.main:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ],
    env={**os.environ, "SUPABASE_URL": "", "SUPABASE_KEY": ""},
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=Path(__file__).parent
)

# Wait for server to start
print("Waiting for server to start...")
time.sleep(5)

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test-session-" + str(int(time.time()))

try:
    print("=" * 80)
    print("대화형 RAG 챗봇 로컬 테스트 (Mock 모드)")
    print("=" * 80)
    print(f"Session ID: {SESSION_ID}")
    print()

    # 서버 헬스 체크
    print("[1] 서버 헬스 체크...")
    print("-" * 80)
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        print(f"응답 코드: {response.status_code}")
        print(f"응답 내용: {response.json()}")
        print()
    except Exception as e:
        print(f"오류: {e}")
        print("서버가 시작되지 않았을 수 있습니다.")
        sys.exit(1)

    # 턴 1: 첫 번째 질문
    print("[2] 턴 1: 청량리 아파트 가격 질문")
    print("-" * 80)
    request_1 = {
        "message": "청량리 아파트 가격이 오를까요?",
        "session_id": SESSION_ID,
        "region": "청량리동"
    }

    try:
        response_1 = httpx.post(
            f"{BASE_URL}/api/v1/chat",
            json=request_1,
            timeout=30.0
        )
        print(f"응답 코드: {response_1.status_code}")

        if response_1.status_code == 200:
            data_1 = response_1.json()
            print(f"Session ID: {data_1.get('session_id')}")
            print(f"Fallback: {data_1.get('fallback', False)}")
            print(f"Answer: {data_1.get('answer', 'N/A')[:200]}...")
            print(f"Sources: {len(data_1.get('sources', []))}개")
            if data_1.get('forecast_summary'):
                print(f"Forecast: {data_1['forecast_summary']}")
        else:
            print(f"오류: {response_1.text}")

        print()
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

    # 턴 2: 이전 대화 맥락 참조
    print("[3] 턴 2: 이문동 질문 (맥락: 청량리와 비교)")
    print("-" * 80)
    request_2 = {
        "message": "이문동은 어떤가요?",
        "session_id": SESSION_ID,  # 같은 세션 ID 사용
        "region": "이문동"
    }

    try:
        response_2 = httpx.post(
            f"{BASE_URL}/api/v1/chat",
            json=request_2,
            timeout=30.0
        )
        print(f"응답 코드: {response_2.status_code}")

        if response_2.status_code == 200:
            data_2 = response_2.json()
            print(f"Session ID: {data_2.get('session_id')}")
            print(f"Fallback: {data_2.get('fallback', False)}")
            print(f"Answer: {data_2.get('answer', 'N/A')[:200]}...")
            print(f"Sources: {len(data_2.get('sources', []))}개")
        else:
            print(f"오류: {response_2.text}")

        print()
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

    # 턴 3: 재개발 질문 (이문동 맥락 유지)
    print("[4] 턴 3: 재개발 질문 (맥락: 이문동)")
    print("-" * 80)
    request_3 = {
        "message": "재개발 가능성은 어떤가요?",
        "session_id": SESSION_ID,  # 같은 세션 ID 사용
        "region": "이문동"
    }

    try:
        response_3 = httpx.post(
            f"{BASE_URL}/api/v1/chat",
            json=request_3,
            timeout=30.0
        )
        print(f"응답 코드: {response_3.status_code}")

        if response_3.status_code == 200:
            data_3 = response_3.json()
            print(f"Session ID: {data_3.get('session_id')}")
            print(f"Fallback: {data_3.get('fallback', False)}")
            print(f"Answer: {data_3.get('answer', 'N/A')[:200]}...")
            print(f"Sources: {len(data_3.get('sources', []))}개")
        else:
            print(f"오류: {response_3.text}")

        print()
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 80)
    print("테스트 완료!")
    print("=" * 80)
    print()
    print("검증 포인트:")
    print("  [1] 세 번의 요청 모두 같은 session_id 사용")
    print("  [2] 턴 2에서 '이문동은 어떤가요?' → 청량리와 비교하는 맥락 이해")
    print("  [3] 턴 3에서 '재개발 가능성' → 이문동에 대한 질문인 걸 이해")
    print()
    print("대화 히스토리가 제대로 유지되고 있는지 확인하세요!")
    print()

finally:
    # Cleanup: kill server
    print("Stopping server...")
    server_process.terminate()
    server_process.wait(timeout=5)
    print("Server stopped.")
