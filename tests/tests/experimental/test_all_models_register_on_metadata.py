import pytest

from pytest_alembic.plugin.error import AlembicTestFailure
from pytest_alembic.tests.experimental.all_models_register_on_metadata import (
    get_full_tableset,
    traverse_modules,
)


class Module:
    pass


def make_module(name, *, package=None, path=None, dict=None):
    module = Module()
    module.__name__ = name
    module.__package__ = package
    if path:
        module.__path__ = [path]

    if dict:
        module.__dict__.update(dict)
    return module


def yield_per_call(*calls):
    state = iter(calls)

    def call(*args, **kwargs):
        result = next(state)
        if isinstance(result, Exception):
            raise result
        return result

    return call


class Test_traverse_modules:
    def test_non_existent_module(self):
        result = list(traverse_modules("asdf"))
        assert result == []

    def test_non_package(self):
        module = make_module("foo")
        import_module = yield_per_call(module, module)

        result = list(traverse_modules("asdf", import_module=import_module))
        assert result == [module]

    def test_package_without_path(self):
        module = make_module("name", package="name")
        import_module = yield_per_call(module)

        result = list(traverse_modules("asdf", import_module=import_module))
        assert result == []

    def test_package_children_single_level(self):
        module = make_module("name", package="name", path="name")
        child = make_module("child", package="name.child", path="name")
        import_module = yield_per_call(module, child)

        walk_packages = yield_per_call([(None, "child", False)], [])

        result = list(
            traverse_modules("asdf", import_module=import_module, walk_packages=walk_packages)
        )
        assert result == [module, child]

    def test_package_child_import_error(self):
        module = make_module("name", package="name", path="name")
        import_module = yield_per_call(module, ImportError("name.child"))

        walk_packages = yield_per_call([(None, "child", False)], [])

        result = list(
            traverse_modules("asdf", import_module=import_module, walk_packages=walk_packages)
        )
        assert result == [module]

    def test_package_child_is_package(self):
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
    def test_null_metadata(self):
        with pytest.raises(AlembicTestFailure) as e:
            get_full_tableset("foo")
        assert "Invalid module name: foo" in str(e.value)

    def test_no_metadata(self):
        with pytest.raises(AlembicTestFailure) as e:
            get_full_tableset("pytest_alembic")
        assert "Unable to locate a MetaData" in str(e.value)
