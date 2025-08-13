# Phase 1 Dockerfile for AI Profanity Filter - Render Optimized (258MB)
FROM python:3.9-slim

# Set environment variables for Render
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app_supabase.py \
    FLASK_ENV=production \
    PORT=10000

# Install system dependencies (including libmagic for file validation)
RUN apt-get update && apt-get install -y \
    curl \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

    # Copy requirements file
    COPY requirements-phase1.txt .
    
    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements-phase1.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads processed logs

# Health check for Render
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port (Render uses 10000 by default)
EXPOSE $PORT

# Run with Gunicorn optimized for Render
    # Start the application
    CMD ["sh", "start.sh"]