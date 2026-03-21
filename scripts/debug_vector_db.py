
from src.config import settings
from src.shared.vector_db import get_vector_db

print(f"DEBUG: {settings.debug}")
print(f"OPENAI_API_KEY: '{settings.openai_api_key}'")
print(f"SUPABASE_URL: {settings.supabase_url}")
print(f"Vector DB Class: {get_vector_db().__class__.__name__}")
