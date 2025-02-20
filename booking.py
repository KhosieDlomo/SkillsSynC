import datetime
import click
from firebase_auth import db, auth, require_auth, current_session
from googleapiclient.errors import HttpError
from availability import available_mentors, available_peers
from calender import get_calendar

@click.command()
def bookings():
    '''Book a meeting with your peers or mentors.'''

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
        expertise = click.prompt('Enter desired expertise (optional)', default="")
        language = click.prompt("Enter desired language (optional)", default="")
        mentors = available_mentors(expertise=expertise, language=language)
        peers = available_peers(expertise=expertise, language=language)

        combined_lst = mentors + peers
        if not combined_lst:
            click.echo("No mentors or peer found.")
            click.echo("Please try a different expertise or language, or check back later.")
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
            
            except ValueError:
                click.echo("Invalid input. Please enter a number or 'done'.")
        if not selected_members:
            click.echo("No members selected for group session.")
            return
        
        subject = click.prompt('Event subject: ')
        date = click.prompt('Event date(DD/MM/YYYY): ')
        start_time = click.prompt('Event start time (HH:MM): ')
        end_time = click.prompt('Event end time (HH:MM): ')
        location = click.prompt('Event Location (e.g: "Online" or a physical address): ')
        
        online_link = None
        if location == 'online'.lower():
            online_link = click.prompt("Enter the online meeting link: ")
        try:
            start_hour = datetime.datetime.strptime(f"{date} {start_time}", "%d/%m/%Y %H:%M")
            end_hour = datetime.datetime.strptime(f"{date} {end_time}", "%d/%m/%Y %H:%M")
        except ValueError:
            click.echo("Invalid date or time format. Please use DD/MM/YYYY and HH:MM.")
            return
        if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
            click.echo("Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
            return
        
        time_min = start_hour.isoformat() + 'Z'
        time_max = end_hour.isoformat() + 'Z'
        attendees =[]

        for person in selected_members:
            attendees.append({'email': person['email']})
        attendees.append({'email': auth.current_user['email']})

        service = get_calendar()
        if not service:
            return
        
        event = {'summary': subject,
                    'location': location,
                    'start':{'dateTime': start_hour.isoformat(), 'timeZone': 'UTC'},
                    'end':{'dateTime': end_hour.isoformat(), 'timeZone': 'UTC'},
                    'attendees': [{'email': email.strip()} for email in attendees],
                    'remainder': {'useDefault': False,
                                'override': [{'method': 'email','minutes':24 * 60},
                                            {'method':'popup', 'minutes': 15}],
                                },
                }
        if online_link:
            event['description'] = f"{event.get('descriptio', '')}\nJoin online: {online_link}"
        try:
            event_result = service.events().insert(calendarId='primary', body=event,sendUpdates='all').execute()
            db.collection('meetings').add({'subject': subject,
                                            'date': date,
                                            'start_time':start_hour.isoformat(),
                                            'attendees':[person['email'] for person in selected_members],
                                            'location': location,
                                            'status':'confirmed',
                                            'google_event_id': event_result.get('id'),
                                            'online_link': online_link
                                         })
            click.echo(f"Event created successfully: {event_result.get('htmlLink')}")
        except HttpError as error:
            click.echo(f"An error occured: {error}")
        except Exception as e:
            click.echo(f"An error occured while creating group events: {e}")
    
    else:
        click.echo('\nFetching available mentors and peers...')
        mentors = available_mentors()
        peers = available_peers()

        user_choice = click.prompt("Book with a (M)-for-Mentor or (P)-for-Peer?", type=click.Choice(['M','P','m','p'])).lower()
        booking_mentor = user_choice == 'm'
        if booking_mentor:
            click.echo('\nFecthing available mentors...')
            if not mentors:
                click.echo('No available mentors')
                click.echo("Please try a group session or check back later.")
                return
            for i, mentor in enumerate(mentors):
                click.echo(f"{i + 1}: Name: {mentor['name']}, Email:{mentor['email']}, Expertise: {mentor['expertise']}")

            while True:
                try:
                    select_mentor = int(click.prompt('Select the Mentor(e.g., 1, 2, 3,etc).')) - 1
                    if 0 <= select_mentor < len(mentors):
                        break
                    else:
                        click.echo('Invalid selection!')
                except ValueError:
                        click.echo('Invalid input. Please enter a number(e.g., 1, 2, 3, etc...)')
            chosen_person = mentors[select_mentor]

        else:
            click.echo('\nFetching available peers...')
            if not peers:
                click.echo('No Available peers at the moment.')
                click.echo("Please try a group session or check back later.")
                return
            for i, peer in enumerate(peers):
                click.echo(f"{i + 1}: Name: {peer['name']}, Email: {peer['email']}, Expertise: {peer['expertise']}")
            
            while True:
                try:
                    select_peer = int(click.prompt('Select the Peer(e.g., 1, 2, 3, etc...).')) - 1
                    if 0 <= select_peer < len(peers):
                        break
                    else:
                        click.echo('Invalid Selection!')
                except ValueError:
                    click.echo('Invalid input. Please enter a number (e.g., 1, 2, 3, etc...).')
            chosen_person = peers[select_peer]

        
    service = get_calendar()
    if not service:
        return

    subject = click.prompt('Event subject: ')
    date = click.prompt('Event date(DD/MM/YYYY): ')
    start_time = click.prompt('Event start time (HH:MM): ')
    end_time = click.prompt('Event end time (HH:MM): ')
    location = click.prompt('Event Location (e.g: "Online" or a physical address): ')
    
    attendees = [chosen_person['email']]

    online_link = None
    if location == 'online'.lower():
        online_link = click.prompt("Enter the online meeting link: ")

    try:
        start_hour = datetime.datetime.strptime(f'{date} {start_time}', "%d/%m/%Y %H:%M")
        end_hour = datetime.datetime.strptime(f'{date} {end_time}', "%d/%m/%Y %H:%M")
    except ValueError:
        click.echo('Invalid date or time format. Please use DD/MM/YYYY and HH:MM.')
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
        click.echo(f"Apologies an HTTP error occured: {e}")
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
    if online_link:
            event['description'] = f"{event.get('description', '')}\nJoin online: {online_link}"  
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
            'online_link':online_link
        })
        click.echo(f'Event created successfully: {event_result.get('htmlLink')}') 


    except HttpError as error:
        print(f'An error occured: {error}')