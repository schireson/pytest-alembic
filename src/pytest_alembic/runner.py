import contextlib
import functools
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import alembic.command
import alembic.migration
import alembic.util
from alembic.script.revision import RevisionMap

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
        config,
        command_executor,
        ConnectionExecutor(engine),
    )

    command_executor.configure(connection=engine)
    yield migration_context


@dataclass
class MigrationContext:
    """Within a given environment/execution context, executes alembic commands."""

    command_executor: CommandExecutor
    revision_data: RevisionData
    connection_executor: ConnectionExecutor
    history: AlembicHistory
    config: Config

    @classmethod
    def from_config(
        cls,
        config: Config,
        command_executor: CommandExecutor,
        connection_executor: ConnectionExecutor,
    ):
        history = AlembicHistory.parse(command_executor.script.revision_map)

        return cls(
            command_executor=command_executor,
            revision_data=RevisionData.from_config(config),
            connection_executor=connection_executor,
            history=history,
            config=config,
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

        def get_current(connection):
            context = alembic.migration.MigrationContext.configure(connection)
            heads = context.get_current_heads()
            if heads:
                return heads[0]
            return None

        current = self.connection_executor.run_task(get_current)
        if current:
            return current
        return "base"

    def refresh_history(self) -> AlembicHistory:
        """Refresh the context's version of the alembic history.

        Note this is not done automatically to avoid the expensive reevaluation
        step which can make long histories take seconds longer to evaluate for
        each test.
        """
        script = self.command_executor.script
        script.revision_map = RevisionMap(script._load_revisions)  # noqa: SLF001
        self.history = AlembicHistory.parse(self.command_executor.script.revision_map)
        return self.history

    def generate_revision(
        self,
        process_revision_directives=None,
        *,
        prevent_file_generation=True,
        autogenerate=False,
        **kwargs
    ):
        """Generate a test revision.

        If `prevent_file_generation` is `True`, the final act of this process raises a
        `RevisionSuccess`, which is used as a sentinal to indicate the revision was
        generated successfully, while not actually finishing the generation of the
        revision file on disk.
        """
        alembic_config = self.command_executor.alembic_config
        config_directive = alembic_config.attributes["process_revision_directives"]

        directive = _sequence_directives(config_directive, process_revision_directives)

        if prevent_file_generation:
            directive = RevisionSuccess.process_revision_directives(directive)

        try:
            result = self.command_executor.run_command(
                "revision",
                process_revision_directives=directive,
                autogenerate=autogenerate,
                **kwargs,
            )

            # The history will only have changed if we didn't aritifically prevent it from failing.
            if not prevent_file_generation:
                self.refresh_history()
        except RevisionSuccess:
            pass
        else:
            return result

    def raw_command(self, *args, **kwargs):
        """Execute a raw alembic command."""
        return self.command_executor.run_command(*args, **kwargs)

    def managed_upgrade(self, dest_revision):
        """Perform an upgrade one migration at a time, inserting static data at the given points."""
        current = self.current
        for current_revision, next_revision in self.history.revision_window(current, dest_revision):
            before_upgrade_data = self.revision_data.get_before(next_revision)
            self.insert_into(data=before_upgrade_data, revision=current_revision, table=None)

            if next_revision in (self.config.skip_revisions or {}):
                self.set_revision(next_revision)
            else:
                self.command_executor.upgrade(next_revision)

            at_upgrade_data = self.revision_data.get_at(next_revision)
            self.insert_into(data=at_upgrade_data, revision=next_revision, table=None)

        current = self.current
        return current

    def managed_downgrade(self, dest_revision):
        """Perform an downgrade, one migration at a time."""
        current = self.current
        for next_revision, current_revision in reversed(
            self.history.revision_window(dest_revision, current)
        ):
            if current_revision in (self.config.skip_revisions or {}):
                self.set_revision(next_revision)
            else:
                try:
                    self.command_executor.downgrade(next_revision)
                except alembic.util.CommandError as e:
                    if "not a valid downgrade target" in str(e):
                        pass
                    else:
                        raise

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
        self.managed_downgrade(revision)
        return revision

    def migrate_down_one(self):
        """Migrate down by exactly one revision."""
        previous_revision = self.history.previous_revision(self.current)
        self.managed_downgrade(previous_revision)
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
        if data is None:
            return

        if revision is None:
            revision = self.current

        self.connection_executor.table_insert(
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
        return self.connection_executor.table(revision=revision, name=name, schema=schema)

    def set_revision(self, revision: str):
        self.command_executor.stamp(revision)


class RevisionSuccess(Exception):  # noqa: N818
    """Raise when a revision is successfully generated.

    In order to prevent the generation of an actual revision file on disk when running tests,
    this exception should be raised.
    """

    @classmethod
    def process_revision_directives(cls, fn):
        """Wrap a real `process_revision_directives` function, preventing it from completing."""

        @functools.wraps(fn)
        def _process_revision_directives(context, revision, directives):
            fn(context, revision, directives)
            raise cls

        return _process_revision_directives


def _sequence_directives(*directives):
    def directive_wrapper(*args, **kwargs):
        for directive in directives:
            if not directive:
                continue
            directive(*args, **kwargs)

    return directive_wrapper
