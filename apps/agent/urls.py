"""
GitHub Agent URL Configuration
"""

from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    path('run_agent/', views.run_agent_endpoint, name='run_agent'),
    path('run_agent_status/<str:task_id>/', views.run_agent_status, name='run_agent_status'),
]
