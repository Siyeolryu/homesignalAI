# URGENT: Database Migration Required

## Issue Summary

All API endpoints (forecast, chat, news) are failing with the following error:

```
Could not find the function public.get_news_keyword_frequency(p_keywords) in the schema cache
```

**Root Cause:** The database RPC function `get_news_keyword_frequency` and other RPC functions from migration `006_add_rpc_methods.sql` have not been executed on the Supabase database.

**Impact:**
- GET/POST /api/v1/forecast - Returns 500 error
- POST /api/v1/chat - Returns 500 error
- GET /api/v1/news/insights - Returns 500 error
- Only /health endpoint works

## Solution: Execute Migration Manually

Since direct PostgreSQL connection from this environment has network/authentication issues, the migration must be executed manually in the Supabase Dashboard.

### Step-by-Step Instructions

1. **Open Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Select your project: `yietqoikdaqpwmmvamtv`

2. **Navigate to SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy Migration SQL**
   - Open file: `D:\Ai_project\home_signal_ai\migrations\006_add_rpc_methods.sql`
   - Select all content (Ctrl+A)
   - Copy (Ctrl+C)

4. **Execute Migration**
   - Paste the SQL into the Supabase SQL Editor
   - Click "Run" button (or press Ctrl+Enter)
   - Wait for execution to complete (should take 2-5 seconds)

5. **Verify Success**
   - You should see "Success. No rows returned" message
   - Go to Dashboard > Database > Functions
   - Verify these functions exist:
     - `aggregate_houses_time_series`
     - `get_news_keyword_frequency`
     - `get_latest_predictions`
     - `get_ml_features_with_news`
     - `get_ml_training_data`
     - `get_policy_events_by_period`
     - `get_dashboard_summary`

6. **Test API Endpoints**
   ```bash
   cd D:\Ai_project\home_signal_ai
   uv run python test_api_endpoints.py
   ```

## Migration File Location

```
D:\Ai_project\home_signal_ai\migrations\006_add_rpc_methods.sql
```

## What This Migration Does

The migration creates 7 PostgreSQL RPC (Remote Procedure Call) functions:

1. **aggregate_houses_time_series** - Aggregates real estate transaction data by week/month
2. **get_news_keyword_frequency** - Calculates keyword frequency in news articles
3. **get_latest_predictions** - Retrieves latest forecast predictions
4. **get_ml_features_with_news** - Combines ML features with news data
5. **get_ml_training_data** - Retrieves ML training dataset
6. **get_policy_events_by_period** - Gets policy events in date range
7. **get_dashboard_summary** - Generates dashboard summary statistics

These functions are essential for the API's forecast, chat, and news analysis features.

## Alternative: Use Mock Mode (Temporary)

If you cannot execute the migration immediately, you can temporarily use mock mode:

1. Edit `.env` file:
   ```bash
   # Change this line:
   SUPABASE_URL=https://yietqoikdaqpwmmvamtv.supabase.co

   # To this:
   SUPABASE_URL=placeholder
   ```

2. Restart the server:
   ```bash
   # Kill existing server (Ctrl+C)
   uv run uvicorn src.main:app --reload
   ```

3. Test again - API will use mock data instead of real database

**Note:** Mock mode is only for testing. You still need to execute the migration for production use.

## Troubleshooting

### If migration fails with "function already exists"

Some functions may already exist. Run this query first to drop existing functions:

```sql
DROP FUNCTION IF EXISTS aggregate_houses_time_series CASCADE;
DROP FUNCTION IF EXISTS get_news_keyword_frequency CASCADE;
DROP FUNCTION IF EXISTS get_latest_predictions CASCADE;
DROP FUNCTION IF EXISTS get_ml_features_with_news CASCADE;
DROP FUNCTION IF EXISTS get_ml_training_data CASCADE;
DROP FUNCTION IF EXISTS get_policy_events_by_period CASCADE;
DROP FUNCTION IF EXISTS get_dashboard_summary CASCADE;
```

Then run the full migration.

### If you see "relation does not exist" errors

You need to run previous migrations first:

1. `001_setup_pgvector.sql` - Creates base tables
2. `004_create_ml_features_tables.sql` - Creates ML feature tables
3. `005_add_train_test_split.sql` - Adds train/test split column
4. `006_add_rpc_methods.sql` - Creates RPC functions (THIS ONE)

Execute them in order.

## Need Help?

Contact the development team or check:
- Project Documentation: `docs/13_Database_Schema_and_Relationships.md`
- CLAUDE.md: Database Setup & Migrations section
