from django.shortcuts import render
import os
import requests
import base64
import time
from dotenv import load_dotenv
from groq import Groq

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
            messages=[{"role": "user", "content": f"following are requirments for a project : \n {project} \n don't respond anything else, just give me a starter code for the project in {lang}, don't include feature, just a structure, make sure it is a plain code no '''{lang} at start or end"}],
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