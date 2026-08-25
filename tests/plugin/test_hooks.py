from unittest import mock

from pytest_alembic.plugin import hooks


def test_disabled_plugin_registers_no_hooks() -> None:
    """Assert `pytest_alembic_enabled = false` means the plugin is never registered.

    The option is honoured at session start rather than at collection time, so a
    disabled plugin adds no hooks at all instead of adding hooks which decline to
    collect.
    """
    session = mock.Mock()
    session.config.getini.return_value = False

    hooks.pytest_sessionstart(session)

    session.config.pluginmanager.register.assert_not_called()


def test_enabled_plugin_is_registered_under_its_own_name() -> None:
    """Assert the collection plugin is registered when the option is left on."""
    session = mock.Mock()
    session.config.getini.return_value = True

    hooks.pytest_sessionstart(session)

    (plugin, name) = session.config.pluginmanager.register.call_args.args
    assert name == "pytest-alembic"
    assert plugin.config is session.config
