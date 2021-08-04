import contextlib
import functools
import io
from dataclasses import dataclass
from io import StringIO
from typing import Dict, List, Optional, Union

import alembic
from alembic.config import Config
from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Connection


@dataclass
class CommandExecutor:
    alembic_config: Config
    stdout: StringIO
    stream_position: int

    @classmethod
    def from_config(cls, config):
        file = config.get("file", "alembic.ini")
        script_location = config.get("script_location")
        target_metadata = config.get("target_metadata")
        process_revision_directives = config.get("process_revision_directives")
        include_schemas = config.get("include_schemas", True)

        stdout = StringIO()
        alembic_config = Config(file, stdout=stdout)

        # Only set script_location if set.
        if script_location:
            alembic_config.set_section_option('alembic', "script_location", script_location)
        elif not alembic_config.get_section_option('alembic', 'script_location'):
            # Or in the event that it's not set after already having loaded the config.
            alembic_config.set_main_option("script_location", 'migrations')

        alembic_config.attributes["target_metadata"] = target_metadata
        alembic_config.attributes["process_revision_directives"] = process_revision_directives
        alembic_config.attributes["include_schemas"] = include_schemas

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
            _tablename = item.pop("__tablename__", None)
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
            self.connection.execute(table.insert().values(item))
