"""
GitHub Agent Views

API endpoints for autonomous GitHub repository creation.
"""

import json
import uuid
import threading
import traceback
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .services import GitHubAgentService

# In-memory task store for background GitHub repo creation tasks
TASKS = {}


@require_http_methods(["POST"])
def run_agent_endpoint(request):
    """
    API endpoint to initialize and run the agent.
    Creates a GitHub repository with AI-generated project files based on roadmap.

    Expected POST data:
    {
        "skillset": "user's skills",
        "interest": "area of interest",
        "goal": "learning goal",
        "roadmap_data": {...},
        "gpt_response": "..."
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
        roadmap_data = data.get('roadmap_data', {})
        gpt_response = data.get('gpt_response', '')

        if roadmap_data and not gpt_response:
            gpt_response = json.dumps(roadmap_data)

        if not skillset or not interest:
            return JsonResponse({
                'success': False,
                'error': 'Skillset and Interest fields are required'
            }, status=400)

        task_id = uuid.uuid4().hex
        TASKS[task_id] = {
            'status': 'in_progress',
            'message': 'Your GitHub Repo is being made please wait..',
            'repo_url': None,
            'error': None
        }

        def _background_run_agent(tid, skill, intr, gl, gpt_resp):
            """Background thread function to run the agent."""
            try:
                service = GitHubAgentService()
                repo_url = service.run_agent(skill, intr, gl, gpt_resp, task_id=tid, task_store=TASKS)
                TASKS[tid]['status'] = 'completed'
                TASKS[tid]['repo_url'] = repo_url
                TASKS[tid]['message'] = 'GitHub repository created successfully!'
            except Exception as bg_e:
                tb = traceback.format_exc()
                TASKS[tid]['status'] = 'failed'
                TASKS[tid]['error'] = tb
                TASKS[tid]['message'] = f'Failed to create GitHub repository: {str(bg_e)}'

        thread = threading.Thread(
            target=_background_run_agent,
            args=(task_id, skillset, interest, goal, gpt_response),
            daemon=True
        )
        thread.start()

        try:
            status_path = reverse('agent:run_agent_status', args=[task_id])
            status_url = request.build_absolute_uri(status_path)
        except Exception:
            status_url = f'/run_agent_status/{task_id}/'

        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'status_url': status_url,
            'message': TASKS[task_id]['message']
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Agent execution failed: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def run_agent_status(request, task_id):
    """
    Poll the status of a background run_agent task.

    Args:
        task_id (str): Unique task identifier

    Returns:
        JSON with task status, progress message, and result URL if completed
    """
    task = TASKS.get(task_id)
    if not task:
        return JsonResponse({
            'success': False,
            'error': 'Invalid task id'
        }, status=404)

    return JsonResponse({'success': True, 'task': task})
