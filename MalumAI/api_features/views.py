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


Must provide:

1. A personalized learning path with 5-7 key milestones

2. 3-5 practical projects the user should complete (with project names and brief descriptions)

3. An estimated timeline in weeks for each project

4. Resources and tech stack recommendations

5. A weekly schedule/timetable for the next 12 weeks


Strictly Format the response as structured JSON with the following keys:

- "milestone" (array of milestones)

- "projects" (array of projects with name, description, duration_weeks, tech_stack)

- "weekly_schedule" (array of 12 weeks with tasks)

- "resources" (array of recommended resources)

- "summary" (brief overview of the plan)

NOTE: dont respond with anything else, just the plain json format, no ''' at the end or start, no empty json values"""
        
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

@require_http_methods(["POST"])
def run_agent_endpoint(request):
    """
    API endpoint to initialize and run the agent
    Creates a GitHub repository with AI-generated project files
    """
    try:
        # Get user inputs from request
        try:
            data = json.loads(request.body)
        except:
            data = {}
        
        skillset = data.get('skillset', 'general programming')
        interest = data.get('interest', 'software development')
        goal = data.get('goal', 'skill development')
        gpt_response = data.get('gpt_response', '')  # Roadmap data from GPT
        
        repo_url = run_agent(skillset, interest, goal, gpt_response)
        return JsonResponse({
            'success': True,
            'message': 'Agent synthesis initiated successfully',
            'repo_url': repo_url
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Agent execution failed: {str(e)}'
        }, status=500)


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

def get_name(proj):
    response = github_client.chat.completions.create(
                messages=[{"role": "user", "content": f"I am working on a project {proj}, suggest me a name, don't say anything else just the suggested name"}],
                model="llama-3.3-70b-versatile",
            )
    return response.choices[0].message.content

def get_project(gpt_response):
    response = github_client.chat.completions.create(
                messages=[{"role": "user", "content": f"I asked AI to give me a road map and it gave me {gpt_response}, extract the first recommended project and give me, nothing else, just the project and it's req "}],
                model="llama-3.3-70b-versatile",
            )
    return response.choices[0].message.content

def get_lang(proj):
    response = github_client.chat.completions.create(
                messages=[{"role": "user", "content": f"{proj} is a project i want to work on, don't say anything else just give me the extension of the language that is going to be used, give me only one"}],
                model="llama-3.3-70b-versatile",
            )
    return response.choices[0].message.content

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
        
        time.sleep(2)
    return False

def run_agent(skillset, interest, goal, gpt_response=''):
    proj = get_project(gpt_response) if gpt_response else decide_project(skillset, interest, goal)
    lang = get_lang(proj)
    name = get_name(proj)
    repo_name = f"{name}-{int(time.time())}"
    repo_url = f"https://github.com/{USERNAME}/{repo_name}"

    # Extract project from GPT response
    if create_repository(repo_name, f"AI Agent Project - {interest}"):
        time.sleep(5) 
        
        files = {
            "README.md": decide_readme(proj, lang),
            f"main{lang}": decide_starter(proj, lang)
        }

        for name, content in files.items():
            create_file(repo_name, name, content)
            time.sleep(1)

    print(f"\nAGENT COMPLETE: {repo_url}")
    return repo_url

# Note: run_agent() is commented out to prevent it from running automatically on module import
# Uncomment and call it manually when needed, or create a Django view/management command for it
# run_agent()
