from unittest import mock

import pytest

from pytest_alembic.plugin.plugin import OptionResolver, parse_test_names, PytestAlembicPlugin

pytest_options = (
    "--test-alembic",
    "--alembic-tests-path",
    "conftest.py",
    "-vv",
)


def test_parse_raw_test_names_empty_skips() -> None:
    result = sorted(parse_test_names("up_down_consistency,foo\n\n\nbar\n"))

    expected_result = ["bar", "foo", "up_down_consistency"]
    assert expected_result == result


class Test__collect_test_definitions:
    def test_default_only(self) -> None:
        collector = OptionResolver.collect_test_definitions(default=True, experimental=False)

        assert sorted(collector.available_tests) == [
            "model_definitions_match_ddl",
            "single_head_revision",
            "up_down_consistency",
            "upgrade",
        ]

    def test_experimental_only(self) -> None:
        # `default=False` must actually exclude the default group. `pytest_addoption`
        # relies on this to describe `pytest_alembic_include_experimental`, so a
        # regression here silently advertises non-experimental tests as experimental.
        collector = OptionResolver.collect_test_definitions(default=False, experimental=True)

        assert sorted(collector.available_tests) == [
            "all_models_register_on_metadata",
            "downgrade_leaves_no_trace",
        ]

    def test_both_groups(self) -> None:
        collector = OptionResolver.collect_test_definitions(default=True, experimental=True)

        assert sorted(collector.available_tests) == [
            "all_models_register_on_metadata",
            "downgrade_leaves_no_trace",
            "model_definitions_match_ddl",
            "single_head_revision",
            "up_down_consistency",
            "upgrade",
        ]

    def test_neither_group(self) -> None:
        collector = OptionResolver.collect_test_definitions(default=False, experimental=False)

        assert collector.available_tests == {}


class Test__OptionResolver:
    def test_all_enabled(self) -> None:
        test_collector = OptionResolver.collect_test_definitions()
        result = [t.name for t in test_collector.tests()]

        expected_result = [
            "model_definitions_match_ddl",
            "single_head_revision",
            "up_down_consistency",
            "upgrade",
        ]
        assert expected_result == result

    def test_include_specified_invalid(self) -> None:
        test_collector = OptionResolver.collect_test_definitions()
        test_collector.include("foo", "bar")

        with pytest.raises(ValueError, match="bar, foo"):
            test_collector.tests()

    def test_include_specified(self) -> None:
        test_collector = OptionResolver.collect_test_definitions()
        test_collector.include("single_head_revision", "upgrade")

        result = [t.name for t in test_collector.tests()]

        expected_result = ["single_head_revision", "upgrade"]
        assert expected_result == result

    def test_exclude_specified_invalid(self) -> None:
        test_collector = OptionResolver.collect_test_definitions()
        test_collector.exclude("foo", "bar")

        with pytest.raises(ValueError, match="bar, foo"):
            test_collector.tests()

    def test_exclude_specified(self) -> None:
        test_collector = OptionResolver.collect_test_definitions()
        test_collector.exclude("single_head_revision", "upgrade")

        result = [t.name for t in test_collector.tests()]

        expected_result = [
            "model_definitions_match_ddl",
            "up_down_consistency",
        ]
        assert expected_result == result

    def test_include_experimental(self) -> None:
        test_collector = OptionResolver.collect_test_definitions().include_experimental(
            "all_models_register_on_metadata"
        )
        test_collector.exclude("single_head_revision", "upgrade")

        result = [t.name for t in test_collector.tests()]

        expected_result = [
            "model_definitions_match_ddl",
            "up_down_consistency",
            "all_models_register_on_metadata",
        ]
        assert expected_result == result


class Test_collect_tests:
    def test_disabled_cli(self, testdir: pytest.Testdir) -> None:
        testdir.copy_example("test_no_data")
        result = testdir.runpytest("-vv")
        stdout = result.stdout.str()
        print(stdout)

        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_include_cfg(self, testdir: pytest.Testdir) -> None:
        testdir.copy_example("test_no_data")
        testdir.makefile(".ini", pytest="[pytest]\npytest_alembic_include=single_head_revision\n")
        result = testdir.runpytest(*pytest_options)
        stdout = result.stdout.str()
        print(stdout)

        assert result.ret == 0
        assert "1 passed" in stdout

    def test_exclude_cfg(self, testdir: pytest.Testdir) -> None:
        testdir.copy_example("test_no_data")
        testdir.makefile(".ini", pytest="[pytest]\npytest_alembic_exclude=single_head_revision\n")
        result = testdir.runpytest(*pytest_options)
        stdout = result.stdout.str()
        print(stdout)

        assert result.ret == 0
        assert "3 passed" in stdout

    def test_included_tests_start_with_tests(self, testdir: pytest.Testdir) -> None:
        testdir.copy_example("test_no_data")
        result = testdir.runpytest(*pytest_options)
        stdout = result.stdout.str()
        print(stdout)

        assert result.ret == 0
        tests = [
            "test_model_definitions_match_ddl",
            "test_single_head_revision",
            "test_up_down_consistency",
            "test_upgrade",
        ]
        for test in tests:
            assert f"::pytest-alembic::{test}" in stdout
        assert "4 passed" in stdout


class Test__chained_options:
    """The `include`/`exclude` methods accumulate rather than replace.

    Each starts its list at `None` -- "not specified", which is meaningfully different
    from "specified as nothing" -- and only allocates on the first call. Applying the
    same option twice is what exercises the already-allocated path.
    """

    def test_include_accumulates(self) -> None:
        collector = OptionResolver.collect_test_definitions()
        collector.include("upgrade").include("single_head_revision")

        assert collector.included_tests == ["upgrade", "single_head_revision"]

    def test_include_experimental_accumulates(self) -> None:
        collector = OptionResolver.collect_test_definitions()
        collector.include_experimental("downgrade_leaves_no_trace")
        collector.include_experimental("all_models_register_on_metadata")

        assert collector.included_experimental_tests == [
            "downgrade_leaves_no_trace",
            "all_models_register_on_metadata",
        ]

    def test_exclude_accumulates(self) -> None:
        collector = OptionResolver.collect_test_definitions()
        collector.exclude("upgrade").exclude("single_head_revision")

        assert collector.excluded_tests == ["upgrade", "single_head_revision"]


class Test_pytest_itemcollected:
    def test_item_without_fixtures_is_ignored(self, pytestconfig: pytest.Config) -> None:
        """Assert a collected node carrying no fixtures is left alone.

        `pytest_itemcollected` sees every collected item, including nodes which are not
        function items and so have no `fixturenames` at all.
        """
        plugin = PytestAlembicPlugin(pytestconfig)

        item = mock.Mock()
        del item.fixturenames

        plugin.pytest_itemcollected(item)

        item.add_marker.assert_not_called()
