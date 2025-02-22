import click
from workshops import view_workshop, create_workshop
from login import current_session

def handle_no_mentors_or_peers():
    """Handles where no mentors or peers are available."""
    
    click.echo("\n⚠ No mentors or peers are available at the moment.")
    click.echo("\nWould you like to:")
    click.echo("1. View bookings")
    click.echo("2. View upcoming workshops")
    click.echo("3. Cancel booking")
    if current_session['role'] == 'mentor':
        click.echo("4. Create workshops")
    click.echo("5. Return to the main menu.")
    
    choice = click.prompt("Ente r your choice", type=int)
    
    if choice == 1:
        from events import view_booking
        view_booking()
    elif choice == 2:
        view_workshop()  
    elif choice == 3:
        from events import cancel_booking
        cancel_booking()
    elif choice == 4 and current_session['role'] == 'mentor':
        create_workshop()
    elif choice == 5:
        from main import main_menu
        main_menu()
    else:
        click.echo("Invalid choice. Returning to the main menu.")
        main_menu()
