import datetime
import click

def valid_input(password, email):
    '''function for validating password and email.'''
   
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

    return True

def valid_time(str_time):
    '''Function to validate time.'''
    try:
        val_time = datetime.datetime.strptime(str_time, '%H:%M')
        if val_time.hour < 7 or val_time.hour >= 17:
            click.echo("Meeting can only be scheduled between 07:00 and 17:00.")
            return False
        return True
    except ValueError:
        click.echo('Invalid time format. Please use HH:MM (e.g. 11:25).')
        return False
    
def valid_date(str_date):
    '''Function to validate date.'''
    try:
        val_date = datetime.datetime.strptime(str_date, '%d/%m/%Y')
        week_days = val_date.weekday()
        if week_days >= 5:
            click.echo('Meeting can only be scheduled on weekdays from Monday to Friday.')
            return False
        return True
    except ValueError:
        click.echo('Invalid date format. Please use DD/MM/YYYY (e.g. 20/08/2025).')
        return False 
    