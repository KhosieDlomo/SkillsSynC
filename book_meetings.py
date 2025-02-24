import datetime
import click
from firebase_auth import db, auth, require_auth, current_session
from googleapiclient.errors import HttpError
from availability import available_mentors, available_peers
from google.cloud import firestore
from calender import get_calendar
import pytz

SAST = pytz.timezone('Africa/Johannesburg')

def is_mentor_available(service, mentor_email, start_hour, end_hour):
    """Checking if a mentor is available in their Google Calendar."""
    start_hour_utc = start_hour.astimezone(pytz.UTC)
    end_hour_utc = end_hour.astimezone(pytz.UTC)

    time_min = start_hour_utc.isoformat()
    time_max = end_hour_utc.isoformat()
    try:
        event_result = service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True).execute()
        events = event_result.get('items', [])
        return not events  
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return False  

def find_next_available_slot(service, mentor_email, start_date, duration_hours, max_days=7):
    """Finds the next available time slot for a mentor."""
    current_date = start_date
    for day in range(max_days):
        for hour in range(7, 18):
            start_hour = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_hour = start_hour + datetime.timedelta(hours=duration_hours)

            if start_hour.weekday() < 5:  
                if is_mentor_available(service, mentor_email, start_hour, end_hour):
                    return start_hour, end_hour 
        current_date += datetime.timedelta(days=1)  
    return None, None  

def update_booking(db, google_event_id, new_start_hour, new_end_hour):
    """Updates an existing booking in Firestore and Google Calendar."""
    try:
        meetings_ref = db.collection('meetings')
        query = meetings_ref.where(filter=firestore.FieldFilter('google_event_id', '==', google_event_id)).limit(1) 

        meetings = query.stream()

        for meeting in meetings:
            meeting_data = meeting.to_dict()
            meeting_id = meeting.id
            print(f"found meeting: {meeting_id}")

            service = get_calendar()
            if not service:
                click.echo("Failed to initialize Google Calendar service.")
                return

            event = service.events().get(calendarId='primary', eventId=google_event_id).execute()
            event['start']['dateTime'] = new_start_hour.isoformat()
            event['end']['dateTime'] = new_end_hour.isoformat()

            updated_event = service.events().update(calendarId='primary', eventId=google_event_id, body=event, sendUpdates='all').execute()

            
            db.collection('meetings').document(meeting_id).update({
                'start_time': new_start_hour.isoformat(),
                'end_time': new_end_hour.isoformat()
            })

            click.echo(f"Booking updated successfully: {updated_event.get('htmlLink')}")
            return
        click.echo("No matching bookings found.")

    except Exception as e:
        click.echo(f"An error occurred while updating the booking: {e}")

def book_session(service, subject, start_hour, end_hour, location, attendees, online_link=None):
    """Book a session and save it to Firestore."""
    event = {
        'summary': subject,
        'location': location,
        'start': {'dateTime': start_hour.isoformat(), 'timeZone': 'Africa/Johannesburg'},
        'end': {'dateTime': end_hour.isoformat(), 'timeZone': 'Africa/Johannesburg'},
        'attendees': [{'email': email.strip()} for email in attendees],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 15},
            ],
        },
    }
    if online_link:
        event['description'] = f"{event.get('description', '')}\nJoin online: {online_link}"

    try:
        event_result = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        db.collection('meetings').add({
            'subject': subject,
            'date': start_hour.strftime('%d/%m/%Y'),
            'start_time': start_hour.isoformat(),
            'end_time': end_hour.isoformat(),
            'organizer': current_session['email'],
            'attendees': attendees,
            'location': location,
            'status': 'confirmed',
            'google_event_id': event_result.get('id'),
            'online_link': online_link
        })
        click.echo(f"Event created successfully: {event_result.get('htmlLink')}")
    except HttpError as error:
        click.echo(f"An error occurred: {error}")
    except Exception as e:
        click.echo(f"An error occurred while creating the event: {e}")

