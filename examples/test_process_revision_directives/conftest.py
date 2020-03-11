import pytest


def err(*args):
    raise Exception("foo")


@pytest.fixture
def alembic_config():
    return {
        "process_revision_directives": err,
    }
