# cleanup.py
import datetime
from firebase_auth import db
from google.cloud import firestore
import pytz

SAST = pytz.timezone('Africa/Johannesburg')

def cleanup_expired_entries():
    """Delete expired workshops and meetings from Firestore."""
    try:
        current_time = datetime.datetime.now(SAST)

        # Clean up expired workshops
        workshops_ref = db.collection('workshops').stream()
        for workshop in workshops_ref:
            workshop_data = workshop.to_dict()
            end_time = datetime.datetime.fromisoformat(workshop_data.get('end_time', ''))
            
            if end_time.tzinfo is None:
                end_time = SAST.localize(end_time)
            
            if end_time < current_time:
                db.collection('workshops').document(workshop.id).delete()
                print(f"✅ Deleted expired workshop: {workshop_data.get('Title', 'Untitled Workshop')}")

        # Clean up expired meetings
        meetings_ref = db.collection('meetings').stream()
        for meeting in meetings_ref:
            meeting_data = meeting.to_dict()
            end_time = datetime.datetime.fromisoformat(meeting_data.get('end_time', ''))
            
            if end_time.tzinfo is None:
                end_time = SAST.localize(end_time)
            
            if end_time < current_time:
                db.collection('meetings').document(meeting.id).delete()
                print(f"✅ Deleted expired meeting: {meeting_data.get('subject', 'No Subject')}")

    except Exception as e:
        print(f"⚠️ Error cleaning up expired entries: {e}")