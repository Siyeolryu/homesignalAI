"""
대화 세션 관리 서비스

진짜 대화형 RAG 챗봇을 위한 세션 및 메시지 히스토리 관리
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# Conversation Domain Models
# ============================================================================


class ConversationMessage(BaseModel):
    """대화 메시지"""

    id: str | None = None
    role: str = Field(description="user | assistant | system")
    content: str = Field(description="메시지 내용")
    sequence_number: int = Field(description="세션 내 메시지 순서")

    # 메타데이터 (assistant 메시지만 해당)
    forecast_data: dict[str, Any] | None = None
    news_sources: list[dict[str, Any]] | None = None
    election_signals: dict[str, Any] | None = None
    planner_metadata: dict[str, Any] | None = None

    created_at: datetime | None = None


class ConversationSession(BaseModel):
    """대화 세션"""

    id: str
    session_id: str
    user_id: str | None = None
    region: str = "동대문구"
    status: str = "active"
    message_count: int = 0
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime


# ============================================================================
# ConversationManager (대화 세션 관리자)
# ============================================================================


class ConversationManager:
    """
    대화 세션 및 메시지 히스토리 관리

    기능:
    - 세션 생성/조회
    - 메시지 저장 (user, assistant)
    - 대화 히스토리 로드
    - 만료된 세션 정리
    """

    def __init__(self, supabase_client):
        """
        Args:
            supabase_client: Supabase client (service_role key 사용 권장)
        """
        self.client = supabase_client

    async def get_or_create_session(
        self,
        session_id: str | None = None,
        user_id: str | None = None,
        region: str = "동대문구",
        initial_query: str | None = None,
    ) -> ConversationSession:
        """
        세션 생성 또는 기존 세션 조회

        Args:
            session_id: 클라이언트 제공 세션 ID (없으면 자동 생성)
            user_id: 사용자 식별자 (선택사항)
            region: 주요 관심 지역
            initial_query: 대화 시작 질문

        Returns:
            ConversationSession
        """
        # 세션 ID가 없으면 새로 생성
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"새 세션 ID 생성: {session_id}")

        try:
            # RPC 호출: get_or_create_conversation_session
            result = await self.client.rpc(
                "get_or_create_conversation_session",
                {
                    "p_session_id": session_id,
                    "p_user_id": user_id,
                    "p_region": region,
                    "p_initial_query": initial_query,
                },
            ).execute()

            if not result.data or len(result.data) == 0:
                raise ValueError(f"세션 생성 실패: {session_id}")

            session_data = result.data[0]
            logger.info(
                f"세션 조회/생성 완료: {session_id} (메시지 수: {session_data['message_count']})"
            )

            return ConversationSession(**session_data)

        except Exception as e:
            logger.error(f"세션 조회/생성 실패: {session_id} - {e}")
            raise

    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[ConversationMessage]:
        """
        대화 히스토리 조회 (최근 N개 메시지)

        Args:
            session_id: 세션 ID
            limit: 최대 메시지 수 (기본값: 20)

        Returns:
            list[ConversationMessage]: 시간순 정렬된 메시지 리스트
        """
        try:
            result = await self.client.rpc(
                "get_conversation_history",
                {
                    "p_session_id": session_id,
                    "p_limit": limit,
                },
            ).execute()

            messages = [ConversationMessage(**msg) for msg in result.data]
            logger.info(f"대화 히스토리 조회: {session_id} - {len(messages)}개 메시지")

            return messages

        except Exception as e:
            logger.warning(f"대화 히스토리 조회 실패 (빈 히스토리 반환): {session_id} - {e}")
            return []

    async def save_user_message(
        self,
        session_id: str,
        content: str,
    ) -> str:
        """
        사용자 메시지 저장

        Args:
            session_id: 세션 ID
            content: 메시지 내용

        Returns:
            str: 저장된 메시지 ID
        """
        return await self._save_message(
            session_id=session_id,
            role="user",
            content=content,
        )

    async def save_assistant_message(
        self,
        session_id: str,
        content: str,
        forecast_data: dict[str, Any] | None = None,
        news_sources: list[dict[str, Any]] | None = None,
        election_signals: dict[str, Any] | None = None,
        planner_metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        AI 어시스턴트 메시지 저장 (RAG 컨텍스트 포함)

        Args:
            session_id: 세션 ID
            content: AI 응답 내용
            forecast_data: 예측 데이터 스냅샷
            news_sources: 참조한 뉴스 문서 목록
            election_signals: 선거 공약 데이터
            planner_metadata: Query Planner 디버그 정보

        Returns:
            str: 저장된 메시지 ID
        """
        return await self._save_message(
            session_id=session_id,
            role="assistant",
            content=content,
            forecast_data=forecast_data,
            news_sources=news_sources,
            election_signals=election_signals,
            planner_metadata=planner_metadata,
        )

    async def _save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        forecast_data: dict[str, Any] | None = None,
        news_sources: list[dict[str, Any]] | None = None,
        election_signals: dict[str, Any] | None = None,
        planner_metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        메시지 저장 (내부 헬퍼)

        Returns:
            str: 저장된 메시지 ID
        """
        try:
            result = await self.client.rpc(
                "save_conversation_message",
                {
                    "p_session_id": session_id,
                    "p_role": role,
                    "p_content": content,
                    "p_forecast_data": forecast_data,
                    "p_news_sources": news_sources,
                    "p_election_signals": election_signals,
                    "p_planner_metadata": planner_metadata,
                },
            ).execute()

            message_id = result.data
            logger.info(f"메시지 저장 완료: {session_id} - {role} - {message_id}")

            return str(message_id)

        except Exception as e:
            logger.error(f"메시지 저장 실패: {session_id} - {role} - {e}")
            raise

    async def complete_session(self, session_id: str) -> bool:
        """
        세션 완료 처리

        Args:
            session_id: 세션 ID

        Returns:
            bool: 성공 여부
        """
        try:
            result = await self.client.rpc(
                "complete_conversation_session",
                {"p_session_id": session_id},
            ).execute()

            success = result.data
            logger.info(f"세션 완료 처리: {session_id} - {success}")

            return bool(success)

        except Exception as e:
            logger.error(f"세션 완료 처리 실패: {session_id} - {e}")
            return False

    async def cleanup_expired_sessions(self) -> int:
        """
        만료된 세션 정리

        Returns:
            int: 삭제된 세션 수
        """
        try:
            result = await self.client.rpc("cleanup_expired_sessions").execute()

            deleted_count = result.data
            logger.info(f"만료된 세션 정리 완료: {deleted_count}개 삭제")

            return int(deleted_count)

        except Exception as e:
            logger.error(f"세션 정리 실패: {e}")
            return 0

    def format_history_for_ai(
        self, messages: list[ConversationMessage]
    ) -> list[dict[str, str]]:
        """
        AI API에 전달할 메시지 히스토리 포맷 변환

        Args:
            messages: 대화 메시지 리스트

        Returns:
            list[dict]: OpenAI/Anthropic 호환 메시지 포맷
            [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."},
                ...
            ]
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]


