"""
================================================================================
MALUM AI - API FEATURES VIEWS MODULE
================================================================================

Primary Views Module for the MalumAI Application

OVERVIEW:
This module contains all Django views and functions for the MalumAI platform,
which provides intelligent learning roadmap generation, Google Calendar 
integration, and autonomous GitHub repository creation.

KEY COMPONENTS:

1. ROADMAP GENERATION
   - generate_roadmap(): AI-powered learning roadmap generation using Groq API
   - Processes user skills, interests, and goals to create personalized paths

2. GOOGLE CALENDAR INTEGRATION
   - OAuth2 flow handling for GitHub-compatible web authentication
   - Automatic event creation from roadmaps (weekly tasks, daily reminders, projects)
   - Secure token storage and credential management
   - Callback handler for OAuth response processing

3. AUTONOMOUS AGENT (GitHub Repository Creator)
   - Runs in background threads to create GitHub repositories
   - Generates starter code and README files using AI
   - Integrates project creation with user roadmaps

4. UTILITIES AND HELPERS
   - Task status tracking for long-running operations
   - Error handling and validation
   - CSRF protection and security measures

DEPENDENCIES:
- Django (web framework)
- Groq (large language model API)
- Google Auth Libraries (OAuth2 authentication)
- Google API Client (Calendar API)
- GitHub API (repository management)
- threading (background task execution)

AUTHORS: MalumAI Team
LAST UPDATED: February 2026

================================================================================
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
from django.conf import settings
import json
import re
from groq import Groq
import os
import requests
import base64
import time
from dotenv import load_dotenv
import threading
import uuid
import traceback

load_dotenv()

# ============================================================================
# CONFIGURATION - Paths & API Keys
# ============================================================================

# ✅ FIXED: Credential paths now point to config/credentials/ after reorganization
CREDENTIALS_PATH = os.path.join(settings.BASE_DIR, 'config', 'credentials', 'credentials.json')
TOKEN_PATH = os.path.join(settings.BASE_DIR, 'config', 'credentials', 'token.json')

# ✅ SECURITY: Move these to your .env file and load with os.getenv()
# In your .env file add:
#   GROQ_API_KEY=gsk_your_key_here
#   GROQ_AGENT_KEY=gsk_your_key_here
#   GITHUB_TOKEN=github_pat_your_token_here
#   GITHUB_USERNAME=YourUsername
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')
GROQ_AGENT_KEY = os.getenv('GROQ_AGENT_KEY', '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')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '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')
USERNAME = os.getenv('GITHUB_USERNAME', 'Sad0Bro')

roadmap_client = Groq(api_key=GROQ_API_KEY)
github_client = Groq(api_key=GROQ_AGENT_KEY)

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# In-memory task store for background GitHub repo creation tasks
TASKS = {}

# ============================================================================
# Google Calendar API scopes
# ============================================================================
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# ✅ FIXED: Added InstalledAppFlow import (was used but never imported)
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build

CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']


# ============================================================================
# Main Views
# ============================================================================

@ensure_csrf_cookie
def index(request):
    """Display the input form"""
    # ✅ FIXED: Updated template path after index.html was moved to top-level templates/
    return render(request, 'index.html')


@require_http_methods(["POST"])
def generate_roadmap(request):
    """
    API endpoint that takes skill, interest, and goal as input
    Returns a personalized learning roadmap with projects and timeline
    """
    try:
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body: ' + str(e)
            }, status=400)

        skillset = data.get('skillset', '').strip()
        interest = data.get('interest', '').strip()
        goal = data.get('goal', '').strip()

        if not skillset or not interest:
            return JsonResponse({
                'success': False,
                'error': 'Skillset and Interest fields are required'
            }, status=400)

        prompt = f"""Based on the following user profile, create a detailed learning roadmap:

Current Skillset: {skillset}
Area of Interest: {interest}
Learning Goal: {goal if goal else 'General learning and skill development'}

