"""
================================================================================
SKILLFORGE - DJANGO CONFIGURATION SETTINGS
================================================================================

Django configuration for the SkillForge project (formerly MalumAI).

This is the restructured configuration with proper separation of concerns:
- Environment variables for secrets and configuration
- Modular app structure (roadmap, calendar, agent, core)
- Security best practices for production
- Database abstraction

DOCUMENTATION:
- Full settings reference: https://docs.djangoproject.com/en/6.0/ref/settings/
- Deployment checklist: https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

ENVIRONMENT VARIABLES REQUIRED:
  DEBUG, SECRET_KEY, ALLOWED_HOSTS (see .env.example)
  GROQ_API_KEY, GROQ_AGENT_KEY
  GITHUB_TOKEN, GITHUB_USERNAME
  DATABASE_ENGINE, DATABASE_NAME

================================================================================
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY SETTINGS (Load from environment)
# ============================================================================

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-dev-only-change-in-production'
)

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ============================================================================
# APPLICATION DEFINITION
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # SkillForge Apps (modular structure)
    'apps.roadmap',
    'apps.calendar',
    'apps.agent',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================================
# DATABASE
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': BASE_DIR / os.getenv('DATABASE_NAME', 'db.sqlite3'),
    }
}

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC FILES
# ============================================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ============================================================================
# API CONFIGURATION (Load from environment)
# ============================================================================

# Groq API Keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_AGENT_KEY = os.getenv('GROQ_AGENT_KEY', '')

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', '')

# Google Calendar Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')

# ============================================================================
# GOOGLE CALENDAR API SCOPES
# ============================================================================

CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']

# Credential paths
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'config', 'credentials', 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'config', 'credentials', 'token.json')
