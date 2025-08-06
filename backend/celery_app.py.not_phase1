#!/usr/bin/env python
"""
Celery application entry point.
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.celery_worker import celery

if __name__ == '__main__':
    celery.start()
