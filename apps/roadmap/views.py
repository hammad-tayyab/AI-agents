"""
Roadmap Generation Views

API endpoints for generating and displaying learning roadmaps.
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from .services import RoadmapService


@ensure_csrf_cookie
def index(request):
    """Display the main input form and dashboard."""
    return render(request, 'index.html')


@require_http_methods(["POST"])
def generate_roadmap(request):
    """
    API endpoint to generate a personalized learning roadmap.

    Expected POST data:
    {
        "skillset": "user's current skills",
        "interest": "area of interest",
        "goal": "learning goal (optional)"
    }

    Returns:
    {
        "success": true/false,
        "data": {...roadmap data...},
        "error": "error message if failed"
    }
    """
    try:
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON body: {str(e)}'
            }, status=400)

        skillset = data.get('skillset', '').strip()
        interest = data.get('interest', '').strip()
        goal = data.get('goal', '').strip()

        if not skillset or not interest:
            return JsonResponse({
                'success': False,
                'error': 'Skillset and Interest fields are required'
            }, status=400)

        service = RoadmapService()
        result = service.generate_roadmap(skillset, interest, goal)

        return JsonResponse({'success': True, 'data': result})

    except Exception as api_error:
        error_msg = str(api_error)
        if 'decommissioned' in error_msg.lower():
            return JsonResponse({
                'success': False,
                'error': 'Model is unavailable. Please try again later.'
            }, status=503)
        elif 'rate_limit' in error_msg.lower():
            return JsonResponse({
                'success': False,
                'error': 'API rate limit exceeded. Please try again in a moment.'
            }, status=429)
        else:
            return JsonResponse({
                'success': False,
                'error': f'AI API Error: {error_msg}'
            }, status=500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


def results(request):
    """Display the results from roadmap generation."""
    return render(request, 'index.html')
