from datetime import datetime
from login import signin, signup
import click
from firebase_auth import db, current_session
from calender import get_calendar
from google.cloud import firestore
from notify import send_meeting_notification
from cleanup import cleanup_expired_entries
import pytz

SAST = pytz.timezone('Africa/Johannesburg')

@click.command()
def view_booking():
    """View all your confirmed bookings."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    cleanup_expired_entries()
    
    email = current_session['email']
    click.echo(f"📩 Fetching bookings for {email}")

    try:
        per_page = 5
        page_num = 1

        while True:
            current_time = datetime.now(SAST).isoformat()
            
            requested_bookings_ref = db.collection('meetings').where(filter=firestore.FieldFilter('organizer', '==', email)).where(filter=firestore.FieldFilter('end_time', '>', current_time)).stream()
            requested_bookings = list(requested_bookings_ref)
           
            booking_ref = db.collection('meetings').where(filter=firestore.FieldFilter('attendees', 'array_contains', email)).where(filter=firestore.FieldFilter('end_time', '>',current_time)).stream()
            bookings = list(booking_ref)

            all_bookings = requested_bookings + bookings
            unique_bookings = {booking.id: booking for booking in all_bookings}.values()

            if not unique_bookings:
                click.echo("⚠️ No bookings found for this email address.")
                main_menu()
                return
            
            total_pages = (len(unique_bookings) + per_page - 1) // per_page 
            start_page = (page_num - 1) * per_page
            end_page = start_page + per_page
            booking_page = list(unique_bookings)[start_page:end_page]

            click.echo(f'\n--- Your Bookings (Page {page_num} of {total_pages}) ---')

            for num, booking in enumerate(booking_page, start=1):
                data = booking.to_dict()
                subject = data.get('subject', 'No Subject')
                date = data.get('date', 'Unknown Date')
                start_time = data.get('start_time', 'Unknown Start Time')
                end_time = data.get('end_time', 'Unknown End Time')
                organizer = data.get('organizer', 'Unknown Organizer')
                attendees = data.get('attendees', [])
                status = data.get('status', 'pending')
                location = data.get('location', 'Unknown Location')
                google_event_id = data.get('google_event_id', 'No Event ID')

                try:
                    from datetime import datetime
                    start_time_obj = datetime.fromisoformat(start_time)
                    end_time_obj = datetime.fromisoformat(end_time)
                    formatted_start_time = start_time_obj.strftime('%I:%M %p')
                    formatted_end_time = end_time_obj.strftime('%I:%M %p')
                    formatted_date = start_time_obj.strftime('%A, %d %B %Y')

                except ValueError:
                    formatted_start_time = start_time
                    formatted_end_time = end_time
                    formatted_date = date

                click.echo(f"\n📋 Booking: {num} ")
                click.echo(f"📝 Subject: {subject}")
                click.echo(f"📅 Date: {formatted_date}")
                click.echo(f"🕒 Time: {formatted_start_time} - {formatted_end_time}")
                click.echo(f"📌 Location: {location}")
                click.echo(f"👤 Organizer: {organizer}")
                click.echo(f"👥 Attendees: {', '.join(set(attendees))}")
                click.echo(f"🔍 Status: {status}")
                click.echo(f"🔗 Event ID: {google_event_id}")
                click.echo("-" * 80)  
            
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
                
            main_menu()
                    
    except Exception as e:
        click.echo(f"⚠️ Error fetching bookings: {e}")
        main_menu()

@click.command()

def cancel_booking():
    """Cancel an existing booking."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    cleanup_expired_entries()
    
    email = current_session['email']
    click.echo(f"Fetching all bookings...")

    try:
        per_page = 5
        page_num = 1

        while True:
            current_time = datetime.now(SAST)

            requested_bookings_ref = db.collection('meetings').where(filter=firestore.FieldFilter('organizer', '==', email)).where(filter=firestore.FieldFilter(('end_time', '>', current_time))).stream()
            requested_bookings = list(requested_bookings_ref)

            booking_ref = db.collection('meetings').where(filter=firestore.FieldFilter('attendees', 'array_contains', email)).where(filter=firestore.FieldFilter(('end_time', '>', current_time))).stream()
            bookings = list(booking_ref)

            all_bookings = requested_bookings + bookings
            unique_bookings = {booking.id: booking for booking in all_bookings}.values()        

            if not unique_bookings:
                click.echo("⚠️ No bookings found.")
                main_menu()
                return
            
            total_pages = (len(unique_bookings) + per_page - 1) // per_page
            start_page = (page_num - 1) * per_page
            end_page = start_page + per_page
            booking_page = list(unique_bookings)[start_page:end_page]

            
            click.echo("Your Bookings:")
            for num, booking in enumerate(booking_page, start=1):
                data = booking.to_dict()
                subject = data.get('subject', 'No Subject')
                date = data.get('date', 'Unknown Date')
                start_time = data.get('start_time', 'Unknown Start Time')
                end_time = data.get('end_time', 'Unknown End Time')
                organizer = data.get('organizer', 'Unknown Organizer')
                attendees = data.get('attendees', [])
                status = data.get('status', 'pending')
                location = data.get('location', 'Unknown Location')
                google_event_id = data.get('google_event_id', 'No Event ID')
                
                try:
                    
                    start_time_obj = datetime.fromisoformat(start_time)
                    end_time_obj = datetime.fromisoformat(end_time)
                    formatted_start_time = start_time_obj.strftime('%I:%M %p')
                    formatted_end_time = end_time_obj.strftime('%I:%M %p')
                    formatted_date = start_time_obj.strftime('%A, %d %B %Y')
                    
                except ValueError:
                    formatted_start_time = start_time
                    formatted_end_time = end_time
                    formatted_date = date

                click.echo(f"\n📋 Booking {num}")
                click.echo(f"📝 Subject: {subject}")
                click.echo(f"📅 Date: {formatted_date}")
                click.echo(f"🕒 Time: {formatted_start_time} - {formatted_end_time}")
                click.echo(f"📌 Location: {location}")
                click.echo(f"👤 Organizer: {organizer}")
                click.echo(f"👥 Attendees: {', '.join(set(attendees))}")
                click.echo(f"🔍 Status: {status}")
                click.echo(f"🔗 Event ID: {google_event_id}")
                click.echo("-" * 80)

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
                try:
                    choice = int(click.prompt(f"Enter the number of the booking to cancel (1 - {len(bookings)}), or 0 to cancel "))
                    if 1 <= choice <= len(booking_page):
                        selected_booking = booking_page[choice - 1]
                        event_id = selected_booking.to_dict()['google_event_id']

                        # Remove from Google Calendar
                        service = get_calendar()
                        if not service:
                            main_menu()
                            return
                        try:
                            service.events().delete(calendarId='primary', eventId=event_id).execute()
                        except Exception as e:
                            click.echo(f"⚠️ Error while deleting event: {e}")
                            main_menu()
                            return    
                            
                        try:
                            db.collection('meetings').document(selected_booking.id).delete()
                        except Exception as e:
                            click.echo(f"⚠️ Error while deleting from Firestore: {e}")
                            main_menu()
                            return
                        click.echo("✅ Booking successfully canceled.")

                        meeting_data = selected_booking.to_dict()
                        try:
                            send_meeting_notification(meeting_data, notification_type='cancellation') 
                        except Exception as e:
                            click.echo(f"⚠️ Failed to send cancellation notification: {e}")
                    else:
                        click.echo("⚠️ Invalid choice. Please enter a number within the range.")
                except ValueError:
                    click.echo("⚠️ Invalid input. Please enter a number.")

                if choice == 0:
                    click.echo("❌ Cancel operation aborted.")
                    return
                else:
                    click.echo("⚠️ Invalid choice. Please try again.")
                    main_menu()
                    return
                                
            main_menu()
    except Exception as e:
        click.echo(f"⚠️ Error canceling booking: {e}")
        main_menu()

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[ view_booking, cancel_booking, signup, signin])
    cli()