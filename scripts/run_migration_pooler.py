"""Execute migration using Supabase Pooler connection"""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Execute RPC migration on Supabase using Pooler"""
    # Use pooler connection (session mode for DDL)
    # Format: postgresql://postgres.{project_ref}:{password}@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres

    project_ref = "yietqoikdaqpwmmvamtv"
    password = os.getenv("DATABASE_URL", "").split(":")[2].split("@")[0]

    # Try pooler URL
    pooler_url = f"postgresql://postgres.{project_ref}:{password}@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres"

    print(f"Connecting to Supabase Pooler...")
    print(f"Project: {project_ref}")

    # Read migration file
    migration_path = Path(__file__).parent.parent / "migrations" / "006_add_rpc_methods.sql"
    print(f"Reading migration: {migration_path}")

    if not migration_path.exists():
        print(f"ERROR: Migration file not found: {migration_path}")
        return

    with open(migration_path, "r", encoding="utf-8") as f:
        migration_sql = f.read()

    print(f"Migration file size: {len(migration_sql)} bytes")
    print("=" * 70)

    try:
        # Use session mode (port 5432) for DDL
        conn = psycopg2.connect(pooler_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("Executing migration...")
        cursor.execute(migration_sql)

        print("\n" + "=" * 70)
        print("SUCCESS! Migration executed successfully.")
        print("=" * 70)

        # Verify functions exist
        cursor.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND (routine_name LIKE '%news_keyword%'
                 OR routine_name LIKE '%aggregate_houses%'
                 OR routine_name LIKE '%get_latest_predictions%'
                 OR routine_name LIKE '%get_ml_%'
                 OR routine_name LIKE '%policy_events%'
                 OR routine_name LIKE '%dashboard_summary%')
            ORDER BY routine_name
        """)

        functions = cursor.fetchall()
        print("\nRPC functions in database:")
        for func in functions:
            print(f"  ✓ {func[0]}")

        if not functions:
            print("  WARNING: No RPC functions found. Migration may have failed.")

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("Next steps:")
        print("  1. Test API endpoints: uv run python test_api_endpoints.py")
        print("  2. Verify functions in Supabase Dashboard > Database > Functions")
        print("=" * 70)

    except Exception as e:
        print(f"\nERROR executing migration: {e}")
        print("\nAlternative: Manually execute in Supabase SQL Editor:")
        print(f"  1. Go to Supabase Dashboard > SQL Editor")
        print(f"  2. Open file: {migration_path}")
        print(f"  3. Copy contents and execute")


if __name__ == "__main__":
    main()
