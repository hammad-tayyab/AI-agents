from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
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

# Configure Groq API key for roadmap generation
GROQ_API_KEY = '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'
roadmap_client = Groq(api_key=GROQ_API_KEY)

@ensure_csrf_cookie
def index(request):
    """Display the input form"""
    return render(request, 'api_features/index.html')

@require_http_methods(["POST"])
def generate_roadmap(request):
    """
    API endpoint that takes skill, interest, and goal as input
    Returns a personalized learning roadmap with projects and timeline
    """
    try:
        # Ensure we received JSON
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
        
        # Validate inputs
        if not skillset or not interest:
            return JsonResponse({
                'success': False,
                'error': 'Skillset and Interest fields are required'
            }, status=400)
        
        # Create the prompt for GPT
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
- dont respond with anything else, just the plain json format, no ''' at the end or start
"""
        
        try:
            # Call Groq API with increased token limit for complete responses
            response = roadmap_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert learning roadmap creator. Provide structured, practical, and achievable learning plans. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8000  # Increased from 2000 to allow complete responses
            )

            gpt_response = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason if response.choices else None
            
            if not gpt_response:
                return JsonResponse({
                    'success': False,
                    'error': 'Empty response from AI model'
                }, status=500)
            
            # Check if response was truncated
            if finish_reason == 'length':
                # Response was cut off due to token limit
                # Note: This shouldn't happen with max_tokens=8000, but we check anyway
                pass  # We'll still return the partial response

            # Clean the response - remove markdown code blocks if present
            cleaned_response = gpt_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            # Try to parse as JSON
            try:
                result = json.loads(cleaned_response)
                # Ensure all expected fields exist
                if not isinstance(result, dict):
                    raise json.JSONDecodeError("Response is not a JSON object", cleaned_response, 0)
                
                # Handle field name mismatch: if "milestone" exists, rename to "roadmap"
                if 'milestone' in result and 'roadmap' not in result:
                    result['roadmap'] = result.pop('milestone')
            except json.JSONDecodeError as e:
                # If response is not valid JSON, try to extract useful information
                # and wrap it in a structured format
                result = {
                    'summary': cleaned_response[:500] + ('...' if len(cleaned_response) > 500 else ''),
                    'raw_response': cleaned_response,  # Store full response for debugging
                    'roadmap': [],
                    'projects': [],
                    'weekly_schedule': [],
                    'resources': [],
                    'parse_error': f'JSON parsing failed: {str(e)}'
                }

            return JsonResponse({
                'success': True,
                'data': result
            })
        
        except Exception as api_error:
            error_msg = str(api_error)
            if 'decommissioned' in error_msg.lower():
                return JsonResponse({
                    'success': False,
                    'error': 'Model is unavailable. Please try again later.'
                }, status=503)
            elif 'rate_limit' in error_msg.lower():
                return JsonResponse({
                    'success': False,
                    'error': 'API rate limit exceeded. Please try again in a moment.'
                }, status=429)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'AI API Error: {error_msg}'
                }, status=500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)

def results(request):
    """Display the results from the generation"""
    return render(request, 'api_features/results.html')

@require_http_methods(["POST"])
def run_agent_endpoint(request):
    """
    API endpoint to initialize and run the agent
    Creates a GitHub repository with AI-generated project files based on roadmap
    """
    try:
        # Get user inputs from request
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON body: {str(e)}'
            }, status=400)
        
        skillset = data.get('skillset', '').strip()
        interest = data.get('interest', '').strip()
        goal = data.get('goal', '').strip()
        
        # Get roadmap data - can be passed directly or extracted from roadmap_data
        roadmap_data = data.get('roadmap_data', {})
        gpt_response = data.get('gpt_response', '')
        
        # If roadmap_data is provided, convert it to JSON string
        if roadmap_data and not gpt_response:
            gpt_response = json.dumps(roadmap_data)
        
        # Validate required fields
        if not skillset or not interest:
            return JsonResponse({
                'success': False,
                'error': 'Skillset and Interest fields are required'
            }, status=400)
        
        # Start the agent in background and return a task id immediately
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

        thread = threading.Thread(target=_background_run_agent, args=(task_id, skillset, interest, goal, gpt_response), daemon=True)
        thread.start()

        # Provide a full status URL so clients can poll for completion
        try:
            status_path = reverse('api_features:run_agent_status', args=[task_id])
            status_url = request.build_absolute_uri(status_path)
        except Exception:
            status_url = f'/api_features/run_agent_status/{task_id}/'

        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'status_url': status_url,
            'message': TASKS[task_id]['message']
        })
    except Exception as e:
        error_msg = str(e)
        return JsonResponse({
            'success': False,
            'error': f'Agent execution failed: {error_msg}'
        }, status=500)


@require_http_methods(["GET"])
def run_agent_status(request, task_id):
    """Poll the status of a background run_agent task"""
    task = TASKS.get(task_id)
    if not task:
        return JsonResponse({'success': False, 'error': 'Invalid task id'}, status=404)
    return JsonResponse({'success': True, 'task': task})


# GitHub Agent Functions (for automated project creation)
# Note: These functions use a separate Groq client instance
load_dotenv()

# GitHub agent configuration
project = "calculator, console based"
language = "py"
github_client = Groq(
    api_key="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",
)
GITHUB_TOKEN = "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"
USERNAME = "Sad0Bro"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# In-memory task store for background GitHub repo creation tasks
TASKS = {}

def get_name(proj):
    """Generate a repository name for the project"""
    response = github_client.chat.completions.create(
                messages=[{"role": "user", "content": f"I am working on a project {proj}, suggest me a short repository name (lowercase, no spaces, use hyphens), don't say anything else just the suggested name"}],
                model="llama-3.3-70b-versatile",
            )
    name = response.choices[0].message.content.strip()
    # Clean up the name: lowercase, replace spaces with hyphens, remove special chars
    name = name.lower().replace(' ', '-').replace('_', '-')
    # Remove any non-alphanumeric except hyphens
    name = re.sub(r'[^a-z0-9-]', '', name)
    return name

def get_project(gpt_response):
    """Extract the first project from GPT roadmap response"""
    if not gpt_response:
        return None
    
    # Try to parse as JSON first
    try:
        roadmap_data = json.loads(gpt_response) if isinstance(gpt_response, str) else gpt_response
        if isinstance(roadmap_data, dict) and 'projects' in roadmap_data:
            projects = roadmap_data['projects']
            if projects and len(projects) > 0:
                first_project = projects[0]
                # Return project name and description
                project_name = first_project.get('name', first_project.get('project_name', ''))
                project_desc = first_project.get('description', '')
                return f"{project_name}: {project_desc}" if project_desc else project_name
    except:
        pass
    
    # Fallback to AI extraction
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
    # Remove any dots or extra characters
    lang = lang.replace('.', '').strip()
    return lang

def decide_project(skillset, interest, goal):
    # Generate project idea based on user's profile
    prompt = f"Based on the user's skillset ({skillset}), interest ({interest}), and goal ({goal}), suggest a specific project to build. Keep it concise and practical."
    response = github_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
    return response.choices[0].message.content

def decide_starter(proj_req, lang):
    response = github_client.chat.completions.create(
            messages=[{"role": "user", "content": f"following is the project requirement: \n {proj_req} \n don't respond anything else, just give me a starter code for the project in {lang}, don't include features, just a basic structure and dont include '''{lang} at start or end"}],
            model="llama-3.3-70b-versatile",
        )
    return response.choices[0].message.content

