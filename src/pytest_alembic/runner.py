import contextlib
import functools
from dataclasses import dataclass
from typing import List

from pytest_alembic.executor import CommandExecutor
from pytest_alembic.history import AlembicHistory


@contextlib.contextmanager
def runner(config, engine=None):
    """Manage the alembic execution context, in a given context.

    Yields:
        `MigrationContext` to the caller.
    """
    command_executor = CommandExecutor.from_config(config)
    migration_context = MigrationContext(command_executor)

    if engine:
        with engine.begin() as connection:
            command_executor.configure(connection=connection)
            yield migration_context
    else:
        yield migration_context


@dataclass
class MigrationContext:
    """Within a given environment/execution context, executes alembic commands.
    """

    executor: CommandExecutor

    def generate_revision(self, process_revision_directives=None, **kwargs):
        """Generate a test revision.

        The final act of this process raises a `RevisionSuccess`, which is used as a sentinal
        to indicate the revision was generated successfully, while not actually finishing the
        generation of the revision file.
        """
        fn = RevisionSuccess.process_revision_directives(process_revision_directives)
        try:
            return self.executor.run_command("revision", process_revision_directives=fn, **kwargs)
        except RevisionSuccess:
            pass

    @property
    def history(self) -> AlembicHistory:
        """Get the revision history.
        """
        raw_history = self.executor.run_command("history")
        return AlembicHistory.parse(raw_history)

    @property
    def heads(self) -> List[str]:
        """Get the list of revision heads.
        """
        return self.executor.run_command("heads")

    def raw_command(self, *args, **kwargs):
        """Execute a raw alembic command.
        """
        return self.executor.run_command(*args, **kwargs)

    def migrate_up_before(self, revision):
        """Upgrade up to, but not including the given `revision`.
        """
        preceeding_revision = self.history.previous_revision(revision)
        self.raw_command("upgrade", preceeding_revision)

    def migrate_up_to(self, revision):
        """Upgrade up to, and including the given `revision`.
        """
        self.history.validate_revision(revision)
        self.raw_command("upgrade", revision)

    def migrate_up_one(self):
        """Upgrade up by exactly one revision.
        """
        self.raw_command("downgrade", "+1")

    def migrate_down_before(self, revision):
        """Upgrade down to, but not including the given `revision`.
        """
        next_revision = self.history.next_revision(revision)
        self.raw_command("downgrade", self.get_hash_before(next_revision))

    def migrate_down_to(self, revision):
        """Upgrade down to, and including the given `revision`.
        """
        self.history.validate_revision(revision)
        self.raw_command("downgrade", revision)

    def migrate_down_one(self):
        """Upgrade down by exactly one revision.
        """
        self.raw_command("downgrade", "-1")

    def roundtrip_next_revision(self):
        """Upgrade, downgrade then upgrade.

        This is meant to ensure that the given revision is idempotent.
        """
        self.migrate_up_one()
        self.migrate_down_one()
        self.migrate_up_one()


class RevisionSuccess(Exception):
    """Raise when a revision is successfully generated.

    In order to prevent the generation of an actual revision file on disk when running tests,
    this exception should be raised.
    """

    @classmethod
    def process_revision_directives(cls, fn=None):
        """Wrap a real `process_revision_directives` function, while preventing it from completing.
        """

        @functools.wraps(fn)
        def _process_revision_directives(context, revision, directives):
            if fn:
                fn(context, revision, directives)
            raise cls()

        return _process_revision_directives
