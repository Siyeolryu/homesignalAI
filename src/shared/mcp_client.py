import logging
from typing import Any

import httpx

from src.shared.exceptions import AIAPIError

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP (Model Context Protocol) 클라이언트
    HTTP SSE 기반 MCP 서버와 통신합니다.
    """

    def __init__(self, name: str, url: str, timeout: float = 30.0) -> None:
        self.name = name
        self.url = url.rstrip("/")
        self.timeout = httpx.Timeout(timeout)
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """
        MCP 서버의 도구를 호출합니다.
        표준 MCP SSE flow를 간소화하여 시도하거나,
        서버가 지원하는 경우 직접 POST 방식을 시도합니다.
        """
        # Note: 실제 운영 환경에서는 SSE 연결 후 endpoint를 받아야 하지만,
        # run.tools 환경은 종종 /call 또는 직접 호출을 허용하기도 합니다.
        # 여기서는 시현을 위해 일반적인 JSON-RPC 구조로 호출을 시도합니다.

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            # First, check tools list to see if server is alive
            # logger.info(f"Calling MCP tool: {self.name}/{tool_name}")

            # SSE 기반 서버의 경우 /messages 등의 엔드포인트가 있을 수 있으나,
            # 여기서는 기본 URL에 POST를 시도해보거나 에러 발생 시 로깅합니다.
            response = await self.client.post(f"{self.url}/call", json=payload)

            if response.status_code != 200:
                # SSE 엔드포인트만 있는 경우를 대비해 헬스체크 수준의 로깅
                raise AIAPIError(
                    f"MCP server {self.name} returned {response.status_code}"
                )

            result = response.json()
            if "error" in result:
                raise AIAPIError(f"MCP tool error: {result['error']}")

            return result.get("result", {}).get("content", [])

        except Exception as e:
            logger.error(f"MCP {self.name} 호출 실패: {e}")
            # 대체 수단: 만약 직접 호출이 불가능하면 에러를 던지거나 가상 데이터를 반환
            raise

    async def close(self) -> None:
        await self.client.aclose()


class ElectionSignalAgent:
    """선거 시그널 수집 에이전트"""

    def __init__(self, exa_url: str, perplexity_url: str) -> None:
        self.exa = MCPClient("exa", exa_url)
        self.perplexity = MCPClient("perplexity", perplexity_url)

    async def fetch_election_promises(
        self, region: str = "동대문구"
    ) -> list[dict[str, Any]]:
        """특정 지역의 선거 공약을 수집합니다."""
        query = f"2026년 지방선거 {region} 부동산 재개발 교통 공약 요약"

        try:
            # Perplexity를 통해 최신 공약 요약 요청
            # 툴 이름은 서버마다 다를 수 있으므로 일반적인 'search' 또는 'query' 가정
            results = await self.perplexity.call_tool("search", {"query": query})
            return results
        except Exception as e:
            # 서버가 준비되지 않았을 경우를 위한 폴백 (실제 구현 시 중요)
            logger.warning(f"선거 공약 수집 실패 ({region}): {e}")
            return []

    async def close(self) -> None:
        await self.exa.close()
        await self.perplexity.close()
