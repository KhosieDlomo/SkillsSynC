from firebase_auth import db
import click
from datetime import datetime


def available_mentors(expertise = None, available =True):
    """Functions to display available mentors"""
    mentors = db.collection('users').where('role', '==', 'mentor').stream()

    if expertise:
        mentors = mentors.where('expertise', '==', expertise)
    if available:
        mentors = mentors.where('availability', '==', available)
    
    mentor_lst = []
    click.echo('Available Mentors...')
    for mentor in mentors:
        mentor_info = mentor.to_dict()
        mentor_id = mentor.id
        mentor_lst.append({'id': mentor_id, 'name': mentor_info['name'], 'email': mentor_info['email'], 'expertise': mentor_info.get('expertise', 'unknown')})
        click.echo(f' - Name: {mentor_info['name']}, Email: {mentor_info['email']},Expertise: {mentor_info.get('expertise','unknown')}')
    if not mentor_lst:
        click.echo('No mentors available at the moment.')
    return mentor_lst
            
def available_peers(expertise=None, available=True):
    '''Function to display all the available peers'''
    peers = db.collection('users').where('role', '==', 'peer').stream()

    if expertise:
        peers = peers.where('expertise', '==', expertise)
    if available:
        peers = peers.where('availability', '==', available)

    peers_lst = []
    click.echo('Available Peers...')
    
    for peer in peers:
        peer_info = peer.to_dict()
        peers_lst.append({"id": peer.id, 'name': peer_info['name'],'email': peer_info['email'], 'expertise': peer_info.get('expertise', 'unknown')})
        click.echo(f' - Name: {peer_info['name']}, Email: {peer_info['email']}, Expertise: {peer_info.get('expertise', 'unknown')}')
    if not peers_lst:
        click.echo('No peers available at the moment.')
        
    return peers_lst
    
def feedback(user_id, mentor_id, rates, comment):
    '''Function for sending Feedback about the experience.'''
    feedback_val = db.collection('feedback').document()
    feedback_info = {'user_id': user_id, 'mentor_id': mentor_id, 'rating': rates, 'comment': comment, 'timestamp': datetime.utcnow()}
    feedback_val.set(feedback_info)
    click.echo('Feedback sumbitted successfully!')
