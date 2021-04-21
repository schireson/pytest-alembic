import contextlib
import functools
from dataclasses import dataclass
from typing import Dict, List, Optional

from pytest_alembic.executor import CommandExecutor, ConnectionExecutor
from pytest_alembic.history import AlembicHistory
from pytest_alembic.revision_data import RevisionData


@contextlib.contextmanager
def runner(config, engine=None):
    """Manage the alembic execution context, in a given context.

    Yields:
        `MigrationContext` to the caller.
    """
    command_executor = CommandExecutor.from_config(config)
    migration_context = MigrationContext.from_config(
        config, command_executor, ConnectionExecutor(engine)
    )

    command_executor.configure(connection=engine)
    yield migration_context


def _sequence_directives(*directives):
    def directive_wrapper(*args, **kwargs):
        for directive in directives:
            if not directive:
                continue
            directive(*args, **kwargs)

    return directive_wrapper


@dataclass
class MigrationContext:
    """Within a given environment/execution context, executes alembic commands."""

    command_executor: CommandExecutor
    revision_data: RevisionData
    connection_executor: ConnectionExecutor

    @classmethod
    def from_config(
        cls,
        config: Dict,
        command_executor: CommandExecutor,
        connection_executor: ConnectionExecutor,
    ):
        return cls(
            command_executor=command_executor,
            revision_data=RevisionData.from_config(config),
            connection_executor=connection_executor,
        )

    @property
    def history(self) -> AlembicHistory:
        """Get the revision history."""
        raw_history = self.command_executor.run_command("history")
        return AlembicHistory.parse(tuple(raw_history))

    @property
    def heads(self) -> List[str]:
        """Get the list of revision heads."""
        return self.command_executor.run_command("heads")

    @property
    def current(self) -> Optional[str]:
        """Get the list of revision heads."""
        current = self.command_executor.run_command("current")
        if current:
            return current[0].strip().split(" ")[0]
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
            self.connection_executor.table_insert(current_revision, before_upgrade_data)

            self.raw_command("upgrade", next_revision)

            at_upgrade_data = list(self.revision_data.get_at(next_revision))
            self.connection_executor.table_insert(next_revision, at_upgrade_data)

    def migrate_up_before(self, revision):
        """Upgrade up to, but not including the given `revision`."""
        preceeding_revision = self.history.previous_revision(revision)
        self.managed_upgrade(preceeding_revision)

    def migrate_up_to(self, revision):
        """Upgrade up to, and including the given `revision`."""
        self.managed_upgrade(revision)

    def migrate_up_one(self):
        """Upgrade up by exactly one revision."""
        revision = self.history.next_revision(self.current)
        self.managed_upgrade(revision)

    def migrate_down_before(self, revision):
        """Upgrade down to, but not including the given `revision`."""
        next_revision = self.history.next_revision(revision)
        self.migrate_down_to(next_revision)

    def migrate_down_to(self, revision):
        """Upgrade down to, and including the given `revision`."""
        self.history.validate_revision(revision)
        self.raw_command("downgrade", revision)

    def migrate_down_one(self):
        """Upgrade down by exactly one revision."""
        self.raw_command("downgrade", "-1")

    def roundtrip_next_revision(self):
        """Upgrade, downgrade then upgrade.

        This is meant to ensure that the given revision is idempotent.
        """
        self.migrate_up_one()
        self.migrate_down_one()
        self.migrate_up_one()

    def insert_into(self, table, data):
        """Insert data into a given table.

        Args:
            table: The name of the table to insert data into
            data: The data to insert. This is eventually passed through to SQLAlchemy's
                Table class `values` method, and so should accept either a list of
                `dict`s representing a list of rows, or a `dict` representing one row.
        """
        return self.connection_executor.table_insert(
            revision=self.current, tablename=table, data=data
        )

    def table_at_revision(self, name, *, revision=None, schema=None):
        """Insert data into a given table.

        Args:
            name: The name of the table to insert data into
            revision: The revision of the table to return.
            schema: The schema of the table.
        """
        revision = revision or self.current
        return self.connection_executor.table(revision=revision, name=name, schema=schema)


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
