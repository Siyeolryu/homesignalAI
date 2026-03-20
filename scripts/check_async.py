try:
    from supabase import AsyncClient
    print("AsyncClient exists")
except ImportError:
    print("AsyncClient does not exist")
