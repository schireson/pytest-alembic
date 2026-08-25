from collections.abc import Iterator

import pytest
import sqlalchemy
from sqlalchemy.engine import Connection

from pytest_alembic.tests.experimental.downgrade_leaves_no_trace import WrappingConnection


@pytest.fixture
def connection() -> Iterator[Connection]:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.connect() as conn:
            yield conn
    finally:
        engine.dispose()


class Test_WrappingConnection:
    """A live connection presented as though it were an engine.

    Alembic's `env.py` conventionally calls `connect()` on what it is given, which would
    open a *second* connection and so land outside the transaction this test holds open.
    """

    def test_connect_yields_the_same_connection(self, connection: Connection) -> None:
        wrapper = WrappingConnection(connection)

        with wrapper.connect() as yielded:
            assert yielded is connection

        # And it is still open afterwards, for the next caller.
        assert not connection.closed

    def test_every_other_attribute_falls_through(self, connection: Connection) -> None:
        wrapper = WrappingConnection(connection)

        assert wrapper.dialect is connection.dialect
