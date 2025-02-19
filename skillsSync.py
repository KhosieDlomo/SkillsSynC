import click
from login import signin, signup, reset_password, signout, current_session
from events import view_booking, cancel_booking,bookings
from workshops import view_workshop, create_workshop
import firebase_admin

def main_menu():
    """Hello, Here is the Menu."""
    print("main_menu() called")
    try:
        while True:
            click.echo('\n--- Main Menu ---')
            if current_session['logged_in']:
                click.echo(f"Logged in as {current_session['email']} (Role: {current_session['role']})")
                click.echo("1. Book a Meeting")
                click.echo("2. view Bookings")
                click.echo("3. Cancel Booking")
                click.echo("4. View Workshops")
                
                if current_session['role'] == 'mentor':
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
                elif choice == 5 and current_session['role'] == 'mentor':
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