from collections.abc import Callable
from typing import Any, cast

import pytest
from sqlalchemy.engine.url import make_url, URL

from pytest_alembic.plugin.error import AlembicTestFailure
from pytest_alembic.tests.experimental.all_models_register_on_metadata import (
    get_full_tableset,
    parse_collection_output,
    traverse_modules,
    url_to_string,
)


class Module:
    # A stand-in for a real module, declaring only the dunders `traverse_modules` reads.
    __name__: str
    __package__: str | None
    __path__: list[str]


def make_module(name: str, *, package: str | None = None, path: str | None = None) -> Module:
    module = Module()
    module.__name__ = name
    module.__package__ = package
    if path:
        module.__path__ = [path]
    return module


def yield_per_call(*calls: Any) -> Callable[..., Any]:
    state = iter(calls)

    def call(*_args: Any, **_kwargs: Any) -> Any:
        result = next(state)
        if isinstance(result, Exception):
            raise result
        return result

    return call


class Test_traverse_modules:
    def test_non_existent_module(self) -> None:
        result = list(traverse_modules("asdf"))
        assert result == []

    def test_non_package(self) -> None:
        module = make_module("foo")
        import_module = yield_per_call(module, module)

        result = list(traverse_modules("asdf", import_module=import_module))
        assert result == [module]

    def test_package_without_path(self) -> None:
        module = make_module("name", package="name")
        import_module = yield_per_call(module)

        result = list(traverse_modules("asdf", import_module=import_module))
        assert result == []

    def test_package_children_single_level(self) -> None:
        module = make_module("name", package="name", path="name")
        child = make_module("child", package="name.child", path="name")
        import_module = yield_per_call(module, child)

        walk_packages = yield_per_call([(None, "child", False)], [])

        result = list(
            traverse_modules("asdf", import_module=import_module, walk_packages=walk_packages)
        )
        assert result == [module, child]

    def test_package_child_import_error(self) -> None:
        module = make_module("name", package="name", path="name")
        import_module = yield_per_call(module, ImportError("name.child"))

        walk_packages = yield_per_call([(None, "child", False)], [])

        result = list(
            traverse_modules("asdf", import_module=import_module, walk_packages=walk_packages)
        )
        assert result == [module]

    def test_package_child_is_package(self) -> None:
        module = make_module("name", package="name", path="name")
        child = make_module("child", package="child.name", path="name")
        child_child = make_module("child", package="name.child")
        import_module = yield_per_call(module, child, child_child, child_child)

        walk_packages = yield_per_call([(None, "child", True)])

        result = list(
            traverse_modules("asdf", import_module=import_module, walk_packages=walk_packages)
        )
        assert result == [module, child]


class Test_get_full_tableset:
    def test_null_metadata(self) -> None:
        with pytest.raises(AlembicTestFailure) as e:
            get_full_tableset("foo")
        assert "Invalid module name: foo" in str(e.value)

    def test_no_metadata(self) -> None:
        with pytest.raises(AlembicTestFailure) as e:
            get_full_tableset("pytest_alembic")
        assert "Unable to locate a MetaData" in str(e.value)


class Test_parse_collection_output:
    """The subprocess reports through stdout, which it does not have to itself."""

    def test_ignores_surrounding_noise(self) -> None:
        payload = '<pytest-alembic>{"modules": [], "tables": ["t1"]}</pytest-alembic>'

        assert parse_collection_output(payload) == {"modules": [], "tables": ["t1"]}

    def test_missing_payload_is_a_bug_here(self) -> None:
        """Assert output with no sentinel raises, carrying the raw output.

        No payload means the subprocess never got as far as reporting, which indicates a
        problem in the collection script rather than in the migrations under test -- so
        the raw output is what the reader needs to see.
        """
        with pytest.raises(RuntimeError, match="alembic exploded"):
            parse_collection_output("alembic exploded")


class Test_url_to_string:
    """The password has to survive: the string is handed to a subprocess which connects.

    Which call renders it has changed across sqlalchemy versions, so the alternatives
    are tried in turn.
    """

    def test_modern_url_keeps_the_password(self) -> None:
        url = make_url("postgresql://user:hunter2@localhost/dev")

        assert url_to_string(url) == "postgresql://user:hunter2@localhost/dev"

    def test_url_without_the_hide_password_argument(self) -> None:
        class OldUrl:
            def render_as_string(self) -> str:
                return "rendered"

        assert url_to_string(cast("URL", OldUrl())) == "rendered"

    def test_url_without_render_as_string_at_all(self) -> None:
        class AncientUrl:
            def __str__(self) -> str:
                return "stringified"

        assert url_to_string(cast("URL", AncientUrl())) == "stringified"
