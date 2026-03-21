"""Execute migration 006_add_rpc_methods.sql on Supabase"""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()


async def main():
    """Execute RPC migration on Supabase"""
    # Get Supabase credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Need service role for DDL

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return

    print(f"Connecting to Supabase: {supabase_url}")

    # Create client
    supabase = create_client(supabase_url, supabase_key)

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

    # Split into individual statements (by $$;)
    # PostgreSQL functions end with $$; so we split on that
    statements = []
    current = []

    for line in migration_sql.split("\n"):
        current.append(line)
        # End of function definition
        if line.strip() == "$$;":
            statements.append("\n".join(current))
            current = []
        # End of simple statement
        elif line.strip().endswith(";") and not line.strip().startswith("--"):
            statements.append("\n".join(current))
            current = []

    if current:
        statements.append("\n".join(current))

    print(f"Found {len(statements)} SQL statements")
    print("=" * 70)

    # Execute via PostgreSQL connection string (Supabase REST API doesn't support DDL)
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("\nWARNING: DATABASE_URL not set. Cannot execute migration via REST API.")
        print("\nYou need to:")
        print("1. Go to Supabase Dashboard > SQL Editor")
        print("2. Copy the contents of migrations/006_add_rpc_methods.sql")
        print("3. Paste and execute in the SQL Editor")
        print("\nOr set DATABASE_URL environment variable and run this script again.")
        return

    # Use psycopg2 or asyncpg to execute DDL
    try:
        import psycopg2
    except ImportError:
        print("\nERROR: psycopg2 not installed.")
        print("Install it with: pip install psycopg2-binary")
        print("\nOr manually execute in Supabase SQL Editor:")
        print(f"  {migration_path}")
        return

    print(f"\nConnecting to PostgreSQL: {database_url.split('@')[1]}")  # Hide password

    try:
        conn = psycopg2.connect(database_url)
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
            AND routine_name LIKE '%news_keyword%' OR routine_name LIKE '%aggregate_houses%'
            ORDER BY routine_name
        """)

        functions = cursor.fetchall()
        print("\nVerifying RPC functions in database:")
        for func in functions:
            print(f"  ✓ {func[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nERROR executing migration: {e}")
        print("\nPlease manually execute in Supabase SQL Editor:")
        print(f"  {migration_path}")


if __name__ == "__main__":
    asyncio.run(main())