@click.command()
def bookings():
    '''Book a meeting with your peers or mentors.'''
    from main import main_menu

    if not current_session['user_id']:
        return
    
    user_id =current_session["user_id"]
    success, message = require_auth(user_id)
    if not success:
        click.echo(message)
        return
    
    click.echo(f"Fetching bookings for {current_session['email']}...")
    
    user_meeting = click.prompt('Want a (G)-for-Group session or a (O)-for-One-on-One session?', type=click.Choice(['G','O','g','o'])).lower()
    group_session = user_meeting == 'g'
    if group_session:
        click.echo("You've selected a group session")
        expertise = click.prompt('Enter desired expertise (optional)', default="", show_default=False).strip()
        language = click.prompt("Enter desired language (optional)", default="", show_default=False).strip()

        mentors = available_mentors(expertise=expertise, language=language)
        peers = available_peers(expertise=expertise, language=language)

        combined_lst = mentors + peers
        if not combined_lst:
            click.echo("No mentors or peer found.")
            main_menu()
            return
        
        click.echo("\nAvailable Mentors and Peers for the Group session: ")
        for i, person in enumerate(combined_lst):
            click.echo(f"{i + 1}: {person['name']},({person['expertise']}, {person['language']}) - {person['email']}")
            
        selected_members = []
        while True:
            try:
                selecting_members = click.prompt("Enter the number of a member to add (or 'done')").lower()
                if selecting_members == 'done':
                    break
                member_number = int(selecting_members) - 1
                if 0 <= member_number < len(combined_lst):
                    selected_members.append(combined_lst[member_number])
                    click.echo(f"Added {combined_lst[member_number]['name']} to the group.")
                else:
                    click.echo("Invalid selection. Please try again.")

            except ValueError:
                click.echo("Invalid input. Please enter a number or 'done'.")

        if not selected_members:
            click.echo("No members selected for group session.")
            main_menu()
            return
        
        subject = click.prompt('Event subject ')
        date = click.prompt('Event date(DD/MM/YYYY) ')
        start_time = click.prompt('Event start time (HH:MM) ')
        end_time = click.prompt('Event end time (HH:MM) ')
        location = click.prompt('Event Location (e.g: "Online" or a physical address) ')
        
        online_link = None
        if location == 'online'.lower():
            online_link = click.prompt("Enter the online meeting link: ")
        try:
            start_hour = datetime.datetime.strptime(f"{date} {start_time}", "%d/%m/%Y %H:%M")
            end_hour = datetime.datetime.strptime(f"{date} {end_time}", "%d/%m/%Y %H:%M")
        except ValueError:
            click.echo("Invalid date or time format. Please use DD/MM/YYYY and HH:MM.")
            main_menu()
            return
        
        if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
            click.echo("Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
            main_menu()
            return
        
        attendees =[person['email'] for person in selected_members]
        attendees.append(auth.current_user['email'])

        service = get_calendar()
        if not service:
            main_menu()
            return
        
        book_session(service, subject, start_hour, end_hour, location, attendees, online_link)
        main_menu()
        return
    
    else:
        click.echo('\nFetching available mentors and peers...')
        mentors = available_mentors()
        peers = available_peers()

        user_choice = click.prompt("Book with a (M)-for-Mentor or (P)-for-Peer?", type=click.Choice(['M','P','m','p'])).lower()
        booking_mentor = user_choice == 'm'

        chosen_person = None

        if booking_mentor:
            click.echo('\nFecthing available mentors...')
            if not mentors:
                click.echo('No available mentors')
                main_menu()
                return
            
            for i, mentor in enumerate(mentors):
                click.echo(f"{i + 1}: Name: {mentor['name']}, Email:{mentor['email']}, Expertise: {mentor['expertise']}")

            while True:
                try:
                    select_mentor = int(click.prompt('Select the Mentor(e.g., 1, 2, 3,etc).')) - 1
                    if 0 <= select_mentor < len(mentors):
                        chosen_person = mentors[select_mentor]
                        break
                    else:
                        click.echo('Invalid selection!')
                except ValueError:
                        click.echo('Invalid input. Please enter a number(e.g., 1, 2, 3, etc...)')

        else:
            click.echo('\nFetching available peers...')
            if not peers:
                click.echo('No Available peers at the moment.')
                main_menu()
                return
            for i, peer in enumerate(peers):
                click.echo(f"{i + 1}: Name: {peer['name']}, Email: {peer['email']}, Expertise: {peer['expertise']}, Available:{peer['available_dats']}, Time:{peer['available_time_start']}-{peer['available_time_end']}")
            
            while True:
                try:
                    select_peer = int(click.prompt('Select the Peer(e.g., 1, 2, 3, etc...).')) - 1
                    if 0 <= select_peer < len(peers):
                        chosen_person = peers[select_peer]
                        break
                    else:
                        click.echo('Invalid Selection!')
                except ValueError:
                    click.echo('Invalid input. Please enter a number (e.g., 1, 2, 3, etc...).')

    if chosen_person is None:
            click.echo("Error: No mentor or peer selected.")
            main_menu()
            return
    
    subject = click.prompt('Event subject ')
    date = click.prompt('Event date(DD/MM/YYYY) ')
    start_time = click.prompt('Event start time (HH:MM) ')
    end_time = click.prompt('Event end time (HH:MM) ')
    location = click.prompt('Event Location (e.g: "Online" or a physical address) ')

    online_link = None
    if location == 'online'.lower():
        online_link = click.prompt("Enter the online meeting link: ")

    try:
        start_hour = SAST.localize(datetime.datetime.strptime(f'{date} {start_time}', "%d/%m/%Y %H:%M"))
        end_hour = SAST.localize(datetime.datetime.strptime(f'{date} {end_time}', "%d/%m/%Y %H:%M"))
    except ValueError:
        click.echo('Invalid date or time format. Please use DD/MM/YYYY and HH:MM.')
        main_menu()
        return

    if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
        click.echo("Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
        main_menu()
        return
    
    service = get_calendar()
    if not service:
        main_menu()
        return

    if not is_mentor_available(service, chosen_person['email'], start_hour, end_hour):
            click.echo("The selected mentor/peer is not available at the chosen time.")
            new_start_hour, new_end_hour = find_next_available_slot(service, chosen_person['email'], start_hour, (end_hour - start_hour).seconds // 3600)
            if new_start_hour and new_end_hour:
                click.echo(f"Next available slot: {new_start_hour.strftime('%d/%m/%Y %H:%M')} to {new_end_hour.strftime('%H:%M')}")
                reschedule = click.prompt("Would you like to reschedule? (Y/N)", type=click.Choice(['Y', 'N', 'y', 'n'])).lower()
                if reschedule == 'y':
                    start_hour, end_hour = new_start_hour, new_end_hour
                else:
                    main_menu()
                    return
            else:
                click.echo("No available slots found.")
                main_menu()
                return

    attendees = [chosen_person['email']]
    book_session(service, subject, start_hour, end_hour, location, attendees, online_link)
    main_menu()
    return