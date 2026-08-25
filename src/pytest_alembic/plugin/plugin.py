"""Collection machinery: how the built-in tests become pytest items.

The built-in tests are plain functions in :mod:`pytest_alembic.tests`, not files pytest
would find on its own. They are bound to a single path — ``tests/conftest.py`` by
default — chosen because that is where users define ``alembic_engine``, so the fixture
the tests need is in scope wherever they land.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any, cast

import pytest
from _pytest import config

pytest_version_tuple = getattr(pytest, "version_tuple", None)


@dataclass(eq=False)
class PytestAlembicPlugin:
    """Bind the built-in tests to exactly one collected file.

    Registered in ``pytest_sessionstart`` rather than at import time, so that disabling
    the plugin means no hooks at all. ``registered`` is instance state guarding against
    binding the tests twice if the target path is somehow collected more than once.

    Attributes:
        config: The session config, read for the tests-path option and ``rootpath``.
        registered: Whether the built-in tests have already been bound.
    """

    config: config.Config
    registered = False

    # Some weird decisions were made by pytest it seems like. There is not an obvious
    # way to support both <7 and >=7 without weird nonsense like this.
    #
    # Excluded from coverage, on the whole construct: exactly one of these three
    # variants is defined in any given interpreter, so no single run can execute the
    # other two. The CI matrix runs both pytest 7 and pytest 8, and each entry enforces
    # the coverage floor on its own, so a run that covered them all does not exist. The
    # bodies are three lines of identical logic behind three different signatures; what
    # they do is exercised through the pytester-based tests either way.
    if pytest_version_tuple and pytest_version_tuple >= (8, 1, 0):  # pragma: no cover

        def pytest_collect_file(
            self, file_path: Path, parent: pytest.Collector
        ) -> "TestCollector | None":
            """Collect the built-in tests at *file_path* (pytest >= 8.1 signature)."""
            if self.should_register(file_path):
                return TestCollector.from_parent(parent, path=file_path)
            return None

    elif pytest_version_tuple and pytest_version_tuple[0] >= 7:  # pragma: no cover

        def pytest_collect_file(  # type: ignore[misc]
            self,
            file_path: Path,
            path: Any,  # noqa: ARG002
            parent: pytest.Collector,
        ) -> "TestCollector | None":
            """Collect the built-in tests at *file_path* (pytest 7 signature).

            ``path`` is accepted and ignored: pytest 7 passes both the legacy ``py.path``
            and the new ``pathlib`` argument.
            """
            if self.should_register(file_path):
                return TestCollector.from_parent(parent, path=file_path)
            return None

    else:  # pragma: no cover

        def pytest_collect_file(  # type: ignore[misc]
            self, path: Any, parent: pytest.Collector
        ) -> "TestCollector | None":
            """Collect the built-in tests at *path* (pytest < 7 signature)."""
            if self.should_register(Path(path)):
                return TestCollector.from_parent(parent, fspath=path)
            return None

    def should_register(self, path: PurePath) -> bool:
        """Report whether *path* is the one file the built-in tests should bind to.

        Precedence is command line, then ini, then ``tests/conftest.py``. The comparison
        is against the path relative to ``rootpath``, so the configured value is written
        the same way regardless of where pytest was invoked from.

        Returns ``True`` at most once per session; every later call returns ``False``.

        Args:
            path: The path pytest is currently offering for collection.
        """
        tests_path = PurePath(
            cast("str | None", self.config.option.pytest_alembic_tests_path)
            or cast("str | None", self.config.getini("pytest_alembic_tests_path"))
            or "tests/conftest.py"
        )
        relative_path = path.relative_to(self.config.rootpath)
        if relative_path == tests_path and not self.registered:
            self.registered = True
            return True

        return False

    def pytest_itemcollected(self, item: pytest.Item) -> None:
        """Attach a marker to each test which uses the alembic fixture."""
        if not hasattr(item, "fixturenames"):
            return

        if "alembic_runner" in item.fixturenames:
            item.add_marker("alembic")


class TestCollector(pytest.Module):
    """The synthetic module node under which the built-in tests are collected.

    Presents as a :class:`pytest.Module` so the built-in tests get the same fixture
    resolution and reporting as any other test module, even though no such module
    exists on disk.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Suffix the node id and mark every test below it as ``alembic``."""
        super().__init__(**kwargs)
        self._nodeid += "::pytest-alembic"
        self.add_marker("alembic")

    def collect(self) -> list[pytest.Item]:
        """Resolve which built-in tests are enabled and return them as pytest items.

        Returns an empty list unless ``--test-alembic`` was passed, so merely being
        bound to a path is not enough to run the built-in tests.
        """
        assert self.parent
        config = self.parent.config

        cli_enabled = config.option.pytest_alembic_registration_enabled
        if not cli_enabled:
            return []

        option = config.option

        raw_included_tests = parse_test_names(config.getini("pytest_alembic_include"))
        raw_experimental_included_tests = parse_test_names(
            config.getini("pytest_alembic_include_experimental")
        )
        raw_excluded_tests = parse_test_names(
            option.pytest_alembic_exclude or config.getini("pytest_alembic_exclude")
        )

        test_collector = (
            OptionResolver.collect_test_definitions(default=True, experimental=True)
            .include(*raw_included_tests)
            .include_experimental(*raw_experimental_included_tests)
            .exclude(*raw_excluded_tests)
        )

        result: list[pytest.Item] = []
        for test in test_collector.sorted_tests():
            name = test.raw_name
            self.ihook.pytest_pycollect_makeitem(collector=self, name=name, obj=test)
            result.append(
                PytestAlembicItem.from_parent(
                    self,
                    name=name,
                    callobj=test.function,
                )
            )
        return result


class PytestAlembicItem(pytest.Function):
    """A single built-in test, reported under a ``[pytest-alembic]`` label."""

    def reportinfo(self) -> tuple[Any, int, str]:
        """Report line 0 of the bound file, since these tests have no source location."""
        return (self.fspath, 0, f"[pytest-alembic] {self.name}")


@dataclass(frozen=True)
class PytestAlembicTest:
    """One built-in test function, paired with how it is opted into.

    Attributes:
        raw_name: The function name as defined, including the ``test_`` prefix.
        function: The test function itself.
        is_experimental: Whether the test must be included explicitly.
    """

    raw_name: str
    function: Callable
    is_experimental: bool

    @property
    def name(self) -> str:
        """The name used in options and reports, without the ``test_`` prefix.

        Examples:
            >>> PytestAlembicTest("test_upgrade", lambda: None, False).name
            'upgrade'
        """
        # Chop off the "test_" prefix.
        return self.raw_name[5:]


@dataclass
class OptionResolver:
    """Resolve the include/exclude options into the set of tests to run.

    The ``include*``/``exclude`` methods return ``self`` so the options can be applied
    in one chained expression, in whatever order they were read. Resolution is deferred
    to :meth:`tests`, because an unrecognised name can only be detected once every
    option has been collected.

    ``None`` and empty are deliberately different for ``included_tests``: ``None`` means
    "not specified, so use the defaults", while empty means "specified as nothing".

    Attributes:
        available_tests: Every collected test, keyed by prefix-stripped name.
        included_tests: Explicitly included default tests, or ``None``.
        included_experimental_tests: Explicitly included experimental tests, or ``None``.
        excluded_tests: Explicitly excluded tests, or ``None``.
    """

    available_tests: dict[str, PytestAlembicTest]

    included_tests: list[str] | None = None
    included_experimental_tests: list[str] | None = None
    excluded_tests: list[str] | None = None

    @classmethod
    def collect_test_definitions(
        cls,
        *,
        default: bool = True,
        experimental: bool = True,
    ) -> "OptionResolver":
        """Collect the built-in test functions into a new resolver.

        Discovery is by naming convention: any ``test_``-prefixed attribute of
        :mod:`pytest_alembic.tests` or its ``experimental`` submodule. See the comment
        below for why the imports stay function-local.

        Args:
            default: Whether to collect the stable built-in tests.
            experimental: Whether to collect the experimental tests.
        """
        # Imported here rather than at module scope to contain the blast radius of a
        # broken alembic. This module is reached from `pytest_alembic.plugin`, the
        # pytest11 entry point, so it loads during pytest startup for every project
        # that merely has pytest-alembic installed. The test modules below import
        # private alembic APIs -- `alembic.autogenerate.render._render_cmd_body` in
        # tests/default.py -- and an alembic release that moves one would then break
        # `pytest` itself everywhere, rather than only for people who actually use
        # these tests.
        #
        # Note this placement is *not* required to avoid an import cycle. There is a
        # cycle in the graph (plugin.plugin -> tests -> plugin.error), but it is
        # benign: plugin/error.py imports only textwrap and typing, so it never needs
        # a partially-initialised module. Hoisting these two imports leaves the whole
        # suite green -- the reason to keep them here is the blast radius above.
        import pytest_alembic.tests
        import pytest_alembic.tests.experimental

        test_groups = []
        if default:
            test_groups.append((pytest_alembic.tests, False))
        if experimental:
            test_groups.append((pytest_alembic.tests.experimental, True))

        all_tests = {}
        for test_group, is_experimental in test_groups:
            for name in dir(test_group):
                if name.startswith("test_"):
                    pytest_alembic_test = PytestAlembicTest(
                        name, getattr(test_group, name), is_experimental
                    )
                    all_tests[pytest_alembic_test.name] = pytest_alembic_test

        return cls(all_tests)

    def include(self, *tests: str) -> "OptionResolver":
        """Add *tests* to the explicit include list, and return ``self`` for chaining.

        Specifying any include is what suppresses the default selection, so an empty
        call is a no-op rather than a way to select nothing.
        """
        if tests:
            if self.included_tests is None:
                self.included_tests = []

            self.included_tests.extend(tests)
        return self

    def include_experimental(self, *tests: str) -> "OptionResolver":
        """Add experimental *tests* to the include list, and return ``self``.

        Tracked separately from :meth:`include` because experimental tests are never
        selected by default.
        """
        if tests:
            if self.included_experimental_tests is None:
                self.included_experimental_tests = []

            self.included_experimental_tests.extend(tests)
        return self

    def exclude(self, *tests: str) -> "OptionResolver":
        """Add *tests* to the exclude list, and return ``self`` for chaining.

        Exclusions are applied after inclusions, so naming a test in both drops it.
        """
        if tests:
            if self.excluded_tests is None:
                self.excluded_tests = []

            self.excluded_tests.extend(tests)
        return self

    def sorted_tests(self) -> list[PytestAlembicTest]:
        """The resolved tests in a stable order, so collection order is reproducible."""
        return sorted(self.tests(), key=lambda t: t.raw_name)

    def tests(self) -> list[PytestAlembicTest]:
        """Resolve the options into the selected tests.

        Every unrecognised name is gathered before raising, so a typo in one option does
        not hide a typo in another.

        Raises:
            ValueError: If any included or excluded name is not a known test.
        """
        selected_tests = []
        invalid_tests = []

        excluded_set = set(self.excluded_tests or [])
        for excluded_test in excluded_set:
            if excluded_test not in self.available_tests:
                invalid_tests.append(excluded_test)

        if self.included_tests is None:
            included_tests = [
                t.name for t in self.available_tests.values() if t.is_experimental is False
            ]
        else:
            included_tests = self.included_tests

        for test_group in [included_tests, self.included_experimental_tests or []]:
            for included_test in test_group:
                if included_test in excluded_set:
                    continue

                if included_test not in self.available_tests:
                    invalid_tests.append(included_test)
                    continue

                selected_tests.append(included_test)

        if invalid_tests:
            invalid_str = ", ".join(sorted(invalid_tests))
            message = f"The following tests were unrecognized: {invalid_str}"
            raise ValueError(message)

        return [self.available_tests[t] for t in selected_tests]


def parse_test_names(raw_test_names: str) -> set[str]:
    r"""Split a comma- or newline-separated option value into a set of test names.

    Both separators are accepted because pytest ini values are commonly written across
    several lines, while command-line values are comma-separated. Blank entries are
    dropped, so trailing separators and indentation are harmless.

    Args:
        raw_test_names: The raw option value.

    Examples:
        >>> sorted(parse_test_names("upgrade, single_head_revision"))
        ['single_head_revision', 'upgrade']

        >>> sorted(parse_test_names("upgrade,\n  single_head_revision,\n"))
        ['single_head_revision', 'upgrade']

        >>> parse_test_names("")
        set()
    """
    test_names = re.split(r"[,\n]", raw_test_names)

    result = set()
    for test_name in test_names:
        test_name = test_name.strip()
        if not test_name:
            continue
        result.add(test_name)
    return result
