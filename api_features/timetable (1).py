"""
================================================================================
TIMETABLE & CALENDAR UTILITIES
================================================================================

Legacy calendar utilities for task scheduling and event management.

⚠️  DEPRECATION NOTICE:
This module contains legacy/experimental code. The primary calendar integration
is now handled by the google_calendar_integration module in views.py.

LEGACY FUNCTIONS:
  get_calendar_service()       - Authenticate and get Google Calendar API client
  add_tasks_to_calendar()      - Parse task dictionary and add to calendar

CURRENT STATUS:
This file is preserved for reference but may contain outdated patterns.
For new calendar functionality, use the functions in views.py:
  - get_calendar_service(request)
  - add_roadmap_to_calendar(roadmap_data, start_date, request)
  - oauth_callback(request)

DEPENDENCIES:
  - google-auth
  - google-auth-oauthlib
  - google-auth-httplib2
  - google-api-python-client

DIFFERENCES FROM CURRENT IMPLEMENTATION:
  OLD: InstalledAppFlow (desktop app OAuth)
  NEW: Flow (web app OAuth with browser-based login)
  
  OLD: Stores token.json in current directory
  NEW: Stores token.json in api_features folder with secure handling

MIGRATION GUIDE:
If code depends on this module:
  1. Replace imports with views.py functions
  2. Update OAuth flow to use request object
  3. Update error handling to use new exception formats
  4. Test with web-based OAuth (popup window)

================================================================================
"""

import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OAuth scopes for calendar access
# If modifying these scopes, delete the file token.json to force re-authentication
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    LEGACY FUNCTION - Use views.py version instead
    
    Get authenticated Google Calendar API service using InstalledAppFlow.
    
    AUTHENTICATION FLOW:
      1. Check if token.json exists and is valid
      2. If token exists and expired: attempt refresh
      3. If no token: start OAuth flow with local server
      4. Save token to token.json for future use
    
    RETURNS:
      googleapiclient.discovery.Resource: Authenticated calendar service
    
    RAISES:
      google.auth.exceptions.RefreshError: If token refresh fails
      FileNotFoundError: If credentials.json not found
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def add_tasks_to_calendar(plan_dict):
    """
    LEGACY FUNCTION - Use views.py version instead
    
    Parse task plan dictionary and add events to Google Calendar.
    
    EXPECTED INPUT FORMAT:
      {
        "Day 1": "Task 1, Task 2, Task 3",
        "Day 2": "Task 1, Task 2",
        ...
      }
    
    PROCESSING:
      1. Get calendar service
      2. For each day in plan_dict:
         - Parse comma-separated tasks
         - Create calendar event
         - Set reminders
    
    PARAMETERS:
      plan_dict (dict): Dictionary mapping day labels to task strings
    
    BEHAVIOR:
      Creates Google Calendar events for each day
      (Implementation incomplete in this legacy version)
    """
        
        # Calculate date (starting from today)
        day_buffer = int(day_label.split()[1]) 