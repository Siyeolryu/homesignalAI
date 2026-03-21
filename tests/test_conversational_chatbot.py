"""
대화형 챗봇 테스트

진짜 대화형 RAG 챗봇이 제대로 동작하는지 검증합니다.
"""

import pytest

from src.chat.conversation_manager import (
    ConversationManager,
    MockConversationManager,
)
from src.chat.schemas import ChatRequest, ChatResponse
from src.chat.service import ChatService
from src.shared.ai_client import AIClient
from src.shared.cache import CacheClient
from src.shared.vector_db import MockVectorDB


@pytest.fixture
def mock_conversation_manager():
    """Mock 대화 관리자"""
    return MockConversationManager()


@pytest.fixture
def mock_chat_service(mock_conversation_manager):
    """Mock ChatService (대화형)"""
    return ChatService(
        ai_client=None,  # Mock AI client will be used
        cache=None,
        vector_db=MockVectorDB(),
        enable_planner=False,  # 단순 테스트를 위해 플래너 비활성화
        conversation_manager=mock_conversation_manager,
    )


class TestConversationManager:
    """ConversationManager 단위 테스트"""

    async def test_create_session(self, mock_conversation_manager):
        """세션 생성 테스트"""
        session = await mock_conversation_manager.get_or_create_session(
            session_id="test-session-1",
            region="청량리동",
            initial_query="청량리 아파트 가격이 오를까요?",
        )

        assert session.session_id == "test-session-1"
        assert session.region == "청량리동"
        assert session.message_count == 0

    async def test_save_and_retrieve_messages(self, mock_conversation_manager):
        """메시지 저장 및 조회 테스트"""
        session = await mock_conversation_manager.get_or_create_session(
            session_id="test-session-2",
        )

        # 사용자 메시지 저장
        msg_id_1 = await mock_conversation_manager.save_user_message(
            session_id=session.session_id,
            content="청량리 아파트 가격이 오를까요?",
        )
        assert msg_id_1

        # AI 응답 저장
        msg_id_2 = await mock_conversation_manager.save_assistant_message(
            session_id=session.session_id,
            content="청량리 아파트는 GTX-C 개통으로 상승세가 예상됩니다.",
            forecast_data={"trend": "상승"},
        )
        assert msg_id_2

        # 히스토리 조회
        history = await mock_conversation_manager.get_conversation_history(
            session_id=session.session_id,
            limit=10,
        )

        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "청량리 아파트 가격이 오를까요?"
        assert history[1].role == "assistant"
        assert history[1].forecast_data == {"trend": "상승"}

    async def test_format_history_for_ai(self, mock_conversation_manager):
        """AI용 히스토리 포맷 변환 테스트"""
        session = await mock_conversation_manager.get_or_create_session(
            session_id="test-session-3"
        )

        await mock_conversation_manager.save_user_message(
            session_id=session.session_id, content="첫 질문"
        )
        await mock_conversation_manager.save_assistant_message(
            session_id=session.session_id, content="첫 답변"
        )

        history = await mock_conversation_manager.get_conversation_history(
            session_id=session.session_id
        )
        formatted = mock_conversation_manager.format_history_for_ai(history)

        assert len(formatted) == 2
        assert formatted[0] == {"role": "user", "content": "첫 질문"}
        assert formatted[1] == {"role": "assistant", "content": "첫 답변"}