def decide_readme(proj_req, lang):
    response = github_client.chat.completions.create(
            messages=[{"role": "user", "content": f"""You are an expert software engineer and technical writer.

Write a complete, professional GitHub README.md file based on the following inputs:

Project Requirements: {proj_req}
Programming Language: {lang}

REQUIREMENTS

The README must include these sections in this exact order:

Project Title

Description

Features

Tech Stack

Installation Instructions

Usage Examples

Project Structure

Configuration (if applicable)

Testing Instructions (if applicable)

Future Improvements

Contributing Guidelines

License

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
    url = "https://api.github.com/user/repos"
    data = {"name": repo_name, "description": description, "private": False}
    
    print(f"\nCreating repository: {repo_name}")
    response = requests.post(url, headers=HEADERS, json=data, timeout=20)
    if response.status_code == 201:
        print(f"SUCCESS: Repository created")
        return True
    elif response.status_code == 422:
        print("Repository already exists")
        return True
    return False   

def create_file(repo_name, file_name, content, retries=3):
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
    
    Args:
        skillset: User's current skills
        interest: Area of interest
        goal: Learning goal
        gpt_response: Optional roadmap data from GPT (JSON string or dict)
    
    Returns:
        str: URL of the created repository
    """
    try:
        # Get project details
        if gpt_response:
            proj = get_project(gpt_response)
            if not proj:
                proj = decide_project(skillset, interest, goal)
        else:
            proj = decide_project(skillset, interest, goal)
        if task_id:
            TASKS[task_id]['message'] = 'Decided project, determining language and repo name...'
        
        # Get language and repository name
        lang = get_lang(proj)
        repo_base_name = get_name(proj)
        repo_name = f"{repo_base_name}-{int(time.time())}"
        repo_url = f"https://github.com/{USERNAME}/{repo_name}"

        # Create repository
        if create_repository(repo_name, f"AI Agent Project - {interest}"):
            if task_id:
                TASKS[task_id]['message'] = 'Repository created, generating files...'
            time.sleep(5)  # Short wait for repo to be registered
            
            # Ensure lang has a dot prefix for file extension
            lang_ext = lang.strip()
            if not lang_ext.startswith('.'):
                lang_ext = '.' + lang_ext
            
            # Generate project files
            if task_id:
                TASKS[task_id]['message'] = 'Generating README and starter code...'
            readme_content = decide_readme(proj, lang)
            starter_content = decide_starter(proj, lang)
            
            files = {
                "README.md": readme_content,
                f"main{lang_ext}": starter_content
            }

            # Create files in repository
            for file_name, file_content in files.items():
                if task_id:
                    TASKS[task_id]['message'] = f'Creating file {file_name}...'
                if create_file(repo_name, file_name, file_content):
                    time.sleep(1)  # Small delay between file creations
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
# Google Calendar Integration Functions
# ============================================================================
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Calendar API scopes
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Get authenticated Google Calendar service.
    Handles OAuth2 flow and token refresh automatically.
    """
    # Get the base directory (api_features folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible credential file names
    possible_credential_files = [
        'credentials.json',
        'credintials1.json',  # Handle typo in filename
        'credintials.json',
        'credentials (1).json'
    ]
    
    credentials_path = None
    for cred_file in possible_credential_files:
        test_path = os.path.join(base_dir, cred_file)
        if os.path.exists(test_path):
            credentials_path = test_path
            break
    
    token_path = os.path.join(base_dir, 'token.json')
    
    creds = None
    # Check if token.json exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, CALENDAR_SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path:
                raise FileNotFoundError(
                    f"Google OAuth credentials file not found in {base_dir}. "
                    "Please ensure one of these files exists: credentials.json, credintials1.json, credintials.json"
                )
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, CALENDAR_SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as oauth_error:
                error_msg = str(oauth_error)
                if 'access_denied' in error_msg or '403' in error_msg or 'verification' in error_msg.lower():
                    raise Exception(
                        "Google OAuth Access Denied: Your app is in testing mode.\n\n"
                        "SOLUTION: Add yourself as a test user:\n"
                        "1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=test1-487423\n"
                        "2. Scroll to 'Test users' section\n"
                        "3. Click '+ ADD USERS'\n"
                        "4. Add your Google email address\n"
                        "5. Click 'SAVE'\n"
                        "6. Wait 1-2 minutes, then try again\n\n"
                        "For detailed instructions, see: GOOGLE_OAUTH_FIX.md"
                    )
                raise
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def add_roadmap_to_calendar(roadmap_data, start_date=None):
    """
    Add roadmap tasks to Google Calendar.
    
    Args:
        roadmap_data: Dictionary containing roadmap information with:
            - weekly_schedule: Array of weekly tasks
            - projects: Array of projects with duration_weeks
            - summary: Summary of the roadmap
        start_date: Optional datetime.date object. If None, starts from today.
    
    Returns:
        dict: Status and list of created event IDs
    """
    try:
        service = get_calendar_service()
        created_events = []
        
        # Use today as start date if not provided
        if start_date is None:
            start_date = datetime.date.today()
        
        # Add weekly schedule events with daily reminders
        if roadmap_data.get('weekly_schedule') and isinstance(roadmap_data['weekly_schedule'], list):
            for week_idx, week_data in enumerate(roadmap_data['weekly_schedule'][:12]):
                week_num = week_idx + 1
                week_start = start_date + datetime.timedelta(weeks=week_idx)
                
                # Get week content
                if isinstance(week_data, str):
                    week_content = week_data
                elif isinstance(week_data, dict):
                    week_content = week_data.get('tasks', week_data.get('description', ''))
                else:
                    week_content = str(week_data)
                
                # Create weekly overview event
                weekly_event = {
                    'summary': f'📚 Week {week_num}: Learning Tasks - Skill Development',
                    'description': f'Time to work on your skills!\n\n{week_content}\n\n💡 Remember: Consistency is key to mastering new skills!',
                    'start': {
                        'date': week_start.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'date': (week_start + datetime.timedelta(days=6)).isoformat(),
                        'timeZone': 'UTC',
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},      # Email 1 day before week starts
                            {'method': 'popup', 'minutes': 60},            # Popup 1 hour before
                        ],
                    },
                }
                
                created_event = service.events().insert(calendarId='primary', body=weekly_event).execute()
                created_events.append(created_event.get('id'))
                
                # Create daily learning reminder events for each day of the week (Monday-Friday)
                for day_offset in range(5):  # Monday to Friday (0-4)
                    learning_day = week_start + datetime.timedelta(days=day_offset)
                    day_name = learning_day.strftime('%A')
                    
                    # Create daily learning reminder event
                    daily_event = {
                        'summary': f'📖 Daily Learning: Week {week_num} - {day_name}',
                        'description': f'Daily skill development reminder!\n\nFocus for today:\n{week_content}\n\n⏰ Set aside time today to work on your learning goals.\n\n💪 Every day counts towards your success!',
                        'start': {
                            'date': learning_day.isoformat(),
                            'timeZone': 'UTC',
                        },
                        'end': {
                            'date': learning_day.isoformat(),
                            'timeZone': 'UTC',
                        },
                        'colorId': '5',  # Yellow color for daily reminders
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'email', 'minutes': 24 * 60},      # Email 1 day before
                                {'method': 'email', 'minutes': 60},            # Email 1 hour before (morning reminder)
                                {'method': 'popup', 'minutes': 30},             # Popup 30 minutes before
                                {'method': 'popup', 'minutes': 0},              # Popup at event time
                            ],
                        },
                    }
                    
                    created_daily = service.events().insert(calendarId='primary', body=daily_event).execute()
                    created_events.append(created_daily.get('id'))
        
        # Add project milestones as events
        if roadmap_data.get('projects') and isinstance(roadmap_data['projects'], list):
            current_week = 0
            for project in roadmap_data['projects']:
                project_name = project.get('name', project.get('project_name', 'Project'))
                duration = project.get('duration_weeks', project.get('duration', 1))
                
                # Try to convert duration to int
                try:
                    if isinstance(duration, str):
                        duration = int(duration.split()[0]) if duration.split()[0].isdigit() else 1
                    else:
                        duration = int(duration)
                except:
                    duration = 1
                
                project_start = start_date + datetime.timedelta(weeks=current_week)
                project_end = project_start + datetime.timedelta(weeks=duration)
                
                # Create project event with enhanced email reminders
                project_description = project.get('description', '')
                tech_stack = project.get('tech_stack', [])
                tech_str = ', '.join(tech_stack) if isinstance(tech_stack, list) else str(tech_stack)
                
                event = {
                    'summary': f'🚀 Project: {project_name}',
                    'description': f'Project Milestone: {project_name}\n\n{project_description}\n\n{"Tech Stack: " + tech_str if tech_str else ""}\n\n💪 Stay focused and complete this project to advance your skills!',
                    'start': {
                        'date': project_start.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'date': project_end.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'colorId': '10',  # Green color for projects
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},      # Email 1 day before project starts
                            {'method': 'email', 'minutes': 2 * 60},        # Email 2 hours before (daily reminder)
                            {'method': 'popup', 'minutes': 60},            # Popup 1 hour before
                            {'method': 'popup', 'minutes': 15},             # Popup 15 minutes before
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
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to add to calendar: {str(e)}'
        }

@require_http_methods(["POST"])
def add_to_calendar(request):
    """
    API endpoint to add roadmap to Google Calendar.
    Expects JSON with roadmap_data and optional start_date.
    """
    try:
        data = json.loads(request.body)
        roadmap_data = data.get('roadmap_data', {})
        
        if not roadmap_data:
            return JsonResponse({
                'success': False,
                'error': 'roadmap_data is required'
            }, status=400)
        
        # Parse optional start_date
        start_date = None
        if data.get('start_date'):
            try:
                start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except:
                pass  # Use default (today)
        
        result = add_roadmap_to_calendar(roadmap_data, start_date)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Successfully added {result["events_created"]} events to your Google Calendar',
                'events_created': result['events_created']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=500)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)

# Note: run_agent() is commented out to prevent it from running automatically on module import
# Uncomment and call it manually when needed, or create a Django view/management command for it
# run_agent()
