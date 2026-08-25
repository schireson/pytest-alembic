import contextlib
import io
from dataclasses import dataclass, field
from io import StringIO

import alembic
import alembic.config
from alembic.runtime.environment import EnvironmentContext
from alembic.script.base import ScriptDirectory
from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Connectable, Connection, Engine

from pytest_alembic.config import Config


@dataclass
class CommandExecutor:
    """Run alembic commands against a captured config, buffering their output.

    This is the seam between pytest-alembic and alembic proper: every ``alembic
    upgrade``/``downgrade``/``revision`` invocation a test triggers goes through here,
    with stdout captured into a buffer so command output can be asserted on rather than
    printed.

    Construct it with :meth:`from_config` rather than directly, since it needs a
    ``ScriptDirectory`` derived from the same alembic config.

    Examples:
        >>> def test_history_is_reachable(alembic_runner):
        ...     executor = alembic_runner.command_executor
        ...     executor.upgrade("heads")
        ...     assert executor.heads()
    """

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

    def execute_fn(self, fn):
        with EnvironmentContext(self.alembic_config, self.script, fn=fn):
            self.script.run_env()

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
            return self.script._upgrade_revs(revision, rev)  # noqa: SLF001

        self._run_env(upgrade, revision)

    def downgrade(self, revision):
        """Downgrade to the given `revision`."""

        def downgrade(rev, _):
            return self.script._downgrade_revs(revision, rev)  # noqa: SLF001

        self._run_env(downgrade, revision)

    def stamp(self, revision: str):
        return self.run_command("stamp", revision)

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
    """Read and write actual data through the connection under test.

    Where :class:`CommandExecutor` drives alembic, this drives the database: reflecting
    tables as they exist at a particular revision, and inserting rows into them.

    A separate ``MetaData`` is kept per revision, because the same table can have a
    different shape before and after a migration; sharing one would cache the wrong
    definition. See :meth:`metadata`.
    """

    connection: Connectable
    metadatas: dict[str, MetaData] = field(default_factory=dict)

    def metadata(self, revision: str) -> MetaData:
        """Return the ``MetaData`` for `revision`, creating it on first use.

        The result is memoized per revision, so tables reflected at one revision are not
        reused at another. Nothing here touches the connection, so it is safe to call
        before any migration has run.

        Examples:
            >>> executor = ConnectionExecutor(connection=None)
            >>> metadata = executor.metadata("a1")

            The same revision hands back the identical object:

            >>> executor.metadata("a1") is metadata
            True

            A different revision gets its own:

            >>> executor.metadata("b2") is metadata
            False
            >>> sorted(executor.metadatas)
            ['a1', 'b2']
        """
        metadata = self.metadatas.get(revision)
        if metadata is None:
            metadata = MetaData()
            self.metadatas[revision] = metadata

        return metadata

    def table(
        self,
        revision: str,
        name: str,
        schema: str | None = None,
        connection: Connection | Engine | None = None,
    ) -> Table:
        meta = self.metadata(revision)
        if name in meta.tables:
            return meta.tables[name]

        autoload_with = connection or self.connection

        assert isinstance(autoload_with, (Engine, Connection)), autoload_with
        return Table(name, meta, schema=schema, autoload_with=autoload_with)

    def table_insert(
        self,
        revision: str,
        data: dict | list,
        tablename: str | None = None,
        schema: str | None = None,
    ):
        def table_insert(
            connection: Connection,
            data: dict | list,
            tablename: str | None = None,
            schema: str | None = None,
        ):
            if isinstance(data, dict):
                data = [data]

            for item in data:
                _tablename = item.get("__tablename__", None)
                table = _tablename or tablename

                if table is None:
                    message = "No table name provided as either `table` argument, or '__tablename__' key in `data`."
                    raise ValueError(message)

                with contextlib.suppress(ValueError):
                    # Attempt to parse the schema out of the tablename
                    # However, if it doesn't work, both `table` and `schema` are in scope, so failure is fine.
                    schema, table = table.split(".", 1)

                table = self.table(revision, table, schema=schema, connection=connection)
                values = {k: v for k, v in item.items() if k != "__tablename__"}
                connection.execute(table.insert().values(values))

        self.run_task(table_insert, data=data, tablename=tablename, schema=schema)

    def run_task(self, fn, **kwargs):
        """Run a given task on the provided connect, with the correct async/sync context.

        Given an async engine, we need to run the task in an async execution context,
        even though all internals are synchronous. This is how alembic suggests
        running the migrations themselves, so this matches that style.
        """
        # The user may not have sqlalchemy 1.4+, and therefore may not even be able to
        # use async engines.
        AsyncEngine = None  # noqa: N806
        with contextlib.suppress(ImportError):
            from sqlalchemy.ext.asyncio import AsyncEngine

        if AsyncEngine and isinstance(self.connection, AsyncEngine):
            import asyncio

            async def run(engine):
                async with engine.connect() as connection:
                    result = await connection.run_sync(fn, **kwargs)
                    await connection.commit()

                await engine.dispose()
                return result

            return asyncio.run(run(self.connection))

        if isinstance(self.connection, Engine):
            with self.connection.begin() as connection:
                result = fn(connection=connection, **kwargs)

            # SQLite does not close via the context manager, close expliclitly
            connection.close()
            return result

        return fn(connection=self.connection, **kwargs)
