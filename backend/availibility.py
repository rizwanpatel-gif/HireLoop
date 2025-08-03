from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']

def check_availability_and_schedule():
    # Load credentials
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    # Define the time range to check availability
    start_time = datetime.utcnow() + timedelta(days=1)  # Start tomorrow
    end_time = start_time + timedelta(hours=1)  # Check for 1-hour slot

    # Format time for Google Calendar API
    start_time_iso = start_time.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time_iso = end_time.isoformat() + 'Z'

    print(f"🔍 Checking availability from {start_time_iso} to {end_time_iso}...")

    # Query events in the time range
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time_iso,
        timeMax=end_time_iso,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if events:
        print("❌ You are busy during this time. Finding next available slot...")
        # Iterate to find the next free hour
        while events:
            start_time += timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)
            start_time_iso = start_time.isoformat() + 'Z'
            end_time_iso = end_time.isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time_iso,
                timeMax=end_time_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

        print(f"✅ Found free slot from {start_time_iso} to {end_time_iso}")
    else:
        print(f"✅ You are free during this time!")

    # Schedule a meeting in the free slot
    event = {
        'summary': 'Automated Meeting',
        'location': 'Virtual',
        'description': 'This is a test meeting scheduled via Google Calendar API.',
        'start': {
            'dateTime': start_time_iso,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time_iso,
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': 'example@gmail.com'},  # Add attendees here
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # Reminder 1 day before
                {'method': 'popup', 'minutes': 10},  # Reminder 10 minutes before
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"✅ Meeting scheduled: {event.get('htmlLink')}")

if __name__ == "__main__":
    check_availability_and_schedule()