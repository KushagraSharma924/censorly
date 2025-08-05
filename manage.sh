#!/bin/bash

# AI Profanity Filter SaaS Management Script - Phase 1
# Pure Supabase Architecture

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Helper functions for colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show Phase 1 banner
show_banner() {
    echo -e "${PURPLE}"
    echo "=========================================="
    echo "  AI Profanity Filter SaaS - Phase 1"
    echo "=========================================="
    echo "🚀 Pure Supabase Architecture"
    echo "📊 Real-time Dashboard"
    echo "🔑 API Key Management"
    echo "💼 Job Processing System"
    echo -e "${NC}"
}

# Setup development environment
setup_dev() {
    show_banner
    echo "🔧 Setting up Phase 1 development environment..."
    echo "=============================================="
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is required but not installed"
        exit 1
    fi
    log_success "Python3 found: $(python3 --version)"
    
    # Setup backend
    echo "🐍 Setting up Python backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Created virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    log_success "Activated virtual environment"
    
    # Install requirements
    pip install -r requirements.txt
    log_success "Installed Python dependencies"
    
    cd ..
    
    # Setup frontend
    echo "⚛️  Setting up React frontend..."
    cd frontend
    
    # Check if bun is available, otherwise use npm
    if command -v bun &> /dev/null; then
        bun install
        log_success "Installed frontend dependencies with Bun"
    elif command -v npm &> /dev/null; then
        npm install
        log_success "Installed frontend dependencies with NPM"
    else
        log_error "Neither Bun nor NPM found. Please install one of them."
        exit 1
    fi
    
    cd ..
    
    log_success "Phase 1 development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Setup your Supabase project: ./manage.sh db-setup"
    echo "2. Start backend: ./manage.sh backend"
    echo "3. Start frontend: ./manage.sh frontend"
}

# Database setup for Supabase
db_setup() {
    echo "🗄️  Phase 1 Database Setup"
    echo "========================"
    echo ""
    echo "Please complete these steps in your Supabase dashboard:"
    echo ""
    echo "1. Go to your Supabase project dashboard"
    echo "2. Navigate to SQL Editor"
    echo "3. Run the schema from: backend/migrations/supabase_schema.sql"
    echo "4. Update your environment variables with:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_SERVICE_KEY"
    echo "   - SUPABASE_ANON_KEY"
    echo ""
    echo "📋 Required tables for Phase 1:"
    echo "   ✓ users (authentication & profiles)"
    echo "   ✓ api_keys (API key management)"
    echo "   ✓ jobs (processing jobs)"
    echo "   ✓ subscriptions (billing plans)"
    echo ""
    log_info "After setup, test with: ./manage.sh health"
}

# Phase status check
phase_status() {
    show_banner
    echo "📊 Phase 1 System Status"
    echo "======================="
    
    echo ""
    echo "🔧 Phase 1 Features:"
    echo "  ✅ Pure Supabase Architecture"
    echo "  ✅ User Authentication (Supabase Auth)"
    echo "  ✅ API Key Management"
    echo "  ✅ Job Processing System"
    echo "  ✅ Real-time Updates"
    echo "  ✅ Row Level Security"
    echo ""
    
    echo "🚀 Services Status:"
    # Check backend
    if curl -s http://localhost:8080/api/health >/dev/null 2>&1; then
        echo "  ✅ Backend (Port 8080)"
    else
        echo "  ❌ Backend (Port 8080) - Not running"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "  ✅ Frontend (Port 3000)"
    else
        echo "  ❌ Frontend (Port 3000) - Not running"
    fi
    
    echo ""
    echo "📦 Dependencies:"
    if python3 -c "import supabase" 2>/dev/null; then
        echo "  ✅ Supabase SDK"
    else
        echo "  ❌ Supabase SDK - Run: ./manage.sh setup-dev"
    fi
    
    if [ -d "frontend/node_modules" ]; then
        echo "  ✅ Frontend Dependencies"
    else
        echo "  ❌ Frontend Dependencies - Run: ./manage.sh setup-dev"
    fi
}

# Start backend service
backend() {
    echo "🐍 Starting Phase 1 Backend..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    python app_supabase.py
}

