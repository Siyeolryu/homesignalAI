"""Direct API test without async"""
import sys
from src.forecast.schemas import ForecastRequest
from src.forecast.service import ForecastService
import asyncio

async def test():
    print("Testing ForecastService...")
    service = ForecastService(cache=None, use_real_model=False)
    request = ForecastRequest(
        region="청량리동",
        period="week",
        horizon=4,
        include_news_weight=True
    )

    try:
        result = await service.get_forecast(request)
        print("SUCCESS")
        print(f"  Trend: {result.trend}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Forecast points: {len(result.forecast)}")
        print(f"  News weights: {len(result.news_weights) if result.news_weights else 0}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(test()))
