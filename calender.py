import datetime
import os
import click
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow 
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.events'
         ]

def get_calendar():
    cred = None
    token_path = 'token.json'
    if os.path.exists('token.json'):
        cred = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not cred or not cred.valid:
        try:
            if cred and cred.expired and cred.refresh_token:
                try:
                    cred.refresh(Request())
                except Exception as e:
                    click.echo(f'Token refresh failed: {e}. Deleting token and requesting new authentication.')
                    os.remove(token_path)  
                    return get_calendar()
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                cred = flow.run_local_server(port=0)
                
            with open('token.json', 'w') as token:
                token.write(cred.to_json())

        except Exception as e:
            click.echo(f'Authentication Error: {e}')
            return None
        
    return build('calendar', 'v3', credentials=cred)   