# Start frontend service
frontend() {
    echo "⚛️  Starting Phase 1 Frontend..."
    cd frontend
    if command -v bun &> /dev/null; then
        bun run dev
    else
        npm run dev
    fi
}

# Health check
health_check() {
    echo "🔍 Phase 1 Health Check"
    echo "======================"
    
    echo ""
    echo "🐍 Python Environment:"
    python3 --version 2>/dev/null || echo "❌ Python3 not found"
    
    echo ""
    echo "📦 Supabase Package:"
    if python3 -c "import supabase" 2>/dev/null; then
        echo "✅ Supabase SDK installed"
    else
        echo "❌ Supabase SDK not installed"
    fi
    
    echo ""
    echo "🌐 Backend Service (localhost:8080):"
    if curl -s http://localhost:8080/api/health >/dev/null 2>&1; then
        echo "✅ Backend service running"
        # Get detailed health info
        health_response=$(curl -s http://localhost:8080/api/health 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "📋 Health Details: $health_response"
        fi
    else
        echo "❌ Backend service not running"
    fi
    
    echo ""
    echo "⚛️  Frontend Service (localhost:3000):"
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend service running"
    else
        echo "❌ Frontend service not running"
    fi
}

# Start both services
start_all() {
    show_banner
    echo "🚀 Starting Phase 1 AI Profanity Filter SaaS"
    echo "==========================================="
    
    echo "🐍 Starting backend service..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    python app_supabase.py &
    BACKEND_PID=$!
    cd ..
    
    echo "⚛️  Starting frontend service..."
    cd frontend
    if command -v bun &> /dev/null; then
        bun run dev &
    else
        npm run dev &
    fi
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    log_success "Services starting..."
    log_info "Backend: http://localhost:8080"
    log_info "Frontend: http://localhost:3000"
    log_info "Press Ctrl+C to stop all services"
    
    # Wait for interruption
    trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT
    wait
}

# Clean temporary files
clean() {
    echo "🧹 Cleaning up temporary files..."
    echo "=============================="
    
    echo "🗑️  Removing Python cache files..."
    find backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find backend -name "*.pyc" -delete 2>/dev/null || true
    
    echo "🗑️  Removing log files..."
    rm -f backend/*.log 2>/dev/null || true
    rm -f backend/logs/*.log 2>/dev/null || true
    
    echo "🗑️  Removing temporary uploads..."
    rm -rf backend/uploads/temp/* 2>/dev/null || true
    rm -rf backend/processed/temp/* 2>/dev/null || true
    
    echo "🗑️  Removing node modules cache..."
    rm -rf frontend/node_modules/.cache 2>/dev/null || true
    
    echo "✅ Cleanup complete!"
}

# Show help
show_help() {
    show_banner
    echo ""
    echo "📖 Phase 1 Management Commands"
    echo "============================="
    echo ""
    echo "🔧 Setup & Configuration:"
    echo "  setup-dev     Setup development environment"
    echo "  db-setup      Show database setup instructions"
    echo ""
    echo "🚀 Services:"
    echo "  start         Start both backend and frontend"
    echo "  backend       Start backend server (port 8080)"
    echo "  frontend      Start frontend server (port 3000)"
    echo ""
    echo "📊 Monitoring:"
    echo "  phase-status  Show Phase 1 system status"
    echo "  health        Run health checks"
    echo ""
    echo "🧹 Maintenance:"
    echo "  clean         Clean up temporary files"
    echo ""
    echo "❓ Help:"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./manage.sh start        # Start both services"
    echo "  ./manage.sh setup-dev    # First time setup"
    echo "  ./manage.sh backend      # Start backend only"
    echo "  ./manage.sh frontend     # Start frontend only"
    echo "  ./manage.sh phase-status # Check system status"
}

# Main command handler
case "$1" in
    start)
        start_all
        ;;
    setup-dev)
        setup_dev
        ;;
    db-setup)
        db_setup
        ;;
    phase-status)
        phase_status
        ;;
    backend)
        backend
        ;;
    frontend)
        frontend
        ;;
    health)
        health_check
        ;;
    clean)
        clean
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
