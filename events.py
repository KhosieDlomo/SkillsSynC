import datetime
import os
import click
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow 
from googleapiclient.discovery import build  
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.events'
         ]

def get_calendar():
    cred = None
    if os.path.exists('token.json'):
        cred = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            cred = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(cred.to_json())
    return build('calendar', 'v3', credentials=cred)

@click.command()
def bookings():
    service = get_calendar()
    
    subject = input('Event subject: ')
    date = input('Event date(DD-MM-YYYY): ')
    start_time = input('Event start time (HH-MM): ')
    end_time = input('Event end time (HH-MM): ')
    attendees = input('Emails of the participants: ').split(',')

    start_hour = datetime.datetime.strptime(f'{date} {start_time}', "%d-%m-%Y %H:%M")
    end_hour = datetime.datetime.strptime(f'{date} {end_time}', "%d-%m-%Y %H:%M")

    if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
        click.echo("Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
        return
    event = {'summary': subject,
                'start':{'dateTime': start_hour.isoformat(), 'timeZone': 'UTC'},
                'end':{'dateTime': end_hour.isoformat(), 'timeZone': 'UTC'},
                'attendees': [{'email': email.strip() for email in attendees}],
                'reminders': {'useDefault': False,
                            'overrides' : [{'method':'email', 'minutes': 24 * 60},
                                            {'method': 'popup', 'minutes': 15},
                                            ],
                            },
            }    
    try:
        event_result = service.events().insert(calendarId='primary', body=event,sendUpdates='all').execute()
        click.echo(f'Event created successfully: {event_result.get('htmlLink')}') 

    except HttpError as error:
        print(f'An error occured: {error}')