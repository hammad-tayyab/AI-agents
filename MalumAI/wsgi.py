"""
================================================================================
MALUMIA - WSGI APPLICATION CONFIGURATION
================================================================================

WSGI (Web Server Gateway Interface) configuration for production deployment.

WHAT IS WSGI?
WSGI is a Python standard for how web servers communicate with Python web
applications. It defines the interface between a web server and Django.

PURPOSE:
This module exposes a WSGI-compatible callable that production web servers
(Gunicorn, uWSGI, Apache+mod_wsgi) can use to run the Django application.

CURRENT SETUP:
  - Loads Django settings from MalumAI.settings
  - Creates WSGI application instance
  - Application is ready for deployment

PRODUCTION DEPLOYMENT:
When deploying to production, use this WSGI application with a web server:

  Gunicorn Example:
    gunicorn MalumAI.wsgi:application --bind 0.0.0.0:8000

  uWSGI Example:
    uwsgi --http :8000 --module MalumAI.wsgi:application

  Apache + mod_wsgi:
    WSGIScriptAlias / /path/to/MalumAI/wsgi.py

DEVELOPMENT vs PRODUCTION:
  Development:  python manage.py runserver (uses development server)
  Production:   Gunicorn/uWSGI serving WSGI application

ENVIRONMENT MANAGEMENT:
The DJANGO_SETTINGS_MODULE environment variable tells Django which
settings file to use. It's required and automatically set here.

For production with different settings:
  export DJANGO_SETTINGS_MODULE=MalumAI.settings.production
  gunicorn MalumAI.wsgi:application

SECURITY:
- DEBUG must be False in production
- Use environment variables for sensitive data
- Configure allowed hosts correctly
- Use HTTPS
- Set secure cookie flags

ADDITIONAL RESOURCES:
  Django WSGI docs: https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
  Gunicorn: https://gunicorn.org/
  uWSGI: https://uwsgi-docs.readthedocs.io/

================================================================================
"""

"""
WSGI config for MalumAI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MalumAI.settings')

application = get_wsgi_application()
