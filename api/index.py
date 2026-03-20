"""
Vercel Serverless Function Entry Point for FastAPI

This file serves as the entry point for Vercel's Python runtime.
It imports the FastAPI app from src/main.py and exports it for Vercel.

Official Vercel FastAPI guide:
https://vercel.com/docs/frameworks/fastapi

CRITICAL SECTION: Environment Variables Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment variables MUST be set BEFORE any imports that trigger Settings initialization.
This prevents Pydantic ValidationError during module loading.
"""

# ═══════════════════════════════════════════════════════════════
# STEP 1: Environment Variables (HIGHEST PRIORITY - BEFORE ALL IMPORTS!)
# ═══════════════════════════════════════════════════════════════
import os

# CRITICAL: Set fallback defaults for missing OR EMPTY environment variables
# setdefault() only works if the key doesn't exist, but Vercel might set empty strings
# So we explicitly check for empty strings and None values

def ensure_env_var(key: str, default: str) -> None:
    """Ensure environment variable is set with a non-empty value and stripped of whitespace"""
    value = os.environ.get(key)
    if value:
        # 이미 설정된 값이 있으면 공백 제거 (특히 \n 대응)
        os.environ[key] = value.strip()
    
    # 다시 가져와서 확인 (strip 된 상태이거나 None)
    value = os.environ.get(key)
    if not value or value.strip() == "":
        os.environ[key] = default

# Set fallback defaults BEFORE any other imports
ensure_env_var("SUPABASE_URL", "https://placeholder.supabase.co")
ensure_env_var("SUPABASE_KEY", "placeholder-key")
ensure_env_var("SUPABASE_SERVICE_ROLE_KEY", "placeholder-service-key")

# Normalize and ensure valid values for Pydantic Literal fields
app_env = (os.environ.get("APP_ENV") or "production").lower()
if app_env not in ["development", "staging", "production"]:
    os.environ["APP_ENV"] = "production"
else:
    os.environ["APP_ENV"] = app_env

ai_provider = (os.environ.get("AI_PROVIDER") or "openai").lower()
if ai_provider not in ["openai", "anthropic"]:
    os.environ["AI_PROVIDER"] = "openai"
else:
    os.environ["AI_PROVIDER"] = ai_provider

ensure_env_var("DEBUG", "false")

# ═══════════════════════════════════════════════════════════════
# STEP 2: Python Path Setup
# ═══════════════════════════════════════════════════════════════
import sys
from pathlib import Path

# Add project root to Python path (CRITICAL for imports)
root = Path(__file__).parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# ═══════════════════════════════════════════════════════════════
# STEP 3: Debug Logging
# ═══════════════════════════════════════════════════════════════
print("[Vercel] ═══════════════════════════════════════════════════════")
print("[Vercel] HomeSignal AI FastAPI - Vercel Serverless Function")
print("[Vercel] ═══════════════════════════════════════════════════════")
print(f"[Vercel] Python version: {sys.version}")
print(f"[Vercel] Project root: {root}")
print("[Vercel]")
print("[Vercel] Environment Variables Check:")
print(f"  - SUPABASE_URL: {'✓ SET' if os.getenv('SUPABASE_URL') else '✗ MISSING'}")
print(f"  - SUPABASE_KEY: {'✓ SET' if os.getenv('SUPABASE_KEY') else '✗ MISSING'}")
print(f"  - SUPABASE_SERVICE_ROLE_KEY: {'✓ SET' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '✗ MISSING'}")
print(f"  - OPENAI_API_KEY: {'✓ SET' if os.getenv('OPENAI_API_KEY') else '✗ MISSING'}")
print(f"  - APP_ENV: {os.getenv('APP_ENV', 'NOT SET')}")
print(f"  - DEBUG: {os.getenv('DEBUG', 'NOT SET')}")
print("[Vercel]")

# ═══════════════════════════════════════════════════════════════
# STEP 4: Import FastAPI App (Safe now that env vars are set)
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# STEP 4: Import FastAPI App (Safe now that env vars are set)
# ═══════════════════════════════════════════════════════════════

try:
    print("[Vercel] Loading FastAPI app from src.main...")
    from src.main import app as main_app
    app = main_app # Literal assignment for Vercel scanner

    print("[Vercel] ✅ SUCCESS: FastAPI app loaded")
    print(f"[Vercel]   - App title: {app.title}")
    print(f"[Vercel]   - App version: {getattr(app, 'version', 'N/A')}")
    print("[Vercel]")

except Exception as e:
    print("[Vercel] ═══════════════════════════════════════════════════════")
    print("[Vercel] ❌ CRITICAL ERROR: Failed to load FastAPI app")
    print("[Vercel] ═══════════════════════════════════════════════════════")
    print(f"[Vercel] Error type: {type(e).__name__}")
    print(f"[Vercel] Error message: {e}")
    print("[Vercel]")
    print("[Vercel] Stack trace:")
    import traceback
    traceback.print_exc()
    print("[Vercel] ═══════════════════════════════════════════════════════")

    # ═══════════════════════════════════════════════════════════════
    # Fallback: Create minimal emergency app
    # ═══════════════════════════════════════════════════════════════
    print("[Vercel] Creating emergency fallback app...")
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(
        title="HomeSignal AI (Emergency Mode)",
        description="Main app failed to initialize - running in emergency mode",
        version="0.0.0-emergency"
    )

    # Store error for debugging
    _init_error = str(e)
    _init_traceback = traceback.format_exc()

    @app.get("/")
    @app.get("/health")
    async def emergency_health():
        """Emergency health check - app initialization failed"""
        return JSONResponse(
            status_code=503,
            content={
                "status": "emergency_mode",
                "message": "🚨 Application failed to initialize - check Vercel deployment logs",
                "error": {
                    "type": type(e).__name__,
                    "message": _init_error,
                },
                "environment": {
                    "SUPABASE_URL": "✓ SET" if os.getenv("SUPABASE_URL") else "✗ MISSING",
                    "SUPABASE_KEY": "✓ SET" if os.getenv("SUPABASE_KEY") else "✗ MISSING",
                    "OPENAI_API_KEY": "✓ SET" if os.getenv("OPENAI_API_KEY") else "✗ MISSING",
                    "APP_ENV": os.getenv("APP_ENV", "NOT SET"),
                },
                "troubleshooting": {
                    "step_1": "Check Vercel Dashboard → Environment Variables",
                    "step_2": "Verify SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY are set",
                    "step_3": "Check Build Logs in Vercel deployment panel",
                    "step_4": "Review stack trace above for specific error details",
                },
                "documentation": "See VERCEL_DEPLOYMENT_FIX.md for complete guide"
            }
        )

    @app.get("/error/trace")
    async def error_trace():
        """Full error traceback for debugging"""
        return JSONResponse(
            content={
                "error": _init_error,
                "traceback": _init_traceback
            }
        )

    print("[Vercel] ✅ Emergency app created successfully")
    print("[Vercel]   - Health endpoint: /health")
    print("[Vercel]   - Error trace: /error/trace")
    print("[Vercel]")

# ═══════════════════════════════════════════════════════════════
# Export for Vercel
# ═══════════════════════════════════════════════════════════════
print("[Vercel] Finalizing...")
print(f"[Vercel]   - App type: {type(app)}")
print(f"[Vercel]   - App callable: {callable(app)}")
print("[Vercel] ═══════════════════════════════════════════════════════")
print("[Vercel] ✅ Vercel serverless function ready")
print("[Vercel] ═══════════════════════════════════════════════════════")

# CRITICAL: Module must export 'app' for Vercel
# Using explicit assignment for scanner discovery
__all__ = ["app"]
