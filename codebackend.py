from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only, restrict in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# Define input data structure
class UserInput(BaseModel):
    skills: str
    hobbies: str
    goal: str = ""  # optional

# Example AI simulation function
def generate_projects(skills, hobbies, goal):
    """
    Generates structured projects based on user input.
    Replace this with real AI call for dynamic generation.
    """
    return [
        {
            "project_name": "Python Coding Workshop",
            "skills_required": ["Python"],
            "impact": "Teach Python through hands-on exercises.",
            "roadmap": [
                "Week 1: Design beginner-friendly Python lessons",
                "Week 2: Create interactive exercises",
                "Week 3: Conduct workshops",
                "Week 4: Collect feedback and improve"
            ],
            "README": "Hands-on Python workshop project.",
            "mentor_message": "Hi [Mentor Name], I'd love your advice on this project."
        },
        {
            "project_name": "AI Chess Trainer",
            "skills_required": ["Python", "Chess"],
            "impact": "Build an AI coach to help beginners improve chess skills.",
            "roadmap": [
                "Week 1: Build basic chess engine",
                "Week 2: Integrate AI opponent",
                "Week 3: Add performance tracking and feedback",
                "Week 4: Beta test with beginners"
            ],
            "README": "AI-powered chess trainer for beginners.",
            "mentor_message": "Hi [Mentor Name], can you guide me on AI difficulty scaling?"
        },
        {
            "project_name": "Digital Art Story Platform",
            "skills_required": ["Digital Art", "Creativity"],
            "impact": "Enable users to create and share digital stories.",
            "roadmap": [
                "Week 1: Design platform layout and story submission flow",
                "Week 2: Implement backend and user accounts",
                "Week 3: Integrate upload and editing features",
                "Week 4: Launch beta and collect feedback"
            ],
            "README": "Digital storytelling platform.",
            "mentor_message": "Hi [Mentor Name], I’d love feedback on user engagement."
        }
    ]

# POST endpoint to generate projects
@app.post("/generate")
async def generate(input: UserInput):
    projects = generate_projects(input.skills, input.hobbies, input.goal)
    return {"projects": projects}

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
