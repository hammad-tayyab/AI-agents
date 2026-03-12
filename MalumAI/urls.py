"""
================================================================================
MALUMIA - PROJECT URL ROUTING CONFIGURATION
================================================================================

Root URL configuration for the MalumAI Django project.

ROUTE STRUCTURE:
  /                    - Home page (redirects to /api/)
  /admin/              - Django admin interface
  /api/                - API Features app routes (roadmap, calendar, agent)

url patterns are processed in order: first match wins.

MAIN ROUTES:

  Django Admin:
    /admin/                     - Admin login and interface
    Requires superuser credentials

  API Features App (api_features/urls.py):
    /api/                       - Homepage/form
    /api/generate_roadmap/      - AI roadmap generation
    /api/add_to_calendar/       - Google Calendar integration
    /api/oauth_callback/        - OAuth validation
    /api/run_agent/             - GitHub repo creation
    /api/run_agent_status/<id>/ - Task status polling
    /api/results/               - Results display

REQUEST FLOW:
  User request → URL patterns matching (top to bottom) → View function
  → Response

URL NAMESPACE:
  Use reverse() function to generate URLs dynamically:
  
  from django.urls import reverse
  url = reverse('api_features:generate_roadmap')
  # Returns: '/api/generate_roadmap/'

ADDING NEW ROUTES:
  1. Define view in api_features/views.py
  2. Add to api_features/urls.py
  3. Include in this file (already done)
  4. No changes needed to this file

TRAILING SLASHES:
  All urls use path() which handles trailing slashes flexibly.
  Both /api/ and /api are valid by default.

DOCUMENTATION:
  Django URL dispatcher: https://docs.djangoproject.com/en/6.0/topics/http/urls/
  URL patterns: https://docs.djangoproject.com/en/6.0/ref/urls/

================================================================================
"""

"""
URL configuration for MalumAI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api_features.urls')),
]
