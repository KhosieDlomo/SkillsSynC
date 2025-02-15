import click
from login import * 
from session import logged_in, user_email, user_role
from workshops import view_workshop, create_workshop
from events import *
import firebase_admin
from firebase_admin import auth

@click.group()
def cli():
    pass

cli.add_command(signin)
cli.add_command(signup)
cli.add_command(reset_password)
cli.add_command(signout)
# cli.add_command(bookings)
# cli.add_command(view_booking)
# cli.add_command(cancel_booking)
# cli.add_command(view_workshop)
# cli.add_command(create_workshop)

def main_menu():
    """Hello, Here is the Menu."""
    try:
        while True:
            click.echo('\n--- Main Menu ---')
            if logged_in:
                click.echo(f"Logged in as {user_email} (Role: {user_role})")
                click.echo("1. Book a Meeting")
                click.echo("2. view Bookings")
                click.echo("3. Cancel Booking")
                click.echo("4. View Workshops")
                if user_role == 'mentor':
                    click.echo("5. Create Workshop")
                click.echo("6. Signout")
                click.echo("7. Exit")
                
                choice = click.prompt("Enter your choice", type=int)

                if choice == 1:
                    bookings()
                elif choice == 2:
                    view_booking()
                elif choice == 3:
                    cancel_booking()
                elif choice == 4:
                    view_workshop()
                elif choice == 5 and user_role == 'mentor':
                    create_workshop()
                elif choice == 6:
                    signout()
                    break  
                elif choice == 7:
                    try:
                        firebase_admin.delete_app(firebase_admin.get_app())
                    except ValueError:
                        pass
                    click.echo("Exiting...")
                    exit()
                else:
                    click.echo("Invalid choice. Please try again.")
            else:
                click.echo("1. Sign In")
                click.echo("2. Sign Up")
                click.echo("3. Reset Password")
                click.echo("4. Exit")

                choice = click.prompt("Enter your choice", type=int)

                if choice == 1:
                    if signin(): 
                        main_menu()
                        break 
                elif choice == 2:
                    signup()
                elif choice == 3:
                    reset_password()
                elif choice == 4:
                    try:
                        firebase_admin.delete_app(firebase_admin.get_app())
                    except ValueError:
                        pass
                    click.echo("Exiting...")
                    exit()
                else:
                    click.echo("Invalid choice. Please try again.")
    
    except Exception as e:
        click.echo(f"ERROR: An exception occurred: {e}")

if __name__ =='__main__':
    main_menu()