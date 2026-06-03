# SkillForge - AI Skill-to-Impact Project Generator

> **Formerly MalumAI** - Now restructured with a professional modular architecture!

An AI-powered agent that analyzes a user's skills, interests, and goals, and generates personalized, high-impact projects to accelerate learning, career growth, and real-world impact.

**Aligned with:**
- 🎓 SDG 4 – Quality Education  
- 💼 SDG 8 – Decent Work & Economic Growth  

---

## 🎯 Overview

SkillForge is an intelligent career architect that:

- 📋 **Extracts user skills and interests** - Understands your profile
- 🗺️ **Maps them to impactful opportunities** - Identifies relevant projects
- 💡 **Generates project ideas with roadmap** - Creates personalized learning paths
- 🚀 **Auto-creates GitHub repositories** - Launches starter projects automatically
- 📅 **Integrates with Google Calendar** - Schedules learning milestones

This reduces the gap between learning and real-world application.

---

## ✨ Core Features

### 🧠 AI Roadmap Generation
- 5-7 key milestones tailored to your skills
- 3-5 practical projects with tech recommendations
- Weekly schedule for 12 weeks
- Resource recommendations

### 📚 Skill Intake
- Current skills
- Areas of interest
- Learning goals
- Experience level

### 🤖 Autonomous GitHub Agent
- Generates professional README files
- Creates starter code in target language
- Integrates with AI-generated roadmaps
- Runs in background threads

### 📅 Google Calendar Integration
- Weekly learning tasks
- Daily reminders (Mon-Fri)
- Project milestones
- Email and popup notifications

### 📊 Progress Tracking (Optional)
- User progress monitoring
- Completed projects
- Skill growth analytics

---

## 🏗️ System Architecture

**Modular & Maintainable Structure:**

```
apps/
├── roadmap/          # Learning roadmap generation
├── calendar/         # Google Calendar integration
├── agent/            # GitHub repository automation
└── core/             # Shared utilities
```

---

## 🔧 Tech Stack

- **Backend:** Django 4.2+ 
- **AI/LLM:** Groq API
- **Calendar:** Google Calendar API
- **Repository:** GitHub API
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Auth:** OAuth2

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git

### Step-by-Step Setup & Run

**On Windows (PowerShell):**
```powershell
# 1️⃣ Clone repository (if not already done)
git clone <repo-url>
cd skillforge

# 2️⃣ Create virtual environment
python -m venv venv

# 3️⃣ Activate virtual environment
venv\Scripts\activate

# 4️⃣ Install dependencies
pip install -r requirements.txt

# 5️⃣ Configure environment (API keys already in .env)
# If needed: cp .env.example .env

# 6️⃣ Run database migrations
python manage.py migrate

# 7️⃣ Start development server
python manage.py runserver
```

**On Mac/Linux:**
```bash
# 1️⃣ Clone repository
git clone <repo-url>
cd skillforge

# 2️⃣ Create virtual environment
python3 -m venv venv

# 3️⃣ Activate virtual environment
source venv/bin/activate

# 4️⃣ Install dependencies
pip install -r requirements.txt

# 5️⃣ Configure environment
cp .env.example .env

# 6️⃣ Run database migrations
python manage.py migrate

# 7️⃣ Start development server
python manage.py runserver
```

### Access the App
👉 Open browser: **`http://localhost:8000`**

### Verify Installation
```bash
# Check Django configuration
python manage.py check

# Run tests
python manage.py test
```

---

## 📱 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Display main form |
| `/generate_roadmap/` | POST | Generate learning roadmap |
| `/add_to_calendar/` | POST | Add events to Google Calendar |
| `/oauth_callback/` | GET | OAuth2 callback |
| `/run_agent/` | POST | Create GitHub repository |
| `/run_agent_status/<id>/` | GET | Check agent progress |

---

---

## 🔐 Security

✅ All secrets in `.env` (not committed)
✅ Fresh API keys configured
✅ Environment-specific settings
✅ Production-ready structure

---

## 🧪 Testing

```bash
python manage.py check              # Verify configuration
python manage.py test               # Run all tests
python manage.py test apps.roadmap  # Test specific app
```

---

## 📈 Future Enhancements

- [ ] API Documentation (Swagger)
- [ ] Comprehensive tests
- [ ] Docker support
- [ ] User authentication
- [ ] Analytics dashboard
- [ ] Mobile app

---

## 📄 License

MIT License - See LICENSE file

---

**Let SkillForge accelerate your learning journey! 🚀**