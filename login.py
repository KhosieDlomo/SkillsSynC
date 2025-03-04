import click
import pwinput
from firebase_auth import auth, db, current_session
from validation import valid_input
import requests
from datetime import datetime

def signin():
    """Welcome Back, Please Sign in"""
    email = click.prompt("Enter your email ")
    password = pwinput.pwinput(prompt='Enter your Password: ', mask='#')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_info = auth.get_account_info(user['idToken'])
        if not user_info['users'][0]['emailVerified']:
            click.echo('Error: Please verify your email first.')
            print("Email not verified")
            return False
         

        user_doc = db.collection('users').document(user['localId']).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            user_role = user_data.get('role')
            print(f"User role: {user_role}")

            # Updating the current session in memory
            current_session['user_id'] = user['localId']
            current_session['email'] = email
            current_session['role'] = user_role
            current_session['logged_in'] = True
            
            #creating a session in Firestore
            db.collection('sessions').document(user['localId']).set({'logged_in': True, 'email':email, 'role': 'user', 'last_active': datetime.now()})
            
            click.echo(f'Successfully signed in {email} (Role: {user_role})')
            return True 
        else:
            click.echo("Error: Could not retrieve user role.")
            print("Could not retrieve user role.")
            return False
                
    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            try:
                error_response = e.response.json()
                if error_response.get("error", {}).get("message") == "INVALID_LOGIN_CREDENTIALS":
                    click.echo("Invalid email or password. Please try again.")
                else:
                    click.echo(f"An error occurred: {error_response.get('error', {}).get('message', 'Unknown error')}")
                
            except ValueError:
                click.echo("Error decoding the error response.")
        else:
            click.echo("A network error occurred. Please check your connection and try again.")
        return False
    
    except Exception as e:
        click.echo(f'Invalid credentials or the user does not exist : {e}')
        return False

@click.command()
def signup():
    """Hello, Join us by signing up"""
    name = click.prompt("Enter your Full Name ")
    email = click.prompt("Enter your email ")
    role = click.prompt('Enter your role (Mentor/Peer) ').lower()
    while role not in ['mentor', 'peer']:
        click.echo('Invalid role. Please enter "Mentor" or "Peer".')
        role = click.prompt('Enter your role (Mentor/Peer) ').lower()
    
    if role == 'mentor':
        expertise = click.prompt('Enter your expertise, e.g ("Frontend Developer", "Backend Developer", "Fullstack Developer") ').title()
        languages = click.prompt('Enter your expertise languages, separated by commas (e.g., Python, React, Java, etc): ').capitalize()
       
    elif role == 'peer':
        expertise = click.prompt('Enter your area of interest or expertise (e.g., Frontend Developer, Backend Developer, or Fullstack Developer) ').title()
        languages = click.prompt('Enter your area of interest or expertise language, seperated by commas (e.g., Python, Java, Nextjs, etc) ').capitalize()
    
    expertise_languages = []
    for lang in languages.split(','):
        if languages:
            expertise_languages.append(lang.strip())
        else:
            expertise_languages


    while True:
        password = pwinput.pwinput(prompt='Enter your Password: ', mask='#')
        confirm_password = pwinput.pwinput(prompt='Confirm Your password: ', mask='#')
        if password != confirm_password:
            click.echo('Error: Passwords do not match!')
            continue
        validation = valid_input(password, email)
        if not validation:
            click.echo('Error! Invalid Password or Email.')
            continue
        try:
            user = auth.create_user_with_email_and_password(email,password)
            auth.send_email_verification(user['idToken'])
            click.echo(f'Account created successfully, {email}')
            db.collection('users').document(user['localId']).set({'name': name, 'email': email, 'role': role, 'expertise' : expertise, 'languages': expertise_languages})
            break
        except Exception as e:
            if email:
                click.echo(f'Error: The email {email}has already been used: {e}')
            else:
                click.echo(f'Error! An unexpected erro occured: {e}')

@click.command()
def reset_password():
    '''Please provide us with your email to reset the password.'''
    email = click.prompt('Enter your email: ')
    try:
        auth.send_password_reset_email(email)
        click.echo(f'Password reset email sent to {email} inbox')
    except Exception as e:
        click.echo(f'Error: Invalid email provided, Could not send reset email: {e}')

@click.command()
def signout():
    '''Hate to see you leave, Come back soon...'''
    if not current_session['logged_in']:
        click.echo("No user is currently logged in.")
        return

    try:
        db.collection('sessions').document(current_session['user_id']).delete()
        current_session['user_id'] = None
        current_session['email'] = None
        current_session['role'] = None
        current_session['logged_in'] = False
        click.echo('Signed out Successfully. Thank you for visiting. Goodbye')
    except Exception as e:
        click.echo(f'Run into an issue while signing out: {e}')