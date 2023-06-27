from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from models import Base

fileConfig(context.config.config_file_name)
target_metadata = Base.metadata


connectable = context.config.attributes.get("connection", None)

if connectable is None:
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

with connectable.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema="version_table_schema",
    )

    with context.begin_transaction():
        context.run_migrations()
