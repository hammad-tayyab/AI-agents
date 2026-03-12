"""
================================================================================
GOOGLE CALENDAR CREDENTIALS SETUP UTILITY
================================================================================

Utility script for initializing Google OAuth credentials.

PURPOSE:
This script automates the setup of Google OAuth credentials by copying
the source credentials file to the standard location expected by the
calendar integration module.

WORKFLOW:
1. Locates credintials1.json (legacy filename with typo)
2. Copies to credentials.json (standard filename) if not present
3. Verifies the copy operation succeeded
4. Handles Windows console encoding issues

USAGE:
  python api_features/setup_credentials.py

EXPECTED FILES:
  Source:  api_features/credintials1.json
  Target:  api_features/credentials.json

FILE FORMAT:
Both files should contain valid Google OAuth2 credentials in JSON format:
  {
    "web": {
      "client_id": "...",
      "project_id": "...",
      "auth_uri": "...",
      "token_uri": "...",
      "client_secret": "...",
      "redirect_uris": ["..."]
    }
  }

SECURITY:
⚠️  WARNING: Never commit credentials.json or credintials1.json to version control
  - Add to .gitignore
  - Store only locally on your machine
  - Use environment variables for sensitive keys in production

WINDOWS COMPATIBILITY:
Handles UTF-8 encoding for Windows console output without errors.

EXIT CODES:
  0 (True)  - Setup successful
  1 (False) - Setup failed

TROUBLESHOOTING:
  - If "Source file not found": Ensure credintials1.json exists
  - If "Permission denied": Run with appropriate file system permissions
  - If encoding errors: Script auto-configures UTF-8 for Windows

================================================================================
"""

import os
import shutil
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def setup_credentials():
    """
    Copy credintials1.json to credentials.json if it doesn't exist.
    
    LOGIC:
      1. Get the directory containing this script
      2. Check for source file (credintials1.json)
      3. Check if target already exists
      4. If sourceexists and target doesn't: copy file
      5. Return success/failure status
    
    RETURNS:
      bool: True if credentials are successfully set up, False otherwise
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(base_dir, 'credintials1.json')
    target_file = os.path.join(base_dir, 'credentials.json')
    
    if os.path.exists(source_file) and not os.path.exists(target_file):
        try:
            # Copy file with metadata preservation
            shutil.copy2(source_file, target_file)
            print(f"SUCCESS: Copied {os.path.basename(source_file)} to {os.path.basename(target_file)}")
            print("SUCCESS: Google Calendar credentials are now set up!")
            return True
        except Exception as e:
            print(f"ERROR: Error copying file: {e}")
            return False
    elif os.path.exists(target_file):
        print("SUCCESS: credentials.json already exists!")
        return True
    else:
        print(f"ERROR: Source file {os.path.basename(source_file)} not found!")
        print("Please ensure credintials1.json exists in the api_features folder.")
        return False

# == SCRIPT ENTRY POINT ==
if __name__ == "__main__":
    setup_credentials()
