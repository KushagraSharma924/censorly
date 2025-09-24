#!/usr/bin/env python3
"""
Script to manually create required Supabase storage buckets.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    from services.supabase_service import supabase_service
    
    print("🗂️  Creating Supabase storage buckets...")
    
    buckets_to_create = [
        {
            'name': 'video-uploads',
            'options': {
                'public': False,
                'file_size_limit': 524288000,  # 500MB
                'allowed_mime_types': ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm']
            }
        },
        {
            'name': 'processed-videos', 
            'options': {
                'public': False,
                'file_size_limit': 524288000,  # 500MB
                'allowed_mime_types': ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm']
            }
        }
    ]
    
    # List existing buckets first
    try:
        existing = supabase_service.client.storage.list_buckets()
        existing_names = [b.name for b in existing] if existing else []
        print(f"📋 Existing buckets: {existing_names}")
    except Exception as e:
        print(f"⚠️  Could not list buckets: {e}")
        existing_names = []
    
    for bucket_config in buckets_to_create:
        bucket_name = bucket_config['name']
        
        if bucket_name in existing_names:
            print(f"✅ Bucket '{bucket_name}' already exists")
            continue
            
        try:
            result = supabase_service.client.storage.create_bucket(bucket_name)
            if hasattr(result, 'error') and result.error:
                print(f"❌ Failed to create '{bucket_name}': {result.error}")
            else:
                print(f"✅ Created bucket '{bucket_name}'")
                
        except Exception as e:
            print(f"❌ Exception creating '{bucket_name}': {e}")
    
    print("\n🎉 Storage bucket setup complete!")
    print("Now you can upload videos through your app.")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure you have the backend dependencies installed and environment variables set.")
