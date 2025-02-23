from login import signin, signup
import click
from firebase_auth import db, current_session
from calender import get_calendar
from google.cloud import firestore

@click.command()
def view_booking():
    """View all your confirmed bookings."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    email = current_session['email']
    click.echo(f"Fetching bookings...")

    try:
        booking_ref = db.collection('meetings').where(filter=firestore.FieldFilter('attendees', 'array_contains', email))
        bookings = list(booking_ref.stream())

        click.echo(f'Bookings for {email}:')
        if not bookings:
            click.echo("⚠ No bookings found for this email address.")
            main_menu()
            return

        click.echo(f'Bookings for {email}:')
        for booking in bookings:
            data = booking.to_dict()
            click.echo(f"Subject: {data['subject']}, Date: {data['date']}, Time: {data['start_time']} - {data['end_time']}, Event ID: {data['google_event_id']}")
        main_menu()
                    
    except Exception as e:
        click.echo(f"Error fetching bookings: {e}")
        main_menu()

@click.command()
def cancel_booking():
    """Cancel an existing booking."""
    from main import main_menu

    if not current_session['logged_in']:
        click.echo("Please sign up or sign in to use this feature")
        return
    
    email = current_session['email']
    click.echo(f"Fetching all bookings...")

    try:
        booking_ref = db.collection('meetings').where(filter=firestore.FieldFilter('attendees', 'array_contains', email))
        bookings = list(booking_ref.stream())

        if not bookings:
            click.echo("No bookings found.")
            main_menu()
            return
        click.echo("Your Bookings:")
        for num, booking in enumerate(bookings):
            data = booking.to_dict()
            click.echo(f"{num + 1}. Subject: {data['subject']}, Date: {data['date']}, Time: {data['start_time']} - {data['end_time']}, Event ID: {data['google_event_id']}")
            while True:
                try:
                    choice = int(click.prompt(f"Enter the number of the booking to cancel (1 - {len(bookings)}), or 0 to cancel: "))
                    if 0 <= choice <= len(bookings):
                        break
                    else:
                        click.echo("Invalid choice. Please enter a number within the range.")
                except ValueError:
                    click.echo("Invalid input. Please enter a number.")

            if choice == 0:
                click.echo("Cancel operation aborted.")
                main_menu()
                return
            
            selected_booking = booking[choice - 1]
            event_id = selected_booking.to_dict()['google_event_id']

            # Remove from Google Calendar
            service = get_calendar()
            if not service:
                main_menu()
                return
            try:
                service.events().delete(calendarId='primary', eventId=event_id).execute()
            except Exception as e:
                click.echo(f"Error while deleting event: {e}")
                main_menu()
                return
            try:
                db.collection('meetings').document(selected_booking.id).delete()
            except Exception as e:
                click.echo(f"Error while deleting from Firestore: {e}")
                main_menu()
                return
            click.echo("Booking successfully canceled.")
    
    except Exception as e:
        click.echo(f"Error canceling booking: {e}")
        main_menu()

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[ view_booking, cancel_booking, signup, signin])
    cli()