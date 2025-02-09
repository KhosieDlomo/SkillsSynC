import click
import pwinput
from firebase_auth import auth, db
from validation import valid_input

@click.command()
def signin():
    """Welcome Back, Please Sign in"""
    email = click.prompt("Enter your email: ")
    password = pwinput.pwinput(prompt='Enter your Password: ', mask='#')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_info = auth.get_account_info(user['idToken'])
        if not user_info['users'][0]['emailVerified']:
            click.echo('Error: Please verify your email first.')
            return
        click.echo(f'Successfully signed in {email}')
        auth.current_user = user
    except Exception as e:
        click.echo(f'Invalid credentials or the user does not exist : {e}')
        return

@click.command()
def signup():
    """Hello, Join us by signing up"""
    name = click.prompt("Enter your Full Name: ")
    email = click.prompt("Enter your email: ")
    role = click.prompt('Enter your role (Mentor/Peer): ').lower()
    while role not in ['mentor', 'peer']:
        click.echo('Invalid role. Please enter "Mentor" or "Peer".')
        role = click.prompt('Enter your role (Mentor/Peer): ').lower()
    
    if role == 'mentor':
        expertise = click.prompt('Enter your expertise, e.g ("Frontend Developer", "Backend Developer", "Fullstack Developer"): ').title()
        languages = click.prompt('Enter your expertise languages, separated by commas (e.g., Python, React, Java, etc): ').capitalize()
       
    elif role == 'peer':
        expertise = click.prompt('Enter your area of interest or expertise (e.g., Frontend Developer, Backend Developer, or Fullstack Developer): ').title()
        languages = click.prompt('Enter your area of interest or expertise language, seperated by commas (e.g., Python, Java, Nextjs, etc): ').capitalize()
    
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
    try:
        auth.current_user = None
        click.echo('Signed out Successfully. Thank you for visiting. Goodbye')
    except Exception as e:
        click.echo(f'Run into an issue while signing out: {e}')