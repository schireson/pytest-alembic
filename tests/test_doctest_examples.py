"""Undefined names in doctest examples, as a gate -- including inside `>>> def` bodies.


ruff does not lint code inside docstrings (checked against exactly that shape with
`--select F821`), so this reads the examples out with `doctest` and runs pyflakes over them.
"""

import ast
import doctest
import importlib
import pkgutil
from types import ModuleType

import pytest
from pyflakes.checker import Checker
from pyflakes.messages import UndefinedName

import pytest_alembic


def _modules() -> list[ModuleType]:
    """Import every module in the package, so `DocTestFinder` can be given the objects."""
    modules = [pytest_alembic]
    for module in pkgutil.walk_packages(pytest_alembic.__path__, f"{pytest_alembic.__name__}."):
        modules.append(importlib.import_module(module.name))
    return modules


def _doctests() -> list[doctest.DocTest]:
    finder = doctest.DocTestFinder(exclude_empty=True)
    return [test for module in _modules() for test in finder.find(module) if test.examples]


def _permitted_names(name: str) -> set[str]:
    """The names an example may use without importing them.

    Deliberately narrow: the object being documented, and its class if it is a method. An
    example is something a reader copies into their own file, so anything else it references
    it should import -- and the wider, more obvious choice of seeding the module's whole
    namespace makes this gate a no-op. `alembic_runner` *is* a module-level name in
    `plugin.fixtures`, so seeding `vars(module)` finds zero problems in this package and
    would have let #236's bug through unchanged.
    """
    parts = name.split(".")
    return set(parts[-2:])


def _undefined_names(test: doctest.DocTest) -> list[str]:
    """Report the undefined names across one docstring's examples."""
    # Examples in one docstring share a namespace, in doctest and for a reader working
    # through them in order, so they are checked as one unit rather than one at a time.
    source = "".join(example.source for example in test.examples)

    checker = Checker(ast.parse(source), filename=test.name, builtins=_permitted_names(test.name))
    return [str(message) for message in checker.messages if isinstance(message, UndefinedName)]


@pytest.mark.parametrize("test", _doctests(), ids=lambda test: test.name)
def test_examples_reference_no_undefined_names(test: doctest.DocTest) -> None:
    """Assert every name an example uses is defined, imported, or the documented object."""
    undefined = _undefined_names(test)
    assert not undefined, "\n".join(undefined)


def test_the_check_sees_inside_a_def_body() -> None:
    """Assert this gate catches the shape it exists for, which #236 fixed by hand.

    Without this, the gate can be quietly neutered -- widen `_permitted_names` to the
    module namespace and every assertion above still passes, because the undefined name in
    the real bug was itself a module-level fixture.
    """
    docstring = """Create a fixture.

    Examples:
        >>> alembic = create_alembic_fixture()
        >>>
        >>> def test_upgrade(alembic):
        ...     alembic_runner.migrate_up_one()
    """
    test = doctest.DocTestParser().get_doctest(docstring, {}, "create_alembic_fixture", None, 0)

    assert [message.split(": ", 1)[1] for message in _undefined_names(test)] == [
        "undefined name 'alembic_runner'"
    ]
