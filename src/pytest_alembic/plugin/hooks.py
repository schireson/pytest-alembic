from pytest_alembic.plugin.plugin import OptionResolver, PytestAlembicPlugin


def pytest_addoption(parser):
    default_collector = OptionResolver.collect_test_definitions(default=True, experimental=False)
    default_tests = ", ".join(t.name for t in default_collector.available_tests.values())

    experimental_collector = OptionResolver.collect_test_definitions(
        default=False, experimental=True
    )
    experimental_tests = ", ".join(t.name for t in experimental_collector.available_tests.values())

    parser.addini(
        "pytest_alembic_enabled",
        "Whether to enable/disable the plugin's behavior entirely. Defaults to true.",
        default=True,
    )
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
        "pytest_alembic_include_experimental",
        "List of built-in experimental tests to include. Experimental tests must be explicitly "
        f"included. Valid options include: {experimental_tests}",
    )
    parser.addini(
        "pytest_alembic_tests_path",
        "The location at which the built-in tests will be bound. This defaults to 'tests/conftest.py'. "
        "Typically, you would want this to coincide with the path at which your `alembic_engine` is being "
        "defined/registered. Note that this path must be the full path, relative to the root location "
        "at which pytest is being invoked.",
    )

    group = parser.getgroup("collect")
    group.addoption(
        "--test-alembic",
        action="store_true",
        default=False,
        help="Enable pytest-alembic built-in tests",
        dest="pytest_alembic_registration_enabled",
    )
    group.addoption(
        "--alembic-exclude",
        default=None,
        help=f"List of built-in tests to exclude. Valid options include: {default_tests}",
        dest="pytest_alembic_exclude",
    )
    group.addoption(
        "--alembic-tests-path",
        help=(
            "The location at which the built-in tests will be bound. Has higher precedence than the "
            "corresponding `pytest_alembic_tests_path` ini option."
        ),
        dest="pytest_alembic_tests_path",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "alembic: Tests which use pytest-alembic.")


def pytest_sessionstart(session):
    if session.config.getini("pytest_alembic_enabled"):
        plugin = PytestAlembicPlugin(session.config)
        session.config.pluginmanager.register(plugin, "pytest-alembic")
