from django.urls import path
from . import views

app_name = 'api_features'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('results/', views.results, name='results'),
]
