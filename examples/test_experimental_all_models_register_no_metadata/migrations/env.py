from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

fileConfig(context.config.config_file_name)


connectable = context.config.attributes.get("connection", None)

if connectable is None:
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

with connectable.connect() as connection:
    context.configure(connection=connection)

    with context.begin_transaction():
        context.run_migrations()
