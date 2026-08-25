from io import StringIO

import alembic.config
import pytest
from pytest_mock_resources import create_postgres_fixture
from sqlalchemy import Column, MetaData, Table, types
from sqlalchemy.engine import Engine

from pytest_alembic.executor import CommandExecutor, ConnectionExecutor

metadata = MetaData()

table = Table("t", metadata, Column("name", types.Unicode(), primary_key=True))

pg = create_postgres_fixture(metadata)


def test_table_insert(pg: Engine) -> None:
    command_executor = ConnectionExecutor(pg)
    command_executor.table_insert("", [{"name": "who"}], tablename="t")


def test_command_error_becomes_runtime_error() -> None:
    """Assert alembic's `CommandError` is re-raised as a plain `RuntimeError`.

    Callers of `run_command` should not have to import from `alembic.util` to catch a
    failed command, so the translation happens here rather than at each call site.
    """
    command_executor = CommandExecutor(
        alembic_config=alembic.config.Config(),
        stdout=StringIO(),
        stream_position=0,
        script=None,  # type: ignore[arg-type]  # unused by `run_command`
    )

    with pytest.raises(RuntimeError):
        command_executor.run_command("stamp", "abcdef")


def test_table_insert_without_a_table_name() -> None:
    """Assert a row which names no table is rejected rather than silently skipped.

    The table can come from the `tablename` argument or from a `__tablename__` key on
    the row itself; with neither, there is nothing to insert into.
    """
    connection_executor = ConnectionExecutor(connection=None)

    with pytest.raises(ValueError, match="No table name provided"):
        connection_executor.table_insert("", [{"name": "who"}])
