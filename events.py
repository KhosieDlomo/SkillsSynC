from login import signin, signup
import click
from firebase_auth import db, current_session
from calender import get_calendar
from booking import bookings

@click.command()
def view_booking():
    """View all your confirmed bookings."""

    if not current_session['logged_in']:
        return
    
    email = click.prompt("Enter your email to fetch bookings: ")

    try:
        booking_ref = db.collection('meetings').where('attendees', 'array_contains', email)
        bookings = booking_ref.stream()

        click.echo(f'Bookings for {email}:')

        for booking in bookings:
            data = booking.to_dict()
            click.echo(f"Subject: {data['subject']}, Date: {data['date']}, Time: {data['start_time']} - {data['end_time']}, Event ID: {data['google_event_id']}")
    except Exception as e:
        click.echo(f"Error fetching bookings: {e}")

@click.command()
def cancel_booking():
    """Cancel an existing booking."""

    if not current_session['logged_in']:
        click.echo("Please sign up or sign in to use this feature")
        return
    
    event_id = click.prompt("Enter the event ID to cancel: ")
    
    try:
        # Remove from Google Calendar
        service = get_calendar()
        if not service:
            return
        
        service.events().delete(calendarId='primary', eventId=event_id).execute()

        try:      
            meeting_ref = db.collection('meetings').where('google_event_id', '==', event_id)
            meetings = meeting_ref.stream()
            
            for meeting in meetings:
                db.collection('meetings').document(meeting.id).delete()
        except Exception as e:
            click.echo(f"Error while deleting from Firestore: {e}")         
        click.echo("Booking successfully canceled.")
    except Exception as e:
        click.echo(f"Error canceling booking: {e}")

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[bookings, view_booking, cancel_booking, signup, signin])
    cli()