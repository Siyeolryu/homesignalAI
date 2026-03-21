#!/usr/bin/env python3
"""Execute migration 007: conversation tables for conversational chatbot"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg
from src.config import settings

def main():
    if not settings.database_url:
        print("[X] DATABASE_URL is not set.")
        print("    Add DATABASE_URL to .env file")
        print()
        print("Alternative: Execute manually in Supabase SQL Editor")
        print("  1. Go to: https://supabase.com/dashboard/project/<your-project>/sql/new")
        print("  2. Copy contents of: migrations/007_add_conversation_tables.sql")
        print("  3. Execute")
        return 1

    print("=" * 80)
    print("Migration 007: Conversation Tables for Conversational Chatbot")
    print("=" * 80)

    # Read migration SQL
    migration_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "migrations",
        "007_add_conversation_tables.sql"
    )

    if not os.path.exists(migration_file):
        print(f"[X] Migration file not found: {migration_file}")
        return 1

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    print(f"\n[INFO] File: {migration_file}")
    print(f"[INFO] DATABASE_URL: {settings.database_url[:50]}...")
    print(f"[INFO] SQL size: {len(sql)} characters")

    try:
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor() as cur:
                print("\n[RUNNING] Executing SQL...")
                cur.execute(sql)
                conn.commit()
                print("[OK] Migration 007 executed successfully")

                # Verify tables
                print("\n[VERIFY] Checking created tables...")
                cur.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('conversation_sessions', 'conversation_messages')
                    ORDER BY table_name
                """)
                tables = cur.fetchall()

                if len(tables) == 2:
                    print(f"[OK] Tables created: {', '.join([t[0] for t in tables])}")
                else:
                    print(f"[!] Expected 2 tables, found {len(tables)}")

                # Verify RPC functions
                print("\n[VERIFY] Checking RPC functions...")
                cur.execute("""
                    SELECT routine_name FROM information_schema.routines
                    WHERE routine_schema = 'public'
                    AND routine_name LIKE '%conversation%'
                    ORDER BY routine_name
                """)
                functions = cur.fetchall()

                expected_functions = [
                    'cleanup_expired_sessions',
                    'complete_conversation_session',
                    'get_conversation_history',
                    'get_or_create_conversation_session',
                    'save_conversation_message'
                ]

                found_functions = [f[0] for f in functions]
                print(f"[OK] RPC functions created: {len(found_functions)}")
                for func in found_functions:
                    print(f"     - {func}")

                missing = set(expected_functions) - set(found_functions)
                if missing:
                    print(f"[!] Missing functions: {missing}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Migration 007 completed successfully")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Test conversational chatbot: uv run python test_local_chat.py")
        print("  2. Run demo script: uv run python scripts/demo_conversational_chat.py")
        return 0

    except Exception as e:
        print(f"\n[X] Execution failed: {e}")
        print("\nAlternative method:")
        print("  1. Go to Supabase SQL Editor")
        print("     https://supabase.com/dashboard")
        print("  2. Copy contents of migrations/007_add_conversation_tables.sql")
        print("  3. Execute manually")
        return 1

if __name__ == "__main__":
    sys.exit(main())
