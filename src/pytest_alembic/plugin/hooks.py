from pytest_alembic.plugin.plugin import PytestAlembicModule, collect_all_tests


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


def pytest_collect_file(path, parent):
    # XXX: This is called for every file, it really should be called once. Figure out
    #      which hook should be used instead.
    collected = getattr(pytest_collect_file, "collected", False)
    if collected:
        return
    pytest_collect_file.collected = True

    cli_enabled = parent.config.option.pytest_alembic_enabled
    config_enabled = parent.config.getini("pytest_alembic_enabled")
    if not cli_enabled and config_enabled:
        return

    return PytestAlembicModule(path, parent)
