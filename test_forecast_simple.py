"""Simple forecast endpoint test"""
import requests

try:
    print("Testing GET /api/v1/forecast...")
    response = requests.get(
        "http://localhost:8000/api/v1/forecast",
        params={
            "region": "청량리동",
            "period": "week",
            "horizon": 4
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS - Trend: {data['trend']}, Confidence: {data['confidence']}")
        print(f"  Forecast points: {len(data['forecast'])}")
    else:
        print(f"✗ ERROR: {response.text}")
except Exception as e:
    print(f"✗ EXCEPTION: {e}")
