
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# Pooler URL attempt
project_ref = "yietqoikdaqpwmmvamtv"
password = "guswk0926%21"
# Pooler hostname
host = "aws-0-ap-northeast-2.pooler.supabase.com"
user = f"postgres.{project_ref}"
db_url = f"postgresql://{user}:{password}@{host}:5432/postgres?sslmode=require"

print(f"📡 Testing connection to {host}...")
try:
    with psycopg.connect(db_url, autocommit=True) as conn:
        print("✅ Connection successful!")
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print(f"Database version: {cur.fetchone()[0]}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
