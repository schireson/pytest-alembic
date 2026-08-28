"""The object tests actually hold: the migration context, and how it is built.

:class:`MigrationContext` is what the :func:`alembic_runner` fixture yields, and the
surface every test written against a migration history uses. This module assembles it
from the pieces the other modules provide — the two executors, the flattened history,
and the configured revision data.
"""

import contextlib
import functools
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

import alembic.command
import alembic.migration
import alembic.util
from alembic.script.revision import RevisionMap
from sqlalchemy import Table
from sqlalchemy.engine import Connectable

from pytest_alembic.executor import CommandExecutor, ConnectionExecutor
from pytest_alembic.history import AlembicHistory
from pytest_alembic.revision_data import RevisionData

if TYPE_CHECKING:
    from alembic.runtime.migration import MigrationContext as AlembicMigrationContext
    from alembic.runtime.migration import RevisionStep

    from pytest_alembic.config import Config

# A user-supplied ``process_revision_directives`` callback, as alembic invokes it:
# the live migration context, the revision(s) being generated, and the list of
# directives, which the callback mutates in place.
ProcessRevisionDirectives = Callable[..., None]


@contextlib.contextmanager
def runner(config: "Config", engine: Connectable | None = None) -> Iterator["MigrationContext"]:
    """Manage the alembic execution context, in a given context.

    Most tests never call this directly — the :func:`alembic_runner` fixture wraps it and
    yields the same :class:`MigrationContext`. Reach for it when you need a runner outside
    a fixture, such as in a ``conftest.py`` helper.

    Yields:
        `MigrationContext` to the caller.

    Examples:
        >>> import pytest_alembic
        >>> from pytest_alembic.config import Config
        >>>
        >>> def upgrade_to_head(engine):
        ...     with pytest_alembic.runner(config=Config(), engine=engine) as alembic_runner:
        ...         alembic_runner.migrate_up_to("heads")
    """
    command_executor = CommandExecutor.from_config(config)
    migration_context = MigrationContext.from_config(
        config,
        command_executor,
        ConnectionExecutor(engine),
    )

    command_executor.configure(connection=engine)
    yield migration_context


