"""
================================================================================
API FEATURES - APPLICATION CONFIGURATION
================================================================================

Django AppConfig for the api_features application.

This configuration class is automatically loaded when the Django app starts.
It defines metadata about the api_features application.

APPLICATION DETAILS:
  Name: 'api_features'
  Display Name: 'API Features'
  Installation: Add 'api_features' to INSTALLED_APPS in settings.py

FEATURES PROVIDED BY THIS APP:
  - Learning roadmap generation using AI (Groq)
  - Google Calendar integration with OAuth2
  - Autonomous GitHub repository creation
  - Task status tracking for background operations

INITIALIZATION:
The ApiFeaturesConfig class is instantiated automatically by Django.
To customize app behavior, modify this class (e.g., add ready() method).

EXAMPLE CUSTOMIZATION:
  def ready(self):
      import api_features.signals  # Connect signal handlers
      # Run startup code here

DOCUMENTATION:
  - Views: api_features/views.py
  - Routes: api_features/urls.py
  - Models: api_features/models.py

================================================================================
"""

from django.apps import AppConfig


class ApiFeaturesConfig(AppConfig):
    # Application name used in INSTALLED_APPS
    name = 'api_features'
    
    # Human-readable application name (appears in admin interface)
    verbose_name = 'API Features - AI Learning & Repository Generation'
