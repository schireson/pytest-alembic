from pytest_mock_resources import create_postgres_fixture
from sqlalchemy import Column, MetaData, Table, types
from sqlalchemy.engine import Engine

from pytest_alembic.executor import ConnectionExecutor

metadata = MetaData()

table = Table("t", metadata, Column("name", types.Unicode(), primary_key=True))

pg = create_postgres_fixture(metadata)


def test_table_insert(pg: Engine) -> None:
    command_executor = ConnectionExecutor(pg)
    command_executor.table_insert("", [{"name": "who"}], tablename="t")
