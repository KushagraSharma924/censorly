# Production Dockerfile for Censorly Backend - Render Compatible
FROM python:3.9-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app_supabase.py \
    FLASK_ENV=production

# Install system dependencies (including libmagic for file validation)
RUN apt-get update && apt-get install -y \
    curl \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads processed logs

# Health check (use dynamic PORT)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Expose port dynamically (Render sets PORT env var)
EXPOSE ${PORT:-10000}

# Use our Docker-specific startup script
CMD ["python", "start_docker.py"]