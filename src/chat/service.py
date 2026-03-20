import json
import logging
import os
import time

from src.config import settings
from src.forecast.schemas import ForecastRequest
from src.forecast.service import ForecastService
from src.shared.ai_client import AIClient
from src.shared.cache import CacheClient
from src.shared.database import get_supabase_client
from src.shared.exceptions import AIAPIError
from src.shared.mcp_client import ElectionSignalAgent
from src.shared.vector_db import VectorDBInterface, get_vector_db

from .conversation_manager import (
    ConversationManager,
    MockConversationManager,
)
from .fallback import create_fallback_response
from .planner import (
    IntentClassifier,
    PlanExecutor,
    PlanGenerator,
    PlannerMetadata,
    QueryDecomposer,
)
from .prompts import SYSTEM_PROMPT_V1, build_context_message
from .schemas import (
    ChatRequest,
    ChatResponse,
    ForecastSummary,
    SourceReference,
)

logger = logging.getLogger(__name__)


class ChatService:
    """RAG 챗봇 비즈니스 로직 (대화형 챗봇)"""

    def __init__(
        self,
        ai_client: AIClient | None = None,
        cache: CacheClient | None = None,
        vector_db: VectorDBInterface | None = None,
        enable_planner: bool = True,
        conversation_manager: ConversationManager | None = None,
    ):
        self.ai_client = ai_client or AIClient()
        self.cache = cache
        self.vector_db = vector_db or get_vector_db()
        self.forecast_service = ForecastService(cache=cache)
        self.enable_planner = enable_planner

        # 대화 세션 관리자 초기화
        if conversation_manager:
            self.conversation_manager = conversation_manager
        else:
            # TEMPORARY: Force Mock mode for testing until migration 007 is executed
            # TODO: Remove this after executing migrations/007_add_conversation_tables.sql on Supabase
            force_mock = os.environ.get("FORCE_CONVERSATION_MOCK", "true").lower() == "true"

            if force_mock:
                logger.info("FORCED Mock mode: MockConversationManager 사용 (FORCE_CONVERSATION_MOCK=true)")
                self.conversation_manager = MockConversationManager()
            else:
                # Supabase 연결 상태에 따라 자동 선택
                try:
                    supabase_client = get_supabase_client(use_service_role=True)
                    # Mock client인지 확인
                    if hasattr(supabase_client, "__class__") and supabase_client.__class__.__name__ == "MockSupabaseClient":
                        logger.info("Mock mode: MockConversationManager 사용")
                        self.conversation_manager = MockConversationManager()
                    else:
                        logger.info("Production mode: ConversationManager 사용")
                        self.conversation_manager = ConversationManager(supabase_client)
                except Exception as e:
                    logger.warning(f"ConversationManager 초기화 실패, Mock 사용: {e}")
                    self.conversation_manager = MockConversationManager()

        # MCP ElectionSignalAgent 초기화 (선택사항)
        self.election_agent: ElectionSignalAgent | None = None
        try:
            # MCP 서버 URL이 설정되어 있으면 초기화
            # 실제 환경에서는 settings에서 가져와야 함
            # 현재는 MCP 서버가 없어도 동작하도록 None으로 유지
            if hasattr(settings, "mcp_exa_url") and hasattr(settings, "mcp_perplexity_url"):
                self.election_agent = ElectionSignalAgent(
                    exa_url=settings.mcp_exa_url,
                    perplexity_url=settings.mcp_perplexity_url,
                )
                logger.info("MCP ElectionSignalAgent 초기화 완료")
            else:
                logger.info("MCP 서버 URL 미설정 - ElectionSignalAgent 비활성화")
        except Exception as e:
            logger.warning(f"MCP ElectionSignalAgent 초기화 실패: {e}")

        # Query Planner 컴포넌트 초기화
        if self.enable_planner:
            self.classifier = IntentClassifier(self.ai_client)
            self.decomposer = QueryDecomposer(ai_client=self.ai_client)
            self.plan_generator = PlanGenerator()
            self.plan_executor = PlanExecutor(
                vector_db=self.vector_db,
                cache=self.cache,
            )

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """RAG 챗봇 응답 생성 (대화형)"""
        # ================================================================
        # 1. 대화 세션 생성/조회
        # ================================================================
        session = await self.conversation_manager.get_or_create_session(
            session_id=request.session_id,
            region=request.region,
            initial_query=request.message,
        )
        logger.info(
            f"세션: {session.session_id} (메시지: {session.message_count}개)"
        )

        # ================================================================
        # 2. 사용자 메시지 저장
        # ================================================================
        await self.conversation_manager.save_user_message(
            session_id=session.session_id,
            content=request.message,
        )

        # ================================================================
        # 3. 대화 히스토리 로드 (최근 10개 메시지)
        # ================================================================
        conversation_history = await self.conversation_manager.get_conversation_history(
            session_id=session.session_id,
            limit=10,
        )
        logger.info(
            f"대화 히스토리 로드: {len(conversation_history)}개 메시지"
        )

        # ================================================================
        # 4. 캐시 확인 (대화형 챗봇에서는 세션별 캐시)
        #    현재 메시지 + 히스토리 해시로 캐시 키 생성
        # ================================================================
        cache_key = None
        if self.cache:
            # 대화 컨텍스트를 고려한 캐시 키 생성
            # (현재 메시지 + 최근 3개 메시지 해시)
            recent_context = [msg.content for msg in conversation_history[-4:-1]]
            cache_key = CacheClient.generate_key(
                "chat_conversational",
                {
                    "message": request.message,
                    "region": request.region,
                    "context": "|".join(recent_context),
                },
            )
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"대화형 캐시 히트: {cache_key}")
                return ChatResponse(**cached)

        # ================================================================
        # 5. RAG 처리 (플래너 기반 또는 단순)
        # ================================================================
        if self.enable_planner:
            response = await self._chat_with_planner(
                request, cache_key, conversation_history
            )
        else:
            response = await self._chat_simple(
                request, cache_key, conversation_history
            )

        # ================================================================
        # 6. AI 응답 메시지 저장
        # ================================================================
        await self.conversation_manager.save_assistant_message(
            session_id=session.session_id,
            content=response.answer,
            forecast_data=(
                response.forecast_summary.model_dump()
                if response.forecast_summary
                else None
            ),
            news_sources=[src.model_dump() for src in response.sources],
            planner_metadata=(
                response.planner_metadata.model_dump()
                if response.planner_metadata
                else None
            ),
        )

        # 응답에 세션 ID 설정
        response.session_id = session.session_id

        return response

    async def _chat_with_planner(
        self,
        request: ChatRequest,
        cache_key: str | None,
        conversation_history: list | None = None,
    ) -> ChatResponse:
        """플래너를 사용한 RAG 처리 (대화 맥락 고려)"""
        planning_start = time.time()

        # 대화 히스토리가 있으면 로깅
        if conversation_history:
            logger.info(f"대화 맥락 사용: {len(conversation_history)}개 이전 메시지")

        # 1. 의도 분류
        classification = await self.classifier.classify(request.message)
        intents = [classification.primary_intent] + classification.secondary_intents

        # 2. 엔티티 추출 및 질문 분해
        entities = await self.decomposer.extractor.extract(request.message)
        sub_queries = await self.decomposer.decompose(
            request.message, intents, entities
        )

        # 3. 실행 계획 생성
        plan = self.plan_generator.generate(request.message, intents, sub_queries)

        planning_time_ms = int((time.time() - planning_start) * 1000)

        # 4. 단순 쿼리면 기존 로직 사용
        if plan.is_simple:
            logger.info(
                f"단순 쿼리 감지, 기존 로직 사용: {classification.primary_intent}"
            )
            response = await self._chat_simple(request, cache_key)

            # 플래너 메타데이터 추가
            response.planner_metadata = PlannerMetadata(
                intents_detected=intents,
                sub_queries_count=len(sub_queries),
                execution_strategy=plan.strategy,
                planning_time_ms=planning_time_ms,
                is_simple_query=True,
            )
            return response

        # 5. 복합 쿼리 - 플랜 실행
        logger.info(
            f"복합 쿼리 처리: intents={intents}, sub_queries={len(sub_queries)}, "
            f"strategy={plan.strategy}"
        )
        execution_result = await self.plan_executor.execute(plan)

        # 6. 실행 결과로 AI 응답 생성 (대화 히스토리 포함)
        try:
            response = await self._generate_ai_response_from_plan(
                request=request,
                execution_result=execution_result,
                conversation_history=conversation_history,
            )
        except AIAPIError as e:
            logger.warning(f"AI API 오류, Fallback 실행: {e}")
            # Fallback 응답 생성
            forecast_data = execution_result.aggregated_forecast
            if forecast_data:
                from src.forecast.schemas import ForecastResponse, ForecastPoint

                # Convert dict to ForecastResponse
                forecast_points = [
                    ForecastPoint(
                        date=fp["date"],
                        value=fp["value"],
                        lower_bound=fp.get("lower_bound", fp["value"] * 0.95),  # Default: -5%
                        upper_bound=fp.get("upper_bound", fp["value"] * 1.05),  # Default: +5%
                    )
                    for fp in forecast_data.get("forecast", [])
                ]
                fallback_forecast = ForecastResponse(
                    region=request.region,
                    period="week",
                    trend=forecast_data.get("trend", "보합"),
                    confidence=forecast_data.get("confidence", 0.0),
                    forecast=forecast_points,
                )
                response = create_fallback_response(
                    forecast=fallback_forecast,
                    session_id=request.session_id,
                )
            else:
                response = ChatResponse(
                    answer="일시적 장애로 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요.",
                    sources=[],
                    forecast_summary=None,
                    session_id=request.session_id,
                    fallback=True,
                )

        # 플래너 메타데이터 추가
        response.planner_metadata = PlannerMetadata(
            intents_detected=intents,
            sub_queries_count=len(sub_queries),
            execution_strategy=plan.strategy,
            planning_time_ms=planning_time_ms,
            is_simple_query=False,
        )

        # 캐시 저장 (Fallback 응답은 캐시하지 않음)
        if self.cache and cache_key and not response.fallback:
            await self.cache.set(
                cache_key,
                response.model_dump(mode="json"),
                ttl=settings.cache_ttl_chat,
            )

        return response

    async def _chat_simple(
        self,
        request: ChatRequest,
        cache_key: str | None,
        conversation_history: list | None = None,
    ) -> ChatResponse:
        """기존 단순 RAG 처리 로직 (대화 맥락 고려 + MCP 통합)"""
        # 1. 시계열 예측 조회
        forecast = await self._get_forecast(request.region)

        # 2. Vector DB 검색 (RAG) - 대화 맥락을 고려한 검색
        relevant_docs = await self._search_relevant_documents(
            request.message, conversation_history
        )

        # 3. MCP 선거 시그널 조회 (선택사항)
        election_signals = None
        if self.election_agent:
            try:
                election_signals = await self.election_agent.fetch_election_promises(
                    region=request.region
                )
                if election_signals:
                    logger.info(
                        f"MCP 선거 시그널 조회 완료: {len(election_signals)}개"
                    )
            except Exception as e:
                logger.warning(f"MCP 선거 시그널 조회 실패 (계속 진행): {e}")

        # 4. AI 응답 생성 (with Fallback, 대화 히스토리 + MCP 포함)
        try:
            response = await self._generate_ai_response(
                request=request,
                forecast=forecast,
                relevant_docs=relevant_docs,
                conversation_history=conversation_history,
                election_signals=election_signals,
            )
        except AIAPIError as e:
            logger.warning(f"AI API 오류, Fallback 실행: {e}")
            response = create_fallback_response(
                forecast=forecast,
                session_id=request.session_id,
            )

        # 캐시 저장 (Fallback 응답은 캐시하지 않음)
        if self.cache and cache_key and not response.fallback:
            await self.cache.set(
                cache_key,
                response.model_dump(mode="json"),
                ttl=settings.cache_ttl_chat,
            )

        return response

    async def _get_forecast(self, region: str):
        """시계열 예측 조회"""
        forecast_request = ForecastRequest(
            region=region,
            period="month",
            horizon=3,
            include_news_weight=True,
        )
        return await self.forecast_service.get_forecast(forecast_request)

    async def _search_relevant_documents(
        self, query: str, conversation_history: list | None = None
    ) -> list[dict]:
        """
        Vector DB에서 관련 문서 검색 (대화 맥락 고려)

        대화 히스토리가 있으면 최근 메시지들을 조합해서 검색 쿼리를 확장
        """
        # 대화 맥락을 고려한 검색 쿼리 생성
        search_query = query
        if conversation_history and len(conversation_history) > 1:
            # 최근 사용자 메시지 2개를 조합
            recent_user_messages = [
                msg.content
                for msg in conversation_history[-3:]
                if msg.role == "user"
            ]
            if recent_user_messages:
                # 현재 질문 + 이전 질문 컨텍스트
                search_query = " ".join(recent_user_messages[-2:] + [query])
                logger.info(
                    f"대화 맥락을 고려한 검색 쿼리: {search_query[:100]}..."
                )

        chunks = await self.vector_db.search(search_query, top_k=5)
        return [
            {
                "content": chunk.content,
                "source": chunk.source,
                "score": chunk.score,
            }
            for chunk in chunks
        ]

    async def _generate_ai_response(
        self,
        request: ChatRequest,
        forecast,
        relevant_docs: list[dict],
        conversation_history: list | None = None,
        election_signals: list | None = None,
    ) -> ChatResponse:
        """AI 응답 생성 (대화 히스토리 + MCP 포함)"""
        # 컨텍스트 메시지 생성
        forecast_dict = {
            "trend": forecast.trend,
            "confidence": forecast.confidence,
            "forecast": [
                {"date": str(p.date), "value": p.value} for p in forecast.forecast[:3]
            ],
        }

        # MCP 선거 시그널을 컨텍스트에 추가
        election_context = None
        if election_signals:
            election_context = json.dumps(election_signals, ensure_ascii=False, indent=2)

        context_message = build_context_message(
            user_query=request.message,
            forecast_json=json.dumps(forecast_dict, ensure_ascii=False, indent=2),
            news_chunks=relevant_docs,
            election_signals=election_context,
        )

        # 대화 히스토리를 AI API에 전달
        if conversation_history and len(conversation_history) > 1:
            # 이전 메시지들 (현재 사용자 메시지 제외)
            history_for_ai = self.conversation_manager.format_history_for_ai(
                conversation_history[:-1]  # 마지막 메시지(현재)는 제외
            )
            logger.info(f"AI에 대화 히스토리 전달: {len(history_for_ai)}개 메시지")

            # AI API 호출 (대화 히스토리 포함)
            answer = await self.ai_client.generate_with_history(
                system_prompt=SYSTEM_PROMPT_V1,
                conversation_history=history_for_ai,
                user_message=context_message,
            )
        else:
            # 대화 히스토리가 없으면 기존 방식
            answer = await self.ai_client.generate(
                system_prompt=SYSTEM_PROMPT_V1,
                user_message=context_message,
            )

        # 응답 구성
        sources = [
            SourceReference(
                title=doc.get("content", "")[:50] + "...",
                source=doc.get("source", ""),
                relevance_score=doc.get("score", 0.0),
            )
            for doc in relevant_docs
        ]

        forecast_summary = ForecastSummary(
            trend=forecast.trend,
            confidence=forecast.confidence,
            next_month_prediction=forecast.forecast[0].value
            if forecast.forecast
            else None,
        )

        return ChatResponse(
            answer=answer,
            sources=sources,
            forecast_summary=forecast_summary,
            session_id=request.session_id,
            fallback=False,
        )

    async def _generate_ai_response_from_plan(
        self,
        request: ChatRequest,
        execution_result,
        conversation_history: list | None = None,
    ) -> ChatResponse:
        """플랜 실행 결과로 AI 응답 생성 (대화 히스토리 포함)"""
        from .planner.executor import ExecutionResult

        execution_result: ExecutionResult = execution_result

        # 예측 데이터 준비
        forecast_data = execution_result.aggregated_forecast
        if forecast_data:
            # 다중 지역 비교인 경우
            if "regions" in forecast_data:
                forecast_json = json.dumps(
                    {
                        "comparison": True,
                        "regions": forecast_data["regions"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            else:
                forecast_json = json.dumps(
                    {
                        "trend": forecast_data.get("trend"),
                        "confidence": forecast_data.get("confidence"),
                        "forecast": forecast_data.get("forecast", []),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
        else:
            forecast_json = "{}"

        # 문서 데이터 준비
        relevant_docs = execution_result.aggregated_documents

        # 컨텍스트 메시지 생성
        context_message = build_context_message(
            user_query=request.message,
            forecast_json=forecast_json,
            news_chunks=relevant_docs,
        )

        # AI API 호출 (대화 히스토리 포함 여부에 따라)
        if conversation_history and len(conversation_history) > 1:
            # 이전 메시지들 (현재 사용자 메시지 제외)
            history_for_ai = self.conversation_manager.format_history_for_ai(
                conversation_history[:-1]
            )
            logger.info(f"플랜 실행 결과 - AI에 대화 히스토리 전달: {len(history_for_ai)}개")

            answer = await self.ai_client.generate_with_history(
                system_prompt=SYSTEM_PROMPT_V1,
                conversation_history=history_for_ai,
                user_message=context_message,
            )
        else:
            answer = await self.ai_client.generate(
                system_prompt=SYSTEM_PROMPT_V1,
                user_message=context_message,
            )

        # 응답 구성
        sources = [
            SourceReference(
                title=doc.get("content", "")[:50] + "...",
                source=doc.get("source", ""),
                relevance_score=doc.get("score", 0.0),
            )
            for doc in relevant_docs
        ]

        # ForecastSummary 구성
        if forecast_data:
            if "regions" in forecast_data and forecast_data["regions"]:
                primary = forecast_data["primary"]
                forecast_summary = ForecastSummary(
                    trend=primary.get("trend", "알 수 없음"),
                    confidence=primary.get("confidence", 0.0),
                    next_month_prediction=(
                        primary["forecast"][0]["value"]
                        if primary.get("forecast")
                        else None
                    ),
                )
            else:
                forecast_summary = ForecastSummary(
                    trend=forecast_data.get("trend", "알 수 없음"),
                    confidence=forecast_data.get("confidence", 0.0),
                    next_month_prediction=(
                        forecast_data["forecast"][0]["value"]
                        if forecast_data.get("forecast")
                        else None
                    ),
                )
        else:
            forecast_summary = None

        return ChatResponse(
            answer=answer,
            sources=sources,
            forecast_summary=forecast_summary,
            session_id=request.session_id,
            fallback=False,
        )
