"""
================================================================================
API FEATURES - PACKAGE INITIALIZATION
================================================================================

Package initialization file for the api_features Django application.

PACKAGE STRUCTURE:
  api_features/
    ├── __init__.py              (This file - package marker)
    ├── apps.py                  (Django app configuration)
    ├── models.py                (Database models/ORM)
    ├── views.py                 (Request handlers and business logic)
    ├── urls.py                  (URL routing configuration)
    ├── admin.py                 (Django admin customization)
    ├── tests.py                 (Unit tests)
    ├── setup_credentials.py      (Google OAuth setup utility)
    ├── timetable (1).py          (Scheduling/calendar utilities)
    ├── credentials.json          (Google OAuth credentials)
    ├── token.json                (Google OAuth access tokens)
    ├── templates/                (HTML templates)
    │   └── api_features/
    │       └── index.html
    └── migrations/               (Database schema migrations)

IMPORTS:
You can import application components from this package:
  from api_features.views import index, generate_roadmap
  from api_features.models import YourModel

APPLICATION REGISTRATION:
Add this app to Django settings.py:
  INSTALLED_APPS = [
      ...
      'api_features.apps.ApiFeaturesConfig',  # or just 'api_features'
  ]

DEFAULT APP CONFIG:
Django will use ApiFeaturesConfig as the default configuration.

================================================================================
"""
