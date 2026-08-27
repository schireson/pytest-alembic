from pathlib import Path

import pytest
from pytest_mock_resources import create_postgres_fixture

pytest_plugins = "pytester"

db = create_postgres_fixture()

EXAMPLES = Path(__file__).parent.parent / "examples"


def _needs_postgres(item: pytest.Item) -> bool:
    """Whether `item` can only run against a real postgres.

    Two ways a test can need one, and neither is visible from the test body alone:

    - it requests a `create_postgres_fixture` fixture directly (`db`, `pg`);
    - it drives one of the `examples/` projects through `pytester`, and *that* project's
      `conftest.py` overrides `alembic_engine` with a postgres engine. The default
      `alembic_engine` is in-memory sqlite, so most examples need nothing.

    The second case is derived from the example directory rather than listed, because a
    hand-written list would silently rot the moment an example changed backend. The
    directory is found by `pytester`'s own convention -- `pytester_example_dir` plus the
    test name -- which is what `copy_example()` resolves.
    """
    if {"db", "pg"} & set(getattr(item, "fixturenames", ())):
        return True

    example = EXAMPLES / item.name
    return example.is_dir() and any(
        "postgres" in conftest.read_text() for conftest in example.rglob("conftest.py")
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark the tests that need a reachable postgres.

    GitHub Actions supports service containers on Linux runners only, so the Windows and
    macOS job has no database and deselects these with `-m "not postgres"`. Marking is
    additive: nothing is skipped or deselected here, so the Linux matrix keeps running
    the whole suite and the 100% coverage floor still applies to it.
    """
    for item in items:
        if _needs_postgres(item):
            item.add_marker(pytest.mark.postgres)
