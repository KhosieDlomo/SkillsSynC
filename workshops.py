import datetime
import click
from firebase_auth import db, current_session
from events import get_calendar
from google.cloud import firestore
from googleapiclient.errors import HttpError
from login import signin, signup
from notify import send_workshop_notification
import pytz

SAST = pytz.timezone('Africa/Johannesburg')

#workshops
@click.command()
def view_workshop():
    """View all upcoming workshops and Available mentors and peers"""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    email = current_session['email']
    click.echo(f"📩 Fetching workshops for {email}")

    try:
        per_page = 5
        page_num = 1

        while True:
            requested_workshops_ref = db.collection('workshops').where(filter=firestore.FieldFilter('organizer', '==', email))
            requested_workshops = list(requested_workshops_ref.stream())

            workshops_ref = db.collection('workshops').where(filter=firestore.FieldFilter('attendees', 'array_contains', email))
            workshops = list(workshops_ref.stream())

            all_workshop = requested_workshops + workshops
            unique_workshops = {workshop.id: workshop for workshop in all_workshop}.values()
            
            if not unique_workshops:
                click.echo("⚠️ No workshops found for this email address.")
                main_menu()
                return
            
            total_pages = (len(unique_workshops) + per_page - 1) // per_page
            start_page = (page_num - 1) * per_page
            end_page = start_page + per_page
            workshop_page = list(unique_workshops)[start_page:end_page]
            
            # workshops = list(workshops_ref.offset((page_num - 1) * per_page).limit(per_page).stream())
                        
            click.echo(f'📩 ---Upcoming Workshops (Page {page_num} of {total_pages})---')
            
            for num, workshop in enumerate(workshop_page, start=1):
                try:
                    title = workshop.to_dict().get('Title', 'Untitled Workshop')
                    date = workshop.to_dict().get('Date', 'Unknown Date')
                    start_time = workshop.to_dict().get('start_time', 'Unknown Start Time')
                    end_time = workshop.to_dict().get('end_time', 'Unknown End Time')
                    location = workshop.to_dict().get('location', 'Unknown Location')
                    mentors = workshop.to_dict().get('mentors', [])
                    peers = workshop.to_dict().get('peers', [])
                    online_link = workshop.to_dict().get('online_link', '')
                    accepted_mentors = workshop.to_dict().get('accepted_mentors', [])
                    organizer = workshop.to_dict().get('organizer', '')

                    if isinstance(mentors, str):
                        mentors = [mentors]
                    if isinstance(peers, str):
                        peers = [peers]
                    if isinstance(accepted_mentors, str):
                        accepted_mentors = [accepted_mentors]

                    attendees = list(set([organizer] + accepted_mentors + mentors + peers))
                    attendees = [attendee for attendee in attendees if attendee]

                    try:
                        start_time = datetime.datetime.fromisoformat(start_time)
                        end_time = datetime.datetime.fromisoformat(end_time)
                        formatted_date = start_time.strftime('%A, %d %B %Y')
                        formatted_start_time = start_time.strftime('%I:%M %p')
                        formatted_end_time = end_time.strftime('%I:%M %p')
                    except ValueError:
                        formatted_date = date
                        formatted_start_time = start_time
                        formatted_end_time = end_time

                    click.echo(f"\n📋 Workshop {num}")
                    click.echo(f"├─ 📝 Title: {title}")
                    click.echo(f"├─ 🗓️ Date: {formatted_date}")
                    click.echo(f"├─ 🕒 Time: {formatted_start_time} - {formatted_end_time}")
                    click.echo(f"├─ 📌 Location: {location}")
                    click.echo(f"├─ 👤 Mentors: {organizer}")
                    click.echo(f"├─ 👥 Attendees: {', '.join(attendees) if attendees else 'None'}")
                    if workshop.get('online_link'):
                        click.echo(f"└─ 🔗 Online Link: {online_link}")
                    else:
                        click.echo("└─ 🔗 Online Link: Not provided")
                    click.echo("-" * 80)  
                
                except Exception as e:
                    click.echo(f"⚠️ Error displaying workshop {num}: {e}")
                    continue
            
            if page_num > 1:
                click.echo("Enter 'p' for previous page")
            if page_num < total_pages:
                click.echo("Enter 'n' for next page")
            click.echo("Enter 'menu' to return to the main menu")

            choice = click.prompt("Enter your choice").lower()
            if choice == 'p' and page_num > 1:
                page_num -= 1
            elif choice == 'n' and page_num < total_pages:
                page_num += 1
            elif choice == 'menu':
                main_menu()
                return
            else:
                click.echo("⚠️ Invalid choice. Please try again.")
    
    except Exception as e:
        click.echo(f'⚠️ Error while fetching upcoming workshops: {e}')
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
        click.echo("⚠️  User not authenticated. Please sign in.")
        main_menu()
        return

    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        role = user_doc.to_dict().get('role', 'peer')
    else:
        role = 'peer'
        
    if role != 'mentor':
        click.echo("⚠️Only mentors can create workshops")
        main_menu()
        return
    
    service = get_calendar()
    if not service:
        click.echo("⚠️ Failed to initialize Google Calendar service.")
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
        start_hour = SAST.localize(datetime.datetime.strptime(f'{date} {start_time}', '%d/%m/%Y %H:%M'))
        end_hour = SAST.localize(datetime.datetime.strptime(f'{date} {end_time}', '%d/%m/%Y %H:%M'))

    except ValueError:
        click.echo('⚠️ Invalid date or time format, please use DD/MM/YYYY HH:MM')
        main_menu()
        return
    
    if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
        click.echo("⚠️ Error! Meetings are only allowed on weekdays between 07:00 to 17:00.")
        main_menu()
        return
    
    time_min = start_hour.isoformat()
    time_max = end_hour.isoformat()
    try:
        event_result = service.events().list( calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True).execute()
        events = event_result.get('items', [])
        
        if events:
            click.echo("⚠️ Conflicting events found during the specified time.")
            for event in events:
                click.echo(f"Event: {event.get('summary')}, Start: {event.get('start')}, End: {event.get('end')}")
            click.echo("⚠️ Please select a different time.")
            main_menu()
            return
        
    except HttpError as e:
        click.echo(f'⚠️ Error while fetching Events from the calender {e}')
        main_menu()
        return
    
    peers = db.collection('users').where(filter=firestore.FieldFilter('role', '==', 'peer')).stream()
    peers_email = {peer.to_dict().get('email').strip() for peer in peers if peer.exists}
        
    mentors = db.collection('users').where(filter=firestore.FieldFilter('role', '==', 'mentor')).stream()
    mentors_email = {mentor.to_dict().get('email').strip() for mentor in mentors if mentor.exists}  
    
    attendees = [{'email': email.strip(), 'optional':email != user_email} for email in mentors_email.union(peers_email)]

    if user_email not in mentors_email:
        click.echo("⚠️ Only mentors can create workshops.")
        main_menu()
        return
    
    approval_mentor = [user_email]
    
    attendees = []
    #Mentors
    for emails in mentors_email:
        if emails != user_email:
            approval_mentor.append(emails)
            attendees.append({'email': emails.strip(), 'optional': True})

    #peers
    for email in peers_email:
        attendees.append({'email': emails.strip(), 'optional': False})
   
    event = {'summary': title,
             'description': description,
             'location': location,
             'start': {'dateTime': start_hour.isoformat(), 'timeZone': 'Africa/Johannesburg'},
             'end': {'dateTime': end_hour.isoformat(), 'timeZone': 'Africa/Johannesburg'},
             'attendees': attendees,
             'organizer': {'email': user_email},
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
            'mentors': [user_email],
            'peers': list(peers_email),
            'google_event_id': event_result.get('id'),
            'online_link': online_link,
            'organizer' : user_email,
            'approval_mentors': approval_mentor,
            'attendees': list(mentors_email.union(peers_email))
        }
        
        db.collection('workshops').add(workshop_data)
        click.echo('✅ Workshop created and all peers added successfully.')

        send_workshop_notification(workshop_data, notification_type="confirmation")
        
    except HttpError as error:
        click.echo(f"⚠️ An error occured while creating event: {error}")
    except Exception as e:
        click.echo(f'⚠️ Failed to create workshop: {e}')
        
    main_menu()

