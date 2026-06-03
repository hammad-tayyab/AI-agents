"""
Google Calendar Views

API endpoints for Google Calendar integration.
"""

import json
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .oauth import OAuth2Manager
from .services import CalendarService


@require_http_methods(["POST"])
def add_to_calendar(request):
    """
    API endpoint to add roadmap to Google Calendar.

    Expected POST data:
    {
        "roadmap_data": {...},
        "start_date": "YYYY-MM-DD" (optional)
    }
    """
    try:
        data = json.loads(request.body)
        roadmap_data = data.get('roadmap_data', {})

        if not roadmap_data:
            return JsonResponse({
                'success': False,
                'error': 'roadmap_data is required'
            }, status=400)

        start_date = None
        if data.get('start_date'):
            try:
                start_date = datetime.datetime.strptime(
                    data['start_date'],
                    '%Y-%m-%d'
                ).date()
            except Exception:
                pass

        service = CalendarService()
        result = service.add_roadmap_to_calendar(roadmap_data, start_date)

        return JsonResponse({
            'success': True,
            'message': f'Successfully added {result["events_created"]} events to your Google Calendar',
            'events_created': result['events_created']
        })

    except FileNotFoundError as e:
        return JsonResponse({
            'success': False,
            'oauth_required': True,
            'error': str(e)
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def oauth_callback(request):
    """
    Handle OAuth callback from Google Calendar.

    This endpoint is called after the user authorizes the application.
    """
    try:
        oauth_manager = OAuth2Manager()

        state = request.session.get('oauth_state')
        if not state or state != request.GET.get('state'):
            return JsonResponse({
                'success': False,
                'error': 'Invalid OAuth state'
            }, status=400)

        # Get redirect URI from reverse URL
        redirect_uri = request.build_absolute_uri(reverse('calendar:oauth_callback'))

        # Exchange code for credentials
        _, _, flow = oauth_manager.initiate_oauth_flow(redirect_uri)
        code = request.GET.get('code')
        oauth_manager.exchange_code_for_credentials(flow, code)

        del request.session['oauth_state']
        del request.session['oauth_flow']

        return JsonResponse({
            'success': True,
            'message': 'Google Calendar authenticated successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'OAuth callback failed: {str(e)}'
        }, status=500)
