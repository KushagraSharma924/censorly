#!/bin/bash

# Phase 1 startup script - Simple Flask + Frontend only
cd backend && python3 app.py &
cd frontend && npm run dev &
# Celery disabled for Phase 1 - will be enabled in later phases
# cd backend && celery -A celery_app worker --loglevel=info &

wait