Must provide:
1. A personalized learning path with 5-7 key milestones
2. 3-5 practical projects the user should complete (with project names and brief descriptions)
3. An estimated timeline in weeks for each project
4. Resources and tech stack recommendations
5. A weekly schedule/timetable for the next 12 weeks

Strictly Format the response as structured JSON with the following keys:
- "roadmap" (array of milestones) - Note: use "roadmap" key, not "milestone"
- "projects" (array of projects with name, description, duration_weeks, tech_stack)
- "weekly_schedule" (array of 12 weeks with tasks)
- "resources" (array of recommended resources)
- "summary" (brief overview of the plan)
- dont respond with anything else, just the plain json format, no ``` at the end or start
"""

        try:
            response = roadmap_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert learning roadmap creator. Provide structured, practical, and achievable learning plans. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8000
            )

            gpt_response = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason if response.choices else None

            if not gpt_response:
                return JsonResponse({
                    'success': False,
                    'error': 'Empty response from AI model'
                }, status=500)

            # Clean the response - remove markdown code blocks if present
            cleaned_response = gpt_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            try:
                result = json.loads(cleaned_response)
                if not isinstance(result, dict):
                    raise json.JSONDecodeError("Response is not a JSON object", cleaned_response, 0)

                # Handle field name mismatch
                if 'milestone' in result and 'roadmap' not in result:
                    result['roadmap'] = result.pop('milestone')

            except json.JSONDecodeError as e:
                result = {
                    'summary': cleaned_response[:500] + ('...' if len(cleaned_response) > 500 else ''),
                    'raw_response': cleaned_response,
                    'roadmap': [],
                    'projects': [],
                    'weekly_schedule': [],
                    'resources': [],
                    'parse_error': f'JSON parsing failed: {str(e)}'
                }

            return JsonResponse({'success': True, 'data': result})

        except Exception as api_error:
            error_msg = str(api_error)
            if 'decommissioned' in error_msg.lower():
                return JsonResponse({'success': False, 'error': 'Model is unavailable. Please try again later.'}, status=503)
            elif 'rate_limit' in error_msg.lower():
                return JsonResponse({'success': False, 'error': 'API rate limit exceeded. Please try again in a moment.'}, status=429)
            else:
                return JsonResponse({'success': False, 'error': f'AI API Error: {error_msg}'}, status=500)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)


def results(request):
    """Display the results from the generation"""
    return render(request, 'index.html')  # Redirects to main page since results.html doesn't exist


# ============================================================================
# GitHub Agent
# ============================================================================

@require_http_methods(["POST"])
def run_agent_endpoint(request):
    """
    API endpoint to initialize and run the agent.
    Creates a GitHub repository with AI-generated project files based on roadmap.
    """
    try:
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Invalid JSON body: {str(e)}'}, status=400)

        skillset = data.get('skillset', '').strip()
        interest = data.get('interest', '').strip()
        goal = data.get('goal', '').strip()
        roadmap_data = data.get('roadmap_data', {})
        gpt_response = data.get('gpt_response', '')

        if roadmap_data and not gpt_response:
            gpt_response = json.dumps(roadmap_data)

        if not skillset or not interest:
            return JsonResponse({'success': False, 'error': 'Skillset and Interest fields are required'}, status=400)

        task_id = uuid.uuid4().hex
        TASKS[task_id] = {
            'status': 'in_progress',
            'message': 'Your GitHub Repo is being made please wait..',
            'repo_url': None,
            'error': None
        }

        def _background_run_agent(tid, skill, intr, gl, gpt_resp):
            try:
                repo_url = run_agent(skill, intr, gl, gpt_resp, task_id=tid)
                TASKS[tid]['status'] = 'completed'
                TASKS[tid]['repo_url'] = repo_url
                TASKS[tid]['message'] = 'GitHub repository created successfully!'
            except Exception as bg_e:
                tb = traceback.format_exc()
                TASKS[tid]['status'] = 'failed'
                TASKS[tid]['error'] = tb
                TASKS[tid]['message'] = f'Failed to create GitHub repository: {str(bg_e)}'

        thread = threading.Thread(
            target=_background_run_agent,
            args=(task_id, skillset, interest, goal, gpt_response),
            daemon=True
        )
        thread.start()

        try:
            status_path = reverse('api_features:run_agent_status', args=[task_id])
            status_url = request.build_absolute_uri(status_path)
        except Exception:
            status_url = f'/api/run_agent_status/{task_id}/'

        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'status_url': status_url,
            'message': TASKS[task_id]['message']
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Agent execution failed: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def run_agent_status(request, task_id):
    """Poll the status of a background run_agent task"""
    task = TASKS.get(task_id)
    if not task:
        return JsonResponse({'success': False, 'error': 'Invalid task id'}, status=404)
    return JsonResponse({'success': True, 'task': task})


def get_name(proj):
    """Generate a repository name for the project"""
    response = github_client.chat.completions.create(
        messages=[{"role": "user", "content": f"I am working on a project {proj}, suggest me a short repository name (lowercase, no spaces, use hyphens), don't say anything else just the suggested name"}],
        model="llama-3.3-70b-versatile",
    )
    name = response.choices[0].message.content.strip()
    name = name.lower().replace(' ', '-').replace('_', '-')
    name = re.sub(r'[^a-z0-9-]', '', name)
    return name


def get_project(gpt_response):
    """Extract the first project from GPT roadmap response"""
    if not gpt_response:
        return None

    try:
        roadmap_data = json.loads(gpt_response) if isinstance(gpt_response, str) else gpt_response
        if isinstance(roadmap_data, dict) and 'projects' in roadmap_data:
            projects = roadmap_data['projects']
            if projects and len(projects) > 0:
                first_project = projects[0]
                project_name = first_project.get('name', first_project.get('project_name', ''))
                project_desc = first_project.get('description', '')
                return f"{project_name}: {project_desc}" if project_desc else project_name
    except Exception:
        pass

    response = github_client.chat.completions.create(
        messages=[{"role": "user", "content": f"I asked AI to give me a road map and it gave me {gpt_response}, extract the first recommended project name and description, nothing else"}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content


def get_lang(proj):
    """Get programming language extension for the project"""
    response = github_client.chat.completions.create(
        messages=[{"role": "user", "content": f"{proj} is a project i want to work on, don't say anything else just give me the extension of the language that is going to be used (e.g., py, js, java), give me only one extension without dot"}],
        model="llama-3.3-70b-versatile",
    )
    lang = response.choices[0].message.content.strip()
    lang = lang.replace('.', '').strip()
    return lang


def decide_project(skillset, interest, goal):
    """Generate project idea based on user's profile"""
    prompt = f"Based on the user's skillset ({skillset}), interest ({interest}), and goal ({goal}), suggest a specific project to build. Keep it concise and practical."
    response = github_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content


def decide_starter(proj_req, lang):
    """Generate starter code for the project"""
    response = github_client.chat.completions.create(
        messages=[{"role": "user", "content": f"following is the project requirement: \n {proj_req} \n don't respond anything else, just give me a starter code for the project in {lang}, don't include features, just a basic structure and dont include ```{lang} at start or end"}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content


