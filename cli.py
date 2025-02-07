import click
from login import signin, signup, signout, reset_password
from events import *

@click.group()
def cli():
    pass

cli.add_command(signin)
cli.add_command(signup)
cli.add_command(reset_password)
cli.add_command(signout)
cli.add_command(bookings)
cli.add_command(view_booking)
cli.add_command(cancel_booking)
cli.add_command(view_workshorp)
cli.add_command(create_workshop)

if __name__ =='__main__':
    cli()