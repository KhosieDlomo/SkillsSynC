import pyrebase
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
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
creds = {'db_firebase': os.getenv('DB_FIRESTORE')}
cred = credentials.Certificate(creds)
firebase_admin.initialize_app(cred)

db = firestore.client()

firebase=pyrebase.initialize_app(Config)
auth=firebase.auth()