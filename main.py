import pyrebase
import click
import os
import pwinput
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
        click.echo(f'successfully signed in {email}')
    except Exception as e:
        click.echo(f'Invalid credentials or the user {e} does not exist')

@cli.command()
def signup():
    """Hello, Join us by signing up"""
    email = input("Enter your email: ")
    password = pwinput.pwinput(prompt='Enter your Password: ', mask='#')
    try:
        user = auth.create_user_with_email_and_password(email,password)
        click.echo(f'Account created successfully, {email}')
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

cli.add_command(signin)
cli.add_command(signup)
cli.add_command(reset_password)
cli.add_command(signout)

if __name__ =='__main__':
    cli()