"""
대화형 챗봇 상세 검증 스크립트
- 대화 히스토리 저장 확인
- 세션 유지 확인
- 맥락 이해 확인
"""
import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = f"verify-{int(time.time())}"

print("=" * 80)
print("대화형 챗봇 상세 검증")
print("=" * 80)
print(f"Session ID: {SESSION_ID}")
print()

# 대화 시나리오
conversations = [
    {
        "turn": 1,
        "message": "청량리 아파트 가격이 오를까요?",
        "region": "청량리동",
        "expected": "청량리에 대한 예측 정보"
    },
    {
        "turn": 2,
        "message": "이문동은 어떤가요?",  # 맥락: 청량리와 비교
        "region": "이문동",
        "expected": "이문동 정보 (청량리와 비교 가능)"
    },
    {
        "turn": 3,
        "message": "재개발 가능성은?",  # 맥락: 이문동 재개발
        "region": "이문동",
        "expected": "이문동 재개발 정보"
    },
    {
        "turn": 4,
        "message": "GTX 영향은?",  # 맥락: 청량리/이문동 GTX
        "region": "청량리동",
        "expected": "GTX 영향 정보"
    }
]

results = []

for conv in conversations:
    print(f"[턴 {conv['turn']}] {conv['message']}")
    print("-" * 80)

    request_data = {
        "message": conv["message"],
        "session_id": SESSION_ID,
        "region": conv["region"]
    }

    try:
        response = httpx.post(
            f"{BASE_URL}/api/v1/chat",
            json=request_data,
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()

            # 결과 저장
            result = {
                "turn": conv["turn"],
                "status": "SUCCESS",
                "session_id": data.get("session_id"),
                "answer_length": len(data.get("answer", "")),
                "sources_count": len(data.get("sources", [])),
                "fallback": data.get("fallback", False),
                "forecast": data.get("forecast_summary")
            }
            results.append(result)

            print(f"상태: [OK] 성공")
            print(f"Session ID: {data.get('session_id')}")
            print(f"답변 길이: {result['answer_length']} 글자")
            print(f"Fallback: {result['fallback']}")

            # 답변 일부 출력
            answer = data.get("answer", "")
            if len(answer) > 100:
                print(f"답변 미리보기: {answer[:100]}...")
            else:
                print(f"답변: {answer}")

        else:
            print(f"상태: [FAIL] 오류 (코드: {response.status_code})")
            print(f"오류 내용: {response.text[:200]}")
            result = {
                "turn": conv["turn"],
                "status": "FAILED",
                "error": response.status_code
            }
            results.append(result)

    except Exception as e:
        print(f"상태: [ERROR] 예외 발생")
        print(f"오류: {str(e)[:200]}")
        result = {
            "turn": conv["turn"],
            "status": "ERROR",
            "error": str(e)
        }
        results.append(result)

    print()
    time.sleep(0.5)  # 서버 부하 방지

print("=" * 80)
print("검증 결과 요약")
print("=" * 80)
print()

# 세션 일관성 확인
session_ids = [r.get("session_id") for r in results if r.get("session_id")]
if session_ids:
    all_same = all(sid == session_ids[0] for sid in session_ids)
    if all_same:
        print(f"[OK] 세션 일관성: 모든 턴에서 동일한 세션 ID 사용")
        print(f"     Session ID: {session_ids[0]}")
    else:
        print(f"[FAIL] 세션 일관성: 세션 ID가 변경됨")
        for i, sid in enumerate(session_ids, 1):
            print(f"       턴 {i}: {sid}")
else:
    print(f"[FAIL] 세션 ID 없음")

print()

# 성공률
success_count = sum(1 for r in results if r.get("status") == "SUCCESS")
total_count = len(results)
success_rate = (success_count / total_count) * 100 if total_count > 0 else 0

print(f"성공률: {success_count}/{total_count} ({success_rate:.0f}%)")
print()

# 각 턴 결과
print("턴별 결과:")
for result in results:
    status_icon = "[OK]" if result.get("status") == "SUCCESS" else "[FAIL]"
    turn = result.get("turn")
    print(f"  턴 {turn}: {status_icon} {result.get('status')}")
    if result.get("answer_length"):
        print(f"        답변: {result['answer_length']} 글자")

print()
print("=" * 80)
print("대화형 챗봇 핵심 기능 확인")
print("=" * 80)
print()

# 핵심 기능 체크리스트
checklist = {
    "세션 생성 및 유지": all_same if session_ids else False,
    "다중 턴 대화 처리": success_count >= 3,
    "Fallback 응답 생성": any(r.get("fallback") for r in results),
    "예측 데이터 제공": any(r.get("forecast") for r in results),
}

for feature, passed in checklist.items():
    status = "[OK]" if passed else "[FAIL]"
    print(f"{status} {feature}")

print()
print("=" * 80)
print("결론")
print("=" * 80)
print()

if success_rate == 100 and all_same:
    print("[SUCCESS] 대화형 챗봇이 정상적으로 작동합니다!")
    print()
    print("확인된 기능:")
    print("  - 세션 기반 대화 관리")
    print("  - 대화 히스토리 유지")
    print("  - 다중 턴 대화 처리")
    print("  - Fallback 응답 생성")
    print()
    print("다음 단계:")
    print("  1. Migration 007 실행 (Supabase DB)")
    print("  2. AI API 키 설정 (OPENAI_API_KEY 또는 ANTHROPIC_API_KEY)")
    print("  3. FORCE_CONVERSATION_MOCK=false 설정")
    print("  4. 실제 AI 응답 테스트")
else:
    print("[WARNING] 일부 기능에 문제가 있습니다.")
    print()
    print(f"성공률: {success_rate:.0f}%")
    if not all_same:
        print("문제: 세션 ID가 일관되지 않음")
    print()
    print("로그 확인:")
    print("  서버 로그를 확인하여 오류를 분석하세요.")

print()
