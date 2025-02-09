from firebase_auth import db
import click
from datetime import datetime


def listing_available_mentors():
    """Functions to display available mentors"""
    mentors = db.collection('users').where('role', '==', 'mentor').stream()
    
    mentor_lst = []
    click.echo('Available Mentors...')
    for mentor in mentors:
        mentor_info = mentor.to_dict()
        mentor_id = mentor.id
        mentor_lst.append({'id': mentor_id, 'name': mentor_info['name'], 'email': mentor_info['email']})
        click.echo(f' - Name: {mentor_info['name']}, Email: {mentor_info['email']},ID: {mentor.id}')
    if not mentor_lst:
        click.echo('No mentors available at the moment.')
    else:
        return mentor_lst
            
def available_peers():
    '''Function to display all the available peers'''
    peers = db.collection('users').where('role', '==', 'peer').get()
    if not peers:
        click.echo('No peers available at the moment.')
        return []
    click.echo('Available Peers...')
    peers_lst = []
    for peer in peers:
        peer_info = peer.to_dict()
        click.echo(f' - Name: {peer_info['name']}, Email: {peer_info['email']}, ID: {peer.id}')
        peers_lst.append({"id": peer.id, 'name': peer_info['name'],'email': peer_info['Email']})
        return peers_lst
    
