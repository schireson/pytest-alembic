import asyncio
from logging.config import fileConfig

from alembic import context
from models import Base
from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio.engine import AsyncEngine

fileConfig(context.config.config_file_name)
target_metadata = Base.metadata


def run_migrations_online():
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = AsyncEngine(
            engine_from_config(
                context.config.get_section(context.config.config_ini_section),
                prefix="sqlalchemy.",
                future=True,
            )
        )

    if isinstance(connectable, AsyncEngine):
        # Check if there's already a running event loop (e.g., from anyio)
        try:
            asyncio.get_running_loop()
            # There's a running loop, use ThreadPoolExecutor to run in a separate thread
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor() as pool:
                pool.submit(asyncio.run, run_async_migrations(connectable)).result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run() directly
            asyncio.run(run_async_migrations(connectable))
    else:
        with connectable.connect() as connection:
            do_run_migrations(connection)


async def run_async_migrations(connectable):
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