# ============================================================================
# Mock ConversationManager (개발/테스트용)
# ============================================================================


class MockConversationManager:
    """
    Mock 대화 세션 관리자 (외부 DB 없이 개발)

    In-memory 저장소 사용
    """

    def __init__(self):
        self.sessions: dict[str, ConversationSession] = {}
        self.messages: dict[str, list[ConversationMessage]] = {}

    async def get_or_create_session(
        self,
        session_id: str | None = None,
        user_id: str | None = None,
        region: str = "동대문구",
        initial_query: str | None = None,
    ) -> ConversationSession:
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.sessions:
            now = datetime.now()
            self.sessions[session_id] = ConversationSession(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                region=region,
                status="active",
                message_count=0,
                created_at=now,
                updated_at=now,
                last_message_at=now,
            )
            self.messages[session_id] = []
            logger.info(f"[Mock] 새 세션 생성: {session_id}")

        return self.sessions[session_id]

    async def get_conversation_history(
        self, session_id: str, limit: int = 20
    ) -> list[ConversationMessage]:
        messages = self.messages.get(session_id, [])
        logger.info(f"[Mock] 대화 히스토리 조회: {session_id} - {len(messages)}개")
        return messages[-limit:]

    async def save_user_message(self, session_id: str, content: str) -> str:
        return await self._save_message(session_id, "user", content)

    async def save_assistant_message(
        self,
        session_id: str,
        content: str,
        forecast_data: dict[str, Any] | None = None,
        news_sources: list[dict[str, Any]] | None = None,
        election_signals: dict[str, Any] | None = None,
        planner_metadata: dict[str, Any] | None = None,
    ) -> str:
        return await self._save_message(
            session_id,
            "assistant",
            content,
            forecast_data,
            news_sources,
            election_signals,
            planner_metadata,
        )

    async def _save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        forecast_data: dict[str, Any] | None = None,
        news_sources: list[dict[str, Any]] | None = None,
        election_signals: dict[str, Any] | None = None,
        planner_metadata: dict[str, Any] | None = None,
    ) -> str:
        if session_id not in self.messages:
            self.messages[session_id] = []

        message_id = str(uuid.uuid4())
        sequence_number = len(self.messages[session_id])

        message = ConversationMessage(
            id=message_id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            forecast_data=forecast_data,
            news_sources=news_sources,
            election_signals=election_signals,
            planner_metadata=planner_metadata,
            created_at=datetime.now(),
        )

        self.messages[session_id].append(message)

        # 세션 메시지 카운트 업데이트
        if session_id in self.sessions:
            self.sessions[session_id].message_count += 1
            self.sessions[session_id].last_message_at = datetime.now()

        logger.info(f"[Mock] 메시지 저장: {session_id} - {role} - {message_id}")
        return message_id

    async def complete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            self.sessions[session_id].status = "completed"
            logger.info(f"[Mock] 세션 완료: {session_id}")
            return True
        return False

    async def cleanup_expired_sessions(self) -> int:
        logger.info("[Mock] 만료 세션 정리 (mock - 아무것도 안 함)")
        return 0

    def format_history_for_ai(
        self, messages: list[ConversationMessage]
    ) -> list[dict[str, str]]:
        return [{"role": msg.role, "content": msg.content} for msg in messages]
