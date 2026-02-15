# Google Calendar Integration Guide

## Overview
This application integrates with Google Calendar to automatically add your learning roadmap tasks, weekly schedules, and project milestones to your Google Calendar with daily reminders.

## How It Works

### 1. **First-Time Setup (One-Time Process)**

#### Step 1: Install Required Packages
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### Step 2: Credentials File Setup
- The `credentials.json` file is already in the `api_features` folder
- This file contains your Google OAuth2 credentials
- **Important**: Never commit this file to public repositories!

#### Step 3: First Authentication
When you first click "Add to Google Calendar", the system will:
1. Open a browser window for Google OAuth authentication
2. Ask you to sign in to your Google account
3. Request permission to access your Google Calendar
4. Save the authentication token to `token.json` in the `api_features` folder

**Note**: The `token.json` file will be created automatically after first authentication.

### 2. **How to Use**

#### Option A: Through the Web Interface
1. Generate your learning roadmap using the form
2. Review the generated roadmap
3. Click the **"Add to Google Calendar"** button
4. If it's your first time, authenticate with Google
5. Events will be automatically added to your calendar!

#### Option B: Through API (Programmatic)
```python
POST /api/add_to_calendar/
Content-Type: application/json

{
    "roadmap_data": {
        "weekly_schedule": [
            "Week 1 tasks...",
            "Week 2 tasks...",
            ...
        ],
        "projects": [
            {
                "name": "Project Name",
                "description": "Project description",
                "duration_weeks": 2
            }
        ],
        "summary": "Roadmap summary"
    },
    "start_date": "2024-01-15"  // Optional: YYYY-MM-DD format, defaults to today
}
```

### 3. **What Gets Added to Calendar**

#### Weekly Schedule Events
- **Type**: All-day events for each week
- **Duration**: 7 days (Monday to Sunday)
- **Reminders**: 
  - Email reminder 1 day before
  - Popup reminder 15 hours before
- **Content**: Weekly learning tasks and goals

#### Project Milestones
- **Type**: All-day events spanning project duration
- **Duration**: Based on project's `duration_weeks`
- **Color**: Green (for easy identification)
- **Reminders**: 
  - Email reminder 1 day before
  - Popup reminder 1 hour before
- **Content**: Project name and description

### 4. **File Structure**

```
api_features/
├── credentials.json          # Google OAuth credentials (DO NOT SHARE!)
├── token.json               # Auto-generated after first auth (DO NOT SHARE!)
├── views.py                 # Contains calendar integration functions
└── templates/
    └── api_features/
        └── index.html        # Frontend with calendar button
```

### 5. **Authentication Flow**

```
User clicks "Add to Calendar"
    ↓
Check if token.json exists
    ↓
If NO → Open browser for OAuth → Save token.json
    ↓
If YES → Check if token is valid
    ↓
If expired → Refresh token automatically
    ↓
Create calendar events
    ↓
Return success message
```

### 6. **Security Notes**

⚠️ **IMPORTANT SECURITY CONSIDERATIONS:**

1. **Never commit credentials.json or token.json to Git**
   - Add to `.gitignore`:
     ```
     api_features/credentials.json
     api_features/token.json
     ```

2. **Token.json contains sensitive data**
   - Contains access tokens for your Google account
   - Keep it secure and private
   - If compromised, revoke access in Google Account settings

3. **Credentials.json**
   - Contains OAuth client ID and secret
   - Keep it secure
   - Regenerate if exposed

### 7. **Troubleshooting**

#### Issue: "credentials.json not found"
**Solution**: 
- Ensure `credentials.json` is in the `api_features` folder
- Rename `credentials (1).json` to `credentials.json` if needed

#### Issue: "Authentication failed"
**Solution**:
- Delete `token.json` and try again
- Check if credentials.json is valid
- Ensure Google Calendar API is enabled in Google Cloud Console

#### Issue: "Permission denied"
**Solution**:
- Revoke access in Google Account → Security → Third-party apps
- Delete `token.json` and re-authenticate

#### Issue: Events not appearing
**Solution**:
- Check your Google Calendar (may take a few seconds)
- Verify you're checking the correct Google account
- Check browser console for errors

### 8. **Customization**

#### Change Start Date
In the frontend JavaScript, modify:
```javascript
body: JSON.stringify({
    roadmap_data: roadmapData,
    start_date: "2024-01-15"  // Your desired start date
})
```

#### Modify Reminders
In `views.py`, edit the `add_roadmap_to_calendar` function:
```python
'reminders': {
    'useDefault': False,
    'overrides': [
        {'method': 'email', 'minutes': 24 * 60},  # Email 1 day before
        {'method': 'popup', 'minutes': 15 * 60},   # Popup 15 hours before
    ],
},
```

#### Change Event Colors
Use Google Calendar color IDs (1-11):
- 1: Lavender
- 2: Sage
- 3: Grape
- 4: Flamingo
- 5: Banana
- 6: Tangerine
- 7: Peacock
- 8: Graphite
- 9: Blueberry
- 10: Basil (Green) ← Currently used for projects
- 11: Tomato

### 9. **API Endpoints**

#### Add to Calendar
```
POST /api/add_to_calendar/
Headers: Content-Type: application/json, X-CSRFToken: <token>
Body: {
    "roadmap_data": {...},
    "start_date": "YYYY-MM-DD" (optional)
}
Response: {
    "success": true/false,
    "message": "Success message",
    "events_created": 15
}
```

### 10. **Daily Reminders**

Once events are added:
- **Email reminders**: Sent 1 day before each event
- **Popup reminders**: Shown 15 hours before (in Google Calendar app)
- **Notifications**: Configure in Google Calendar settings

### 11. **Testing**

1. Generate a test roadmap
2. Click "Add to Google Calendar"
3. Complete OAuth if first time
4. Check your Google Calendar
5. Verify events appear with correct dates
6. Test reminders by checking notification settings

## Summary

The Google Calendar integration:
- ✅ Automatically adds weekly learning tasks
- ✅ Adds project milestones with durations
- ✅ Sets up daily reminders
- ✅ Handles authentication automatically
- ✅ Refreshes tokens when needed
- ✅ Provides user-friendly error messages

**First Use**: Requires one-time Google authentication
**Subsequent Uses**: Automatic, no authentication needed (token is saved)

Enjoy your automated learning schedule! 🚀📅
