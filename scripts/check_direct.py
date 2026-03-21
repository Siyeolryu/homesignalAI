import asyncio
import os
from supabase import create_async_client

async def check_direct():
    url = "https://soeunyim-art.supabase.co" # Replace with actual if known, but I should use env
    # I'll get them from settings if possible, but I'll just use a test script that imports settings
    from src.config import settings
    
    print(f"Connecting to {settings.supabase_url}")
    client = await create_async_client(settings.supabase_url, settings.supabase_key)
    try:
        result = await client.table("news_signals").select("id, title, published_at").order("published_at", desc=True).limit(5).execute()
        print("Latest ingested articles (Direct Check):")
        for row in result.data:
            print(f"- [{row['published_at']}] {row['title']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.auth.close_stale_sessions()

if __name__ == "__main__":
    asyncio.run(check_direct())
