
import os
import sys
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv()

def run_migration(filename):
    project_root = Path(__file__).parent.parent
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False

    migration_file = project_root / "migrations" / filename
    if not migration_file.exists():
        print(f"❌ File not found: {migration_file}")
        return False

    print(f"🚀 Running {filename} on Supabase...")
    with open(migration_file, "r", encoding="utf-8") as f:
        sql = f.read()

    try:
        # psycopg (v3) use connect directly
        with psycopg.connect(database_url, autocommit=True) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                print(f"✅ Successfully executed {filename}")
        return True
    except Exception as e:
        print(f"❌ Error executing {filename}: {e}")
        return False

if __name__ == "__main__":
    migrations = [
        "001_setup_pgvector.sql",
        "004_create_ml_features_tables.sql",
        "006_add_rpc_methods.sql"
    ]
    for m in migrations:
        run_migration(m)
