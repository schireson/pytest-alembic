import pytest_alembic.tests.experimental


def test_all_models_register_on_metadata(alembic_runner):
    pytest_alembic.tests.experimental.test_all_models_register_on_metadata(alembic_runner, "models", offline=True)
