# HTML Form Complete Code Reference

## 📌 Summary of What Was Built

Your platform now has:
1. ✅ **HTML Form** (`index.html`) - Collects user input
2. ✅ **API Endpoint** (`views.py`) - Processes input & calls GPT
3. ✅ **Results Page** (`results.html`) - Displays the roadmap
4. ✅ **JavaScript Handlers** - Manages form submission & data transfer
5. ✅ **URL Routing** - Connects all components

---

## 📋 File Locations

All files are created in:
- `f:\HackGik\AI-agents\MalumAI\api_features\`

### Templates:
```
api_features/templates/api_features/
├── index.html        ← Input Form Page
└── results.html      ← Results Display Page
```

### Backend:
```
api_features/
├── views.py          ← API Logic (Updated)
├── urls.py           ← Routing (Updated)
└── models.py         ← Database Models (Optional for this feature)
```

---

## 🎯 How the HTML Form Works

### **1. Form Collection:**
```html
<form id="roadmapForm">
    <input name="skillset" placeholder="Python, JavaScript, HTML/CSS" required />
    <textarea name="interest" placeholder="Web Development" required />
    <textarea name="goal" placeholder="Build a job-ready portfolio" required />
    <button type="submit">Generate My Roadmap</button>
</form>
```

### **2. JavaScript Intercepts Submission:**
```javascript
form.addEventListener('submit', async (e) => {
    e.preventDefault();  // Stop page reload
    
    // Collect data
    const formData = {
        skillset: document.getElementById('skillset').value,
        interest: document.getElementById('interest').value,
        goal: document.getElementById('goal').value
    };
```

### **3. Send Data to API:**
```javascript
const response = await fetch('/api/generate-roadmap/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(formData)
});
```

### **4. Receive Response:**
```javascript
const result = await response.json();
if (result.success) {
    // Store data
    sessionStorage.setItem('roadmapData', JSON.stringify(result.data));
    // Redirect
    window.location.href = '/api/results/';
}
```

### **5. Display on Results Page:**
```javascript
const roadmapData = JSON.parse(sessionStorage.getItem('roadmapData'));
displayRoadmap(roadmapData);  // Renders all sections
```

---

## 🔄 Complete Data Flow

```
┌─────────────────┐
│  User fills     │
│  HTML Form      │  ← index.html
│ (skillset, etc) │
└────────┬────────┘
         │ Form submitted
         ↓
┌─────────────────┐
│  JavaScript     │
│  Collects data  │  ← JavaScript in index.html
│  & validates    │
└────────┬────────┘
         │ POST /api/generate-roadmap/
         ↓
┌─────────────────┐
│  Django API     │
│  (views.py)     │  ← Backend processing
│  Calls GPT      │     generate_roadmap() function
└────────┬────────┘
         │ JSON Response
         ↓
┌─────────────────┐
│  JavaScript     │
│  Stores in      │  ← sessionStorage
│  sessionStorage │
└────────┬────────┘
         │ Redirect to /api/results/
         ↓
┌─────────────────┐
│  Results Page   │
│  Retrieves data │  ← results.html
│  & Displays     │
└─────────────────┘
```

---

## 🛠️ Setup Checklist

Run these commands:

```bash
# 1. Install dependencies
pip install django openai

# 2. Edit your OpenAI API key in views.py
# Find this line and replace:
openai.api_key = 'sk-your-actual-key-here'

# 3. Add api_features to INSTALLED_APPS in settings.py
# Already done ✓

# 4. Run migrations (if needed)
python manage.py makemigrations
python manage.py migrate

# 5. Start the server
python manage.py runserver

# 6. Open browser
# Visit: http://localhost:8000/api/
```

---

## 📝 Key Code Sections

### **In views.py:**
```python
@csrf_exempt
@require_http_methods(["POST"])
def generate_roadmap(request):
    # Receives: {'skillset': '...', 'interest': '...', 'goal': '...'}
    # Calls OpenAI API
    # Returns: JSON with roadmap data
```

### **In index.html:**
```javascript
form.addEventListener('submit', async (e) => {
    // 1. Prevent default form submission
    e.preventDefault();
    
    // 2. Show loading spinner
    loadingSpinner.style.display = 'block';
    
    // 3. Send data to API
    const response = await fetch('/api/generate-roadmap/', {...});
    
    // 4. Handle response and redirect
    const result = await response.json();
    if (result.success) {
        sessionStorage.setItem('roadmapData', JSON.stringify(result.data));
        window.location.href = '/api/results/';
    }
});
```

### **In results.html:**
```javascript
// Retrieve data from sessionStorage
const roadmapData = JSON.parse(sessionStorage.getItem('roadmapData'));

// Display sections:
// - Summary
// - Milestones
// - Projects with tech stack
// - Weekly schedule
// - Resources
```

---

## 🎨 Form Input Examples

### Example Input:
```
Skillset: Python, JavaScript, basic HTML/CSS, Git
Interest: Full-Stack Web Development with AI
Goal: Build an AI-powered web app and get hired as a junior developer
```

### Example Output from GPT:
```json
{
    "summary": "A comprehensive 12-week journey...",
    "roadmap": [
        "Master Python Advanced OOP",
        "Learn React Fundamentals",
        "Build REST APIs with Django",
        "Connect AI APIs to web apps"
    ],
    "projects": [
        {
            "name": "Personal Portfolio Website",
            "description": "Build and deploy a responsive portfolio",
            "duration_weeks": 2,
            "tech_stack": ["HTML", "CSS", "JavaScript", "Bootstrap"]
        }
    ],
    "weekly_schedule": [
        "Week 1: Setup development environment, learn JavaScript basics",
        "Week 2: Build with React, learn components and state"
    ],
    "resources": [
        "Free Code Camp - Full Stack Course",
        "React Official Documentation"
    ]
}
```

---

## ⚠️ Common Issues & Fixes

### Issue: Form won't submit
**Check:**
- CSRF token is present in form
- JavaScript console for errors (F12)
- API endpoint `/api/generate-roadmap/` exists

### Issue: Results page shows empty
**Check:**
- sessionStorage has data (check browser DevTools)
- JavaScript errors in console
- Data structure matches display code

### Issue: "OpenAI API not found"
**Fix:**
- Get key from https://platform.openai.com/api-keys
- Add to views.py: `openai.api_key = 'sk-...your key...'`

### Issue: Templates not loading
**Fix:**
- Create folder: `api_features/templates/api_features/`
- Files must be: `index.html` and `results.html`
- Folder structure is case-sensitive on Linux

---

## 🚀 Advanced Customizations

### Customize the GPT Prompt:
Edit `views.py`, function `generate_roadmap()`:
```python
prompt = f"""Your custom prompt here
Current Skillset: {skillset}
Area of Interest: {interest}
Learning Goal: {goal}
"""
```

### Add Database Storage:
```python
# In models.py
class Roadmap(models.Model):
    skillset = models.CharField(max_length=255)
    interest = models.TextField()
    goal = models.TextField()
    roadmap_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Add Email Notification:
```python
from django.core.mail import send_mail
send_mail('Your Roadmap is Ready', 
          'Click here to view...', 
          'from@example.com',
          ['user@example.com'])
```

---

## 📚 Resources

- Django Docs: https://docs.djangoproject.com/
- OpenAI API: https://platform.openai.com/docs/api-reference
- HTML Forms: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form
- JavaScript Fetch: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

---

**Everything is ready! Just add your OpenAI API key and run the server.** 🎉
