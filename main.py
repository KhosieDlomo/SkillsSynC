import click
from login import signin, signup, reset_password, signout, current_session
from events import view_booking, cancel_booking
from book_meetings import bookings
from workshops import view_workshop, create_workshop,cancel_workshop
import firebase_admin
from stretch_feature import *

def main_menu():
    """Hello, Here is the Menu."""
    try:
        while True:
            click.echo('\n--- Main Menu ---')
            if current_session['logged_in']:
                click.echo(f"Logged in as {current_session['email']} (Role: {current_session['role']})")
                click.echo("1. Book a Meeting")
                click.echo("2. view Bookings")
                click.echo("3. Cancel Booking")
                if current_session['role'] == 'mentor':
                    click.echo("4. Create Workshop")
                click.echo("5. View Workshops")
                click.echo("6. Cancel Workshops")
                click.echo("7. Submit Feedback")
                click.echo("8. View Feedback")
                click.echo("9. Search Mentors/Peers")

                click.echo("#. Signout")
                click.echo("*. Exit")
                
                choice = click.prompt("Enter your choice", type=str)
                if choice == '#':
                    signout()
                    click.echo("Signed out successfully.")
                    break 
                elif choice == '*':
                    try:
                        firebase_admin.delete_app(firebase_admin.get_app())
                    except ValueError:
                        pass
                    click.echo("Exiting...")
                    exit()

                try:
                    choice = int(choice)
                    if choice == 1:
                        bookings()
                    elif choice == 2:
                        view_booking()
                    elif choice == 3:
                        cancel_booking()
                    elif choice == 4 and current_session['role'] == 'mentor':
                        create_workshop()
                    elif choice == 5:
                        view_workshop()
                    elif choice == 6:
                        cancel_workshop()
                    elif choice == 7:
                        submit_feedback() 
                    elif choice == 8:
                        view_feedback()
                    elif choice == 9:
                        search_mentors_peers()
                    else:
                        click.echo("Invalid choice. Please try again.")
                except ValueError:
                    click.echo("⚠️ Invalid input. Please enter a number or one of the special options (#, *).")
            else:
                click.echo("1. Sign In")
                click.echo("2. Sign Up")
                click.echo("3. Reset Password")
                click.echo("4. Exit")

                choice = click.prompt("Enter your choice", type=int)

                if choice == 1:
                    if signin():
                        continue 
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