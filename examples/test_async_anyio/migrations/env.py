import asyncio
from logging.config import fileConfig

from alembic import context
from models import Base
from sqlalchemy import engine_from_config, pool, Engine

fileConfig(context.config.config_file_name)
target_metadata = Base.metadata


def run_migrations_online():
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = Engine(
            engine_from_config(
                context.config.get_section(context.config.config_ini_section),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
                future=True,
            )
        )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
