import click

from .extensions import db
from .models import Admin


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, help="Admin username")
    @click.password_option(help="Password (min 10 characters). Prompted, never echoed.")
    def create_admin(username, password):
        """Create the admin account, or reset its password if it exists."""
        username = username.strip().lower()
        if not username or len(password) < 10:
            raise click.ClickException("Username is required and the password needs 10+ characters.")
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            click.confirm(f"'{username}' already exists. Reset the password?", abort=True)
        else:
            admin = Admin(username=username)
            db.session.add(admin)
        admin.set_password(password)
        admin.failed_attempts, admin.locked_until = 0, None
        db.session.commit()
        click.echo(f"Admin '{username}' is ready. Sign in at /admin/login.")
