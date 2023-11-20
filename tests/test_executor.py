from pytest_mock_resources import create_postgres_fixture
from sqlalchemy import Column, MetaData, Table, types

from pytest_alembic.executor import ConnectionExecutor

metadata = MetaData()

table = Table("t", metadata, Column("name", types.Unicode(), primary_key=True))

pg = create_postgres_fixture(metadata)


def test_table_insert(pg):
    with pg.begin() as conn:
        command_executor = ConnectionExecutor(conn)
        command_executor.table_insert("", [{"name": "who"}], tablename="t")
