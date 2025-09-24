#!/usr/bin/env python3
"""
Script to check and potentially create the required database schema for jobs table.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    from services.supabase_service import supabase_service
    
    print("🔍 Checking current jobs table schema...")
    
    # Try to get a sample job to see what columns exist
    try:
        result = supabase_service.client.table("jobs").select("*").limit(1).execute()
        if result.data:
            print("✅ Jobs table exists")
            print("Current columns:", list(result.data[0].keys()) if result.data else "No data")
        else:
            print("⚠️  Jobs table exists but has no data")
            
    except Exception as e:
        print(f"❌ Jobs table issue: {e}")
    
    print("\n📝 Required columns for current implementation:")
    required_columns = [
        'id', 'user_id', 'storage_path', 'original_name', 'file_size',
        'censoring_mode', 'profanity_threshold', 'languages', 'whisper_model',
        'status', 'created_at', 'completed_at', 'error_message', 'result'
    ]
    
    for col in required_columns:
        print(f"  - {col}")
    
    print("\n🚀 If the jobs table doesn't exist or has wrong columns,")
    print("you need to create it in your Supabase dashboard with these columns:")
    print("""
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    original_name TEXT NOT NULL,
    file_size BIGINT,
    censoring_mode TEXT DEFAULT 'beep',
    profanity_threshold FLOAT DEFAULT 0.8,
    languages TEXT DEFAULT '["en"]',
    whisper_model TEXT DEFAULT 'base',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    result JSONB
);
""")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure you have the backend dependencies installed and environment variables set.")
