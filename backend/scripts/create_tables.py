#!/usr/bin/env python3
"""
Create missing tables in Supabase database
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_missing_tables():
    """Create the jobs and training_sessions tables in Supabase."""
    
    # Get database connection details from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not found")
        return False
    
    try:
        # Connect to PostgreSQL
        logger.info("Connecting to Supabase PostgreSQL...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create jobs table
        logger.info("Creating jobs table...")
        jobs_sql = """
        CREATE TABLE IF NOT EXISTS jobs (
            id VARCHAR(36) PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            original_filename VARCHAR(255) NOT NULL,
            file_size INTEGER,
            duration FLOAT,
            censoring_mode VARCHAR(20) DEFAULT 'beep',
            profanity_threshold FLOAT DEFAULT 0.8,
            languages TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            input_path VARCHAR(500),
            output_path VARCHAR(500),
            profane_segments_count INTEGER DEFAULT 0,
            censored_duration FLOAT DEFAULT 0.0,
            result_url VARCHAR(500),
            download_url VARCHAR(500),
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            expires_at TIMESTAMP WITH TIME ZONE,
            celery_task_id VARCHAR(255)
        );
        """
        cur.execute(jobs_sql)
        
        # Create training_sessions table
        logger.info("Creating training_sessions table...")
        training_sql = """
        CREATE TABLE IF NOT EXISTS training_sessions (
            id VARCHAR(36) PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            original_filename VARCHAR(255) NOT NULL,
            file_size INTEGER,
            total_words INTEGER DEFAULT 0,
            new_words_added INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            result_url VARCHAR(500),
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE
        );
        """
        cur.execute(training_sql)
        
        # Create indexes for better performance
        logger.info("Creating indexes...")
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_training_sessions_user_id ON training_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON training_sessions(status);"
        ]
        
        for sql in indexes_sql:
            cur.execute(sql)
        
        # Commit changes
        conn.commit()
        logger.info("✅ Successfully created missing tables and indexes")
        
        # Verify tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('jobs', 'training_sessions')
        """)
        
        tables = [row['table_name'] for row in cur.fetchall()]
        logger.info(f"Verified tables exist: {tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    logger.info("🔧 Creating missing Supabase tables...")
    success = create_missing_tables()
    
    if success:
        logger.info("🎉 Database schema setup complete!")
    else:
        logger.error("❌ Database schema setup failed!")
        exit(1)
