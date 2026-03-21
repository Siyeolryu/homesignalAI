#!/usr/bin/env python3
"""Claude API 크레딧 테스트"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    exit(1)

print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
print("🔄 Claude API 테스트 중...")

try:
    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        messages=[
            {"role": "user", "content": "Hello"}
        ]
    )

    print("✅ Claude API 정상 작동!")
    print(f"📝 응답: {message.content[0].text}")

except Exception as e:
    print(f"❌ Claude API 오류: {e}")
    exit(1)
