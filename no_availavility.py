import click
from workshops import view_workshop, create_workshop
from events import view_booking, cancel_booking
from skillsSync import main_menu

def handle_no_mentors_or_peers():
    """Handles where no mentors or peers are available."""
    click.echo("\n⚠ No mentors or peers are available at the moment.")
    click.echo("\nWould you like to:")
    click.echo("1. View bookings?")
    click.echo("2. View upcoming workshops?")
    click.echo("3. Cancel booking?")
    click.echo("4. Create workshops?")
    click.echo("5. Return to the main menu.")
    
    choice = click.prompt("Enter your choice", type=int)
    
    if choice == 1:
        view_booking()
    elif choice == 2:
        view_workshop()  
    elif choice == 3:
        cancel_booking()
    elif choice == 4:
        create_workshop()
    elif choice == 5:
        main_menu()
    else:
        click.echo("Invalid choice. Returning to the main menu.")
        main_menu()
