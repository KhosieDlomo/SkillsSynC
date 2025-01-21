import click
from login import signin, signup, signout, reset_password

@click.group()
def cli():
    pass

cli.add_command(signin)
cli.add_command(signup)
cli.add_command(reset_password)
cli.add_command(signout)