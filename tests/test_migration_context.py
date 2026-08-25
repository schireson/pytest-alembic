"""Direct tests for the `MigrationContext` paths the example-driven suite cannot reach.

Most of `tests/test_runner.py` drives a real alembic history through `pytester`, which
is the right shape for anything involving migrations actually running. The paths here
are the opposite: error handling and early returns which need a specific executor
response rather than a specific migration history, so they are exercised against stubs.
"""

from typing import Any
from unittest import mock

import alembic.config
import alembic.util
import pytest

from pytest_alembic.config import Config
from pytest_alembic.revision_data import RevisionData
from pytest_alembic.runner import MigrationContext


def make_command_executor() -> Any:
    """A stub executor carrying the one real thing `generate_revision` reads."""
    command_executor = mock.Mock()
    command_executor.alembic_config = alembic.config.Config()
    command_executor.alembic_config.attributes["process_revision_directives"] = None
    return command_executor


def make_context(
    command_executor: Any = None,
    connection_executor: Any = None,
    history: Any = None,
) -> MigrationContext:
    """Build a `MigrationContext` whose collaborators are stubs."""
    config = Config()
    return MigrationContext(
        command_executor=command_executor or make_command_executor(),
        revision_data=RevisionData.from_config(config),
        connection_executor=connection_executor or mock.Mock(),
        history=history or mock.Mock(),
        config=config,
    )


def test_raw_command_forwards_to_the_executor() -> None:
    """Assert `raw_command` is a pass-through to `alembic.command`.

    It is the escape hatch for commands with no dedicated method here, so it must not
    interpret its arguments -- they go through untouched, and the captured stdout comes
    straight back.
    """
    command_executor = make_command_executor()
    command_executor.run_command.return_value = ["a line"]
    context = make_context(command_executor=command_executor)

    result = context.raw_command("history", verbose=True)

    assert result == ["a line"]
    command_executor.run_command.assert_called_once_with("history", verbose=True)


def test_insert_into_without_data_is_a_no_op() -> None:
    """Assert `insert_into` with no data touches neither the connection nor the schema.

    `managed_upgrade` calls this for every revision, and most revisions have no
    configured data, so the empty case has to be free rather than reflecting a table.
    """
    connection_executor = mock.Mock()
    context = make_context(connection_executor=connection_executor)

    context.insert_into("foo", None)

    connection_executor.table_insert.assert_not_called()


def test_generate_revision_does_not_refresh_history_when_preventing_generation() -> None:
    """Assert the history is only re-parsed when a revision file was actually written.

    Re-parsing is the expensive step `refresh_history` documents, so it is skipped when
    nothing can have changed on disk.
    """
    command_executor = make_command_executor()
    command_executor.run_command.return_value = ["ok"]
    context = make_context(command_executor=command_executor)

    with mock.patch.object(MigrationContext, "refresh_history") as refresh_history:
        result = context.generate_revision(message="test revision")

    assert result == ["ok"]
    refresh_history.assert_not_called()


class Test_managed_downgrade:
    """`managed_downgrade` distinguishes one alembic error from every other."""

    @staticmethod
    def context_raising(error: Exception) -> MigrationContext:
        command_executor = make_command_executor()
        command_executor.downgrade.side_effect = error

        history = mock.Mock()
        history.revision_window.return_value = [("a1", "b2")]

        return make_context(command_executor=command_executor, history=history)

    def test_invalid_downgrade_target_is_tolerated(self) -> None:
        """Assert a branch alembic cannot downgrade past is walked over, not raised.

        A branched history yields `(from, to)` pairs which are not all reachable from
        one another; alembic rejects those, and it is not a failure of the migrations.
        """
        error = alembic.util.CommandError(
            "Destination b2 is not a valid downgrade target from current head(s)"
        )
        context = self.context_raising(error)

        assert context.managed_downgrade("a1", current="b2", return_current=False) is None

    def test_other_command_errors_propagate(self) -> None:
        """Assert an unrelated alembic failure is not swallowed by that tolerance."""
        context = self.context_raising(alembic.util.CommandError("Can't locate revision"))

        with pytest.raises(alembic.util.CommandError, match="Can't locate revision"):
            context.managed_downgrade("a1", current="b2", return_current=False)
