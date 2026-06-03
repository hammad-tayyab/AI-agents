"""
SkillForge - Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.roadmap.urls')),
    path('', include('apps.calendar.urls')),
    path('', include('apps.agent.urls')),
]
