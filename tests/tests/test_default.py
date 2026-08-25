from typing import Any, cast, TYPE_CHECKING

import pytest

from pytest_alembic.plugin.error import AlembicTestFailure
from pytest_alembic.tests import default

if TYPE_CHECKING:
    from pytest_alembic.runner import MigrationContext


class Test_test_upgrade:
    def test_runtime_error_becomes_test_failure(self) -> None:
        """Assert a `RuntimeError` from the alembic layer is translated for the user.

        `CommandExecutor.run_command` converts `alembic`'s `CommandError` into a
        `RuntimeError`, and `test_upgrade` is responsible for turning that into an
        `AlembicTestFailure` which carries the underlying alembic message as context.
        """

        class Runner:
            def migrate_up_to(self, *_args: Any, **_kwargs: Any) -> None:
                msg = "Can't locate revision identified by 'abcdef'"
                raise RuntimeError(msg)

        with pytest.raises(AlembicTestFailure) as e:
            # A duck-typed stand-in: `test_upgrade` only ever calls `migrate_up_to`.
            default.test_upgrade(cast("MigrationContext", Runner()))

        assert "Failed to upgrade to the head revision" in str(e.value)
        assert "Alembic Error" in str(e.value)
        assert "Can't locate revision identified by 'abcdef'" in str(e.value)
