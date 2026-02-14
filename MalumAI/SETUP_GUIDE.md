# Learning Roadmap Platform - Complete Setup Guide

## 📋 Overview
This platform generates personalized learning roadmaps based on:
- Current skillset
- Area of interest
- Learning goal

The system creates a 12-week plan with projects, milestones, and weekly schedules.

## 🔧 Installation & Setup

### 1. Install Required Packages
```bash
pip install django openai django-cors-headers
```

### 2. Set Your OpenAI API Key
Edit `api_features/views.py` and replace:
```python
openai.api_key = 'your_openai_api_key_here'
```

With your actual OpenAI API key from https://platform.openai.com/api-keys

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Start Development Server
```bash
python manage.py runserver
```

Visit: `http://localhost:8000/api/`

---

## 📁 Project Structure

```
api_features/
├── templates/
│   └── api_features/
│       ├── index.html          # Input form page
│       └── results.html        # Results display page
├── views.py                    # Django views & API endpoints
├── urls.py                     # URL routing
└── __init__.py
```

---

## 🔌 API Endpoints

### 1. **Input Form Page**
- **URL**: `/api/`
- **Method**: GET
- **Returns**: HTML form for user input

### 2. **Generate Roadmap API**
- **URL**: `/api/generate-roadmap/`
- **Method**: POST
- **Request Body**:
```json
{
    "skillset": "Python basics, HTML/CSS, Git",
    "interest": "Web Development",
    "goal": "Build a full-stack web application"
}
```

- **Response**:
```json
{
    "success": true,
    "data": {
        "summary": "...",
        "roadmap": ["Milestone 1", "Milestone 2", ...],
        "projects": [
            {
                "name": "Project Name",
                "description": "...",
                "duration_weeks": 2,
                "tech_stack": ["Tech1", "Tech2"]
            }
        ],
        "weekly_schedule": ["Week 1 tasks", "Week 2 tasks", ...],
        "resources": ["Resource 1", "Resource 2", ...]
    }
}
```

### 3. **Results Display Page**
- **URL**: `/api/results/`
- **Method**: GET
- **Returns**: HTML displaying the generated roadmap

---

## 🎨 Frontend Flow

### **Step 1: User Inputs Data** (`index.html`)
```html
<form id="roadmapForm">
    <input name="skillset" placeholder="Your current skills" />
    <textarea name="interest" placeholder="What interests you" />
    <textarea name="goal" placeholder="Your learning goal" />
    <button type="submit">Generate Roadmap</button>
</form>
```

### **Step 2: JavaScript Submission**
```javascript
// Collect form data
const formData = {
    skillset: document.getElementById('skillset').value,
    interest: document.getElementById('interest').value,
    goal: document.getElementById('goal').value
};

// Send to API
const response = await fetch('/api/generate-roadmap/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(formData)
});

// Store result in sessionStorage
sessionStorage.setItem('roadmapData', JSON.stringify(result.data));

// Redirect to results page
window.location.href = '/api/results/';
```

### **Step 3: Display Results** (`results.html`)
```javascript
// Retrieve stored data
const roadmapData = JSON.parse(sessionStorage.getItem('roadmapData'));

// Render roadmap sections:
// - Summary
// - Learning Milestones
// - Projects
// - Weekly Schedule
// - Resources
```

---

## 💾 Data Flow

```
User Input Form (index.html)
    ↓
JavaScript collects data
    ↓
POST to /api/generate-roadmap/
    ↓
Django View (views.py)
    ↓
OpenAI ChatCompletion API
    ↓
Structured Response (JSON)
    ↓
Store in sessionStorage
    ↓
Redirect to results.html
    ↓
Results.html retrieves & displays data
```

---

## 🎯 Usage Example

### **Input:**
- Skillset: "Python, basic JavaScript, HTML/CSS"
- Interest: "Full-stack Web Development"
- Goal: "Get hired as a junior web developer"

### **Output:**
1. **Milestones** (7-8 key stages)
2. **Projects** (3-5 projects with:
   - Project name
   - Description
   - Duration
   - Tech stack
3. **Weekly Schedule** (12-week breakdown)
4. **Resources** (curated learning materials)

---

## 🔐 Security Notes

1. **CSRF Protection**: Always include CSRF token in POST requests
2. **API Key**: Keep OpenAI API key in environment variable (not hardcoded)
3. **Rate Limiting**: Consider adding rate limiting for production

### Better Way to Store API Key:
```python
# In settings.py
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
```

Create `.env` file:
```
OPENAI_API_KEY=sk-your-api-key-here
```

---

## 🎨 Customization

### Change GPT Model
In `views.py`:
```python
response = openai.ChatCompletion.create(
    model="gpt-4",  # or "gpt-3.5-turbo", "gpt-4-turbo"
    ...
)
```

### Modify Styling
Edit CSS in `index.html` or `results.html` static styles

### Change Prompt Template
Edit the `prompt` variable in `generate_roadmap()` function to customize output

---

## 🐛 Troubleshooting

### Issue: "OpenAI API key not found"
**Solution**: Make sure to set `openai.api_key` in views.py

### Issue: "Page not found at /api/"
**Solution**: Check that `api_features` is in `INSTALLED_APPS` in settings.py

### Issue: Templates not found
**Solution**: Ensure folder structure is:
```
api_features/templates/api_features/index.html
api_features/templates/api_features/results.html
```

### Issue: CSRF token errors
**Solution**: Include CSRF token in POST requests:
```html
{% csrf_token %}
```

---

## 📦 Dependencies

- Django 6.0+
- OpenAI 0.27.0+
- Python 3.8+

---

## 🚀 Production Deployment

Before deploying:
1. Set `DEBUG = False` in settings.py
2. Add domain to `ALLOWED_HOSTS`
3. Use environment variables for sensitive data
4. Add rate limiting
5. Implement proper error logging
6. Use dedicated API servers

---

## 📝 Next Steps

1. Install packages: `pip install django openai`
2. Add OpenAI API key to settings
3. Run `python manage.py runserver`
4. Visit `http://localhost:8000/api/`
5. Test the form submission

Enjoy! 🎉
