from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from groq import Groq

# Configure Groq API key
GROQ_API_KEY = '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'  # Replace with your actual Groq API key
client = Groq(api_key=GROQ_API_KEY)

@ensure_csrf_cookie
def index(request):
    """Display the input form"""
    return render(request, 'api_features/index.html')

@require_http_methods(["POST"])
def generate_roadmap(request):
    """
    API endpoint that takes skill, interest, and goal as input
    Returns a personalized learning roadmap with projects and timeline
    """
    try:
        # Ensure we received JSON
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({
                'success': False,
                'error': 'Expected JSON body, received HTML or invalid payload.'
            }, status=400)
        skillset = data.get('skillset', '')
        interest = data.get('interest', '')
        goal = data.get('goal', '')
        
        # Validate inputs
        if not all([skillset, interest, goal]):
            return JsonResponse({
                'success': False,
                'error': 'Please fill all fields: skillset, interest, and goal'
            }, status=400)
        
        # Create the prompt for GPT
        prompt = f"""Based on the following user profile, create a detailed learning roadmap:

Current Skillset: {skillset}
Area of Interest: {interest}
Learning Goal: {goal}

Please provide:
1. A personalized learning path with 5-7 key milestones
2. 3-5 practical projects the user should complete (with project names and brief descriptions)
3. An estimated timeline in weeks for each project
4. Resources and tech stack recommendations
5. A weekly schedule/timetable for the next 12 weeks

Format the response as structured JSON with the following keys:
- "roadmap" (array of milestones)
- "projects" (array of projects with name, description, duration_weeks, tech_stack)
- "weekly_schedule" (array of 12 weeks with tasks)
- "resources" (array of recommended resources)
- "summary" (brief overview of the plan)
"""
        
        # Call Groq API with fallback models in case a model is decommissioned
        models_to_try = [
            "gemma-7b",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
        ]

        gpt_response = None
        last_err = None
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert learning roadmap creator. Provide structured, practical, and achievable learning plans."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )

                # Extract response
                # Groq client returns objects; adapt to commonly used shape
                try:
                    gpt_response = response.choices[0].message.content
                except Exception:
                    # Fallback extraction if the response shape differs
                    gpt_response = getattr(response, 'text', None) or str(response)

                # If we got a response, stop trying other models
                if gpt_response:
                    break

            except Exception as e:
                last_err = e
                # If API indicates model decommissioned, try next model
                err_msg = str(e)
                if 'decommissioned' in err_msg or 'model' in err_msg:
                    continue
                # For other errors, keep last and continue trying
                continue

        if not gpt_response:
            # Return a helpful error message to the client
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate roadmap. Last error: ' + (str(last_err) if last_err else 'unknown')
            }, status=500)
        
        # Try to parse as JSON, if it fails, structure it
        try:
            result = json.loads(gpt_response)
        except json.JSONDecodeError:
            result = {
                'raw_response': gpt_response,
                'formatted': True
            }
        
        return JsonResponse({
            'success': True,
            'data': result
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def results(request):
    """Display the results from the generation"""
    return render(request, 'api_features/results.html')
