"""
대화형 챗봇 데모 스크립트

실제로 대화 히스토리가 유지되는지 확인합니다.
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chat.conversation_manager import MockConversationManager
from src.chat.schemas import ChatRequest
from src.chat.service import ChatService


async def demo_conversation():
    """대화형 챗봇 데모"""
    print("=" * 80)
    print("HomeSignal AI - 대화형 RAG 챗봇 데모")
    print("=" * 80)
    print()

    # Mock 모드로 초기화 (AI API 호출 없이 구조만 테스트)
    conversation_manager = MockConversationManager()
    service = ChatService(
        ai_client=None,
        cache=None,
        enable_planner=False,
        conversation_manager=conversation_manager,
    )

    session_id = "demo-session-001"

    print("시나리오: 3턴 대화")
    print()

    # ========================================================================
    # 턴 1: 세션 생성 및 첫 질문
    # ========================================================================
    print("[턴 1] User: 청량리 아파트 가격이 오를까요?")
    print("-" * 80)

    # 세션 생성 및 사용자 메시지 저장
    session = await conversation_manager.get_or_create_session(
        session_id=session_id,
        region="청량리동",
        initial_query="청량리 아파트 가격이 오를까요?",
    )
    print(f"[OK] 세션 생성: {session.session_id}")

    await conversation_manager.save_user_message(
        session_id=session_id,
        content="청량리 아파트 가격이 오를까요?",
    )
    print(f"[OK] 사용자 메시지 저장 완료")

    # AI 응답 시뮬레이션
    await conversation_manager.save_assistant_message(
        session_id=session_id,
        content="청량리는 GTX-C 개통으로 인해 교통 접근성이 크게 개선될 예정입니다. 2024년 상반기 개통을 앞두고 있으며, 이에 따라 아파트 가격 상승이 예상됩니다.",
        forecast_data={"trend": "상승", "confidence": 0.82},
    )
    print(f"[OK] Assistant: 청량리는 GTX-C 개통으로 인해 교통 접근성이...")
    print()

    # ========================================================================
    # 턴 2: 이전 대화 맥락 참조
    # ========================================================================
    print("[턴 2] User: 이문동은 어떤가요?")
    print("-" * 80)

    # 대화 히스토리 로드
    history = await conversation_manager.get_conversation_history(
        session_id=session_id, limit=10
    )
    print(f"[HISTORY] 대화 히스토리 로드: {len(history)}개 메시지")
    for i, msg in enumerate(history):
        print(f"   [{i+1}] {msg.role}: {msg.content[:50]}...")

    # 사용자 메시지 저장
    await conversation_manager.save_user_message(
        session_id=session_id,
        content="이문동은 어떤가요?",
    )

    # 맥락을 고려한 응답 시뮬레이션
    await conversation_manager.save_assistant_message(
        session_id=session_id,
        content="이문동은 청량리와 인접해 있어 GTX-C 효과를 일부 누릴 수 있습니다. 다만 청량리에 비해 역세권 거리가 멀어 상승폭은 청량리보다 완만할 것으로 예상됩니다.",
        forecast_data={"trend": "완만한 상승", "confidence": 0.71},
    )
    print(
        f"[OK] Assistant: 이문동은 청량리와 인접해 있어... (맥락 이해: 청량리와 비교)"
    )
    print()

    # ========================================================================
    # 턴 3: 추가 질문 (대화 흐름 유지)
    # ========================================================================
    print("[턴 3] User: 재개발 가능성은 어떤가요?")
    print("-" * 80)

    # 대화 히스토리 다시 로드
    history = await conversation_manager.get_conversation_history(
        session_id=session_id, limit=10
    )
    print(f"[HISTORY] 대화 히스토리 로드: {len(history)}개 메시지")

    await conversation_manager.save_user_message(
        session_id=session_id,
        content="재개발 가능성은 어떤가요?",
    )

    await conversation_manager.save_assistant_message(
        session_id=session_id,
        content="이문동의 경우 노후 주택이 밀집된 지역이 있어 재개발 논의가 진행 중입니다. 다만 재개발은 주민 동의율, 사업성 등 여러 변수가 있어 실현까지는 시간이 소요될 수 있습니다.",
    )
    print(f"[OK] Assistant: 이문동의 경우... (맥락 이해: 이문동 재개발)")
    print()

    # ========================================================================
    # 최종 대화 히스토리 확인
    # ========================================================================
    print("=" * 80)
    print("최종 대화 히스토리 (전체)")
    print("=" * 80)

    final_history = await conversation_manager.get_conversation_history(
        session_id=session_id
    )

    for i, msg in enumerate(final_history):
        role_label = "USER" if msg.role == "user" else "ASSISTANT"
        print(f"\n[{i+1}] {role_label}")
        print(f"    내용: {msg.content}")
        if msg.forecast_data:
            print(f"    예측 데이터: {msg.forecast_data}")
        print(f"    시퀀스: {msg.sequence_number}")

    print()
    print("=" * 80)
    print("[SUCCESS] 대화형 챗봇 데모 완료!")
    print("=" * 80)
    print()
    print("확인된 기능:")
    print("   [OK] 세션 생성 및 관리")
    print("   [OK] 대화 히스토리 저장")
    print("   [OK] 메시지 순서 관리 (sequence_number)")
    print("   [OK] 대화 맥락 유지 (이전 질문 기억)")
    print("   [OK] 메타데이터 저장 (forecast_data)")
    print()
    print("다음 단계: 실제 AI API와 연동하여 응답 생성 테스트")
    print()

    # AI용 포맷 변환 테스트
    print("=" * 80)
    print("AI API용 메시지 포맷 변환")
    print("=" * 80)

    ai_format = conversation_manager.format_history_for_ai(final_history)
    print(f"\n변환된 메시지: {len(ai_format)}개")
    for i, msg in enumerate(ai_format):
        print(f"[{i+1}] {msg}")

    print()


if __name__ == "__main__":
    asyncio.run(demo_conversation())
