#!/usr/bin/env python3

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import Optional

import typer

from alembic import command
from alembic.config import Config
from alembic.util import CommandError
from app.core.config import Paths, get_settings
from app.core.database import MODEL_PATHS
from app.utils import get_logger

cli = typer.Typer()
logger = get_logger(__name__)


@cli.command()
def run(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(None, "--port", "-p", help="Port to bind to (defaults to settings.PORT)"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload on code changes"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of worker processes"),
    log_level: str = typer.Option("info", "--log-level", "-l", help="Log level (debug, info, warning, error)"),
):
    """Run the FastAPI application with uvicorn"""
    import uvicorn

    settings = get_settings()
    port = port or settings.PORT

    typer.echo(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    typer.echo(f"📍 Environment: {settings.ENVIRONMENT}")
    typer.echo(f"🌐 Server: http://{host}:{port}")
    typer.echo(f"📚 Documentation: http://{host}:{port}/docs")
    typer.echo(f"🔧 Debug mode: {settings.DEBUG}")
    typer.echo(f"🔄 Auto-reload: {reload}")
    typer.echo(f"👥 Workers: {workers}")
    typer.echo("─" * 50)
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level=log_level,
        access_log=True,
    )


@cli.command()
def upgrade(rev: str = "head", config_file: Path = Path("alembic.ini")):
    """Apply database migrations"""
    typer.echo(f"🔄 Migrating to revision {rev}")
    config = Config(config_file)
    try:
        command.upgrade(config, rev)
        typer.echo(f"✅ Successfully migrated to revision {rev}")
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def downgrade(rev: str = "head", config_file: Path = Path("alembic.ini")):
    """Downgrade to the given revision"""
    typer.echo(f"⚠️  Downgrading to revision {rev}")
    config = Config(config_file)
    try:
        command.downgrade(config, rev)
        typer.echo(f"✅ Successfully downgraded to revision {rev}")
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def show(config_file: Path = Path("alembic.ini"), rev: str = "head"):
    """Show the revision"""
    config = Config(config_file)
    try:
        command.show(config, rev)
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def revision(
    message: Optional[str] = None,
    config_file: Path = Path("alembic.ini"),
    autogenerate: bool = True,
    head: str = "head",
    splice: bool = False,
):
    """Create a new Alembic revision"""
    # Import all the models to be able to autogenerate migrations
    for model_path in MODEL_PATHS:
        importlib.import_module(model_path)
        logger.debug(f"✅ Loaded models: {model_path}")

    config = Config(config_file)
    try:
        command.revision(
            config,
            message=message,
            autogenerate=autogenerate,
            head=head,
            splice=splice,
        )
        typer.echo("✅ Revision created successfully")
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def current(config_file: Path = Path("alembic.ini")):
    """Show the current database revision"""
    config = Config(config_file)
    try:
        command.current(config)
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def history(config_file: Path = Path("alembic.ini"), rev_range: Optional[str] = None, verbose: bool = False):
    """Show migration history"""
    config = Config(config_file)
    try:
        command.history(config, rev_range=rev_range, verbose=verbose)
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def stamp(revision: str, config_file: Path = Path("alembic.ini"), purge: bool = False):
    """Mark the database as being at a specific revision without running migrations"""
    config = Config(config_file)
    try:
        command.stamp(config, revision, purge=purge)
        typer.echo(f"✅ Successfully stamped database to revision {revision}")
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def check(config_file: Path = Path("alembic.ini")):
    """Check if there are any pending migrations"""
    config = Config(config_file)
    try:
        # Get current revision
        current = command.current(config)
        # Get head revision
        head = command.head(config)

        if current == head:
            typer.echo("✅ Database is up to date")
        else:
            typer.echo(f"⚠️  Database is behind. Current: {current}, Head: {head}")
            typer.echo("ℹ️  Run 'python manage.py upgrade' to apply pending migrations")

    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def reset(
    config_file: Path = Path("alembic.ini"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Reset the database by downgrading to base and upgrading to head"""
    if not confirm:
        typer.echo("⚠️  This will reset the database. All data will be lost!")
        if not typer.confirm("Are you sure you want to continue?"):
            typer.echo("Operation cancelled.")
            return

    typer.echo("⚠️  Resetting database...")

    config = Config(config_file)
    try:
        # Downgrade to base
        command.downgrade(config, "base")
        typer.echo("✅ Downgraded to base")

        # Upgrade to head
        command.upgrade(config, "head")
        typer.echo("✅ Upgraded to head")

        typer.echo("✅ Database reset completed!")
    except CommandError as exc:
        typer.echo(f"❌ Error: {exc}")
        raise typer.Exit(code=1) from exc


@cli.command()
def create_user(
    email: str = typer.Option(..., help="User email"),
    username: str = typer.Option(..., help="Username"),
    password: str = typer.Option(..., help="Password"),
    full_name: str = typer.Option(None, help="Full name"),
    is_superuser: bool = typer.Option(False, help="Create superuser"),
):
    """Create a new user"""
    async def _create_user():
        from app.core.database import get_async_session
        from app.crud.user import user_crud
        from app.models.user import UserCreate

        user_in = UserCreate(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            is_active=True,
        )

        async with get_async_session() as db:
            # Check if user already exists
            existing_user = await user_crud.get_by_email(db, email=email)
            if existing_user:
                typer.echo(f"❌ User with email {email} already exists")
                raise typer.Exit(code=1)

            existing_user = await user_crud.get_by_username(db, username=username)
            if existing_user:
                typer.echo(f"❌ User with username {username} already exists")
                raise typer.Exit(code=1)

            # Create user
            user = await user_crud.create(db, obj_in=user_in)
            
            if is_superuser:
                user.is_superuser = True
                await user_crud.update(db, db_obj=user, obj_in={"is_superuser": True})

            typer.echo(f"✅ User created successfully:")
            typer.echo(f"   ID: {user.id}")
            typer.echo(f"   Email: {user.email}")
            typer.echo(f"   Username: {user.username}")
            typer.echo(f"   Superuser: {user.is_superuser}")

    asyncio.run(_create_user())


def main():
    """Main entry point"""
    try:
        cli()
    except TypeError as e:
        if "Parameter.make_metavar()" in str(e):
            # Fallback for typer compatibility issue
            print("SDLC Agents Management Commands:")
            print("  run         - Run the FastAPI application")
            print("\nDatabase Management Commands:")
            print("  upgrade     - Apply database migrations")
            print("  downgrade   - Downgrade database migrations")
            print("  show        - Show revision details")
            print("  revision    - Create a new migration")
            print("  current     - Show current revision")
            print("  history     - Show migration history")
            print("  stamp       - Stamp database with revision")
            print("  check       - Check migration status")
            print("  reset       - Reset database (destructive)")
            print("\nUser Management Commands:")
            print("  create-user - Create a new user")
            print("\nUse: python manage.py <command> --help for more info")
        else:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
