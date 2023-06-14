# -*- coding: utf-8 -*-
"""
@create: 2023-06-21 10:40:57.

@author: ppolxda

@desc: reportbro db util
"""
import contextlib
import os
import time

import click
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import text

from ..clients import create_db_sessionmaker
from ..clients import create_db_sync_engine
from ..settings import settings
from .models import Base


@click.group()
def dbcli():  # pylint: disable=invalid-name
    """Database group command."""


def _get_alembic_config():
    """Replace alembic config."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(current_dir, "migrate")
    config = Config(os.path.join(directory, "alembic.ini"))
    config.set_main_option("script_location", directory.replace("%", "%%"))
    config.set_main_option("sqlalchemy.url", settings.db_url_sync.replace("%", "%%"))
    click.echo(settings.db_url_sync_mark)
    return config


@contextlib.contextmanager
def create_global_lock(
    session, pg_lock_id=1, lock_name="init", mysql_lock_timeout=1800
):
    """Contextmanager that will create and teardown a global db lock."""
    dialect = session.connection().dialect
    try:
        if dialect.name == "postgresql":
            session.connection().execute(
                text(f"select PG_ADVISORY_LOCK({pg_lock_id});")
            )

        if dialect.name == "mysql" and dialect.server_version_info >= (
            5,
            6,
        ):
            session.connection().execute(
                text(f"select GET_LOCK('{lock_name}',{mysql_lock_timeout});")
            )

        if dialect.name == "mssql":
            # TODO: make locking works for MSSQL
            pass

        yield None
    finally:
        if dialect.name == "postgresql":
            session.connection().execute(
                text(f"select PG_ADVISORY_UNLOCK({pg_lock_id});")
            )

        if dialect.name == "mysql" and dialect.server_version_info >= (
            5,
            6,
        ):
            session.connection().execute(text(f"select RELEASE_LOCK('{lock_name}');"))

        if dialect.name == "mssql":
            # TODO: make locking works for MSSQL
            pass


@click.command()
@click.option("--timeout", default=180, help="timeout.")
def checkdb(timeout):
    """Function to wait for all airflow migrations to complete.

    :param timeout: Timeout for the migration in seconds
    :return: None
    """
    config = _get_alembic_config()
    script_ = ScriptDirectory.from_config(config)
    engine = create_db_sync_engine()
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        ticker = 0
        while True:
            source_heads = set(script_.get_heads())
            db_heads = set(context.get_current_heads())
            if source_heads == db_heads:
                break
            if ticker >= timeout:
                raise TimeoutError(
                    f"There are still unapplied migrations after {ticker} seconds. "
                    f"Migration Head(s) in DB: {db_heads} | Migration Head(s) in Source Code: {source_heads}"
                )

            ticker += 1
            time.sleep(1)
            click.echo(f"Waiting for migrations... {ticker} second(s)")


def upgrade_db():
    """Upgrade Initialized."""
    config = _get_alembic_config()

    # check automatic migration is available
    # errs = auto_migrations_available()
    # if errs:
    #     for err in errs:
    #         click.echo("Automatic migration is not available\n%s", err)
    #     return
    sessionmaker = create_db_sessionmaker()
    with sessionmaker() as session:
        with create_global_lock(session=session, pg_lock_id=2, lock_name="upgrade"):
            command.upgrade(config, "heads")
        session.commit()


def downgrade_db():
    """Downgrade Initialized."""
    config = _get_alembic_config()

    # check automatic migration is available
    # errs = auto_migrations_available()
    # if errs:
    #     for err in errs:
    #         click.echo("Automatic migration is not available\n%s", err)
    #     return
    sessionmaker = create_db_sessionmaker()
    with sessionmaker() as session:
        with create_global_lock(session=session, pg_lock_id=2, lock_name="upgrade"):
            command.downgrade(config, "-1")
        session.commit()


def drop_reportbro_models(connection):
    """Drops all reportbro models."""
    Base.metadata.drop_all(connection)

    migration_ctx = MigrationContext.configure(connection)
    version = migration_ctx._version  # pylint: disable=protected-access
    version.drop(connection, checkfirst=False)


def drop_db():
    """Drops all reportbro models."""
    sessionmaker = create_db_sessionmaker()
    # engine = sessionmaker.kw["bind"]
    with sessionmaker() as session:
        with create_global_lock(session=session, pg_lock_id=3, lock_name="reset"):
            drop_reportbro_models(session.connection())
        session.commit()


@click.command()
def initdb():
    """Database Initialized."""
    click.echo("Initialized the database")
    click.echo(f"Process url: {settings.db_url_sync_mark}")
    upgrade_db()


@click.command()
def dropdb():
    """Database Drop."""
    click.echo("Droped the database")
    click.echo(f"Process url: {settings.db_url_sync_mark}")
    drop_db()


@click.command()
def upgradedb():
    """Upgroup Database to head."""
    click.echo("Upgrade the database")
    click.echo(f"Process url: {settings.db_url_sync_mark}")
    upgrade_db()


@click.command()
def downgradedb():
    """Upgroup Database to head."""
    click.echo("Downgrade the database -1")
    click.echo(f"Process url: {settings.db_url_sync_mark}")
    downgrade_db()


@click.command()
def resetdb():
    """Database Drop."""
    click.echo("Dropping tables that exist")
    click.echo(f"Process url: {settings.db_url_sync_mark}")
    drop_db()
    initdb()


@click.command()
@click.option("-m", type=str, help="revision commit message.")
@click.option("--autogenerate", is_flag=True, help="revision commit message.")
def revision(m, autogenerate):
    """Create Database revision version."""
    click.echo("Revision verstion")
    click.echo(f"Process url: {settings.db_url_sync_mark}")
    config = _get_alembic_config()
    sessionmaker = create_db_sessionmaker()
    with sessionmaker() as session:
        with create_global_lock(session=session, pg_lock_id=1, lock_name="revision"):
            command.revision(config, m, autogenerate)
        session.commit()


dbcli.add_command(initdb)
dbcli.add_command(dropdb)
dbcli.add_command(upgradedb)
dbcli.add_command(downgradedb)
dbcli.add_command(resetdb)
dbcli.add_command(checkdb)
dbcli.add_command(revision)


if __name__ == "__main__":
    dbcli()
