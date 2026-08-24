import pytest

from pytest_alembic.plugin.error import AlembicTestFailure
from pytest_alembic.tests import default


class Test_test_upgrade:
    def test_runtime_error_becomes_test_failure(self):
        """Assert a `RuntimeError` from the alembic layer is translated for the user.

        `CommandExecutor.run_command` converts `alembic`'s `CommandError` into a
        `RuntimeError`, and `test_upgrade` is responsible for turning that into an
        `AlembicTestFailure` which carries the underlying alembic message as context.
        """

        class Runner:
            def migrate_up_to(self, *_args, **_kwargs):
                msg = "Can't locate revision identified by 'abcdef'"
                raise RuntimeError(msg)

        with pytest.raises(AlembicTestFailure) as e:
            default.test_upgrade(Runner())

        assert "Failed to upgrade to the head revision" in str(e.value)
        assert "Alembic Error" in str(e.value)
        assert "Can't locate revision identified by 'abcdef'" in str(e.value)
