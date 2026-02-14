from django.urls import path
from . import views

app_name = 'api_features'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('run_agent/', views.run_agent_endpoint, name='run_agent'),
    path('results/', views.results, name='results'),
]
