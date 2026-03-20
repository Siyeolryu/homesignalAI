import asyncio
import logging
from datetime import datetime

from src.ingest.schemas import NewsSignalBatchRequest, NewsSignalItem
from src.ingest.service import IngestService
from src.shared.mcp_client import ElectionSignalAgent

logger = logging.getLogger(__name__)


async def collect_election_signals():
    """
    지방선거 공약 시그널 수집 및 적재
    """
    # MCP URLs (이후 settings에 추가 필요)
    # 현재는 요청받은 URL들을 직접 사용
    EXA_URL = "https://exa.run.tools"
    PERPLEXITY_URL = "https://perplexity-search--arjunkmrm.run.tools"

    agent = ElectionSignalAgent(exa_url=EXA_URL, perplexity_url=PERPLEXITY_URL)
    ingest_service = IngestService()

    logger.info("선거 공약 시그널 수집 시작...")

    try:
        # 1. 공약 데이터 수집 (Perplexity/Exa 활용)
        regions = ["동대문구", "용두동", "청량리동", "전농동", "이문동"]
        all_signals = []

        for region in regions:
            logger.info(f"{region} 관련 공약 검색 중...")
            promises = await agent.fetch_election_promises(region)

            # 수집된 데이터를 NewsSignalItem 형식으로 변환
            # 결과가 리스트 형태라고 가정 (MCP content 구조)
            for p in promises:
                text_content = p.get("text", "") if isinstance(p, dict) else str(p)
                if not text_content:
                    continue

                signal = NewsSignalItem(
                    title=f"[선거공약] {region} 부동산 관련 이슈/공약",
                    content=text_content,
                    url=None,  # MCP에서 출처 URL을 주면 좋겠지만 일단 누락
                    keywords=["선거", "지방선거", "공약", region, "재개발"],
                    published_at=datetime.now(),
                )
                all_signals.append(signal)

            # API 할당량 고려하여 약간의 대기
            await asyncio.sleep(1)

        if not all_signals:
            logger.warning("수집된 선거 시그널이 없습니다.")
            return

        # 2. 데이터 적재
        request = NewsSignalBatchRequest(
            source="mcp_election_agent", items=all_signals, generate_embeddings=True
        )

        result = await ingest_service.ingest_news(request)
        logger.info(f"선거 시그널 적재 완료: {result.inserted_count}건 성공")

    except Exception as e:
        logger.error(f"선거 시그널 수집 중 오류 발생: {e}")
    finally:
        await agent.close()


if __name__ == "__main__":
    # 로컬 테스트용
    logging.basicConfig(level=logging.INFO)
    asyncio.run(collect_election_signals())
