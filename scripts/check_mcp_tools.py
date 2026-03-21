import logging
import asyncio
import httpx
from src.shared.mcp_client import MCPClient

async def check_tools():
    # Perplexity search server
    url = "https://perplexity-search--arjunkmrm.run.tools"
    client = MCPClient("perplexity", url)
    
    # Try to list tools
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(f"{url}/call", json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_tools())
