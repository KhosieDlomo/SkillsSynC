from firebase_auth import db
import click
from datetime import datetime,timedelta
from google.cloud import firestore
from utils import handle_no_mentors_or_peers
import pytz

SAST =pytz.timezone('African/Johannesburg')

def get_all_users(role=None, expertise=None, language=None, available=True):
    try:
        users_ref = db.collection('users')
        if role:
            users_ref = users_ref.where(filter=firestore.FieldFilter('role', '==', role))
        
        users = users_ref.stream()
        user_lst = list(users)
        click.echo(f"Debug: Fetched {len(user_lst)} users with role={role}, expertise={expertise}, language={language}, available={available}")
        return user_lst
    except Exception as e:
        click.echo(f"Error fetching users: {e}")
        return []

def calculate_availability(user_data):
    '''Getting the availability days of users '''
    available_days = user_data.get('available_days', 'Not Specified')
    available_time_start = user_data.get('available_time_start', 'Not Specified')
    available_time_end = user_data.get('available_time_end', 'Not Specified')

    if available_days == 'Not Specified' or available_time_start == 'Not Specified' or available_time_end == 'Not Specified':
        return {
            'available_days': 'Everyday',
            'available_time_start': '00:00',
            'available_time_end': '23:59'
        }

    today = datetime.now(SAST)
    unavailable_for_first_4_days = True
    for day in range(4):
        check_date = today + timedelta(days=day)
        if check_date.strftime('%A') in available_days:
            unavailable_for_first_4_days = False
            break

    if unavailable_for_first_4_days:
        return {
            'available_days': available_days,
            'available_time_start': available_time_start,
            'available_time_end': available_time_end
        }
    else:
        return {
            'available_days': 'Everyday',
            'available_time_start': '00:00',
            'available_time_end': '23:59'
        }
def available_mentors(expertise = None, language = None):
    """Functions to display available mentors"""
    try:
        mentors = get_all_users(role='mentor')
                
        mentor_lst = []
        click.echo('Available Mentors...')
        for mentor in mentors:
            mentor_info = mentor.to_dict()    
            availability = calculate_availability(mentor_info)        
            mentor_lst.append({'id': mentor.id, 'name': mentor_info.get('name', 'unknown'), 'email': mentor_info.get('email', 'unknown'), 'expertise': mentor_info.get('expertise', 'unknown'), 'language': mentor_info.get('language', 'unknown'), 'available_days': availability['available_days'], 'available_time_start':availability['available_time_start'], 'available_time_end':availability['available_time_end']})
            
            click.echo(f" - Name: {mentor_info.get('name', 'Unknown')}, Email: {mentor_info.get('email', 'Unknown')}, Expertise: {mentor_info.get('expertise', 'Unknown')}, Language: {mentor_info.get('language', 'Unknown')}, Available: {availability['available_days']}, Time: {availability['available_time_start']}-{availability['available_time_end']}")
        
        if not mentor_lst:
            click.echo('No mentors available at the moment.')
            handle_no_mentors_or_peers()
        return mentor_lst
    except Exception as e:
        click.echo(f"Error fetching mentors: {e}")
        return []
            
def available_peers(expertise=None, language = None):
    '''Function to display all the available peers'''
    try:
        peers = get_all_users(role='peer')
        
        peers_lst = []
        click.echo('Available Peers...')
        
        for peer in peers:
            peer_info = peer.to_dict()
            availability = calculate_availability(peer_info)        

            peers_lst.append({"id": peer.id, 'name': peer_info['name'],'email': peer_info['email'], 'expertise': peer_info.get('expertise', 'unknown'), 'language': peer_info.get('language', 'unknown'),'available_days': availability['available_days'], 'available_time_start':availability['available_time_start'], 'available_time_end':availability['available_time_end']})
            click.echo(f" - Name: {peer_info['name']}, Email: {peer_info['email']}, Expertise: {peer_info.get('expertise', 'unknown')}, Language: {peer_info.get('language', 'unknown')}, Available: {availability['available_days']}, Time: {availability['available_time_start']}-{availability['available_time_end']}")
        
        if not peers_lst:
            click.echo('No peers available at the moment.')
            handle_no_mentors_or_peers()
        return peers_lst
    except Exception as e:
        click.echo(f"Error while fetching peers: {e}")
    
def feedback(user_id, mentor_id, rates, comment):
    '''Function for sending Feedback about the experience.'''
    try:
        feedback_val = db.collection('feedback').document()
        feedback_info = {'user_id': user_id, 'mentor_id': mentor_id, 'rating': rates, 'comment': comment, 'timestamp': datetime.now(SAST)}
        feedback_val.set(feedback_info)
        click.echo('Feedback sumbitted successfully!')
    except Exception as e:
        click.echo(f"Error submitting feedback: {e}")
        click.echo('Failed to submit feedback. Please try again.')

def registered_users(role = None):
    '''Getting all existing users in the firebase.'''
    try:
        users = get_all_users(role=role)
        
        users_lst = []
        for user in users:
            user_data = user.to_dict()
            users_lst.append({'email': user_data.get('email'), 'role': user_data.get('role', 'peer'), 'expertise': user_data.get('expertise', 'N/A'), 'availability': user_data.get('availability', True)})
        return users_lst
    except Exception as e:
        click.echo(f"Error fetching users: {e}")
        return []
