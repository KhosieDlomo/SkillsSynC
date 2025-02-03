from firebase_auth import auth, db
import click
from datetime import datetime

def listing_available_mentors():
    """Functions to display available mentors"""
    mentors = db.collection('users').where('role', '==', 'mentor').get()
    if not mentors:
        click.echo('No mentors available at the moment.')
        return []
    click.echo('Available Mentors: ')
    mentor_lst = []
    for mentor in mentors:
        mentor_info = mentor.to_dict()
        click.echo(f' - Name: {mentor_info['name']}, Email: {mentor_info['email']},ID: {mentor.id}')
        mentor_lst.append({'id': mentor.id, 'name': mentor_info['name'], 'email': mentor_info['email']})
        return mentor_lst