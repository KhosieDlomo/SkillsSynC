import pyrebase
import click
import os
from dotenv import load_dotenv

load_dotenv()

firebaseConfig = {

  'apiKey':os.getenv('API_KEY'),

  'authDomain':os.getenv('AUTH_DOMAIN'),

  'projectId': os.getenv('PROJECT_ID'),

  'storageBucket':os.getenv('STORAGEB_UCKET'),

  'messagingSenderId': os.getenv('MESSAGE_SENDER_ID'),

  'appId': os.getenv('APP_ID'),

  'measurementId': os.getenv('MEASUREMENT_ID') 

}
