import pyrebase
import os
import firebase_admin
from firebase_admin import firestore, credentials
from dotenv import load_dotenv

load_dotenv()


Config = {
          'apiKey':os.getenv('API_KEY'),
          'authDomain':os.getenv('AUTH_DOMAIN'),
          'projectId': os.getenv('PROJECT_ID'),
          'storageBucket':os.getenv('STORAGE_BUCKET'),
          'messagingSenderId': os.getenv('MESSAGE_SENDER_ID'),
          'appId': os.getenv('APP_ID'),
          'measurementId': os.getenv('MEASUREMENT_ID'),
          'databaseURL':os.getenv('DATABASE_URL')
          }

cred = credentials.Certificate('skillssync-f88a7-firebase-adminsdk-u1lm7-2bf0d05d8f.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

firebase=pyrebase.initialize_app(Config)
auth=firebase.auth()

#storing the current session
current_session = {
    'user_id': None,
    'email': None,
    'role': None,
    'logged_in': False
}

def require_auth(user_id):
    '''Checking and make sure that user loged in before using features, by querying Firestore.'''
    try:
        session_ref = firestore.client().collection('sessions').document(user_id)
        session = session_ref.get()
        
        if not session.exists or not session.to_dict().get('logged_in'):
            return False, "Please sign in to use this feature."
        return True, "User is authenticated."
    except Exception as e:
        return False, f"Error checking authentication: {e}"
