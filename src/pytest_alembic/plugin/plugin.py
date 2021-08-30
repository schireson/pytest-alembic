import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import pytest
from _pytest import fixtures

from pytest_alembic.plugin.error import AlembicReprError, AlembicTestFailure


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
class _TestCollector:
    available_tests: Dict[str, PytestAlembicTest]

    included_tests: Optional[List[str]] = None
    included_experimental_tests: Optional[List[str]] = None
    excluded_tests: Optional[List[str]] = None

    @classmethod
    def collect(cls, default=True, experimental=True):
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


def collect_tests(session, config):
    cli_enabled = config.option.pytest_alembic_enabled
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

    # The tests folder field is important because we cannot predict the test location
    # of user tests. And so if someone invokes pytest like `pytest mytests/`, the user
    # would need to attach **these** tests to the `mytests/` namespace, or else run
    # `pytest mytests tests`.
    tests_folder = config.getini("pytest_alembic_tests_folder")

    test_collector = (
        _TestCollector.collect(default=True, experimental=True)
        .include(*raw_included_tests)
        .include_experimental(*raw_experimental_included_tests)
        .exclude(*raw_excluded_tests)
    )

    result = []
    for test in test_collector.sorted_tests():
        result.append(
            PytestAlembicItem.from_parent(
                session,
                name=f"{tests_folder}::pytest_alembic::{test.raw_name}",
                test_fn=test.function,
            )
        )

    return result


class PytestAlembicItem(pytest.Item):
    """Pytest representation of each built-in test.

    Tests such as these are more complex because they are not represented in the
    users' source, which means we need to act as pytest does when producing tests
    normally.

    In particular, fixture resolution is the main complicating factor, and seemingly
    not an external detail for which pytest has an officially recommended public API.
    """

    obj = None

    @classmethod
    def from_parent(cls, parent, *, name, test_fn):
        kwargs = dict(name=name, parent=parent, nodeid=name)
        if hasattr(super(), "from_parent"):
            self = super().from_parent(**kwargs)
        else:
            self = cls(**kwargs)

        self.test_fn = test_fn
        self.funcargs = {}
        self.add_marker("alembic")
        return self

    def runtest(self):
        fm = self.session._fixturemanager
        self._fixtureinfo = fm.getfixtureinfo(node=self, func=self.test_fn, cls=None)

        try:
            # Pytest deprecated direct construction of this, but there doesn't appear to
            # be an obvious non-deprecated way to produce `pytest.Item`s (i.e. tests)
            # which fullfill fixtures depended on by this plugin.
            fixture_request = fixtures.FixtureRequest(self, _ispytest=True)
        except TypeError:
            # For backwards compatibility, attempt to make the `fixture_request` in the interface
            # shape pre pytest's addition of this warning-producing parameter.
            fixture_request = fixtures.FixtureRequest(self)
        except Exception:
            # Just to avoid a NameError in an unforeseen error constructing the `fixture_request`.
            raise NotImplementedError(
                "Failed to fill the fixtures. "
                "This is almost certainly a pytest version incompatibility, please submit a bug report!"
            )

        fixture_request._fillfixtures()

        params = {arg: self.funcargs[arg] for arg in self._fixtureinfo.argnames}

        self.test_fn(**params)

    def reportinfo(self):
        return (self.fspath, 0, f"[pytest-alembic] {self.name}")

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, AlembicTestFailure):
            return AlembicReprError(excinfo, self)
        return super().repr_failure(excinfo)
