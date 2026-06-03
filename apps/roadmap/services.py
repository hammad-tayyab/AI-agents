"""
Roadmap Generation Service

Handles AI-powered learning roadmap generation using Groq API.
"""

import json
import os
from groq import Groq
from django.conf import settings


class RoadmapService:
    """Service for generating personalized learning roadmaps."""

    def __init__(self):
        """Initialize Groq client with API key."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def generate_roadmap(self, skillset, interest, goal=''):
        """
        Generate a personalized learning roadmap based on user profile.

        Args:
            skillset (str): User's current skills
            interest (str): Area of interest
            goal (str): Learning goal

        Returns:
            dict: Roadmap data with projects, milestones, and schedule
        """
        prompt = f"""Based on the following user profile, create a detailed learning roadmap:

Current Skillset: {skillset}
Area of Interest: {interest}
Learning Goal: {goal if goal else 'General learning and skill development'}

Must provide:
1. A personalized learning path with 5-7 key milestones
2. 3-5 practical projects the user should complete (with project names and brief descriptions)
3. An estimated timeline in weeks for each project
4. Resources and tech stack recommendations
5. A weekly schedule/timetable for the next 12 weeks

Strictly Format the response as structured JSON with the following keys:
- "roadmap" (array of milestones) - Note: use "roadmap" key, not "milestone"
- "projects" (array of projects with name, description, duration_weeks, tech_stack)
- "weekly_schedule" (array of 12 weeks with tasks)
- "resources" (array of recommended resources)
- "summary" (brief overview of the plan)
- dont respond with anything else, just the plain json format, no ``` at the end or start
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert learning roadmap creator. Provide structured, practical, and achievable learning plans. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=8000
        )

        gpt_response = response.choices[0].message.content

        if not gpt_response:
            raise ValueError("Empty response from AI model")

        # Clean the response - remove markdown code blocks if present
        cleaned_response = gpt_response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        try:
            result = json.loads(cleaned_response)
            if not isinstance(result, dict):
                raise json.JSONDecodeError("Response is not a JSON object", cleaned_response, 0)

            # Handle field name mismatch
            if 'milestone' in result and 'roadmap' not in result:
                result['roadmap'] = result.pop('milestone')

        except json.JSONDecodeError as e:
            result = {
                'summary': cleaned_response[:500] + ('...' if len(cleaned_response) > 500 else ''),
                'raw_response': cleaned_response,
                'roadmap': [],
                'projects': [],
                'weekly_schedule': [],
                'resources': [],
                'parse_error': f'JSON parsing failed: {str(e)}'
            }

        return result
