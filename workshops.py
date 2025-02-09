import datetime
import click
from firebase_auth import db, auth, require_auth
from events import get_calendar
from googleapiclient.errors import HttpError
from login import signin, signup

#workshops
@click.command()
def view_workshop():
    """View all upcoming workshops and Available mentors and peers"""
    if not require_auth():
        click.echo('Please sign up or sign in to use this feature')
        return
    
    try:
        workshops = db.collection('workshops').where('date', '>=', datetime.datetime.now().isoformat()).stream()
        click.echo('Upcoming workshops')

        for workshop in workshops:
            data = workshop.to_dict()
            click.echo(f'Title: {data['Title']}, Date: {data['Date']}, Time: {data['start_time']} - {data['end_time']}, Mentors: {', '.join(data.get('mentors', []))}, Peers: {', '.join(data.get('peers',[]))}')
    
    except Exception as e:
        click.echo(f'Error while fetching upcoming workshops: {e}')

@click.command()
def create_workshop():
    '''Mentors creating workshops and make it compulsory for peers. Only Mentors should access this feature'''
    if not require_auth():
        click.echo('Please sign up or sign in to use this feature')
        return
    
    user = db.collection('users').document(auth.current_user.uid).get()
    if not user.exists or user.to_dict().get('role') != 'mentor':
        click.echo("Only mentors can create workshops")
        return
    
    service = get_calendar()
    if not service:
        return

    title = click.prompt('Workshop title: ')
    description = click.prompt('About the workshop: ')
    date = click.prompt("Date of the workshop(DD/MM/YYYY): ")
    start_time = click.prompt('Workshop start time(HH:MM): ')
    end_time = click.prompt('Workshop end_time (HH:MM): ')
    location = click.prompt('Workshop location: ')

    try:
        start_hour = datetime.datetime.strptime(f'{date} {start_time}', '%d/%m/%Y %H:%M')
        end_hour = datetime.datetime.strptime(f'{date} {end_time}', '%d/%m/%Y %H:%M')
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
            peer_email = peer.to_dict().get('email')
            if peer_email:
                peers_email.append(peer_email)
    
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
        db.collection('workshops').add(workshop_data)
        click.echo('Workshop created and all peers added successfully.')
    except HttpError as error:
        print(f"An error occured while creating event: {error}")
    except Exception as e:
        click.echo(f'Failed to create workshop: {e}')

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[view_workshop, create_workshop, signup, signin])
    cli()