"""
Phase 1 Entry Point for AI Profanity Filter SaaS Platform
Simple entry point that imports the Phase 1 Supabase-based app.
"""

from app_supabase import create_app

# Create the Flask app using Phase 1 configuration
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
