import pyrebase
import click
import os
import pwinput
import datetime
import os.path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow 
from googleapiclient.discovery import build  
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.events'
         ]

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

cred = credentials.Certificate("skillssync-f88a7-firebase-adminsdk-u1lm7-2bf0d05d8f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

firebase=pyrebase.initialize_app(Config)
auth=firebase.auth()

@click.group()
def cli():
    pass

@cli.command()
def signin():
    """Welcome Back, Please Sign in"""
    email = input("Enter your email: ")
    password = pwinput.pwinput(prompt='Enter your Password: ', mask='#')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_info = auth.get_account_info(user['idToken'])
        if not user_info['users'][0]['emailVerified']:
            click.echo('Error: Please verify your email first.')
            return
        click.echo(f'successfully signed in {email}')
    except Exception as e:
        click.echo(f'Invalid credentials or the user {e} does not exist')

@cli.command()
def signup():
    """Hello, Join us by signing up"""
    name = input("Enter your Full Name: ")
    email = input("Enter your email: ")

    while True:
        password = pwinput.pwinput(prompt='Enter your Password: ', mask='#')
        confirm_password = pwinput.pwinput(prompt='Confirm Your password: ', mask='#')
        if password != confirm_password:
            click.echo('Error: Password do not match!')
            continue
        validation = valid_input(password, email)
        if not validation:
            click.echo('Error! Invalid Password or Email')
            continue
        try:
            user = auth.create_user_with_email_and_password(email,password)
            auth.send_email_verification(user['idToken'])
            click.echo(f'Account created successfully, {email}')
            db.collection('users').add({'name':name, 'email': email})
            break
        except Exception as e:
            click.echo(f'Error: Email already been used {e}')

@cli.command()
def reset_password():
    '''Please provide us with your email to reset the password.'''
    email = input('Enter your email: ')
    try:
        auth.send_password_reset_email(email)
        click.echo(f'Password reset email sent to {email} inbox')
    except Exception as e:
        click.echo(f'Error: Invalid email provided {e}')

@cli.command()
def signout():
    '''Hate to see you leave, Come back soon...'''
    try:
        auth.current_user = None
        click.echo('Thank you for visiting. Bye')
    except Exception as e:
        click.echo(f'Run into an issue while signing out: {e}')

def valid_input(password, email):
    if len(password) < 8:
        return False

    has_digit = False
    has_lowercase = False
    has_uppercase = False
    has_specialChar = False

    for char in password:
        if char.isdigit():
            has_digit = True
        if char.islower():
            has_lowercase = True
        if char.isupper():
            has_uppercase = True
        if not char.isalnum(): 
            has_specialChar = True

    if not has_digit:
        return False
    if not has_lowercase:
        return False
    if not has_uppercase:
        return False
    if not has_specialChar:
        return False
   
    if '@gmail.com' not in email:
        return False

    return email, password
    
def bookings():
    cred = None
    if os.path.exists('token.json'):
        cred = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json',SCOPES)
            cred = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(cred.to_json())
    try:
        service = build('calendar', 'v3', credentials=cred)
        now = datetime.datetime.now().isoformat() + 'Z'
        event_result = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents= True, orderBy='startTime')
    except HttpError as error:
        click.echo(f'An error occured: {error}')
cli.add_command(signin)
cli.add_command(signup)
cli.add_command(reset_password)
cli.add_command(signout)

if __name__ =='__main__':
    cli()