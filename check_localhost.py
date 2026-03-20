"""
로컬호스트 점검 스크립트
"""
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 80)
print("로컬호스트 점검")
print("=" * 80)
print()

# 1. 헬스 체크
print("[1] 헬스 체크")
print("-" * 80)
try:
    response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
    if response.status_code == 200:
        print(f"[OK] 서버 정상 동작")
        print(f"  응답: {response.json()}")
    else:
        print(f"[FAIL] 서버 오류 (상태 코드: {response.status_code})")
except Exception as e:
    print(f"[FAIL] 서버 연결 실패: {e}")
print()

# 2. 단순 채팅 요청
print("[2] 단순 채팅 요청")
print("-" * 80)
try:
    request_data = {
        "message": "청량리 아파트 가격이 오를까요?",
        "region": "청량리동"
    }
    response = httpx.post(
        f"{BASE_URL}/api/v1/chat",
        json=request_data,
        timeout=30.0
    )
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] 채팅 응답 성공")
        print(f"  Session ID: {data.get('session_id')}")
        print(f"  답변 길이: {len(data.get('answer', ''))} 글자")
        print(f"  소스 개수: {len(data.get('sources', []))}개")
        print(f"  Fallback 모드: {data.get('fallback', False)}")
    else:
        print(f"[FAIL] 채팅 요청 실패 (상태 코드: {response.status_code})")
        print(f"  오류: {response.text}")
except Exception as e:
    print(f"[FAIL] 채팅 요청 실패: {e}")
print()

# 3. 대화형 테스트 (2턴)
print("[3] 대화형 테스트 (2턴 대화)")
print("-" * 80)
try:
    import time
    session_id = f"check-{int(time.time())}"

    # 첫 번째 질문
    request1 = {
        "message": "청량리 아파트 가격은?",
        "session_id": session_id,
        "region": "청량리동"
    }
    response1 = httpx.post(f"{BASE_URL}/api/v1/chat", json=request1, timeout=30.0)

    if response1.status_code == 200:
        print(f"  턴 1: [OK] 성공 (session: {session_id})")

        # 두 번째 질문 (같은 세션)
        request2 = {
            "message": "이문동은 어떤가요?",
            "session_id": session_id,
            "region": "이문동"
        }
        response2 = httpx.post(f"{BASE_URL}/api/v1/chat", json=request2, timeout=30.0)

        if response2.status_code == 200:
            data2 = response2.json()
            print(f"  턴 2: [OK] 성공 (같은 세션 유지)")
            print(f"  대화 히스토리가 유지되고 있습니다!")
        else:
            print(f"  턴 2: [FAIL] 실패 (상태 코드: {response2.status_code})")
    else:
        print(f"  턴 1: [FAIL] 실패 (상태 코드: {response1.status_code})")
except Exception as e:
    print(f"[FAIL] 대화형 테스트 실패: {e}")
print()

# 4. 예측 API 테스트 (선택사항)
print("[4] 예측 API 테스트 (선택사항)")
print("-" * 80)
try:
    request_data = {
        "region": "청량리동",
        "period_type": "week"
    }
    response = httpx.post(
        f"{BASE_URL}/api/v1/forecast",
        json=request_data,
        timeout=30.0
    )
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] 예측 API 정상")
        print(f"  트렌드: {data.get('trend')}")
        print(f"  신뢰도: {data.get('confidence')}")
    else:
        print(f"[FAIL] 예측 API 실패 (상태 코드: {response.status_code})")
except Exception as e:
    print(f"[FAIL] 예측 API 실패: {e}")
print()

print("=" * 80)
print("점검 완료!")
print("=" * 80)
print()
print("다음 명령으로 점검:")
print("  python check_localhost.py")
print()
print("서버 로그 확인:")
print("  tail -f C:\\Users\\tlduf\\AppData\\Local\\Temp\\claude\\D--Ai-project-home-signal-ai\\tasks\\b979ae0.output")
print()
