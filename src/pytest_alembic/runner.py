import contextlib
import functools
from dataclasses import dataclass

from pytest_alembic.history import AlembicHistory
from pytest_alembic.executor import CommandExecutor


@contextlib.contextmanager
def runner(config, engine=None):
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
    executor: CommandExecutor

    def generate_revision(self, process_revision_directives=None, **kwargs):
        fn = RevisionSuccess.process_revision_directives(process_revision_directives)
        try:
            return self.executor.run_command("revision", process_revision_directives=fn, **kwargs)
        except RevisionSuccess:
            pass

    @property
    def history(self) -> AlembicHistory:
        raw_history = self.executor.run_command("history")
        return AlembicHistory.parse(raw_history)

    @property
    def heads(self):
        return self.executor.run_command("heads")

    def run(self, *args, **kwargs):
        return self.executor.run_command(*args, **kwargs)

    def migrate_up_before(self, revision):
        preceeding_revision = self.history.previous_revision(revision)
        self.executor.run_command("upgrade", preceeding_revision)

    def migrate_up_to(self, revision):
        self.history.validate_revision(revision)
        self.executor.run_command("upgrade", revision)

    def migrate_up_one(self):
        self.executor.run_command("downgrade", "+1")

    def migrate_down_before(self, revision):
        next_revision = self.history.next_revision(revision)
        self.run("downgrade", self.get_hash_before(next_revision))

    def migrate_down_to(self, revision):
        self.history.validate_revision(revision)
        self.executor.run_command("downgrade", revision)

    def migrate_down_one(self):
        self.executor.run_command("downgrade", "-1")

    def roundtrip_next_revision(self):
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
