from django.urls import path
from . import views

app_name = 'api_features'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('add_to_calendar/', views.add_to_calendar, name='add_to_calendar'),
    path('run_agent/', views.run_agent_endpoint, name='run_agent'),
    path('run_agent_status/<str:task_id>/', views.run_agent_status, name='run_agent_status'),
    path('results/', views.results, name='results'),
]
