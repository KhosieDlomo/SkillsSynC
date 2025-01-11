import pyrebase
import click
import os
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
firebase=pyrebase.initialize_app(Config)
auth=firebase.auth()

def signin():
    email = input("Enter your email: ")
    password = input('Enter your Password:')
    try:
        signin = auth.sign_in_with_email_and_password(email, password)
        print('successfully signedIn')
    except Exception as e:
        print('Invalid credentials')
    return

def signup():
    email = input("Enter your email: ")
    password = input('Enter your Password:')
    try:
        user = auth.create_user_with_email_and_password(email,password)
    except Exception as e:
        print('Email already been used')
    return

