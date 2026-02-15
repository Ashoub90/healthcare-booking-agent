import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class CalendarService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.creds = self._load_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds)

    def _load_credentials(self):
        creds = None
        # Checks for the token generated with test_calendar.py
        paths = ['token.json', 'app/token.json']
        token_path = next((p for p in paths if os.path.exists(p)), None)
        
        if token_path:
            creds = Credentials.from_authorized_user_file(token_path, self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise Exception("Token not found. Run test_calendar.py locally first!")
        return creds

    def get_busy_slots(self, target_date: datetime.date):
        """Fetches external Google events to block them in availability logic."""
        # Define the start and end of the day in ISO format
        start_dt = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + 'Z'
        end_dt = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId='primary', timeMin=start_dt, timeMax=end_dt,
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        busy_slots = []
        for e in events_result.get('items', []):
            start = e['start'].get('dateTime', e['start'].get('date'))
            end = e['end'].get('dateTime', e['end'].get('date'))
            
            # Convert ISO strings to datetime objects for comparison in your logic
            busy_slots.append((
                datetime.datetime.fromisoformat(start.replace('Z', '+00:00')).replace(tzinfo=None),
                datetime.datetime.fromisoformat(end.replace('Z', '+00:00')).replace(tzinfo=None)
            ))
        return busy_slots

    def create_event(self, summary, start_time, end_time):
        """Adds the appointment to Google Calendar with UTC suffix."""
        event = {
            'summary': summary,
            # Adding 'Z' ensures Google knows this is UTC
            'start': {'dateTime': start_time.isoformat() + 'Z'},
            'end': {'dateTime': end_time.isoformat() + 'Z'},
        }
        return self.service.events().insert(calendarId='primary', body=event).execute()
    

    def delete_event(self, event_id):
            """Removes an event from Google Calendar."""
            try:
                self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            except Exception as e:
                # Handle the case where the event was already deleted manually
                print(f"Google Delete Error: {e}")    