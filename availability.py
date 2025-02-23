from firebase_auth import db
import click
from datetime import datetime
from google.cloud import firestore
from utils import handle_no_mentors_or_peers

def available_mentors(expertise = None, language = None, available = True):
    """Functions to display available mentors"""
    try:
        mentors_ref = db.collection('users').where(filter=firestore.FieldFilter('role', '==', 'mentor'))

        if expertise:
            mentors_ref = mentors_ref.where(filter=firestore.FieldFilter('expertise', '==', expertise))
        if language:
            mentors_ref = mentors_ref.where(filter=firestore.FieldFilter('language', '==', language))
        if available:
            mentors_ref = mentors_ref.where(filter=firestore.FieldFilter('availability', '==', available))
        
        mentors = mentors_ref.stream()
        
        mentor_lst = []
        click.echo('Available Mentors...')
        for mentor in mentors:
            mentor_info = mentor.to_dict()
            mentor_id = mentor.id
            available_days = mentor_info.get('available_days', 'Not Specified')
            available_time_start = mentor_info.get('available_time_start', 'Not Specified')
            available_time_end = mentor_info.get('available_time_end', 'Not Specified')

            mentor_lst.append({'id': mentor_id, 'name': mentor_info['name'], 'email': mentor_info['email'], 'expertise': mentor_info.get('expertise', 'unknown'), 'language': mentor_info.get('language', 'unknown'), 'available_days': available_days, 'available_time_start':available_time_start, 'available_time_end': available_time_end})
            
            click.echo(f" - Name: {mentor_info['name']}, Email: {mentor_info['email']},Expertise: {mentor_info.get('expertise','unknown')}, Language: {mentor_info.get('language', 'unknown')},  Available:{available_days}, Time:{available_time_start}-{available_time_end} ")
        
        if not mentor_lst:
            click.echo('No mentors available at the moment.')
            handle_no_mentors_or_peers()
        return mentor_lst
    except Exception as e:
        click.echo(f"Error fetching mentors: {e}")
        return []
            
def available_peers(expertise=None, language = None, available=True):
    '''Function to display all the available peers'''
    try:
        peers_ref = db.collection('users').where(filter=firestore.FieldFilter('role', '==', 'peer'))

        if expertise:
            peers_ref = peers_ref.where(filter=firestore.FieldFilter('expertise', '==', expertise))
        if language:
            peers_ref = peers_ref.where(filter=firestore.FieldFilter('language', '==', language))
        # if available:
        #     peers_ref = peers_ref.where(filter=firestore.FieldFilter('availability', '==', available))

        peers = peers_ref.stream()
        
        peers_lst = []
        click.echo('Available Peers...')
        
        for peer in peers:
            peer_info = peer.to_dict()
            available_days = peer_info.get('available_days', 'Not Specified')
            available_time_start = peer_info.get('available_time_start', 'Not Specified')
            available_time_end = peer_info.get('available_time_end', 'Not Specified')

            peers_lst.append({"id": peer.id, 'name': peer_info['name'],'email': peer_info['email'], 'expertise': peer_info.get('expertise', 'unknown'), 'language': peer_info.get('language', 'unknown'), 'available_days':available_days, 'available_time_start':available_time_start, 'available_time_end':available_time_end})
            click.echo(f" - Name: {peer_info['name']}, Email: {peer_info['email']}, Expertise: {peer_info.get('expertise', 'unknown')}, Language: {peer_info.get('language', 'unknown')}, Available:{available_days}, Time:{available_time_start}-{available_time_end}")
        
        if not peers_lst:
            click.echo('No peers available at the moment.')
            handle_no_mentors_or_peers()
        return peers_lst
    except Exception as e:
        click.echo(f"Error while fetching peers: {e}")
    
def feedback(user_id, mentor_id, rates, comment):
    '''Function for sending Feedback about the experience.'''
    feedback_val = db.collection('feedback').document()
    feedback_info = {'user_id': user_id, 'mentor_id': mentor_id, 'rating': rates, 'comment': comment, 'timestamp': datetime.utcnow()}
    feedback_val.set(feedback_info)
    click.echo('Feedback sumbitted successfully!')

def registered_users(role = None):
    '''Getting all existing users in the firebase.'''
    try:
        if role:
            user_ref = db.collection('users').where(filter=firestore.FieldFilter('role', '==', role)).stream()
        else:
            user_ref = db.collection('users').stream()
        
        users = []
        for user in user_ref:
            user_data = user.to_dict()
            users.append({'email': user_data.get('email'), 'role': user_data.get('role', 'peer'), 'expertise': user_data.get('expertise', 'N/A'), 'availability': user_data.get('availability', True)})
        return users
    except Exception as e:
        click.echo(f"Error fetching users: {e}")
        return []
