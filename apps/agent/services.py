"""
GitHub Agent Service

Autonomous agent for creating GitHub repositories with AI-generated project files.
"""

import json
import re
import time
import traceback
from groq import Groq
from django.conf import settings
from .github import GitHubClient


class GitHubAgentService:
    """Service for autonomous GitHub repository creation."""

    def __init__(self):
        """Initialize agent with Groq client."""
        self.client = Groq(api_key=settings.GROQ_AGENT_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.github = GitHubClient()

    def get_project_name(self, proj):
        """Generate a repository name for the project."""
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"I am working on a project {proj}, suggest me a short repository name (lowercase, no spaces, use hyphens), don't say anything else just the suggested name"
            }],
            model=self.model,
        )
        name = response.choices[0].message.content.strip()
        name = name.lower().replace(' ', '-').replace('_', '-')
        name = re.sub(r'[^a-z0-9-]', '', name)
        return name

    def get_programming_language(self, proj):
        """Determine programming language for the project."""
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"{proj} is a project i want to work on, don't say anything else just give me the extension of the language that is going to be used (e.g., py, js, java), give me only one extension without dot"
            }],
            model=self.model,
        )
        lang = response.choices[0].message.content.strip()
        lang = lang.replace('.', '').strip()
        return lang

    def decide_project(self, skillset, interest, goal):
        """Generate project idea based on user's profile."""
        prompt = f"Based on the user's skillset ({skillset}), interest ({interest}), and goal ({goal}), suggest a specific project to build. Keep it concise and practical."
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
        )
        return response.choices[0].message.content

    def get_starter_code(self, proj_req, lang):
        """Generate starter code for the project."""
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"following is the project requirement: \n {proj_req} \n don't respond anything else, just give me a starter code for the project in {lang}, don't include features, just a basic structure and dont include ```{lang} at start or end"
            }],
            model=self.model,
        )
        return response.choices[0].message.content

    def get_readme(self, proj_req, lang):
        """Generate a professional README for the project."""
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"""You are an expert software engineer and technical writer.

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
Do NOT use code block fences around the entire README."""
            }],
            model=self.model,
        )
        return response.choices[0].message.content

    def extract_project_from_roadmap(self, gpt_response):
        """Extract the first project from GPT roadmap response."""
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

        # Fallback: ask AI to extract project
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"I asked AI to give me a road map and it gave me {gpt_response}, extract the first recommended project name and description, nothing else"
            }],
            model=self.model,
        )
        return response.choices[0].message.content

    def run_agent(self, skillset, interest, goal, gpt_response='', task_id=None, task_store=None):
        """
        Main agent function that creates a GitHub repository with project files.

        Args:
            skillset (str): User's current skillset
            interest (str): Area of interest
            goal (str): Learning goal
            gpt_response (str): Previously generated roadmap (optional)
            task_id (str): Task ID for tracking (optional)
            task_store (dict): Shared task store for status updates

        Returns:
            str: URL of created GitHub repository
        """
        try:
            # Decide on project
            if gpt_response:
                proj = self.extract_project_from_roadmap(gpt_response)
                if not proj:
                    proj = self.decide_project(skillset, interest, goal)
            else:
                proj = self.decide_project(skillset, interest, goal)

            if task_id and task_store:
                task_store[task_id]['message'] = 'Decided project, determining language and repo name...'

            # Get language and repo name
            lang = self.get_programming_language(proj)
            repo_base_name = self.get_project_name(proj)
            repo_name = f"{repo_base_name}-{int(time.time())}"
            repo_url = f"https://github.com/{settings.GITHUB_USERNAME}/{repo_name}"

            # Create repository
            if self.github.create_repository(repo_name, f"AI Agent Project - {interest}"):
                if task_id and task_store:
                    task_store[task_id]['message'] = 'Repository created, generating files...'

                time.sleep(5)

                lang_ext = lang.strip()
                if not lang_ext.startswith('.'):
                    lang_ext = '.' + lang_ext

                if task_id and task_store:
                    task_store[task_id]['message'] = 'Generating README and starter code...'

                # Generate files
                readme_content = self.get_readme(proj, lang)
                starter_content = self.get_starter_code(proj, lang)

                files = {
                    "README.md": readme_content,
                    f"main{lang_ext}": starter_content
                }

                # Create files in repo
                for file_name, file_content in files.items():
                    if task_id and task_store:
                        task_store[task_id]['message'] = f'Creating file {file_name}...'

                    if self.github.create_file(repo_name, file_name, file_content):
                        time.sleep(1)
                    else:
                        print(f"[AGENT] WARNING: Failed to create {file_name}")
                        if task_id and task_store:
                            task_store[task_id]['message'] = f'Failed to create file {file_name}'

                if task_id and task_store:
                    task_store[task_id]['message'] = 'Finalizing repository and finishing up...'

                print(f"\n[AGENT] COMPLETE: {repo_url}")
                return repo_url
            else:
                raise Exception("Failed to create repository")

        except Exception as e:
            print(f"[AGENT] ERROR: {str(e)}")
            if task_id and task_store:
                task_store[task_id]['status'] = 'failed'
                task_store[task_id]['error'] = traceback.format_exc()
                task_store[task_id]['message'] = f'Error: {str(e)}'
            raise
