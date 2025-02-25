import datetime
import click
from firebase_auth import db, auth, current_session
from events import get_calendar
from google.cloud import firestore
from googleapiclient.errors import HttpError
from login import signin, signup

#workshops
@click.command()
def view_workshop():
    """View all upcoming workshops and Available mentors and peers"""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    try:
        workshops = db.collection('workshops').stream()
        all_workshop = []
        for workshop in workshops:
            data = workshop.to_dict()
            all_workshop.append(data)
                
        all_workshop.sort(key=lambda i: datetime.datetime.strptime(i['Date'], '%d/%m/%Y'))
        if not all_workshop:
            click.echo('No upcoming workshops found.')
            main_menu()
            return
        
        click.echo('---Upcoming workshops---')
        for num, workshop in all_workshop:
            try:
                start_time = datetime.datetime.fromisoformat(workshop['start_time'])
                end_time = datetime.datetime.fromisoformat(workshop['end_time'])
                formatted_date = start_time.strftime('%A, %d %B %Y')
                formatted_start_time = start_time.strftime('%I:%M %p')
                formatted_end_time = end_time.strftime('%I:%M %p')

            except ValueError:
                formatted_date = workshop['Date']
                formatted_start_time = workshop['start_time']
                formatted_end_time = workshop['end_time']

            click.echo(f"\n📅 Workshop {num + 1}")
            click.echo(f"├─🗓️ Date: {formatted_date}")
            click.echo(f"├─📝 Title: {workshop['Title']}")
            click.echo(f"├─🕒 {formatted_start_time} - {formatted_end_time}")
            click.echo(f"├─📌 Location: {workshop['location']}")
            click.echo(f"├─👤 Mentors: {', '.join(set(workshop.get('mentors', [])))}")
            click.echo(f"├─👥 Peers: {', '.join(set(workshop.get('peers', [])))}")
            if workshop.get('online_link'):
                click.echo(f"└─ 🔗 Online Link: {workshop['online_link']}")
            else:
                click.echo("└─ 🔗 Online Link: Not provided")
            click.echo("-" * 100)  
        
        main_menu()
    
    except Exception as e:
        click.echo(f'Error while fetching upcoming workshops: {e}')
        main_menu()

