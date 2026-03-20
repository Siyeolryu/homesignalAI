import asyncio
from src.shared.database import get_async_supabase_client

async def check_ingested_data():
    client = get_async_supabase_client()
    result = await client.table("news_signals").select("id, title, published_at").order("published_at", desc=True).limit(5).execute()
    print("Latest ingested articles in Vector DB:")
    for row in result.data:
        print(f"- [{row['published_at']}] {row['title']}")

if __name__ == "__main__":
    asyncio.run(check_ingested_data())
