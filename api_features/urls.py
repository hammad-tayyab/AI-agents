"""
================================================================================
API FEATURES - URL ROUTING CONFIGURATION
================================================================================

URL Configuration for the api_features Django application.

ROUTE DESCRIPTION:

Homepage & Core Features:
  / (GET)                      - Display the main input form and dashboard
  generate_roadmap/ (POST)     - Generate AI-powered learning roadmap
  results/ (GET)               - Display results from roadmap generation

Calendar Integration:
  add_to_calendar/ (POST)      - Add generated roadmap to Google Calendar
  oauth_callback/ (GET)        - OAuth2 callback handler for Google auth

Agent & Repository Creation:
  run_agent/ (POST)            - Trigger autonomous GitHub repository creation
  run_agent_status/ (GET)      - Poll status of background agent task

URL NAMESPACE: 'api_features'
Used for reverse URL lookups: reverse('api_features:generate_roadmap')

DEPLOYMENT CONSIDERATIONS:
- All POST endpoints require CSRF token
- OAuth callback must match Google Cloud Console redirect URIs
- Task status polling should use reasonable intervals (2-5 seconds)

================================================================================
"""

from django.urls import path
from . import views

app_name = 'api_features'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('add_to_calendar/', views.add_to_calendar, name='add_to_calendar'),
    path('oauth_callback/', views.oauth_callback, name='oauth_callback'),
    path('run_agent/', views.run_agent_endpoint, name='run_agent'),
    path('run_agent_status/<str:task_id>/', views.run_agent_status, name='run_agent_status'),
    path('results/', views.results, name='results'),
]
