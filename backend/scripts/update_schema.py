"""
Database Schema Update Script for SaaS Platform
Updates existing tables to support new SaaS features.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv()

def create_db_engine():
    """Create database engine."""
    database_url = os.getenv('SUPABASE_DB_URL')
    if not database_url:
        print("❌ SUPABASE_DB_URL environment variable not set!")
        return None
    
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    return create_engine(database_url)

def update_users_table(engine: Engine):
    """Update users table with SaaS columns."""
    print("🔧 Updating users table schema...")
    
    try:
        with engine.connect() as conn:
            # Add missing columns to users table
            updates = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS videos_processed INTEGER DEFAULT 0;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_processing_time FLOAT DEFAULT 0.0;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;"
            ]
            
            for update in updates:
                try:
                    conn.execute(text(update))
                    print(f"✅ Executed: {update}")
                except Exception as e:
                    print(f"⚠️  Column might already exist: {update}")
            
            conn.commit()
            print("✅ Users table updated successfully!")
            
    except Exception as e:
        print(f"❌ Failed to update users table: {str(e)}")
        return False
    
    return True

def create_saas_tables(engine: Engine):
    """Create SaaS-specific tables."""
    print("🔧 Creating SaaS tables...")
    
    saas_tables = {
        'api_keys': """
            CREATE TABLE IF NOT EXISTS api_keys (
                id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                key_prefix VARCHAR(10),
                key_hash VARCHAR(128) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );
        """,
        'subscriptions': """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                plan_name VARCHAR(50) NOT NULL,
                plan_price FLOAT DEFAULT 0.0,
                status VARCHAR(20) DEFAULT 'pending',
                is_active BOOLEAN DEFAULT FALSE,
                auto_renew BOOLEAN DEFAULT TRUE,
                razorpay_subscription_id VARCHAR(100),
                razorpay_customer_id VARCHAR(100),
                razorpay_order_id VARCHAR(100),
                razorpay_payment_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                cancelled_at TIMESTAMP
            );
        """
    }
    
    try:
        with engine.connect() as conn:
            for table_name, create_sql in saas_tables.items():
                try:
                    conn.execute(text(create_sql))
                    print(f"✅ Table '{table_name}' created/verified")
                except Exception as e:
                    print(f"⚠️  Table '{table_name}' might already exist: {str(e)}")
            
            conn.commit()
            print("✅ SaaS tables created successfully!")
            
    except Exception as e:
        print(f"❌ Failed to create SaaS tables: {str(e)}")
        return False
    
    return True

def create_admin_user(engine: Engine):
    """Create admin user if it doesn't exist."""
    print("👤 Creating admin user...")
    
    try:
        with engine.connect() as conn:
            # Check if admin exists
            result = conn.execute(text(
                "SELECT id FROM users WHERE email = 'admin@profanityfilter.ai'"
            ))
            admin_exists = result.fetchone()
            
            if not admin_exists:
                from werkzeug.security import generate_password_hash
                import uuid
                
                admin_id = str(uuid.uuid4())
                password_hash = generate_password_hash('admin123')
                
                conn.execute(text("""
                    INSERT INTO users (id, email, password_hash, full_name, is_verified, subscription_tier, is_active)
                    VALUES (:id, :email, :password_hash, :full_name, :is_verified, :subscription_tier, :is_active)
                """), {
                    'id': admin_id,
                    'email': 'admin@profanityfilter.ai',
                    'password_hash': password_hash,
                    'full_name': 'System Administrator',
                    'is_verified': True,
                    'subscription_tier': 'enterprise',
                    'is_active': True
                })
                
                # Create admin subscription
                subscription_id = str(uuid.uuid4())
                conn.execute(text("""
                    INSERT INTO subscriptions (id, user_id, plan_name, plan_price, status, is_active)
                    VALUES (:id, :user_id, :plan_name, :plan_price, :status, :is_active)
                """), {
                    'id': subscription_id,
                    'user_id': admin_id,
                    'plan_name': 'enterprise',
                    'plan_price': 0.0,
                    'status': 'active',
                    'is_active': True
                })
                
                conn.commit()
                
                print(f"✅ Admin user created:")
                print(f"   Email: admin@profanityfilter.ai")
                print(f"   Password: admin123")
                print("   🚨 CHANGE THE PASSWORD IN PRODUCTION!")
            else:
                print("ℹ️  Admin user already exists")
                
    except Exception as e:
        print(f"❌ Failed to create admin user: {str(e)}")
        return False
    
    return True

def main():
    """Main migration function."""
    print("🚀 AI Profanity Filter SaaS - Schema Update")
    print("=" * 50)
    
    engine = create_db_engine()
    if not engine:
        return False
    
    print(f"🔗 Connected to database")
    
    # Update existing tables
    if not update_users_table(engine):
        return False
    
    # Create new SaaS tables
    if not create_saas_tables(engine):
        return False
    
    # Create admin user
    if not create_admin_user(engine):
        return False
    
    print("\n🎉 Schema update completed successfully!")
    print("\n📝 Next Steps:")
    print("   1. Test the updated schema")
    print("   2. Start the SaaS backend server")
    print("   3. Register test users")
    print("   4. Configure payment webhooks")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
