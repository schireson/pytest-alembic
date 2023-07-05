import pytest


def err(*_):
    msg = "foo"
    raise Exception(msg)  # noqa: TRY


@pytest.fixture()
def alembic_config():
    return {
        "process_revision_directives": err,
    }
