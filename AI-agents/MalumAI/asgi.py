"""
================================================================================
MALUMIA - ASGI APPLICATION CONFIGURATION
================================================================================

ASGI (Asynchronous Server Gateway Interface) configuration for async deployment.

WHAT IS ASGI?
ASGI is a newer standard than WSGI that supports asynchronous Python web
applications. It enables real-time features like WebSockets and long-polling.

PURPOSE:
This module exposes an ASGI-compatible callable for async web servers.

CURRENT SETUP:
  - Loads Django settings from MalumAI.settings
  - Creates ASGI application instance
  - Application is ready for async-capable servers

WSGI vs ASGI:

  WSGI (Synchronous):
    - Traditional request/response model
    - Simpler but blocks on I/O operations
    - Good for most applications
    - Used by: Gunicorn (default), uWSGI

  ASGI (Asynchronous):
    - Supports async/await Python syntax
    - Handles WebSockets and HTTP/2
    - Better performance for I/O-heavy applications
    - Used by: Daphne, Hypercorn, Uvicorn

WHEN TO USE ASGI:
  ✓ Real-time features needed (notifications, chat)
  ✓ WebSocket support required
  ✓ High-concurrency scenarios (thousands of connections)
  ✓ Task queues with background workers
  
  ✗ Simple CRUD applications (use WSGI instead)

CURRENT APPLICATION STATUS:
The MalumAI application uses synchronous views and doesn't require async.
Using WSGI with Gunicorn is sufficient for current needs.

ENABLING ASYNC (Future):
To use ASGI in your views, install a channel layer and define async views:

  pip install channels channels-redis

  In settings.py:
    INSTALLED_APPS += ['daphne']
    ASGI_APPLICATION = 'MalumAI.asgi.application'

  In views.py:
    async def async_view(request):
        # async code here
        return JsonResponse({'data': 'response'})

PRODUCTION DEPLOYMENT WITH ASGI:

  Daphne (recommended for Django):
    daphne -b 0.0.0.0 -p 8000 MalumAI.asgi:application

  Hypercorn:
    hypercorn MalumAI.asgi:application --bind 0.0.0.0:8000

  Uvicorn:
    uvicorn MalumAI.asgi:application --host 0.0.0.0 --port 8000

ADDITIONAL RESOURCES:
  Django ASGI docs: https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
  Django Channels: https://channels.readthedocs.io/
  Daphne: https://github.com/django/daphne

================================================================================
"""

"""
ASGI config for MalumAI project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MalumAI.settings')

application = get_asgi_application()
