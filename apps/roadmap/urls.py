"""
Roadmap URL Configuration
"""

from django.urls import path
from . import views

app_name = 'roadmap'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('results/', views.results, name='results'),
]
