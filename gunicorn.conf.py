"""
Gunicorn configuration for production deployment.

Usage:
    gunicorn wsgi:application -c gunicorn.conf.py
"""

import multiprocessing
import os

# Server socket
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"

# Worker processes — rule of thumb: (2 × CPU cores) + 1
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"           # stdout
errorlog = "-"            # stderr
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Restart workers periodically to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Preload app for faster worker spawning
preload_app = True

# Graceful restart
graceful_timeout = 30
