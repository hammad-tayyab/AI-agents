from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from groq import Groq
import os
import requests
import base64
import time
from dotenv import load_dotenv

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

Please provide:
1. A personalized learning path with 5-7 key milestones
2. 3-5 practical projects the user should complete (with project names and brief descriptions)
3. An estimated timeline in weeks for each project
4. Resources and tech stack recommendations
5. A weekly schedule/timetable for the next 12 weeks

Format the response as structured JSON with the following keys:
- "roadmap" (array of milestones)
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


# GitHub Agent Functions (for automated project creation)
# Note: These functions use a separate Groq client instance
load_dotenv()

# GitHub agent configuration
project = "calculator, console based"
lang = "py"
github_client = Groq(
    api_key="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",
)
GITHUB_TOKEN = "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"
USERNAME = "ABUHURAIRA114"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def decide_project(project):
    response = github_client.chat.completions.create(
                messages=[{"role": "user", "content": f"I want to develop my skills, give me requirements for a task for this project : {project} in {lang}"}],
                model="llama-3.3-70b-versatile",
            )
    return response.choices[0].message.content

def decide_starter(proj_req):
    response = github_client.chat.completions.create(
            messages=[{"role": "user", "content": f"following are requirments for a project : \n {project} \n don't respond anything else, just give me a starter code for the project in {lang}, don't include feature, just a structure"}],
            model="llama-3.3-70b-versatile",
        )
    return response.choices[0].message.content

def decide_readme(proj_req):
    response = github_client.chat.completions.create(
            messages=[{"role": "user", "content": f"following are requirments for a project : \n {project} \n in {lang} don't respond anything else, just give me a readme for the project for github repo"}],
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
        
        time.sleep(2)
    return False

def run_agent():
    repo_name = f"ai-agent-project-{int(time.time())}"
    
    if create_repository(repo_name, "Malum AI Agent Project"):
        time.sleep(5) 
        
        files = {
            "README.md": decide_readme(decide_project(project)),
            f"main.{lang}": decide_starter(decide_project(project))
        }

        for name, content in files.items():
            create_file(repo_name, name, content)
            time.sleep(1)

    print(f"\nAGENT COMPLETE: https://github.com/{USERNAME}/{repo_name}")

# Note: run_agent() is commented out to prevent it from running automatically on module import
# Uncomment and call it manually when needed, or create a Django view/management command for it
# run_agent()