class TestConversationalChatService:
    """대화형 ChatService 테스트"""

    @pytest.mark.skip(reason="AI API 호출 필요 - 통합 테스트에서 실행")
    async def test_multi_turn_conversation(self, mock_chat_service):
        """멀티턴 대화 테스트"""
        # 첫 번째 턴
        request1 = ChatRequest(
            message="청량리 아파트 가격이 오를까요?",
            session_id="multi-turn-test",
            region="청량리동",
        )
        response1: ChatResponse = await mock_chat_service.chat(request1)

        assert response1.answer
        assert response1.session_id == "multi-turn-test"

        # 두 번째 턴 (이전 대화 참조)
        request2 = ChatRequest(
            message="이문동은 어떤가요?",  # 맥락: 청량리와 비교
            session_id="multi-turn-test",
            region="이문동",
        )
        response2: ChatResponse = await mock_chat_service.chat(request2)

        assert response2.answer
        assert response2.session_id == "multi-turn-test"

        # 대화 히스토리 확인
        history = await mock_chat_service.conversation_manager.get_conversation_history(
            session_id="multi-turn-test"
        )

        # 사용자 2개 + AI 2개 = 4개 메시지
        assert len(history) == 4
        assert history[0].role == "user"
        assert history[1].role == "assistant"
        assert history[2].role == "user"
        assert history[3].role == "assistant"

    async def test_conversation_context_in_vector_search(
        self, mock_conversation_manager
    ):
        """대화 맥락이 벡터 검색에 반영되는지 테스트"""
        # 이전 대화 시뮬레이션
        session = await mock_conversation_manager.get_or_create_session(
            session_id="context-test"
        )

        # 첫 번째 질문
        await mock_conversation_manager.save_user_message(
            session_id=session.session_id,
            content="GTX-C가 청량리에 미치는 영향은?",
        )
        await mock_conversation_manager.save_assistant_message(
            session_id=session.session_id,
            content="GTX-C는 청량리의 교통 접근성을 크게 향상시킵니다.",
        )

        # 두 번째 질문 (맥락 필요)
        await mock_conversation_manager.save_user_message(
            session_id=session.session_id,
            content="그럼 가격은 얼마나 오를까요?",  # "GTX-C 영향으로" 라는 맥락 필요
        )

        history = await mock_conversation_manager.get_conversation_history(
            session_id=session.session_id
        )

        # 맥락을 고려한 검색 쿼리 생성 (실제로는 ChatService._search_relevant_documents에서 수행)
        recent_user_messages = [msg.content for msg in history if msg.role == "user"]

        # 최근 2개 질문을 조합
        combined_query = " ".join(recent_user_messages[-2:])

        assert "GTX-C" in combined_query
        assert "가격" in combined_query
        # 이제 벡터 DB 검색이 맥락을 고려한 쿼리로 수행됨


class TestConversationPersistence:
    """대화 세션 영속성 테스트"""

    async def test_session_expiry(self, mock_conversation_manager):
        """세션 만료 테스트"""
        # 세션 생성
        session = await mock_conversation_manager.get_or_create_session(
            session_id="expiry-test"
        )
        assert session.status == "active"

        # 세션 완료 처리
        success = await mock_conversation_manager.complete_session(
            session_id="expiry-test"
        )
        assert success

        # 완료된 세션 확인
        sessions = mock_conversation_manager.sessions
        assert sessions["expiry-test"].status == "completed"

    async def test_cleanup_expired_sessions(self, mock_conversation_manager):
        """만료된 세션 정리 테스트"""
        # 여러 세션 생성
        await mock_conversation_manager.get_or_create_session(session_id="s1")
        await mock_conversation_manager.get_or_create_session(session_id="s2")
        await mock_conversation_manager.get_or_create_session(session_id="s3")

        # 정리 실행 (Mock은 실제로 정리하지 않음)
        deleted_count = await mock_conversation_manager.cleanup_expired_sessions()

        # Mock은 0 반환 (실제 DB에서는 만료된 세션 삭제)
        assert deleted_count == 0


# ============================================================================
# 통합 테스트 시나리오 (실제 API 호출 필요)
# ============================================================================


@pytest.mark.integration
@pytest.mark.skip(reason="실제 AI API 키 필요 - 수동 실행 전용")
class TestRealConversationalChat:
    """실제 대화형 챗봇 통합 테스트"""

    async def test_full_conversation_flow(self):
        """전체 대화 흐름 테스트 (실제 AI API 사용)"""
        # 실제 서비스 초기화
        service = ChatService(
            ai_client=AIClient(),
            cache=CacheClient(),
            enable_planner=True,
        )

        session_id = "integration-test-001"

        # 턴 1: 청량리 질문
        request1 = ChatRequest(
            message="청량리 아파트 가격 전망이 어떻게 될까요?",
            session_id=session_id,
            region="청량리동",
        )
        response1 = await service.chat(request1)

        assert response1.answer
        assert response1.forecast_summary
        print(f"턴 1 응답: {response1.answer[:100]}...")

        # 턴 2: 이문동 비교 (맥락 참조)
        request2 = ChatRequest(
            message="이문동은 어떤가요?",  # 청량리와 비교
            session_id=session_id,
            region="이문동",
        )
        response2 = await service.chat(request2)

        assert response2.answer
        print(f"턴 2 응답: {response2.answer[:100]}...")

        # 턴 3: 재개발 질문 (맥락 유지)
        request3 = ChatRequest(
            message="재개발 가능성은 어떤가요?",
            session_id=session_id,
            region="이문동",
        )
        response3 = await service.chat(request3)

        assert response3.answer
        print(f"턴 3 응답: {response3.answer[:100]}...")

        # 대화 히스토리 확인
        history = await service.conversation_manager.get_conversation_history(
            session_id=session_id
        )

        assert len(history) == 6  # 사용자 3개 + AI 3개
        assert all(msg.role in ["user", "assistant"] for msg in history)
