#!/bin/bash

cd backend && python3 app.py &
cd frontend && npm run dev &
cd backend && celery -A celery_app worker --loglevel=info &

wait