# On this module's size, which is deliberate. `runner.py` is the largest module in the
# package and the most imported one, and `MigrationContext` below carries both the
# migration verbs (`migrate_up_one`, `migrate_down_to`, `roundtrip_next_revision`) and the
# history/state accessors (`current`, `heads`, `table_at_revision`, `insert_into`). Read as
# a class in isolation, that is two responsibilities and an obvious split.
#
# It is one class because it is *the* documented public surface: the object
# `alembic_runner` yields, and the receiver of every call in every example in the docs.
# Splitting it would rename or re-home names that users have written tests against, for no
# defect -- the metrics are healthy (no block above `B`, maintainability index `A`), so the
# split would buy a tidier graph at the cost of an API break.
#
# If a genuine reason to split arrives, keep the public names on this class and delegate,
# rather than asking callers to reach for a second object.
@dataclass
class MigrationContext:
    """Within a given environment/execution context, executes alembic commands.

    This is the object the :func:`alembic_runner` fixture yields, and the primary surface
    for tests written against a specific migration history. The methods fall into three
    groups:

    - **Moving through the history**: :meth:`migrate_up_one`, :meth:`migrate_up_to`,
      :meth:`migrate_up_before`, and their ``down`` counterparts.
    - **Inspecting it**: :attr:`current`, :attr:`heads`, and ``history``
      (an :class:`~pytest_alembic.history.AlembicHistory`).
    - **Reading and writing data**: :meth:`insert_into` and :meth:`table_at_revision`.

    Examples:
        >>> def test_migration_backfills_existing_rows(alembic_runner):
        ...     alembic_runner.migrate_up_before("abc123")
        ...     alembic_runner.insert_into("foo", {"id": 1})
        ...     alembic_runner.migrate_up_one()
        ...
        ...     foo = alembic_runner.table_at_revision("foo")
        ...     assert foo.name == "foo"
    """

    command_executor: CommandExecutor
    revision_data: RevisionData
    connection_executor: ConnectionExecutor
    history: AlembicHistory
    config: "Config"

    @classmethod
    def from_config(
        cls,
        config: "Config",
        command_executor: CommandExecutor,
        connection_executor: ConnectionExecutor,
    ) -> "MigrationContext":
        """Assemble a context from its parts, parsing the history as it goes.

        The executors are passed in rather than built here, because the caller is what
        knows the engine under test — see :func:`runner`.
        """
        history = AlembicHistory.parse(command_executor.script.revision_map)

        return cls(
            command_executor=command_executor,
            revision_data=RevisionData.from_config(config),
            connection_executor=connection_executor,
            history=history,
            config=config,
        )

    @property
    def heads(self) -> list[str]:
        """Get the list of revision heads.

        Result is cached for the lifetime of the `MigrationContext`.

        Examples:
            >>> def test_history_has_one_head(alembic_runner):
            ...     assert len(alembic_runner.heads) == 1
        """
        return self.command_executor.heads()

    @property
    def current(self) -> str:
        """Get the revision the database is currently at.

        Returns the string ``"base"`` when no migration has been applied yet, rather than
        ``None``, so the result is always comparable against a revision hash.

        Examples:
            >>> def test_starts_at_base(alembic_runner):
            ...     assert alembic_runner.current == "base"
            ...
            ...     alembic_runner.migrate_up_one()
            ...     assert alembic_runner.current != "base"
        """
        current = "base"

        def get_current(rev: Any, _: "AlembicMigrationContext") -> "list[RevisionStep]":
            nonlocal current
            if rev:
                current = rev[0]

            return []

        self.command_executor.execute_fn(get_current)

        # No fallback needed: `current` starts as "base" and `get_current` only ever
        # reassigns it to a revision hash.
        return current

    def refresh_history(self) -> AlembicHistory:
        """Refresh the context's version of the alembic history.

        Note this is not done automatically to avoid the expensive reevaluation
        step which can make long histories take seconds longer to evaluate for
        each test.

        Call this after writing a revision file during a test; otherwise the cached
        history will not contain it.

        Examples:
            >>> def test_history_picks_up_new_revision(alembic_runner):
            ...     alembic_runner.generate_revision(prevent_file_generation=False)
            ...
            ...     history = alembic_runner.refresh_history()
            ...     assert history.revisions
        """
        script = self.command_executor.script
        script.revision_map = RevisionMap(script._load_revisions)  # noqa: SLF001
        self.history = AlembicHistory.parse(self.command_executor.script.revision_map)
        return self.history

    def generate_revision(
        self,
        process_revision_directives: ProcessRevisionDirectives | None = None,
        *,
        prevent_file_generation: bool = True,
        autogenerate: bool = False,
        **kwargs: Any,
    ) -> list[str] | None:
        """Generate a test revision.

        If `prevent_file_generation` is `True`, the final act of this process raises a
        `RevisionSuccess`, which is used as a sentinel to indicate the revision was
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
            # The sentinel means the revision was generated successfully but its file
            # was deliberately not written, so there is no command output to hand back.
            return None
        else:
            return result

    def raw_command(self, *args: Any, **kwargs: Any) -> list[str]:
        """Execute a raw alembic command.

        An escape hatch for alembic commands with no dedicated method here. Arguments are
        forwarded to the corresponding function in ``alembic.command``, and captured
        stdout is returned as a list of lines.

        Examples:
            >>> def test_history_command_runs(alembic_runner):
            ...     output = alembic_runner.raw_command("history")
            ...     assert isinstance(output, list)
        """
        return self.command_executor.run_command(*args, **kwargs)

    def managed_upgrade(
        self, dest_revision: str | None, *, current: str | None = None, return_current: bool = True
    ) -> str | None:
        """Perform an upgrade one migration at a time, inserting static data at the given points."""
        if current is None:
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

        if return_current:
            return self.current
        return None

    def managed_downgrade(
        self, dest_revision: str | None, *, current: str | None = None, return_current: bool = True
    ) -> str | None:
        """Perform an downgrade, one migration at a time."""
        if current is None:
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

        if return_current:
            return self.current
        return None

    def migrate_up_before(self, revision: str) -> str | None:
        """Migrate up to, but not including the given `revision`.

        This is the usual way to set up state that a migration is then asked to
        transform: get the schema to the point just before the revision under test,
        insert rows, then apply exactly one migration.

        Examples:
            >>> def test_migration_transforms_existing_rows(alembic_runner):
            ...     alembic_runner.migrate_up_before("abc123")
            ...     alembic_runner.insert_into("foo", {"id": 1})
            ...     alembic_runner.migrate_up_one()
        """
        preceeding_revision = self.history.previous_revision(revision)
        return self.managed_upgrade(preceeding_revision)

    def migrate_up_to(
        self, revision: str, *, current: str | None = None, return_current: bool = True
    ) -> str | None:
        """Migrate up to, and including the given `revision`.

        Accepts ``"heads"`` to apply the whole history.

        Examples:
            >>> def test_upgrade_to_specific_revision(alembic_runner):
            ...     alembic_runner.migrate_up_to("abc123")
            ...     assert alembic_runner.current == "abc123"

            >>> def test_full_history_applies(alembic_runner):
            ...     alembic_runner.migrate_up_to("heads")
        """
        return self.managed_upgrade(revision, current=current, return_current=return_current)

    def migrate_up_one(self) -> str | None:
        """Migrate up by exactly one revision.

        Returns the revision migrated to, or ``None`` if already at the head — which
        makes it usable as a loop condition when stepping through a history.

        Examples:
            >>> def test_each_revision_applies(alembic_runner):
            ...     while alembic_runner.migrate_up_one():
            ...         pass
        """
        current = self.current
        next_revision = self.history.next_revision(current)
        new_revision = self.managed_upgrade(next_revision, current=current)
        if current == new_revision:
            return None
        return new_revision

    def migrate_down_before(self, revision: str) -> str | None:
        """Migrate down to, but not including the given `revision`.

        Examples:
            >>> def test_downgrade_stops_short(alembic_runner):
            ...     alembic_runner.migrate_up_to("heads")
            ...     alembic_runner.migrate_down_before("abc123")
        """
        next_revision = self.history.next_revision(revision)
        return self.migrate_down_to(next_revision)

    def migrate_down_to(
        self, revision: str | None, *, current: str | None = None, return_current: bool = True
    ) -> str | None:
        """Migrate down to, and including the given `revision`.

        Accepts ``"base"`` to unwind the entire history.

        Examples:
            >>> def test_downgrade_to_base(alembic_runner):
            ...     alembic_runner.migrate_up_to("heads")
            ...     alembic_runner.migrate_down_to("base")
        """
        self.history.validate_revision(revision)
        self.managed_downgrade(revision, current=current, return_current=return_current)
        return revision

    def migrate_down_one(self) -> str | None:
        """Migrate down by exactly one revision.

        Returns the revision migrated down to.

        Examples:
            >>> def test_downgrade_one_step(alembic_runner):
            ...     alembic_runner.migrate_up_to("heads")
            ...     previous = alembic_runner.migrate_down_one()
            ...     assert alembic_runner.current == previous
        """
        current = self.current
        previous_revision = self.history.previous_revision(current)
        self.managed_downgrade(previous_revision, current=current)
        return previous_revision

    def roundtrip_next_revision(self) -> str | None:
        """Upgrade, downgrade then upgrade.

        This is meant to ensure that the given revision is idempotent.

        Returns the revision arrived at, or ``None`` if already at the head.

        Examples:
            >>> def test_every_revision_round_trips(alembic_runner):
            ...     while alembic_runner.roundtrip_next_revision():
            ...         pass
        """
        next_revision = self.migrate_up_one()
        if next_revision:
            self.migrate_down_one()
            return self.migrate_up_one()
        return None

    def insert_into(
        self, table: str | None, data: dict | list | None = None, revision: str | None = None
    ) -> None:
        """Insert data into a given table.

        The table is reflected at `revision`, which defaults to the current revision — so
        the rows are written against the schema as it exists at that point, not as it
        exists at the head.

        Args:
            table: The name of the table to insert data into
            data: The data to insert. This is eventually passed through to SQLAlchemy's
                Table class `values` method, and so should accept either a list of
                `dict`s representing a list of rows, or a `dict` representing one row.
            revision: The revision of MetaData to use as the table definition for the insert.

        Examples:
            One row:

            >>> def test_insert_one_row(alembic_runner):
            ...     alembic_runner.migrate_up_to("abc123")
            ...     alembic_runner.insert_into("foo", {"id": 1, "name": "one"})

            Several, as a list of dicts:

            >>> def test_insert_many_rows(alembic_runner):
            ...     alembic_runner.migrate_up_to("abc123")
            ...     alembic_runner.insert_into(
            ...         "foo", [{"id": 1, "name": "one"}, {"id": 2, "name": "two"}]
            ...     )

            The table name can also travel with the data, which is what lets one call
            span more than one table:

            >>> def test_insert_across_tables(alembic_runner):
            ...     alembic_runner.insert_into(
            ...         None,
            ...         [
            ...             {"__tablename__": "foo", "id": 1},
            ...             {"__tablename__": "bar", "id": 2},
            ...         ],
            ...     )
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

    def table_at_revision(
        self, name: str, *, revision: str | None = None, schema: str | None = None
    ) -> Table:
        """Return a reference to a `sqlalchemy.Table` at the given revision.

        Useful for asserting on what a migration actually did — the returned table is
        reflected from the live database, so its columns are the real post-migration
        shape rather than whatever the current models declare.

        Args:
            name: The name of the table to produce a `sqlalchemy.Table` for.
            revision: The revision of the table to return.
            schema: The schema of the table.

        Examples:
            >>> def test_migration_adds_column(alembic_runner):
            ...     alembic_runner.migrate_up_to("abc123")
            ...
            ...     foo = alembic_runner.table_at_revision("foo")
            ...     assert "new_column" in foo.columns
        """
        revision = revision or self.current
        return self.connection_executor.table(revision=revision, name=name, schema=schema)

    def set_revision(self, revision: str) -> None:
        """Declare the database to be at `revision` without running any migration.

        This stamps the alembic version table and nothing else. Useful for putting the
        database at a known point cheaply, but note that the schema is *not* brought in
        line with that revision — that is the caller's problem.

        Examples:
            >>> def test_from_midway_through_the_history(alembic_runner):
            ...     alembic_runner.set_revision("abc123")
        """
        self.command_executor.stamp(revision)


class RevisionSuccess(Exception):  # noqa: N818
    """Raise when a revision is successfully generated.

    In order to prevent the generation of an actual revision file on disk when running tests,
    this exception should be raised.
    """

    @classmethod
    def process_revision_directives(
        cls, fn: ProcessRevisionDirectives
    ) -> ProcessRevisionDirectives:
        """Wrap a real `process_revision_directives` function, preventing it from completing."""

        @functools.wraps(fn)
        def _process_revision_directives(context: Any, revision: Any, directives: Any) -> None:
            fn(context, revision, directives)
            raise cls

        return _process_revision_directives


def _sequence_directives(
    *directives: ProcessRevisionDirectives | None,
) -> ProcessRevisionDirectives:
    def directive_wrapper(*args: Any, **kwargs: Any) -> None:
        for directive in directives:
            if not directive:
                continue
            directive(*args, **kwargs)

    return directive_wrapper
