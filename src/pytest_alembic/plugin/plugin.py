import re
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Callable, Dict, List, Optional

import pytest
from _pytest import config

from pytest_alembic.plugin.error import AlembicReprError, AlembicTestFailure

pytest_version_tuple = getattr(pytest, "version_tuple", None)


@dataclass(eq=False)
class PytestAlembicPlugin:
    config: config.Config
    registered = False

    # Some weird decisions were made by pytest it seems like. There is not an obvious
    # way to support both <7 and >=7 without weird nonsense like this.
    if pytest_version_tuple and pytest_version_tuple[0] >= 7:

        def pytest_collect_file(self, file_path, path, parent):
            if self.should_register(file_path):
                return TestCollector.from_parent(parent, path=file_path)

    else:

        def pytest_collect_file(self, path, parent):  # type: ignore
            if self.should_register(Path(path)):
                return TestCollector.from_parent(parent, fspath=path)

    def should_register(self, path):
        tests_path = PurePath(
            self.config.option.pytest_alembic_tests_path
            or self.config.getini("pytest_alembic_tests_path")
            or "tests/conftest.py"
        )
        relative_path = path.relative_to(self.config.rootpath)
        if relative_path == tests_path:
            if not self.registered:
                self.registered = True
                return True

        return False

    def pytest_itemcollected(self, item):
        """Attach a marker to each test which uses the alembic fixture."""
        if not hasattr(item, "fixturenames"):
            return

        if "alembic_runner" in item.fixturenames:
            item.add_marker("alembic")


class TestCollector(pytest.Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._nodeid += "::pytest-alembic"
        self.add_marker("alembic")

    def collect(self):
        config = self.parent.config

        cli_enabled = config.option.pytest_alembic_enabled
        if not cli_enabled:
            return None

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

        result = []
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
    def reportinfo(self):
        return (self.fspath, 0, f"[pytest-alembic] {self.name}")

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, AlembicTestFailure):
            return AlembicReprError(excinfo, self)
        return super().repr_failure(excinfo)


@dataclass(frozen=True)
class PytestAlembicTest:
    raw_name: str
    function: Callable
    is_experimental: bool

    @property
    def name(self):
        # Chop off the "test_" prefix.
        return self.raw_name[5:]


@dataclass
class OptionResolver:
    available_tests: Dict[str, PytestAlembicTest]

    included_tests: Optional[List[str]] = None
    included_experimental_tests: Optional[List[str]] = None
    excluded_tests: Optional[List[str]] = None

    @classmethod
    def collect_test_definitions(cls, default=True, experimental=True):
        import pytest_alembic.tests
        import pytest_alembic.tests.experimental

        test_groups = [(pytest_alembic.tests, False)]
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

    def include(self, *tests):
        if tests:
            if self.included_tests is None:
                self.included_tests = []

            self.included_tests.extend(tests)
        return self

    def include_experimental(self, *tests):
        if tests:
            if self.included_experimental_tests is None:
                self.included_experimental_tests = []

            self.included_experimental_tests.extend(tests)
        return self

    def exclude(self, *tests):
        if tests:
            if self.excluded_tests is None:
                self.excluded_tests = []

            self.excluded_tests.extend(tests)
        return self

    def sorted_tests(self):
        return sorted(self.tests(), key=lambda t: t.raw_name)

    def tests(self):
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
            raise ValueError(f"The following tests were unrecognized: {invalid_str}")

        return [self.available_tests[t] for t in selected_tests]


def parse_test_names(raw_test_names):
    test_names = re.split(r"[,\n]", raw_test_names)

    result = set()
    for test_name in test_names:
        test_name = test_name.strip()
        if not test_name:
            continue
        result.add(test_name)
    return result
