"""
Google Calendar OAuth2 Handler

Manages OAuth2 authentication and token management for Google Calendar API.
"""

import os
import json
from django.conf import settings
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class OAuth2Manager:
    """Manages OAuth2 flow for Google Calendar API."""

    def __init__(self):
        """Initialize OAuth2 manager with paths and scopes."""
        self.credentials_path = settings.CREDENTIALS_PATH
        self.token_path = settings.TOKEN_PATH
        self.scopes = settings.CALENDAR_SCOPES

    def load_credentials_from_file(self):
        """Load credentials from token file if it exists."""
        if os.path.exists(self.token_path):
            return Credentials.from_authorized_user_file(self.token_path, self.scopes)
        return None

    def save_credentials_to_file(self, creds):
        """Save credentials to token file."""
        with open(self.token_path, 'w') as token:
            token.write(creds.to_json())

    def refresh_credentials(self, creds):
        """Refresh expired credentials."""
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.save_credentials_to_file(creds)
            return creds
        return None

    def initiate_oauth_flow(self, redirect_uri):
        """
        Initiate OAuth2 flow for web applications.

        Args:
            redirect_uri (str): URL to redirect after authorization

        Returns:
            tuple: (authorization_url, state)
        """
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google OAuth credentials file not found at {self.credentials_path}. "
                "Please ensure credentials.json exists in config/credentials/."
            )

        flow = Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return authorization_url, state, flow

    def exchange_code_for_credentials(self, flow, code):
        """
        Exchange authorization code for credentials.

        Args:
            flow: OAuth2 flow object
            code (str): Authorization code from callback

        Returns:
            Credentials: OAuth2 credentials
        """
        flow.fetch_token(code=code)
        creds = flow.credentials
        self.save_credentials_to_file(creds)
        return creds

    def get_local_server_credentials(self):
        """
        Get credentials using local server OAuth flow.
        Useful for desktop applications.

        Returns:
            Credentials: OAuth2 credentials
        """
        creds = self.load_credentials_from_file()

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.refresh_credentials(creds)
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google OAuth credentials file not found at {self.credentials_path}. "
                        "Please ensure credentials.json exists in config/credentials/."
                    )
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        self.scopes
                    )
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

                self.save_credentials_to_file(creds)

        return creds
