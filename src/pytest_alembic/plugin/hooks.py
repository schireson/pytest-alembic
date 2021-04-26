from pytest_alembic.plugin.plugin import collect_all_tests, collect_tests


def pytest_addoption(parser):
    default_tests = ", ".join(collect_all_tests().keys())
    parser.addini(
        "pytest_alembic_include",
        "List of built-in tests to include. If specified, 'pytest_alembic_exclude' is ignored. "
        f"If both are omitted, all tests are included. Valid options include: {default_tests}",
    )
    parser.addini(
        "pytest_alembic_exclude",
        "List of built-in tests to exclude. Ignored if 'pytest_alembic_include' is specified."
        f"Valid options include: {default_tests}",
    )
    parser.addini(
        "pytest_alembic_tests_folder",
        "The location under which the built-in tests will be bound. This defaults to 'tests/' "
        "(the tests themselves then being executed from tests/pytest_alembic/*), the typical test "
        "location. However this can be customized if pytest is, for example, invoked from a parent "
        "directory like `pytest folder/tests`, or the tests are otherwise located at a different "
        "location, relative to `pytest`s invocation.",
        default="tests",
    )

    group = parser.getgroup("collect")
    group.addoption(
        "--test-alembic",
        action="store_true",
        default=False,
        help="Enable pytest-alembic built-in tests",
        dest="pytest_alembic_enabled",
    )
    group.addoption(
        "--alembic-exclude",
        default=None,
        help=f"List of built-in tests to exclude. Valid options include: {default_tests}",
        dest="pytest_alembic_exclude",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "alembic: Tests which use pytest-alembic.")


def pytest_collection_modifyitems(session, config, items):
    tests = collect_tests(session, config)
    items.extend(tests)


def pytest_itemcollected(item):
    """Attach a marker to each test which uses the alembic fixture."""
    if not hasattr(item, "fixturenames"):
        return

    if "alembic_runner" in item.fixturenames:
        item.add_marker("alembic")
