import click
import pwinput
from firebase_auth import auth, db
from validation import valid_input

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
    role = input('Enter your role (Mentor/Peer)').capitalize()

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
            db.collection('users').add({'name':name, 'email': email, 'role': role})
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