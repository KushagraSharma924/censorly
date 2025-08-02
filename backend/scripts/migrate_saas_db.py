"""
Database Migration Script for SaaS Platform
Creates all necessary tables in Supabase PostgreSQL database.
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv()

# Import after setting up the path
from models.saas_models import db, User, Job, APIKey, Subscription, TrainingSession
from services.supabase_service import supabase_service

def create_database_tables():
    """Create all database tables."""
    print("🔧 Creating database tables...")
    
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create a test admin user if none exists
        admin_user = User.query.filter_by(email='admin@profanityfilter.ai').first()
        if not admin_user:
            admin_user = User(
                email='admin@profanityfilter.ai',
                full_name='System Administrator',
                subscription_tier='enterprise',
                is_verified=True
            )
            admin_user.set_password('admin123')  # Change this in production!
            
            db.session.add(admin_user)
            db.session.flush()  # Get user ID
            
            # Create admin subscription
            admin_subscription = Subscription(
                user_id=admin_user.id,
                plan_name='enterprise',
                plan_price=0.0,
                status='active',
                is_active=True
            )
            db.session.add(admin_subscription)
            
            # Create admin API key
            admin_api_key = APIKey(user_id=admin_user.id, name='Admin API Key')
            raw_key = admin_api_key.get_raw_key()
            db.session.add(admin_api_key)
            
            db.session.commit()
            
            print(f"✅ Admin user created:")
            print(f"   Email: admin@profanityfilter.ai")
            print(f"   Password: admin123")
            print(f"   API Key: {raw_key}")
            print("   🚨 CHANGE THE PASSWORD IN PRODUCTION!")
        else:
            print("ℹ️  Admin user already exists")
        
        print("\n🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        db.session.rollback()
        return False
    
    return True

def verify_database_connection():
    """Verify database connection and table structure."""
    print("🔍 Verifying database connection...")
    
    try:
        # Test basic connection
        from sqlalchemy import text
        result = db.session.execute(text('SELECT version();'))
        version = result.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version}")
        
        # Check if tables exist
        tables = ['users', 'jobs', 'api_keys', 'subscriptions', 'training_sessions']
        for table in tables:
            result = db.session.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """))
            exists = result.fetchone()[0]
            print(f"{'✅' if exists else '❌'} Table '{table}': {'exists' if exists else 'missing'}")
        
        # Count records
        user_count = User.query.count()
        job_count = Job.query.count()
        key_count = APIKey.query.count()
        subscription_count = Subscription.query.count()
        training_count = TrainingSession.query.count()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Users: {user_count}")
        print(f"   Jobs: {job_count}")
        print(f"   API Keys: {key_count}")
        print(f"   Subscriptions: {subscription_count}")
        print(f"   Training Sessions: {training_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {str(e)}")
        return False

def main():
    """Main migration function."""
    print("🚀 AI Profanity Filter SaaS - Database Migration")
    print("=" * 50)
    
    # Check environment variables
    database_url = os.getenv('SUPABASE_DB_URL')
    if not database_url:
        print("❌ SUPABASE_DB_URL environment variable not set!")
        print("   Please check your .env file.")
        return False
    
    print(f"🔗 Database URL: {database_url[:50]}...")
    
    # Create a simple Flask app to initialize database connection
    try:
        from flask import Flask
        from models.saas_models import db
        
        app = Flask(__name__)
        
        # Configure database
        database_url = os.getenv('SUPABASE_DB_URL')
        if database_url and database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Verify connection first
            if not verify_database_connection():
                print("❌ Initial database connection failed!")
                return False
            
            # Create tables
            if not create_database_tables():
                print("❌ Database table creation failed!")
                return False
            
            # Final verification
            print("\n🔍 Final verification...")
            if verify_database_connection():
                print("\n🎉 Migration completed successfully!")
                print("\n📝 Next Steps:")
                print("   1. Start the Flask server: python app_saas.py")
                print("   2. Test the API endpoints")
                print("   3. Create user accounts via /api/auth/register")
                print("   4. Set up payment webhooks for Razorpay")
                return True
            else:
                print("❌ Final verification failed!")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
