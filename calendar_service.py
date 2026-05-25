import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_calendar_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError("credentials.json not found. Please download OAuth client ID credentials from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def create_appointment(date_str, time_str, patient_name, reason="Dentist Appointment"):
    """
    Creates a calendar event.
    date_str: "YYYY-MM-DD"
    time_str: "HH:MM" (24-hour format)
    """
    service = get_calendar_service()
    if not service:
        return "Failed to connect to Google Calendar."

    try:
        # Combine date and time
        start_datetime_str = f"{date_str}T{time_str}:00"
        start_time = datetime.datetime.fromisoformat(start_datetime_str)
        
        # Assume 1 hour appointment
        end_time = start_time + datetime.timedelta(hours=1)
        
        event = {
            'summary': f'{reason} for {patient_name}',
            'description': 'Automated booking via Voice Bot.',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }


        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Successfully booked appointment for {patient_name} on {date_str} at {time_str}. Event Link: {event.get('htmlLink')}"
    except Exception as e:
        return f"Failed to book appointment due to an error: {str(e)}"

if __name__ == "__main__":
    # Test
    # print(create_appointment("2026-06-01", "14:00", "John Doe"))
    pass
