import click, datetime
from firebase_auth import db, current_session

@click.command()
def submit_feedback():
    """Submit feedback for a mentor or peer."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    user_id = current_session.get('user_id')
    user_email = current_session.get('email')

    if not user_id or not user_email:
        click.echo("⚠️ User not authenticated. Please sign in.")
        main_menu()
        return

    recipient_email = click.prompt("Enter the email of the mentor or peer you want to provide feedback for")
    rating = click.prompt("Rate the mentor/peer (1-5)", type=int)
    comment = click.prompt("Leave a comment (optional)", default="", show_default=False)

    if rating < 1 or rating > 5:
        click.echo("⚠️ Rating must be between 1 and 5.")
        main_menu()
        return

    feedback_data = {
        'user_id': user_id,
        'user_email': user_email,
        'recipient_email': recipient_email,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.datetime.now().isoformat()
    }

    try:
        db.collection('feedback').add(feedback_data)
        click.echo("✅ Feedback submitted successfully.")
    except Exception as e:
        click.echo(f"⚠️ Error submitting feedback: {e}")
    
    main_menu()

@click.command()
def view_feedback():
    """View feedback for a mentor or peer."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    user_email = click.prompt("Enter the email of the mentor or peer to view feedback")

    try:
        feedback_ref = db.collection('feedback').where('recipient_email', '==', user_email).stream()
        feedback_list = [feedback.to_dict() for feedback in feedback_ref]

        if not feedback_list:
            click.echo("⚠️ No feedback found for this user.")
            main_menu()
            return

        click.echo(f"📝 Feedback for {user_email}:")
        for feedback in feedback_list:
            click.echo(f"Rating: {feedback['rating']}/5")
            click.echo(f"Comment: {feedback['comment']}")
            click.echo(f"Submitted by: {feedback['user_email']}")
            click.echo(f"Date: {feedback['timestamp']}")
            click.echo("-" * 80)
    except Exception as e:
        click.echo(f"⚠️ Error fetching feedback: {e}")
    
    main_menu()

@click.command()
def search_mentors_peers():
    """Searching for mentors or peers by expertise or availability."""
    from main import main_menu

    if not current_session['logged_in']:
        return
    
    expertise = click.prompt("Enter desired expertise (optional)", default="", show_default=False)
    availability = click.prompt("Enter desired availability (e.g., 'Monday', 'Tuesday') (optional)", default="", show_default=False)

    try:
        mentors_query = db.collection('users').where('role', '==', 'mentor')
        peers_query = db.collection('users').where('role', '==', 'peer')

        if expertise:
            mentors_query = mentors_query.where('expertise', '==', expertise)
            peers_query = peers_query.where('expertise', '==', expertise)
        
        if availability:
            mentors_query = mentors_query.where('available_days', 'array_contains', availability)
            peers_query = peers_query.where('available_days', 'array_contains', availability)

        mentors = [doc.to_dict() for doc in mentors_query.stream()]
        peers = [doc.to_dict() for doc in peers_query.stream()]

        click.echo("\n📋 Matching Mentors:")
        for mentor in mentors:
            click.echo(f"Name: {mentor['name']}, Email: {mentor['email']}, Expertise: {mentor['expertise']}")

        click.echo("\n📋 Matching Peers:")
        for peer in peers:
            click.echo(f"Name: {peer['name']}, Email: {peer['email']}, Expertise: {peer['expertise']}")

    except Exception as e:
        click.echo(f"⚠️ Error searching mentors/peers: {e}")
    
    main_menu()