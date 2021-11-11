import contextlib
import functools
import io
from dataclasses import dataclass
from io import StringIO
from typing import Dict, List, Optional, Union

import alembic
import alembic.config
from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Connection

from pytest_alembic.config import Config


@dataclass
class CommandExecutor:
    alembic_config: alembic.config.Config
    stdout: StringIO
    stream_position: int

    @classmethod
    def from_config(cls, config: Config):
        stdout = StringIO()
        alembic_config = config.make_alembic_config(stdout)
        return cls(alembic_config=alembic_config, stdout=stdout, stream_position=0)

    def configure(self, **kwargs):
        for key, value in kwargs.items():
            self.alembic_config.attributes[key] = value

    @property
    def connection(self):
        return self.alembic_config.attributes["connection"]

    def run_command(self, command, *args, **kwargs):
        self.stream_position = self.stdout.tell()

        executable_command = getattr(alembic.command, command)
        try:
            # Hide the (relatively) worthless logs of the upgrade revision path, it just clogs
            # up the logs when errors actually occur, but without providing any context.
            buffer = io.StringIO()
            with contextlib.redirect_stderr(buffer):
                executable_command(self.alembic_config, *args, **kwargs)
        except alembic.util.exc.CommandError as e:
            raise RuntimeError(e)

        self.stdout.seek(self.stream_position)
        return self.stdout.readlines()


@dataclass(frozen=True)
class ConnectionExecutor:
    connection: Connection

    @functools.lru_cache()
    def metadata(self, revision: str) -> MetaData:
        return MetaData()

    @functools.lru_cache()
    def table(self, revision: str, name: str, schema: Optional[str] = None) -> Table:
        meta = self.metadata(revision)
        return Table(name, meta, schema=schema, autoload=True, autoload_with=self.connection)

    def table_insert(
        self,
        revision: str,
        data: Union[Dict, List],
        tablename: Optional[str] = None,
        schema: Optional[str] = None,
    ):
        if isinstance(data, dict):
            data = [data]

        for item in data:
            _tablename = item.get("__tablename__", None)
            table = _tablename or tablename

            if table is None:
                raise ValueError(
                    "No table name provided as either `table` argument, or '__tablename__' key in `data`."
                )

            try:
                # Attempt to parse the schema out of the tablename
                schema, table = table.split(".", 1)
            except ValueError:
                # However, if it doesn't work, both `table` and `schema` are in scope, so failure is fine.
                pass

            table = self.table(revision, table, schema=schema)
            values = {k: v for k, v in item.items() if k != "__tablename__"}
            self.connection.execute(table.insert().values(values))
