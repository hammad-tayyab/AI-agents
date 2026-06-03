"""
Google Calendar URL Configuration
"""

from django.urls import path
from . import views

app_name = 'calendar'

urlpatterns = [
    path('add_to_calendar/', views.add_to_calendar, name='add_to_calendar'),
    path('oauth_callback/', views.oauth_callback, name='oauth_callback'),
]
