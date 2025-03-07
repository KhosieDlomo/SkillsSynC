import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from firebase_auth import current_session,db
from google.cloud import firestore
import click
import os

from_password = os.getenv('EMAIL_Password')
def send_email(subject, body, to_email):
    '''Sending an email using SMTP'''
    from_email = current_session['email']
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        click.echo("Email sent successfully")
    except Exception as e:
        click.echo(f"Failed to send email: {e}")

def send_meeting_notification(meeting_data, notification_type="confirmation"):
    '''Sending a meeting confirmation or reminder email to all attendees'''

    if notification_type == "confirmation":
        subject = "Meeting Confirmation"
    elif notification_type == "update":
        subject = "Meeting Update"
    elif notification_type == "cancellation":
        subject = "Meeting Cancellation"
    else:
        subject = "Meeting Notification"

    body = f"""
    Subject: {meeting_data['subject']}
    Date: {meeting_data['date']}
    Time: {meeting_data['start_time']} - {meeting_data['end_time']}
    Location: {meeting_data['location']}
    Organizer: {meeting_data['organizer']}
    Attendees: {', '.join(meeting_data['attendees'])}
    """
    if notification_type == "update":
        body = "Update: " + body
    elif notification_type == "cancellation":
        body = "Cancellation: " + body
        
    for attendee in meeting_data['attendees']:
        send_email(subject, body, attendee)

def fetch_meeting_data(meeting_id):
    '''Getting meeting data from Firestore'''
    try:
        meeting_ref = db.collection('meetings').document(meeting_id)
        meeting = meeting_ref.get()
        if meeting.exists:
            return meeting.to_dict()
        else:
            click.echo("Meeting not found")
            return None
    except Exception as e:
        click.echo(f"Error fetching meeting data: {e}")
        return None

def notify_meeting_confirmation(meeting_id):
    ''''Notifying attendees of the meeting confirmation.'''
    meeting_data = fetch_meeting_data(meeting_id)
    if meeting_data:
        send_meeting_notification(meeting_data)

def send_workshop_notification(workshop_data, notification_type="confirmation"):
    '''Sending workshop notifications based on type (confirmation, reminder, update, etc.)'''

    if notification_type == "confirmation":
        subject = "Workshop Confirmation"
    elif notification_type == "update":
        subject = "Workshop Update"
    elif notification_type == "cancellation":
        subject = "Workshop Cancellation"
    else:
        subject = "Workshop Notification"

    body = f"""
    Workshop: {workshop_data['Title']}
    Date: {workshop_data['date']}
    Time: {workshop_data['start_time']} - {workshop_data['end_time']}
    Location: {workshop_data['location']}
    Organizer: {workshop_data['organizer']}
    Description: {workshop_data['description']}
    """
    
    if notification_type == "reminder":
        body = "Reminder: " + body
    elif notification_type == "update":
        body = "Update: " + body
    elif notification_type == "cancellation":
        body = "Cancellation: " + body

    for attendee in workshop_data['attendees']:
        try:
            send_email(subject, body, attendee)
            click.echo(f"Notification sent to {attendee}")
        except Exception as e:
            click.echo(f"⚠️ Failed to send notification to {attendee}: {e}")