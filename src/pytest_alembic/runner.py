import contextlib
import functools
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import alembic.command
import alembic.migration
from sqlalchemy.engine import Engine

from pytest_alembic.config import Config
from pytest_alembic.executor import CommandExecutor, ConnectionExecutor
from pytest_alembic.history import AlembicHistory
from pytest_alembic.revision_data import RevisionData


@contextlib.contextmanager
def runner(config: Config, engine=None):
    """Manage the alembic execution context, in a given context.

    Yields:
        `MigrationContext` to the caller.
    """
    command_executor = CommandExecutor.from_config(config)
    migration_context = MigrationContext.from_config(
        config, command_executor, ConnectionExecutor(), engine
    )

    command_executor.configure(connection=engine)
    yield migration_context


@dataclass
class MigrationContext:
    """Within a given environment/execution context, executes alembic commands."""

    command_executor: CommandExecutor
    revision_data: RevisionData
    connection_executor: ConnectionExecutor
    config: Config
    history: AlembicHistory
    connection: Engine = None

    @classmethod
    def from_config(
        cls,
        config: Config,
        command_executor: CommandExecutor,
        connection_executor: ConnectionExecutor,
        connection: Engine,
    ):
        raw_history = command_executor.script.revision_map
        history = AlembicHistory.parse(raw_history)

        return cls(
            command_executor=command_executor,
            revision_data=RevisionData.from_config(config),
            connection_executor=connection_executor,
            config=config,
            history=history,
            connection=connection,
        )

    @property
    def heads(self) -> List[str]:
        """Get the list of revision heads.

        Result is cached for the lifetime of the `MigrationContext`.
        """
        return self.command_executor.heads()

    @property
    def current(self) -> str:
        """Get the list of revision heads."""

        def get_current(conn):
            context = alembic.migration.MigrationContext.configure(conn)
            heads = context.get_current_heads()
            if heads:
                return heads[0]
            return None

        current = run_connection_task(self.connection, get_current)
        if current:
            return current
        return "base"

    def generate_revision(self, process_revision_directives=None, **kwargs):
        """Generate a test revision.

        The final act of this process raises a `RevisionSuccess`, which is used as a sentinal
        to indicate the revision was generated successfully, while not actually finishing the
        generation of the revision file.
        """
        alembic_config = self.command_executor.alembic_config
        config_directive = alembic_config.attributes["process_revision_directives"]
        fn = RevisionSuccess.process_revision_directives(
            _sequence_directives(config_directive, process_revision_directives)
        )
        try:
            return self.command_executor.run_command(
                "revision", process_revision_directives=fn, **kwargs
            )
        except RevisionSuccess:
            pass

    def raw_command(self, *args, **kwargs):
        """Execute a raw alembic command."""
        return self.command_executor.run_command(*args, **kwargs)

    def managed_upgrade(self, dest_revision):
        """Perform an upgrade, one migration at a time, inserting static data at the given points."""
        current = self.current
        for current_revision, next_revision in self.history.revision_window(current, dest_revision):
            before_upgrade_data = list(self.revision_data.get_before(next_revision))
            self.insert_into(data=before_upgrade_data, revision=current_revision, table=None)

            self.command_executor.upgrade(next_revision)

            at_upgrade_data = list(self.revision_data.get_at(next_revision))
            self.insert_into(data=at_upgrade_data, revision=next_revision, table=None)

        current = self.current
        return current

    def migrate_up_before(self, revision):
        """Migrate up to, but not including the given `revision`."""
        preceeding_revision = self.history.previous_revision(revision)
        return self.managed_upgrade(preceeding_revision)

    def migrate_up_to(self, revision):
        """Migrate up to, and including the given `revision`."""
        return self.managed_upgrade(revision)

    def migrate_up_one(self):
        """Migrate up by exactly one revision."""
        current = self.current
        next_revision = self.history.next_revision(current)
        new_revision = self.managed_upgrade(next_revision)
        if current == new_revision:
            return None
        return new_revision

    def migrate_down_before(self, revision):
        """Migrate down to, but not including the given `revision`."""
        next_revision = self.history.next_revision(revision)
        return self.migrate_down_to(next_revision)

    def migrate_down_to(self, revision):
        """Migrate down to, and including the given `revision`."""
        self.history.validate_revision(revision)
        self.command_executor.downgrade(revision)
        return revision

    def migrate_down_one(self):
        """Migrate down by exactly one revision."""
        previous_revision = self.history.previous_revision(self.current)
        self.command_executor.downgrade(previous_revision)
        return previous_revision

    def roundtrip_next_revision(self):
        """Upgrade, downgrade then upgrade.

        This is meant to ensure that the given revision is idempotent.
        """
        next_revision = self.migrate_up_one()
        if next_revision:
            self.migrate_down_one()
            return self.migrate_up_one()
        return None

    def insert_into(self, table: Optional[str], data: Union[Dict, List] = None, revision=None):
        """Insert data into a given table.

        Args:
            table: The name of the table to insert data into
            data: The data to insert. This is eventually passed through to SQLAlchemy's
                Table class `values` method, and so should accept either a list of
                `dict`s representing a list of rows, or a `dict` representing one row.
            revision: The revision of MetaData to use as the table definition for the insert.
        """
        if revision is None:
            revision = self.current

        return run_connection_task(
            self.connection,
            self.connection_executor.table_insert,
            revision=revision,
            tablename=table,
            data=data,
        )

    def table_at_revision(self, name, *, revision=None, schema=None):
        """Return a reference to a `sqlalchemy.Table` at the given revision.

        Args:
            name: The name of the table to produce a `sqlalchemy.Table` for.
            revision: The revision of the table to return.
            schema: The schema of the table.
        """
        revision = revision or self.current
        return self.connection_executor.table(
            self.connection, revision=revision, name=name, schema=schema
        )


class RevisionSuccess(Exception):
    """Raise when a revision is successfully generated.

    In order to prevent the generation of an actual revision file on disk when running tests,
    this exception should be raised.
    """

    @classmethod
    def process_revision_directives(cls, fn):
        """Wrap a real `process_revision_directives` function, while preventing it from completing."""

        @functools.wraps(fn)
        def _process_revision_directives(context, revision, directives):
            fn(context, revision, directives)
            raise cls()

        return _process_revision_directives


def _sequence_directives(*directives):
    def directive_wrapper(*args, **kwargs):
        for directive in directives:
            if not directive:
                continue
            directive(*args, **kwargs)

    return directive_wrapper


def run_connection_task(engine, fn, *args, **kwargs):
    """Run a given task on the provided connect, with the correct async/sync context.

    Given an async engine, we need to run the task in an async execution context,
    even though all internals are sychronous. This is how alembic suggests
    running the migrations themselves, so this matches that style.
    """
    # The user may not have sqlalchemy 1.4+, and therefore may not even be able to
    # use async engines.
    try:
        from sqlalchemy.ext.asyncio import AsyncEngine
    except ImportError:  # pragma: no cover
        AsyncEngine = None

    if AsyncEngine and isinstance(engine, AsyncEngine):
        import asyncio

        async def run(engine):
            async with engine.connect() as connection:
                result = await connection.run_sync(fn, *args, **kwargs)
                await connection.commit()

            await engine.dispose()
            return result

        return asyncio.run(run(engine))
    else:
        if isinstance(engine, Engine):
            with engine.connect() as connection:
                result = fn(connection, *args, **kwargs)
        else:
            result = fn(engine, *args, **kwargs)

        return result
