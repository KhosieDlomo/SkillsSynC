import datetime
import os
from login import signin, signup
import click
from firebase_auth import db, auth
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
    '''Book a meeting with your peers or mentors.'''

    if not auth.current_user:
        click.echo("Please sign up or sign in to use this feature")
        return
        
    service = get_calendar()
    
    subject = input('Event subject: ')
    date = input('Event date(DD/MM/YYYY): ')
    start_time = input('Event start time (HH:MM): ')
    end_time = input('Event end time (HH:MM): ')
    attendees = input('Emails of the participants: ').split(',')
    location = input('Event Location (e.g: "Online" or a physical address): ')

    start_hour = datetime.datetime.strptime(f'{date} {start_time}', "%d/%m/%Y %H:%M")
    end_hour = datetime.datetime.strptime(f'{date} {end_time}', "%d/%m/%Y %H:%M")

    if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
        click.echo("Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
        return
    
    time_min = start_hour.isoformat() + 'Z'
    time_max = end_hour.isoformat() + 'Z'
    event_result = service.events().list( calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True).execute()
    events = event_result.get('items', [])
    if events:
        click.echo("Schedule for another meeting at this time. select different time.")
        return
    
    event = {'summary': subject,
             'location' : location,
             'start':{'dateTime': start_hour.isoformat(), 'timeZone': 'UTC'},
             'end':{'dateTime': end_hour.isoformat(), 'timeZone': 'UTC'},
             'attendees': [{'email': email.strip()} for email in attendees],
             'reminders': {'useDefault': False,
                            'overrides' : [{'method':'email', 'minutes': 24 * 60},
                                            {'method': 'popup', 'minutes': 15},
                                            ],
                            },
            }    
    try:
        event_result = service.events().insert(calendarId='primary', body=event,sendUpdates='all').execute()
        db.collection('meetings').add({
            'subject': subject,
            'date': date,
            'start_time': start_hour.isoformat(),
            'end_time': end_hour.isoformat(),
            'attendees': attendees,
            'location': location,  
            'status': 'confirmed',
            'google_event_id': event_result.get('id'), 
        })
        click.echo(f'Event created successfully: {event_result.get('htmlLink')}') 


    except HttpError as error:
        print(f'An error occured: {error}')

@click.command()
def view_booking():
    """View all your confirmed bookings."""

    if not auth.current_user:
        click.echo("Please sign up or sign in to use this feature")
        return
    
    email = input("Enter your email to fetch bookings: ")

    try:
        bookings = db.collection('meetings').where('attendees', 'array_contains', email).stream()
        click.echo(f'Bookings for {email}:')
        for booking in bookings:
            data = booking.to_dict()
            click.echo(f"Subject: {data['subject']}, Date: {data['date']}, Time: {data['start_time']} - {data['end_time']}, Event ID: {data['google_event_id']}")
    except Exception as e:
        click.echo(f"Error fetching bookings: {e}")

@click.command
def cancel_booking():
    """Cancel an existing booking."""

    if not auth.current_user:
        click.echo("Please sign up or sign in to use this feature")
        return
    
    event_id = input("Enter the event ID to cancel: ")
    
    try:
        # Remove from Google Calendar
        cred = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('calendar', 'v3', credentials=cred)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
       
        meetings = db.collection('meetings').where('google_event_id', '==', event_id).stream()
        
        for meeting in meetings:
            db.collection('meetings').document(meeting.id).delete()
                  
        click.echo("Booking successfully canceled.")
    except Exception as e:
        click.echo(f"Error canceling booking: {e}")

#workshops
@click.command
def view_workshorp():
    """View all upcoming workshops and Available mentors and peers"""
    if not auth.current_user:
        click.echo('Please sign up or sign in to use this feature')
        return
    try:
        workshops = db.collection('workshorp').where('date', '>=', datetime.datetime.now().isoformat()).stream()
        click.echo('Upcoming workshorps')
        for workshop in workshops:
            data = workshop.to_dict()
            click.echo(f'Title: {data['Title']}, Date: {data['Date']}, Time: {data['start_time']} - {data['end_time']}, Mentors: {', '.join(data.get('mentors', []))}, Peers: {', '.join(data.get('peers',[]))}')
    except Exception as e:
        click.echo(f'Error while fetching upcoming workshops: {e}')

@click.command
def create_workshop():
    '''Mentors creating workshops and make it compulsory for peers. Only Mentors should access this feature'''
    if not auth.current_user:
        click.echo('Please sign up or sign in to use this feature')
        return
    
    user = db.collection('users').document(auth.current_user.uid).get()
    if not user.exists or user.to_dict().get('role') != 'mentor':
        click.echo("Only mentors can create workshops")
        return
    
    service = get_calendar()

    title = input('Workshop title: ')
    description = input('About the workshop: ')
    date = input("Date of the workshop(DD/MM/YYYY): ")
    start_time = input('Workshop start time(HH:MM): ')
    end_time = input('Workshop end_time (HH:MM): ')
    location = input('Workshop location: ')

    try:
        start_hour = datetime.datetime.strftime(f'{date} {start_time}', '%d/%m/%Y %H:%M')
        end_hour = datetime.datetime.strftime(f'{date} {end_time}', '%d/%m/%Y %H:%M')
    except ValueError:
        click.echo('Invalid date or time format, please use DD/MM/YYYY HH:MM')
        return
    
    if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
        click.echo("Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
        return
    
    time_min = start_hour.isoformat() + 'Z'
    time_max = end_hour.isoformat() + 'Z'
    try:
        event_result = service.events().list( calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True).execute()
        events = event_result.get('items', [])
        if events:
            click.echo("Schedule for another meeting at this time. select different time.")
            return
    except HttpError as e:
        click.echo(f'Error while fetching Events from the calender {e}')
        return
    
    peers = db.collection('users').where('role', '==', 'peer').stream()
    peers_email = []
    for peer in peers:
        if peer.exist:
            peers_email.append(peer.to_dict().get('email'))
    
    event = {'title': title,
             'description': description,
             'location': location,
             'start': {'dateTime': start_hour.isoformat(), 'timeZone': 'UTC'},
             'end': {'dateTime': end_hour.isoformat(), 'timeZone': 'UTC'},
             'attandees': [{'email': email.strip()} for email in peers_email],
             'reminders': {'useDefault': False,
                      'overrides': [{'method': 'email', 'minutes': 24 * 60},
                                     {'method': 'popup', 'minutes': 15},
                                     ]   
                          },
            }
    try:
        event_result = service.events().insert(calendarId='primary', body=event,sendUpdates='all').execute()

        workshop_data = {
            'Title': title,
            'Date': date,
            'start_time': start_hour.isoformat(),
            'end_time': end_hour.isoformat(),
            'location': location,
            'mentors': [auth.current_user.email],
            'peers': peers_email,
            'google_event_id': event_result.get('id')
        }
        db.collection('workshorp').add(workshop_data)
        click.echo('Workshop created and all peers added successfully.')
    except HttpError as error:
        print(f"An error occured while creating event: {error}")
    except Exception as e:
        click.echo(f'Failed to create workshop: {e}')

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[bookings, view_booking, cancel_booking, view_workshorp, create_workshop, signup, signin])
    cli()