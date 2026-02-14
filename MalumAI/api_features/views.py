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

# Configure Groq API key
GROQ_API_KEY = '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'  # Replace with your actual Groq API key
client = Groq(api_key=GROQ_API_KEY)
response = ""
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
        except Exception:
            return JsonResponse({
                'success': False,
                'error': 'Expected JSON body, received HTML or invalid payload.'
            }, status=400)
        skillset = data.get('skillset', '')
        interest = data.get('interest', '')
        goal = data.get('goal', '')
        
        # Validate inputs
        if not all([skillset, interest, goal]):
            return JsonResponse({
                'success': False,
                'error': 'Please fill all fields: skillset, interest, and goal'
            }, status=400)
        
        # Create the prompt for GPT
        prompt = f"""Based on the following user profile, create a detailed learning roadmap:

Current Skillset: {skillset}
Area of Interest: {interest}
Learning Goal: {goal}

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
        
        # Call Groq API with fallback models in case a model is decommissioned
        
        gpt_response = None
        try:
            response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert learning roadmap creator. Provide structured, practical, and achievable learning plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
            )
            gpt_response = response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            gpt_response = None

        if not gpt_response:
            # Return a helpful error message to the client
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate roadmap. Please try again.'
            }, status=500)
        
        response = gpt_response
        # Try to parse as JSON, if it fails, structure it
        try:
            result = json.loads(gpt_response)
        except json.JSONDecodeError:
            result = {
                'raw_response': gpt_response,
                'formatted': True
            }
        
        return JsonResponse({
            'success': True,
            'data': result
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def results(request):
    return render(request, 'api_features/results.html')

load_dotenv()

project = "calculator, console based"
lang = "py"
client = Groq(
    api_key="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",
)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def decide_project(project):
    response = client.chat.completions.create(
                messages=[{"role": "user", "content": f"I want to develop my skills, give me requirements for a task for this project : {project} in {lang}"}],
                model="llama-3.3-70b-versatile",
            )
    return response.choices[0].message.content

def decide_starter(proj_req):
    response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"following are requirments for a project : \n {project} \n don't respond anything else, just give me a starter code for the project in {lang}, don't include feature, just a structure"}],
            model="llama-3.3-70b-versatile",
        )
    return response.choices[0].message.content

def decide_readme(proj_req):
    response = client.chat.completions.create(
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

run_agent()