"""
Helper script to set up Google Calendar credentials.
This script copies credintials1.json to credentials.json
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
    """Copy credintials1.json to credentials.json if it doesn't exist"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(base_dir, 'credintials1.json')
    target_file = os.path.join(base_dir, 'credentials.json')
    
    if os.path.exists(source_file) and not os.path.exists(target_file):
        try:
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

if __name__ == "__main__":
    setup_credentials()
