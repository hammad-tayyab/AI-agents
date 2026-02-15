# Fix Google OAuth "Access Blocked" Error

## Problem
```
Access blocked: skillImpactAgent has not completed the Google verification process
Error 403: access_denied
```

This happens because your Google OAuth app is in "Testing" mode and needs test users added.

## Solution Options

### Option 1: Add Test Users (Quickest - Recommended for Development)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project: `test1-487423`

2. **Navigate to OAuth Consent Screen**
   - Go to: APIs & Services → OAuth consent screen
   - Or direct link: https://console.cloud.google.com/apis/credentials/consent

3. **Add Test Users**
   - Scroll down to "Test users" section
   - Click "+ ADD USERS"
   - Add your Google email address (the one you'll use for calendar)
   - Add any other email addresses that need access
   - Click "SAVE"

4. **Try Again**
   - Run your application again
   - Use the email address you added as a test user
   - OAuth should work now!

### Option 2: Publish Your App (For Production)

**Note**: Publishing requires verification if you use sensitive scopes. For personal use, Option 1 is easier.

1. **Complete OAuth Consent Screen**
   - Go to: APIs & Services → OAuth consent screen
   - Fill in all required fields:
     - App name: "Skill Impact Agent" or your preferred name
     - User support email: Your email
     - Developer contact: Your email
     - App domain (optional for personal use)
     - Authorized domains (optional)

2. **Add Scopes**
   - Click "ADD OR REMOVE SCOPES"
   - Ensure `https://www.googleapis.com/auth/calendar` is added
   - Click "UPDATE"

3. **Publish App**
   - Scroll to bottom
   - Click "PUBLISH APP"
   - Confirm publishing

4. **Note**: For sensitive scopes, Google may require verification which can take days/weeks.

### Option 3: Use Service Account (Alternative - No User Interaction)

This requires changing the authentication method but doesn't need user consent.

## Quick Fix Steps (Recommended)

### Step 1: Add Yourself as Test User

1. Open: https://console.cloud.google.com/apis/credentials/consent?project=test1-487423

2. Scroll to "Test users" section

3. Click "+ ADD USERS"

4. Enter your Google email (the one you'll authenticate with)

5. Click "ADD" then "SAVE"

6. Wait 1-2 minutes for changes to propagate

### Step 2: Try Authentication Again

1. Run your Django application
2. Click "Add to Google Calendar"
3. Sign in with the email you added as test user
4. Grant permissions
5. Should work now! ✅

## Verification Checklist

- [ ] Project ID: `test1-487423` is correct
- [ ] Test users added in OAuth consent screen
- [ ] Your email is in the test users list
- [ ] Calendar API is enabled in the project
- [ ] Credentials file matches the project

## Enable Calendar API (If Not Already Enabled)

1. Go to: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com?project=test1-487423
2. Click "ENABLE"
3. Wait for it to enable

## Common Issues

### "User is not a test user"
→ Make sure you added your email in "Test users" section

### "App not verified"
→ For personal/testing use, you can ignore this warning and continue

### "Invalid client"
→ Check that credentials.json matches your Google Cloud project

### "Access denied"
→ Ensure Calendar API is enabled and test users are added

## For Production Use

If you want to make this available to all users (not just test users):

1. Complete OAuth consent screen fully
2. Submit for verification (if using sensitive scopes)
3. Wait for Google's approval (can take weeks)
4. Or use a service account approach

## Current Project Details

- **Project ID**: test1-487423
- **Client ID**: 40274673944-18iu5oekou1mq4c6pqf7fonau3jcktdb.apps.googleusercontent.com
- **OAuth Consent Screen**: https://console.cloud.google.com/apis/credentials/consent?project=test1-487423

## Quick Links

- **OAuth Consent Screen**: https://console.cloud.google.com/apis/credentials/consent?project=test1-487423
- **Credentials**: https://console.cloud.google.com/apis/credentials?project=test1-487423
- **Calendar API**: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com?project=test1-487423

## Summary

**Quick Fix**: Add your email as a test user in Google Cloud Console → OAuth consent screen → Test users section.

This will allow you to authenticate and use the calendar integration immediately! 🚀
