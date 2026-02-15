"""
================================================================================
MALUMIA - PROJECT PACKAGE INITIALIZATION
================================================================================

Package initialization file for the MalumAI Django project.

PROJECT STRUCTURE:
  MalumAI/                     (Project package - site-wide configuration)
    ├── __init__.py            (This file)
    ├── settings.py            (Django configuration)
    ├── urls.py                (Root URL routing)
    ├── views.py               (Project-level views)
    ├── wsgi.py                (WSGI application for production)
    ├── asgi.py                (ASGI application for async)
    └── __pycache__/           (Compiled Python cache)

  api_features/                (Django app with core features)
  
  manage.py                    (Django management utility)
  db.sqlite3                   (Development database)

WHAT IS THIS PROJECT?
MalumAI is a Django-based web application that:
  - Generates personalized learning roadmaps using AI (Groq)
  - Integrates with Google Calendar for event scheduling
  - Creates GitHub repositories with starter code automatically
  - Tracks long-running background tasks

GETTING STARTED:

  1. Install dependencies:
     pip install -r requirements.txt

  2. Run migrations:
     python manage.py migrate

  3. Start development server:
     python manage.py runserver

  4. Visit http://localhost:8000/api/

KEY COMPONENTS:

  settings.py
    - Database configuration
    - Installed apps
    - Middleware
    - API keys and credentials
    - Static files settings

  urls.py
    - Root URL routing
    - Links to app-specific URL configs

  wsgi.py
    - Production deployment with synchronous servers (Gunicorn)

  asgi.py
    - Production deployment with async servers (Daphne, Hypercorn)

IMPORTANT IMPORTS:
This file can be used to initialize project-wide configurations:

  # Example: Initialize Celery for task queue
  from celery import Celery
  app = Celery('MalumAI')

DJANGO CLI COMMANDS:
  python manage.py runserver          - Start dev server
  python manage.py migrate            - Apply database migrations
  python manage.py makemigrations     - Create migration files
  python manage.py createsuperuser    - Create admin account
  python manage.py shell              - Interactive Python with Django context
  python manage.py collectstatic      - Collect static files for production

PRODUCTION CHECKLIST:
  ☐ Set DEBUG = False in settings.py
  ☐ Change SECRET_KEY to a secure value
  ☐ Configure ALLOWED_HOSTS with production domains
  ☐ Set up proper database (PostgreSQL recommended)
  ☐ Configure static file serving (Whitenoise, CloudFront, etc.)
  ☐ Set up HTTPS/SSL certificates
  ☐ Configure CSRF and CORS properly
  ☐ Use environment variables for sensitive data
  ☐ Set up proper logging
  ☐ Enable security middleware (SECURE_* settings)

DOCUMENTATION:
  Django Docs: https://docs.djangoproject.com/
  Project README: README.md
  Setup Guide: SETUP_GUIDE.md

VERSION: 1.0
CREATED: February 2026

================================================================================
"""
