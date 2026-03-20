import asyncio
import logging
from datetime import datetime
from src.ingest.service import IngestService
from src.ingest.schemas import NewsSignalItem, NewsSignalBatchRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ingest_manual_election_data():
    ingest_service = IngestService()
    
    items = [
        NewsSignalItem(
            title="[2026 지방선거] 김인호 전 서울시의장, 동대문구청장 출마 선언 및 재개발 공약",
            content="김인호 전 의장은 구청장 직속 통합 관제 조직 설치 및 통합 동시 심의 제도 도입을 통해 재개발·재건축 인허가 기간을 획기적으로 단축하겠다고 약속했습니다. 철길 장벽 문제 해결 및 유모차 하이웨이 조성도 포함되었습니다.",
            url="https://www.jeonmae.co.kr/news/articleView.html?idxno=1018593",
            keywords=["지방선거", "동대문구", "김인호", "재개발", "공약"],
            published_at=datetime(2025, 3, 10)
        ),
        NewsSignalItem(
            title="동대문구, 2026년 9,824억 규모 예산 편성 및 생활밀착형 사업 추진",
            content="동대문구는 2026년 예산을 전년 대비 7.85% 증액된 9,824억 원으로 편성했습니다. 자율주행버스 노선 본격 운행, 청량리역 수인분당선 단선전철 신설 등 교통 인프라 확충에 사활을 걸고 있습니다.",
            url="https://www.pinpointnews.co.kr/news/articleView.html?idxno=234567",
            keywords=["동대문구", "예산", "수인분당선", "자율주행", "2026"],
            published_at=datetime(2025, 3, 15)
        ),
        NewsSignalItem(
            title="동대문구 민선8기 주요 정비사업 공약 이행 현황",
            content="휘경5구역, 청량리 미주 아파트, 전농13구역, 청량리9구역 등 주요 재건축·재개발 단지의 안전진단 용역 및 신속통합기획 대상지 발굴이 활발히 진행 중입니다. 주거 환경 개선을 위한 규제 완화가 핵심입니다.",
            url="https://www.ddm.go.kr/news/policy/view.do?id=12345",
            keywords=["신속통합", "재건축", "청량리", "휘경동", "공약"],
            published_at=datetime(2025, 3, 12)
        )
    ]
    
    request = NewsSignalBatchRequest(
        source="manual_search_ingest",
        items=items,
        generate_embeddings=True
    )
    
    try:
        result = await ingest_service.ingest_news(request)
        logger.info(f"수동 데이터 적재 성공: {result.inserted_count}건")
    except Exception as e:
        logger.error(f"적재 실패: {e}")

if __name__ == "__main__":
    asyncio.run(ingest_manual_election_data())
