import os

from pytest_alembic.plugin.plugin import collect_all_tests, collect_tests


def pytest_addoption(parser):
    default_tests = ", ".join(collect_all_tests().keys())
    parser.addini(
        "pytest_alembic_enabled", "Whether to execute pytest-alembic built-in tests", default=True
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

    group = parser.getgroup("collect")
    group.addoption(
        "--test-alembic",
        action="store_true",
        default=True,
        help="Enable pytest-alembic built-in tests",
        dest="pytest_alembic_enabled",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "alembic: Tests produced by pytest-alembic.")


def pytest_collection_modifyitems(session, config, items):
    parent_paths = {os.path.dirname(path) for path in session._initialpaths}
    has_root_parent = any(parent_path == config.rootdir for parent_path in parent_paths)
    if parent_paths and not has_root_parent:
        return

    tests = collect_tests(session, config)
    items.extend(tests)