@click.command()
def create_workshop():
    '''Mentors creating workshops and make it compulsory for peers. Only Mentors should access this feature'''
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    user_id = current_session.get('user_id')
    user_email = current_session.get('email')

    if not user_id or not user_email:
        click.echo("User not authenticated. Please sign in.")
        main_menu()
        return

    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        role = user_doc.to_dict().get('role', 'peer')
    else:
        role = 'peer'
        
    if role != 'mentor':
        click.echo("Only mentors can create workshops")
        main_menu()
        return
    
    service = get_calendar()
    if not service:
        click.echo("Failed to initialize Google Calendar service.")
        main_menu()
        return

    title = click.prompt('Workshop title ')
    description = click.prompt('About the workshop ')
    date = click.prompt("Date of the workshop(DD/MM/YYYY) ")
    start_time = click.prompt('Workshop start time(HH:MM) ')
    end_time = click.prompt('Workshop end_time (HH:MM) ')
    location = click.prompt('Workshop location ')

    online_link = None
    if location == 'online'.lower():
        online_link = click.prompt("Enter the online meeting link ")

    try:
        start_hour = datetime.datetime.strptime(f'{date} {start_time}', '%d/%m/%Y %H:%M')
        end_hour = datetime.datetime.strptime(f'{date} {end_time}', '%d/%m/%Y %H:%M')

    except ValueError:
        click.echo('Invalid date or time format, please use DD/MM/YYYY HH:MM')
        main_menu()
        return
    
    if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
        click.echo("Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
        main_menu()
        return
    
    time_min = start_hour.isoformat() + 'Z'
    time_max = end_hour.isoformat() + 'Z'
    try:
        event_result = service.events().list( calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True).execute()
        events = event_result.get('items', [])
        
        if events:
            click.echo("Conflicting events found during the specified time.")
            for event in events:
                click.echo(f"Event: {event.get('summary')}, Start: {event.get('start')}, End: {event.get('end')}")
            click.echo("Please select a different time.")
            main_menu()
            return
        
    except HttpError as e:
        click.echo(f'Error while fetching Events from the calender {e}')
        main_menu()
        return
    
    peers = db.collection('users').where(filter=firestore.FieldFilter('role', '==', 'peer')).stream()
    peers_email = set()
    for peer in peers:
        if peer.exists:
            peer_email = peer.to_dict().get('email')
            if peer_email:
                peers_email.add(peer_email.strip())

    mentors = db.collection('users').where(filter=firestore.FieldFilter('role', '==', 'mentor')).stream()
    mentors_email = set()  
    for mentor in mentors:
        if mentor.exists:
            mentor_email = mentor.to_dict().get('email')
            if mentor_email:
                mentors_email.add(mentor_email.strip())

    if user_email:
        peers_email.add(user_email)

    attendees = [{'email': email.strip()} for email in mentors_email.union(peers_email)]
    
    event = {'title': title,
             'description': description,
             'location': location,
             'start': {'dateTime': start_hour.isoformat(), 'timeZone': 'UTC'},
             'end': {'dateTime': end_hour.isoformat(), 'timeZone': 'UTC'},
             'attendees': attendees,
             'reminders': {'useDefault': False,
                      'overrides': [{'method': 'email', 'minutes': 24 * 60},
                                     {'method': 'popup', 'minutes': 15},
                                     ]   
                          },
            }
    
    if online_link:
            event['description'] = f"{event.get('description', '')}\nJoin online: {online_link}"
    try:
        event_result = service.events().insert(calendarId='primary', body=event,sendUpdates='all').execute()

        workshop_data = {
            'Title': title,
            'Date': date,
            'start_time': start_hour.isoformat(),
            'end_time': end_hour.isoformat(),
            'location': location,
            'mentors': list(user_email),
            'peers': list(peers_email),
            'google_event_id': event_result.get('id'),
            'online_link': online_link
        }
        db.collection('workshops').add(workshop_data)
        click.echo('Workshop created and all peers added successfully.')
        
    except HttpError as error:
        click.echo(f"An error occured while creating event: {error}")
    except Exception as e:
        click.echo(f'Failed to create workshop: {e}')
        
    main_menu()

def cancel_workshop():
    """Cancel an existing workshop."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    user_id = current_session.get('user_id')
    user_email = current_session.get('email')

    if not user_id or not user_email:
        click.echo("User not authenticated. Please sign in.")
        main_menu()
        return
    
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        role = user_doc.to_dict().get('role', 'peer')
    else:
        role = 'peer'
        
    if role != 'mentor':
        click.echo("Only mentors can cancel workshops.")
        main_menu()
        return

    click.echo(f"Fetching all workshops...")

    try:
        workshop_ref = db.collection('workshops').stream()
        workshops = list(workshop_ref)

        if not workshops:
            click.echo("No workshops found.")
            main_menu()
            return
        
        click.echo('\n--- Upcoming Workshops: ---')
        for num, workshop in enumerate(workshops):
            data = workshop.to_dict()

            try:
                start_time = datetime.datetime.fromisoformat(data['start_time'])
                end_time = datetime.datetime.fromisoformat(data['end_time'])
                formatted_date = start_time.strftime('%A, %d %B %Y')
                formatted_start_time = start_time.strftime('%I:%M %p')
                formatted_end_time = end_time.strftime('%I:%M %p')

            except ValueError:
                formatted_date = data['Date']
                formatted_start_time = data['start_time']
                formatted_end_time = data['end_time']

            click.echo(f"\n📅 Workshop {num + 1}")
            click.echo(f"├─ 📝 Title: {data['Title']}")
            click.echo(f"├─ 🗓️ Date: {formatted_date}")
            click.echo(f"├─ 🕒 Time: {formatted_start_time} - {formatted_end_time}")
            click.echo(f"├─ 📍 Location: {data['location']}")
            click.echo(f"├─ 👤 Mentors: {', '.join(set(data.get('mentors', [])))}")
            click.echo(f"├─ 👥 Peers: {', '.join(set(data.get('peers', [])))}")
            if data.get('online_link'):
                click.echo(f"└─ 🔗 Online Link: {data['online_link']}")
            else:
                click.echo("└─ 🔗 Online Link: Not provided")
            click.echo("-" * 100)
           
            while True:
                try:
                    choice = int(click.prompt(f"Enter the number of the workshop to cancel (1 - {len(workshops)}), or 0 to cancel "))
                    if 0 <= choice <= len(workshops):
                        break
                    else:
                        click.echo("Invalid choice. Please enter a number within the range.")
                
                except ValueError:
                    click.echo("Invalid input. Please enter a number.")

            if choice == 0:
                click.echo("Cancel operation aborted.")
                main_menu()
                return
            
            selected_workshop = workshops[choice - 1]
            workshop_data = selected_workshop.to_dict()
            event_id = workshop_data.get('google_event_id')

            service = get_calendar()
            if not service:
                click.echo("Failed to initialize Google Calendar service.")
                main_menu()
                return

            try:
                service.events().delete(calendarId='primary', eventId=event_id).execute()
            except HttpError as e:
                click.echo(f"Error while deleting Google Calendar event: {e}")
                main_menu()
                return

            try:
                db.collection('workshops').document(selected_workshop.id).delete()
            except Exception as e:
                click.echo(f"Error while deleting workshop from Firestore: {e}")
                main_menu()
                return
            
            attendees = workshop_data.get('mentors', []) + workshop_data.get('peers', [])
            click.echo(f"Workshop '{workshop_data['Title']}' has been canceled.")
            click.echo(f"📩 Notification sent to: {', '.join(set(attendees))}")

    except Exception as e:
        click.echo(f"Error canceling workshop: {e}")
        main_menu() 

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[view_workshop, create_workshop, signup, signin])
    cli()