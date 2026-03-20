import asyncio
import httpx
from src.config import settings

async def verify_rest():
    headers = {
        "apikey": settings.supabase_key,
        "Authorization": f"Bearer {settings.supabase_key}"
    }
    url = f"{settings.supabase_url}/rest/v1/news_signals?select=id,title,published_at&order=published_at.desc&limit=5"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            print("Latest ingested articles (REST Check):")
            for row in response.json():
                print(f"- [{row['published_at']}] {row['title']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(verify_rest())
