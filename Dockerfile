# Phase 1 Dockerfile for AI Profanity Filter - Render Optimized (258MB)
FROM python:3.9-slim

# Set environment variables for Render
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app_supabase.py \
    FLASK_ENV=production \
    PORT=10000

# Install system dependencies (minimal for Phase 1 - no ML compilation needed)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements file from backend directory
COPY backend/requirements-phase1.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-phase1.txt

# Copy backend application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p uploads processed logs

# Health check for Render
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Install curl for healthcheck (already done earlier, but making sure)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Expose port (Render uses 10000 by default)
EXPOSE $PORT

# Make sure startup script is executable
RUN chmod +x start.sh

# Start the application in debug mode for Render deployment troubleshooting
CMD ["sh", "start.sh"]
