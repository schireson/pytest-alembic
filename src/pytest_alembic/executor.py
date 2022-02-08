import contextlib
import io
from dataclasses import dataclass, field
from io import StringIO
from typing import Dict, List, Optional, Union

import alembic
import alembic.config
from alembic.runtime.environment import EnvironmentContext
from alembic.script.base import ScriptDirectory
from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Connection

from pytest_alembic.config import Config


@dataclass
class CommandExecutor:
    alembic_config: alembic.config.Config
    stdout: StringIO
    stream_position: int
    script: ScriptDirectory

    @classmethod
    def from_config(cls, config: Config):
        stdout = StringIO()
        alembic_config = config.make_alembic_config(stdout)
        return cls(
            alembic_config=alembic_config,
            stdout=stdout,
            stream_position=0,
            script=ScriptDirectory.from_config(alembic_config),
        )

    def configure(self, **kwargs):
        for key, value in kwargs.items():
            self.alembic_config.attributes[key] = value

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

    def heads(self):
        return [rev.revision for rev in self.script.get_revisions("heads")]

    def upgrade(self, revision):
        """Upgrade to the given `revision`."""

        def upgrade(rev, _):
            return self.script._upgrade_revs(revision, rev)

        self._run_env(upgrade, revision)

    def downgrade(self, revision):
        """Downgrade to the given `revision`."""

        def downgrade(rev, _):
            return self.script._downgrade_revs(revision, rev)

        self._run_env(downgrade, revision)

    def _run_env(self, fn, revision=None):
        """Execute the migrations' env.py, given some function to execute."""
        dont_mutate = revision is None
        with EnvironmentContext(
            self.alembic_config,
            self.script,
            fn=fn,
            destination_rev=revision,
            dont_mutate=dont_mutate,
        ):
            self.script.run_env()


@dataclass
class ConnectionExecutor:
    metadatas: Dict[str, MetaData] = field(default_factory=dict)

    def metadata(self, revision: str) -> MetaData:
        metadata = self.metadatas.get(revision)
        if metadata is None:
            metadata = MetaData()
            self.metadatas[revision] = metadata

        return metadata

    def table(self, connection, revision: str, name: str, schema: Optional[str] = None) -> Table:
        meta = self.metadata(revision)
        if name in meta.tables:
            return meta.tables[name]

        return Table(name, meta, schema=schema, autoload_with=connection)

    def table_insert(
        self,
        connection: Connection,
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

            table = self.table(connection, revision, table, schema=schema)
            values = {k: v for k, v in item.items() if k != "__tablename__"}
            connection.execute(table.insert().values(values))
