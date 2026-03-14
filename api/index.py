"""
Vercel Serverless Function Entry Point

FastAPI application entrypoint for Vercel.
The actual app is defined in src/main.py and configured in pyproject.toml.

See: https://vercel.com/docs/frameworks/backend/fastapi
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

# Vercel 환경변수 디버깅 (초기 로딩 시 확인)
print("[Vercel] Environment variables check:")
print(f"  SUPABASE_URL: {'✓ Set' if os.getenv('SUPABASE_URL') else '✗ Missing'}")
print(f"  SUPABASE_KEY: {'✓ Set' if os.getenv('SUPABASE_KEY') else '✗ Missing'}")
print(f"  OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
print(f"  APP_ENV: {os.getenv('APP_ENV', 'not set')}")

# 환경변수 기본값 설정 (Vercel 환경에서 누락된 경우 대비)
os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "placeholder-key")
os.environ.setdefault("APP_ENV", "production")

try:
    # Import the FastAPI app instance from src.main
    from src.main import app

    print("[Vercel] ✓ FastAPI app loaded successfully")
except Exception as e:
    print(f"[Vercel] ✗ Failed to load app: {e}")
    import traceback
    traceback.print_exc()

    # Fallback: 최소한의 앱 생성
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="HomeSignal AI (Fallback)")

    @app.get("/")
    @app.get("/health")
    async def emergency_health():
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Application failed to initialize",
                "error": str(e),
                "env_check": {
                    "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "missing",
                    "SUPABASE_KEY": "set" if os.getenv("SUPABASE_KEY") else "missing",
                }
            }
        )

# Export for Vercel (required)
__all__ = ["app"]
