"""
Google Calendar Service

Handles Google Calendar API operations and event management.
"""

import datetime
from googleapiclient.discovery import build
from django.conf import settings
from .oauth import OAuth2Manager


class CalendarService:
    """Service for managing Google Calendar events."""

    def __init__(self, creds=None):
        """Initialize Calendar service with credentials."""
        self.oauth_manager = OAuth2Manager()
        if creds:
            self.credentials = creds
        else:
            self.credentials = self.oauth_manager.load_credentials_from_file()
        self.service = None

    def get_service(self):
        """Get authenticated Google Calendar service."""
        if not self.credentials or not self.credentials.valid:
            self.credentials = self.oauth_manager.load_credentials_from_file()

        if not self.credentials:
            raise Exception("Google Calendar credentials not available")

        if self.credentials.expired and self.credentials.refresh_token:
            self.oauth_manager.refresh_credentials(self.credentials)

        self.service = build('calendar', 'v3', credentials=self.credentials)
        return self.service

    def add_roadmap_to_calendar(self, roadmap_data, start_date=None):
        """
        Add roadmap tasks to Google Calendar.

        Args:
            roadmap_data (dict): Roadmap data with projects and schedule
            start_date (date): Start date for calendar events (defaults to today)

        Returns:
            dict: Result with success status and created event IDs
        """
        service = self.get_service()
        created_events = []

        if start_date is None:
            start_date = datetime.date.today()

        # Add weekly schedule events
        if roadmap_data.get('weekly_schedule') and isinstance(roadmap_data['weekly_schedule'], list):
            for week_idx, week_data in enumerate(roadmap_data['weekly_schedule'][:12]):
                week_num = week_idx + 1
                week_start = start_date + datetime.timedelta(weeks=week_idx)

                if isinstance(week_data, str):
                    week_content = week_data
                elif isinstance(week_data, dict):
                    week_content = week_data.get('tasks', week_data.get('description', ''))
                else:
                    week_content = str(week_data)

                weekly_event = {
                    'summary': f'📚 Week {week_num}: Learning Tasks - Skill Development',
                    'description': f'Time to work on your skills!\n\n{week_content}\n\n💡 Remember: Consistency is key to mastering new skills!',
                    'start': {'date': week_start.isoformat(), 'timeZone': 'UTC'},
                    'end': {'date': (week_start + datetime.timedelta(days=6)).isoformat(), 'timeZone': 'UTC'},
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 60},
                        ],
                    },
                }

                created_event = service.events().insert(calendarId='primary', body=weekly_event).execute()
                created_events.append(created_event.get('id'))

                # Daily reminders Monday-Friday
                for day_offset in range(5):
                    learning_day = week_start + datetime.timedelta(days=day_offset)
                    day_name = learning_day.strftime('%A')

                    daily_event = {
                        'summary': f'📖 Daily Learning: Week {week_num} - {day_name}',
                        'description': f'Daily skill development reminder!\n\nFocus for today:\n{week_content}\n\n⏰ Set aside time today to work on your learning goals.',
                        'start': {'date': learning_day.isoformat(), 'timeZone': 'UTC'},
                        'end': {'date': learning_day.isoformat(), 'timeZone': 'UTC'},
                        'colorId': '5',
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'email', 'minutes': 24 * 60},
                                {'method': 'email', 'minutes': 60},
                                {'method': 'popup', 'minutes': 30},
                                {'method': 'popup', 'minutes': 0},
                            ],
                        },
                    }

                    created_daily = service.events().insert(calendarId='primary', body=daily_event).execute()
                    created_events.append(created_daily.get('id'))

        # Add project milestone events
        if roadmap_data.get('projects') and isinstance(roadmap_data['projects'], list):
            current_week = 0
            for project in roadmap_data['projects']:
                project_name = project.get('name', project.get('project_name', 'Project'))
                duration = project.get('duration_weeks', project.get('duration', 1))

                try:
                    if isinstance(duration, str):
                        duration = int(duration.split()[0]) if duration.split()[0].isdigit() else 1
                    else:
                        duration = int(duration)
                except Exception:
                    duration = 1

                project_start = start_date + datetime.timedelta(weeks=current_week)
                project_end = project_start + datetime.timedelta(weeks=duration)

                project_description = project.get('description', '')
                tech_stack = project.get('tech_stack', [])
                tech_str = ', '.join(tech_stack) if isinstance(tech_stack, list) else str(tech_stack)

                event = {
                    'summary': f'🚀 Project: {project_name}',
                    'description': f'Project Milestone: {project_name}\n\n{project_description}\n\n{"Tech Stack: " + tech_str if tech_str else ""}\n\n💪 Stay focused and complete this project!',
                    'start': {'date': project_start.isoformat(), 'timeZone': 'UTC'},
                    'end': {'date': project_end.isoformat(), 'timeZone': 'UTC'},
                    'colorId': '10',
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'email', 'minutes': 2 * 60},
                            {'method': 'popup', 'minutes': 60},
                            {'method': 'popup', 'minutes': 15},
                        ],
                    },
                }

                created_event = service.events().insert(calendarId='primary', body=event).execute()
                created_events.append(created_event.get('id'))
                current_week += duration

        return {
            'success': True,
            'events_created': len(created_events),
            'event_ids': created_events
        }