@click.command()
def update_workshop():
    """Updating an existing workshop."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    user_id = current_session.get('user_id')
    user_email = current_session.get('email')

    if not user_id or not user_email:
        click.echo('❌ User not authenticated. Please sign in.')
        main_menu()
        return
    
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        role = user_doc.to_dict().get('role', 'peer')
    else:
        role = 'peer'
    
    if role != 'mentor':
        click.echo("⚠️ Only mentors can update workshops.")
        main_menu()
        return
    
    click.echo("🔎Fetching all workshops...")

    try:
        workshop_ref = db.collection('workshops').where(filter=firestore.FieldFilter('organizer', '==', user_email)).stream()
        workshops = [workshop for workshop in workshop_ref]

        if not workshops:
            click.echo("⚠️ No workshops found.")
            main_menu()
            return
        
        for num, workshop in enumerate(workshops, start=1):
            workshops_data = workshop.to_dict()
            title = workshops_data.get('Title', 'Untitled Workshop')
            click.echo(f"{num}. {title}")
            
        try:
            choice = int(click.prompt(f"Enter the number of the workshop to update (1 - {len(workshops)})"))
            if 1 <= choice <= len(workshops):
                selected_workshop = workshops[choice - 1]
            else:
                click.echo("⚠️ Invalid choice.")
                main_menu()
                return
        except ValueError:
            click.echo("⚠️ Invalid input. Please enter a number.")
            main_menu()
            return     
        
        workshop_id = selected_workshop.id
        updates = {}
        
        click.echo("Leave blank to keep the current value, by pessing Enter.")
        new_title = click.prompt("New title", default=selected_workshop.to_dict().get('Title', ''))
        if new_title:
            updates['Title'] = new_title
        
        new_date = click.prompt("New date (DD/MM/YYYY)", default=selected_workshop.to_dict().get('Date', ''))
        if new_date:
            updates['Date'] = new_date

        new_time = click.prompt("New Time (HH:MM)", default=selected_workshop.to_dict().get('Time', ''))
        if new_time:
            updates['Time'] = new_time
        
        new_location = click.prompt("New location", default=selected_workshop.to_dict().get('location', ''))
        if new_location:
            updates['location'] = new_location

        try:
            db.collection('workshops').document(workshop_id).update(updates)
            click.echo("✅ Workshop updated successfully.")

            updated_workshop = db.collection('workshops').document(workshop_id).get().to_dict()

            send_workshop_notification(updated_workshop, notification_type="update") 

        except Exception as e:
            click.echo(f"⚠️ Error updating workshop: {e}")  

        main_menu()   
    except Exception as e:
        click.echo(f"⚠️ Error updating workshop: {e}")
        main_menu()

def cancel_workshop():
    """Cancel an existing workshop."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    user_id = current_session.get('user_id')
    user_email = current_session.get('email')

    if not user_id or not user_email:
        click.echo("❌ User not authenticated. Please sign in.")
        main_menu()
        return
    
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        role = user_doc.to_dict().get('role', 'peer')
    else:
        role = 'peer'
        
    if role != 'mentor':
        click.echo("⚠️ Only mentors can cancel workshops.")
        main_menu()
        return

    click.echo(f"🔎Fetching all workshops...")

    try:
        workshop_ref = db.collection('workshops').where(filter=firestore.FieldFilter('organizer', '==', user_email)).stream()
        workshops = [workshop for workshop in workshop_ref]

        if not workshops:
            click.echo("⚠️ No workshops were created.")
            main_menu()
            return
        
        current_time = datetime.datetime.now(SAST)

        upcoming_workshops = []
        for workshop in workshops:
            workshop_data = workshop.to_dict()
            end_time = datetime.datetime.fromisoformat(workshop_data.get('end_time', ''))

            if end_time.tzinfo is None:
                end_time = SAST.localize(end_time)

            if end_time > current_time:
                upcoming_workshops.append(workshop)
            
        if not upcoming_workshops:
            click.echo("⚠️ No upcoming workshops found.")
            main_menu()
            return

        per_page = 5
        page_num = 1
        total_pages = (len(upcoming_workshops) + per_page - 1) // per_page
        
        while True:
            start_page = (page_num - 1) * per_page
            end_page = start_page + per_page
            workshop_page = upcoming_workshops[start_page:end_page]
                
            click.echo('\n--- Upcoming Workshops: ---')
            for num, workshop in enumerate(workshop_page, start=1):
                try:
                    title = workshop.to_dict().get('Title', 'Untitled Workshop')
                    date = workshop.to_dict().get('Date', 'Unknown Date')
                    start_time = workshop.to_dict().get('start_time', 'Unknown Start Time')
                    end_time = workshop.to_dict().get('end_time', 'Unknown End Time')
                    location = workshop.to_dict().get('location', 'Unknown Location')
                    mentors = workshop.to_dict().get('mentors', [])
                    peers = workshop.to_dict().get('peers', [])
                    online_link = workshop.to_dict().get('online_link', '')
                    accepted_mentors = workshop.to_dict().get('accepted_mentors', [])
                    organizer = workshop.to_dict().get('organizer', '')
                        
                    attendees = list(set([organizer] + mentors + peers + accepted_mentors))
                    attendees = [attendee for attendee in attendees if attendee]

                    try:

                        start_time = datetime.datetime.fromisoformat(start_time)
                        end_time = datetime.datetime.fromisoformat(end_time)
                        formatted_date = start_time.strftime('%A, %d %B %Y')
                        formatted_start_time = start_time.strftime('%I:%M %p')
                        formatted_end_time = end_time.strftime('%I:%M %p')
                    except ValueError:
                        formatted_date = date
                        formatted_start_time = start_time
                        formatted_end_time = end_time

                    if isinstance(mentors, str):
                        mentors = [mentors]


                    click.echo(f"\n📋 Workshop {num}")
                    click.echo(f"├─ 📝 Title: {title}")
                    click.echo(f"├─ 🗓️ Date: {formatted_date}")
                    click.echo(f"├─ 🕒 Time: {formatted_start_time} - {formatted_end_time}")
                    click.echo(f"├─ 📍 Location: {location}")
                    click.echo(f"├─ 👤 Mentors: {organizer}")
                    click.echo(f"├─ 👥 Attendees: {', '.join(attendees) if attendees else 'None'}")
                    if online_link:
                        click.echo(f"└─ 🔗 Online Link: {online_link}")
                    else:
                        click.echo("└─ 🔗 Online Link: Not provided")
                    click.echo("-" * 80)

                except Exception as e:
                    click.echo(f"⚠️ Error displaying workshop {num}: {e}")
                    continue
                
            while True:
                try:
                    choice = int(click.prompt(f"Enter the number of the workshop to cancel (1 - {len(workshops)}), or 0 to cancel "))
                    if 0 <= choice <= len(workshops):
                        break
                    else:
                        click.echo("⚠️ Invalid choice. Please enter a number within the range.")
                
                except ValueError:
                    click.echo("⚠️ Invalid input. Please enter a number.")

            if choice == 0:
                click.echo("❌ Cancel operation aborted.")
                main_menu()
                return
            
            selected_workshop = workshops[choice - 1]
            workshop_data = selected_workshop.to_dict()
            event_id = workshop_data.get('google_event_id')

            if workshop_data.get('organizer') != user_email:
                click.echo("⚠️ You are not authorized to cancel this workshop.")
                main_menu()
                return

            service = get_calendar()
            if not service:
                click.echo("⚠️ Failed to initialize Google Calendar service.")
                main_menu()
                return

            try:
                service.events().delete(calendarId='primary', eventId=event_id).execute()
                click.echo("✅ Google Calendar event deleted.")
            except HttpError as e:
                click.echo(f"⚠️Error while deleting Google Calendar event: {e}")
                main_menu()
                return

            try:
                db.collection('workshops').document(selected_workshop.id).delete()
                click.echo("✅ Workshop deleted from Firestore.")
            except Exception as e:
                click.echo(f"⚠️ Error while deleting workshop from Firestore: {e}")
                main_menu()
                return
             
            if page_num > 1:
                click.echo("Enter 'p' for previous page")
            if page_num < total_pages:
                click.echo("Enter 'n' for next page")
            click.echo("Enter 'menu' to return to the main menu")

            choice = click.prompt("Enter your choice").lower()
            if choice == 'p' and page_num > 1:
                page_num -= 1
            elif choice == 'n' and page_num < total_pages:
                page_num += 1
            elif choice == 'menu':
                main_menu()
                return
            for attendee in attendees:
                click.echo(f"📩 Notification sent to: {attendee}")
            click.echo(f"✅ Workshop '{workshop_data['Title']}' has been canceled.")

            send_workshop_notification(workshop_data, notification_type="cancellation")
            main_menu()

    except Exception as e:
        click.echo(f"⚠️ Error canceling workshop: {e}")
    main_menu() 

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[view_workshop, create_workshop, signup, signin])
    cli()