"""
Supabase 데이터베이스 클라이언트

개발 모드에서 Supabase 라이브러리 로드 실패 시 Mock 클라이언트 사용
"""

import logging
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# Supabase 라이브러리 동적 임포트 시도
try:
    from supabase import (
        AsyncClient,
        Client,
        ClientOptions,
        create_async_client,
        create_client,
    )

    SUPABASE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Supabase 라이브러리 로드 실패: {e}")
    SUPABASE_AVAILABLE = False
    Client = Any  # type: ignore
    ClientOptions = Any  # type: ignore
    AsyncClient = Any  # type: ignore


class MockSupabaseTable:
    """Mock Supabase 테이블 - 개발/테스트용"""

    def __init__(self, table_name: str) -> None:
        self.table_name = table_name
        self._data: list[dict[str, Any]] = []

    def select(self, *args: Any, **kwargs: Any) -> "MockSupabaseTable":
        return self

    def insert(self, data: dict[str, Any]) -> "MockSupabaseTable":
        self._data.append(data)
        return self

    def update(self, data: dict[str, Any]) -> "MockSupabaseTable":
        return self

    def delete(self) -> "MockSupabaseTable":
        return self

    def eq(self, column: str, value: Any) -> "MockSupabaseTable":
        return self

    def neq(self, column: str, value: Any) -> "MockSupabaseTable":
        return self

    def gt(self, column: str, value: Any) -> "MockSupabaseTable":
        return self

    def gte(self, column: str, value: Any) -> "MockSupabaseTable":
        return self

    def lt(self, column: str, value: Any) -> "MockSupabaseTable":
        return self

    def lte(self, column: str, value: Any) -> "MockSupabaseTable":
        return self

    def ilike(self, column: str, pattern: str) -> "MockSupabaseTable":
        return self

    def order(self, column: str, desc: bool = False) -> "MockSupabaseTable":
        return self

    def limit(self, count: int) -> "MockSupabaseTable":
        return self

    def execute(self) -> Any:
        """Mock execute - 빈 결과 반환"""

        class MockResponse:
            data: list[Any] = []
            count: int = 0

        return MockResponse()


class MockSupabaseAuth:
    """Mock Supabase Auth - 개발/테스트용"""

    def get_user(self, token: str) -> Any:
        """Mock user 반환"""

        class MockUser:
            id = "mock-user-id"
            email = "mock@example.com"
            user_metadata: dict[str, Any] = {"role": "service_account"}

        class MockResponse:
            user = MockUser()

        return MockResponse()


class MockRPCCall:
    """Mock RPC 호출 결과 - 빈 결과 반환"""

    def __init__(self, fn_name: str, params: dict[str, Any]) -> None:
        self._fn_name = fn_name
        self._params = params

    def execute(self) -> Any:
        class MockResponse:
            data: list[Any] = []
            count: int = 0

        return MockResponse()


class MockSupabaseClient:
    """Mock Supabase 클라이언트 - 개발/테스트용"""

    def __init__(self) -> None:
        self.auth = MockSupabaseAuth()
        self._tables: dict[str, MockSupabaseTable] = {}
        logger.info("MockSupabaseClient 사용 중 (개발 모드)")

    def table(self, table_name: str) -> MockSupabaseTable:
        if table_name not in self._tables:
            self._tables[table_name] = MockSupabaseTable(table_name)
        return self._tables[table_name]

    def rpc(self, fn_name: str, params: dict[str, Any] | None = None) -> MockRPCCall:
        """Mock RPC 함수 호출"""
        logger.debug(f"MockRPC 호출: {fn_name}({params})")
        return MockRPCCall(fn_name, params or {})


@lru_cache
def get_supabase_client(use_service_role: bool = False) -> Client:
    """Supabase 클라이언트 싱글톤 반환

    Args:
        use_service_role: True면 service_role 키 사용 (INSERT/UPDATE용),
                         False면 anon 키 사용 (SELECT용)
    """
    from src.config import settings

    if not SUPABASE_AVAILABLE:
        logger.warning("Supabase 사용 불가 - MockSupabaseClient 사용")
        return MockSupabaseClient()  # type: ignore

    # placeholder URL 체크
    if "placeholder" in settings.supabase_url:
        logger.warning("Supabase placeholder URL 감지 - MockSupabaseClient 사용")
        return MockSupabaseClient()  # type: ignore

    # ClientOptions 설정 (타임아웃, 연결 풀 등)
    if use_service_role:
        if not settings.supabase_service_role_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY가 설정되지 않았습니다. "
                "Ingest API 사용을 위해 .env에 service_role 키를 추가하세요."
            )

        # service_role 클라이언트는 토큰 갱신이 필요 없으므로 설정을 통해 타이머 이슈 방지 가능 여부 체크
        # 최신 버전에서는 ClientOptions에 직접 전달 가능하거나 headers를 통해 제어
        options = ClientOptions(
            postgrest_client_timeout=settings.supabase_timeout,
            storage_client_timeout=settings.supabase_timeout,
            schema="public",
        )

        logger.debug("service_role 키로 Supabase 클라이언트 생성")
        client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
            options=options,
        )

        # 타이머 이슈 강제 방지 (버그 회피용)
        try:
            if hasattr(client.auth, "_refresh_token_timer") and client.auth._refresh_token_timer:
                client.auth._refresh_token_timer.cancel()
        except:
            pass

        return client

    options = ClientOptions(
        postgrest_client_timeout=settings.supabase_timeout,
        storage_client_timeout=settings.supabase_timeout,
        schema="public",
    )
    return create_client(settings.supabase_url, settings.supabase_key, options=options)


@lru_cache
def get_async_supabase_client(use_service_role: bool = False) -> AsyncClient:
    """Supabase 비동기 클라이언트 싱글톤 반환"""
    from src.config import settings

    if not SUPABASE_AVAILABLE:
        return MockSupabaseClient()  # type: ignore

    if "placeholder" in settings.supabase_url:
        return MockSupabaseClient()  # type: ignore

    options = ClientOptions(
        postgrest_client_timeout=settings.supabase_timeout,
        storage_client_timeout=settings.supabase_timeout,
        schema="public",
    )

    if use_service_role:
        if not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY missing")
        return create_async_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
            options=options,
        )

    return create_async_client(settings.supabase_url, settings.supabase_key, options=options)
