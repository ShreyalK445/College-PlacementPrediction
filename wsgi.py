"""
WSGI entry point for production deployment with Gunicorn.

Usage:
    gunicorn wsgi:application -c gunicorn.conf.py
"""

from app import create_app

application = create_app()
