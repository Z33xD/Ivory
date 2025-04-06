import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES=['https://www.googleapis.com/auth/calendar']

def main():
    creds=None

    if os.path.exists('token.json'):
        creds=credentials.Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow=InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds=flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service=build("calendar", "v3", credentials=creds)
        event={
            'summary': 'Python Event',
            'location': 'Online',
            'description': 'This is a test event created using the Google Calendar API.',
            'colorId':6,
            'start': {
                'dateTime': "2023-06-03T09:00:00+09:00",
                'timeZone': 'Europe/Vienna',
            },
            'end': {
                'dateTime': "2023-06-03T17:00:00+09:00",
                'timeZone': 'Europe/Vienna',
            },
            "recurrence":{
                "RRULE": "FREQ=DAILY;COUNT=3"
            },
            "attendees": [
                {"email":"gargarshi09@gmail.com"},
                {"email":"nstarry333@gmail.com"}
            ]
        }
        event=service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        

if __name__=="__main__":
    main()