def decide_readme(proj_req, lang):
    """Generate a professional README for the project"""
    response = github_client.chat.completions.create(
        messages=[{"role": "user", "content": f"""You are an expert software engineer and technical writer.

Write a complete, professional GitHub README.md file based on the following inputs:

Project Requirements: {proj_req}
Programming Language: {lang}

REQUIREMENTS

The README must include these sections in this exact order:

Project Title, Description, Features, Tech Stack, Installation Instructions,
Usage Examples, Project Structure, Configuration (if applicable),
Testing Instructions (if applicable), Future Improvements,
Contributing Guidelines, License

STYLE RULES

Make the README realistic and tailored to the project requirements.
Assume the reader is a developer who wants to run the project.
Include example commands and code snippets when helpful.
Use clear markdown formatting with headings and bullet points.
If information is missing, make reasonable assumptions.
Do NOT include explanations outside the README content.

OUTPUT RULES

Return ONLY the README content in markdown format.
Do NOT add commentary before or after.
Do NOT use code block fences around the entire README."""}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content


def create_repository(repo_name, description):
    """Create a new GitHub repository"""
    url = "https://api.github.com/user/repos"
    data = {"name": repo_name, "description": description, "private": False}

    print(f"\nCreating repository: {repo_name}")
    response = requests.post(url, headers=HEADERS, json=data, timeout=20)
    if response.status_code == 201:
        print("SUCCESS: Repository created")
        return True
    elif response.status_code == 422:
        print("Repository already exists")
        return True
    return False


def create_file(repo_name, file_name, content, retries=3):
    """Create a file in the GitHub repository"""
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents/{file_name}"
    encoded_content = base64.b64encode(content.encode()).decode()
    data = {"message": f"Create {file_name}", "content": encoded_content}

    for attempt in range(retries):
        print(f"Creating file: {file_name} (Attempt {attempt + 1})")
        response = requests.put(url, headers=HEADERS, json=data, timeout=30)

        if response.status_code in [200, 201]:
            print(f"SUCCESS: {file_name} created")
            return True
        else:
            print(f"FAILED: Status {response.status_code}")

        time.sleep(0.2)
    return False


def run_agent(skillset, interest, goal, gpt_response='', task_id=None):
    """
    Main agent function that creates a GitHub repository with project files.
    """
    try:
        if gpt_response:
            proj = get_project(gpt_response)
            if not proj:
                proj = decide_project(skillset, interest, goal)
        else:
            proj = decide_project(skillset, interest, goal)

        if task_id:
            TASKS[task_id]['message'] = 'Decided project, determining language and repo name...'

        lang = get_lang(proj)
        repo_base_name = get_name(proj)
        repo_name = f"{repo_base_name}-{int(time.time())}"
        repo_url = f"https://github.com/{USERNAME}/{repo_name}"

        if create_repository(repo_name, f"AI Agent Project - {interest}"):
            if task_id:
                TASKS[task_id]['message'] = 'Repository created, generating files...'
            time.sleep(5)

            lang_ext = lang.strip()
            if not lang_ext.startswith('.'):
                lang_ext = '.' + lang_ext

            if task_id:
                TASKS[task_id]['message'] = 'Generating README and starter code...'

            readme_content = decide_readme(proj, lang)
            starter_content = decide_starter(proj, lang)

            files = {
                "README.md": readme_content,
                f"main{lang_ext}": starter_content
            }

            for file_name, file_content in files.items():
                if task_id:
                    TASKS[task_id]['message'] = f'Creating file {file_name}...'
                if create_file(repo_name, file_name, file_content):
                    time.sleep(1)
                else:
                    print(f"WARNING: Failed to create {file_name}")
                    if task_id:
                        TASKS[task_id]['message'] = f'Failed to create file {file_name}'

            if task_id:
                TASKS[task_id]['message'] = 'Finalizing repository and finishing up...'
            print(f"\nAGENT COMPLETE: {repo_url}")
            return repo_url
        else:
            raise Exception("Failed to create repository")

    except Exception as e:
        print(f"ERROR in run_agent: {str(e)}")
        if task_id:
            TASKS[task_id]['status'] = 'failed'
            TASKS[task_id]['error'] = traceback.format_exc()
            TASKS[task_id]['message'] = f'Error: {str(e)}'
        raise


# ============================================================================
# Google Calendar Integration
# ============================================================================

def get_calendar_service(request=None):
    """
    Get authenticated Google Calendar service.
    ✅ FIXED: Uses centralized CREDENTIALS_PATH and TOKEN_PATH constants.
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, CALENDAR_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        else:
            if request:
                return initiate_oauth_flow(request)
            else:
                return get_calendar_service_local()

    return build('calendar', 'v3', credentials=creds)


def get_calendar_service_local():
    """
    Fallback method using local server OAuth flow.
    ✅ FIXED: Uses centralized CREDENTIALS_PATH and TOKEN_PATH constants.
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, CALENDAR_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Google OAuth credentials file not found at {CREDENTIALS_PATH}. "
                    "Please ensure credentials.json exists in config/credentials/."
                )
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, CALENDAR_SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as oauth_error:
                error_msg = str(oauth_error)
                if 'access_denied' in error_msg or '403' in error_msg or 'verification' in error_msg.lower():
                    raise Exception(
                        "Google OAuth Access Denied: Your app is in testing mode.\n\n"
                        "SOLUTION: Add yourself as a test user:\n"
                        "1. Go to: https://console.cloud.google.com/apis/credentials/consent\n"
                        "2. Scroll to 'Test users' section\n"
                        "3. Click '+ ADD USERS'\n"
                        "4. Add your Google email address\n"
                        "5. Click 'SAVE' and wait 1-2 minutes, then try again"
                    )
                raise

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def initiate_oauth_flow(request):
    """
    Initiate the OAuth flow for web applications.
    ✅ FIXED: Uses centralized CREDENTIALS_PATH constant.
    """
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Google OAuth credentials file not found at {CREDENTIALS_PATH}."
        )

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=CALENDAR_SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('api_features:oauth_callback'))
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    request.session['oauth_state'] = state
    request.session['oauth_flow'] = True

    return authorization_url


