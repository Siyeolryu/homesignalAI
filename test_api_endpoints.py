"""Test API endpoints to diagnose issues"""
import asyncio
import json

import httpx


async def test_endpoints():
    """Test all main endpoints"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Health check
        print("=" * 60)
        print("1. Testing /health")
        print("=" * 60)
        try:
            response = await client.get(f"{base_url}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"ERROR: {e}")

        # 2. Forecast GET
        print("\n" + "=" * 60)
        print("2. Testing GET /api/v1/forecast")
        print("=" * 60)
        try:
            response = await client.get(
                f"{base_url}/api/v1/forecast",
                params={
                    "region": "청량리동",
                    "period": "week",
                    "horizon": 4
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"ERROR: {e}")

        # 3. Forecast POST
        print("\n" + "=" * 60)
        print("3. Testing POST /api/v1/forecast")
        print("=" * 60)
        try:
            response = await client.post(
                f"{base_url}/api/v1/forecast",
                json={
                    "region": "청량리동",
                    "period": "week",
                    "horizon": 4,
                    "include_news_weight": True
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"ERROR: {e}")

        # 4. Chat
        print("\n" + "=" * 60)
        print("4. Testing POST /api/v1/chat")
        print("=" * 60)
        try:
            response = await client.post(
                f"{base_url}/api/v1/chat",
                json={
                    "message": "청량리동 부동산 가격 전망은?",
                    "region": "청량리동"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Answer: {result.get('answer')}")
                print(f"Forecast: {result.get('forecast_summary')}")
                print(f"Sources: {len(result.get('sources', []))} sources")
                print(f"Fallback: {result.get('fallback')}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"ERROR: {e}")

        # 5. News Insights
        print("\n" + "=" * 60)
        print("5. Testing GET /api/v1/news/insights")
        print("=" * 60)
        try:
            response = await client.get(
                f"{base_url}/api/v1/news/insights",
                params={
                    "region": "청량리동",
                    "period": "month",
                    "keywords": ["GTX", "재개발"]
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(test_endpoints())
