"""The pytest hook implementations which expose this plugin's options and register it.

Loaded through the ``pytest11`` entry point declared in ``pyproject.toml``, so pytest
imports this module for every session, whether or not the plugin ends up active.
"""

from pytest_alembic.plugin.plugin import OptionResolver, PytestAlembicPlugin


def pytest_addoption(parser):
    """Register this plugin's ini options and command-line flags.

    The set of valid test names is not hard-coded: it is collected from
    :mod:`pytest_alembic.tests` at option-registration time, so ``--help`` always
    lists the tests this version actually ships. Default and experimental tests are
    collected separately because they are opted into differently — experimental ones
    must be named explicitly.

    Args:
        parser: The pytest parser to register ini values and options against.
    """
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
    """Register the ``alembic`` marker, so selecting or deselecting these tests works.

    Registration also keeps the marker from tripping ``--strict-markers``.

    Args:
        config: The pytest config object for the session being configured.
    """
    config.addinivalue_line("markers", "alembic: Tests which use pytest-alembic.")


def pytest_sessionstart(session):
    """Register the collection plugin, unless it has been disabled entirely.

    ``pytest_alembic_enabled`` is honoured here rather than at collection time so that
    a disabled plugin adds no hooks at all, instead of adding hooks which decline to
    collect.

    Args:
        session: The pytest session being started.
    """
    if session.config.getini("pytest_alembic_enabled"):
        plugin = PytestAlembicPlugin(session.config)
        session.config.pluginmanager.register(plugin, "pytest-alembic")