@require_http_methods(["GET"])
def oauth_callback(request):
    """
    Handle OAuth callback from Google.
    ✅ FIXED: Uses centralized CREDENTIALS_PATH and TOKEN_PATH constants.
    """
    try:
        if not os.path.exists(CREDENTIALS_PATH):
            return JsonResponse({'success': False, 'error': 'Credentials file not found'}, status=500)

        state = request.session.get('oauth_state')
        if not state or state != request.GET.get('state'):
            return JsonResponse({'success': False, 'error': 'Invalid OAuth state'}, status=400)

        flow = Flow.from_client_secrets_file(
            CREDENTIALS_PATH,
            scopes=CALENDAR_SCOPES,
            redirect_uri=request.build_absolute_uri(reverse('api_features:oauth_callback'))
        )

        flow.fetch_token(code=request.GET.get('code'))

        creds = flow.credentials
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

        del request.session['oauth_state']
        del request.session['oauth_flow']

        return redirect(reverse('index') + '?oauth_success=1')

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'OAuth callback failed: {str(e)}'}, status=500)


def add_roadmap_to_calendar(roadmap_data, start_date=None, request=None):
    """
    Add roadmap tasks to Google Calendar.
    """
    try:
        service = get_calendar_service(request)

        # Check if OAuth flow was initiated (returns URL string)
        if isinstance(service, str) and service.startswith('http'):
            return {
                'success': False,
                'oauth_url': service,
                'message': 'OAuth authentication required'
            }

        created_events = []

        if start_date is None:
            start_date = datetime.date.today()

        # Add weekly schedule events
        if roadmap_data.get('weekly_schedule') and isinstance(roadmap_data['weekly_schedule'], list):
            for week_idx, week_data in enumerate(roadmap_data['weekly_schedule'][:12]):
                week_num = week_idx + 1
                week_start = start_date + datetime.timedelta(weeks=week_idx)

                if isinstance(week_data, str):
                    week_content = week_data
                elif isinstance(week_data, dict):
                    week_content = week_data.get('tasks', week_data.get('description', ''))
                else:
                    week_content = str(week_data)

                weekly_event = {
                    'summary': f'📚 Week {week_num}: Learning Tasks - Skill Development',
                    'description': f'Time to work on your skills!\n\n{week_content}\n\n💡 Remember: Consistency is key to mastering new skills!',
                    'start': {'date': week_start.isoformat(), 'timeZone': 'UTC'},
                    'end': {'date': (week_start + datetime.timedelta(days=6)).isoformat(), 'timeZone': 'UTC'},
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 60},
                        ],
                    },
                }

                created_event = service.events().insert(calendarId='primary', body=weekly_event).execute()
                created_events.append(created_event.get('id'))

                # Daily reminders Monday-Friday
                for day_offset in range(5):
                    learning_day = week_start + datetime.timedelta(days=day_offset)
                    day_name = learning_day.strftime('%A')

                    daily_event = {
                        'summary': f'📖 Daily Learning: Week {week_num} - {day_name}',
                        'description': f'Daily skill development reminder!\n\nFocus for today:\n{week_content}\n\n⏰ Set aside time today to work on your learning goals.',
                        'start': {'date': learning_day.isoformat(), 'timeZone': 'UTC'},
                        'end': {'date': learning_day.isoformat(), 'timeZone': 'UTC'},
                        'colorId': '5',
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'email', 'minutes': 24 * 60},
                                {'method': 'email', 'minutes': 60},
                                {'method': 'popup', 'minutes': 30},
                                {'method': 'popup', 'minutes': 0},
                            ],
                        },
                    }

                    created_daily = service.events().insert(calendarId='primary', body=daily_event).execute()
                    created_events.append(created_daily.get('id'))

        # Add project milestone events
        if roadmap_data.get('projects') and isinstance(roadmap_data['projects'], list):
            current_week = 0
            for project in roadmap_data['projects']:
                project_name = project.get('name', project.get('project_name', 'Project'))
                duration = project.get('duration_weeks', project.get('duration', 1))

                try:
                    if isinstance(duration, str):
                        duration = int(duration.split()[0]) if duration.split()[0].isdigit() else 1
                    else:
                        duration = int(duration)
                except Exception:
                    duration = 1

                project_start = start_date + datetime.timedelta(weeks=current_week)
                project_end = project_start + datetime.timedelta(weeks=duration)

                project_description = project.get('description', '')
                tech_stack = project.get('tech_stack', [])
                tech_str = ', '.join(tech_stack) if isinstance(tech_stack, list) else str(tech_stack)

                event = {
                    'summary': f'🚀 Project: {project_name}',
                    'description': f'Project Milestone: {project_name}\n\n{project_description}\n\n{"Tech Stack: " + tech_str if tech_str else ""}\n\n💪 Stay focused and complete this project!',
                    'start': {'date': project_start.isoformat(), 'timeZone': 'UTC'},
                    'end': {'date': project_end.isoformat(), 'timeZone': 'UTC'},
                    'colorId': '10',
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'email', 'minutes': 2 * 60},
                            {'method': 'popup', 'minutes': 60},
                            {'method': 'popup', 'minutes': 15},
                        ],
                    },
                }

                created_event = service.events().insert(calendarId='primary', body=event).execute()
                created_events.append(created_event.get('id'))
                current_week += duration

        return {
            'success': True,
            'events_created': len(created_events),
            'event_ids': created_events
        }

    except FileNotFoundError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': f'Failed to add to calendar: {str(e)}'}


@require_http_methods(["POST"])
def add_to_calendar(request):
    """
    API endpoint to add roadmap to Google Calendar.
    """
    try:
        data = json.loads(request.body)
        roadmap_data = data.get('roadmap_data', {})

        if not roadmap_data:
            return JsonResponse({'success': False, 'error': 'roadmap_data is required'}, status=400)

        start_date = None
        if data.get('start_date'):
            try:
                start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except Exception:
                pass

        result = add_roadmap_to_calendar(roadmap_data, start_date, request)

        if result.get('oauth_url'):
            return JsonResponse({
                'success': False,
                'oauth_required': True,
                'oauth_url': result['oauth_url'],
                'message': 'Please authenticate with Google Calendar'
            })
        elif result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Successfully added {result["events_created"]} events to your Google Calendar',
                'events_created': result['events_created']
            })
        else:
            return JsonResponse({'success': False, 'error': result.get('error', 'Unknown error')}, status=500)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)