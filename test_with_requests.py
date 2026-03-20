"""Test API endpoints with requests library"""
import requests
import json

base_url = "http://localhost:8000"

print("=" * 70)
print("1. Testing GET /api/v1/forecast")
print("=" * 70)
try:
    response = requests.get(
        f"{base_url}/api/v1/forecast",
        params={"region": "청량리동", "period": "week", "horizon": 4},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS - Trend: {data['trend']}, Confidence: {data['confidence']}")
        print(f"Forecast points: {len(data['forecast'])}")
        if data.get('news_weights'):
            print(f"News weights: {len(data['news_weights'])}")
    else:
        print(f"ERROR: {response.text[:500]}")
except Exception as e:
    print(f"EXCEPTION: {e}")

print("\n" + "=" * 70)
print("2. Testing GET /api/v1/news/insights")
print("=" * 70)
try:
    response = requests.get(
        f"{base_url}/api/v1/news/insights",
        params={"region": "청량리동", "period": "month"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS - Keywords: {len(data.get('keywords', []))}")
    else:
        print(f"ERROR: {response.text[:500]}")
except Exception as e:
    print(f"EXCEPTION: {e}")

print("\n" + "=" * 70)
print("3. Testing POST /api/v1/chat (might be slow due to AI API)")
print("=" * 70)
try:
    response = requests.post(
        f"{base_url}/api/v1/chat",
        json={"message": "청량리동 가격은?", "region": "청량리동"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS - Answer length: {len(data.get('answer', ''))}")
        print(f"Fallback: {data.get('fallback', False)}")
        if data.get('forecast_summary'):
            print(f"Forecast: {data['forecast_summary']}")
    else:
        print(f"ERROR: {response.text[:500]}")
except requests.exceptions.Timeout:
    print("TIMEOUT - AI API call took too long")
except Exception as e:
    print(f"EXCEPTION: {e}")
