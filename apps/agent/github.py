"""
GitHub API Wrapper

Handles GitHub API operations for repository creation and file management.
"""

import re
import time
import requests
import base64
from django.conf import settings


class GitHubClient:
    """Client for GitHub API operations."""

    def __init__(self):
        """Initialize GitHub client with token and configuration."""
        self.token = settings.GITHUB_TOKEN
        self.username = settings.GITHUB_USERNAME
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }

    def create_repository(self, repo_name, description):
        """
        Create a new GitHub repository.

        Args:
            repo_name (str): Name of the repository
            description (str): Repository description

        Returns:
            bool: True if repository created or already exists, False otherwise
        """
        url = f"{self.base_url}/user/repos"
        data = {
            "name": repo_name,
            "description": description,
            "private": False
        }

        print(f"\n[GITHUB] Creating repository: {repo_name}")
        response = requests.post(url, headers=self.headers, json=data, timeout=20)

        if response.status_code == 201:
            print("[GITHUB] SUCCESS: Repository created")
            return True
        elif response.status_code == 422:
            print("[GITHUB] Repository already exists")
            return True
        else:
            print(f"[GITHUB] FAILED: Status {response.status_code}")
            return False

    def create_file(self, repo_name, file_name, content, retries=3):
        """
        Create a file in the GitHub repository.

        Args:
            repo_name (str): Repository name
            file_name (str): Name of file to create
            content (str): File content
            retries (int): Number of retry attempts

        Returns:
            bool: True if file created successfully, False otherwise
        """
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{file_name}"
        encoded_content = base64.b64encode(content.encode()).decode()
        data = {
            "message": f"Create {file_name}",
            "content": encoded_content
        }

        for attempt in range(retries):
            print(f"[GITHUB] Creating file: {file_name} (Attempt {attempt + 1})")
            response = requests.put(url, headers=self.headers, json=data, timeout=30)

            if response.status_code in [200, 201]:
                print(f"[GITHUB] SUCCESS: {file_name} created")
                return True
            else:
                print(f"[GITHUB] FAILED: Status {response.status_code}")

            time.sleep(0.2)

        return False

    def get_repo_url(self):
        """Get formatted GitHub repository URL."""
        return f"https://github.com/{self.username}"
