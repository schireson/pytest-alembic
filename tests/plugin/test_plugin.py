import pytest

from pytest_alembic.plugin.plugin import _TestCollector, parse_test_names


def test_parse_raw_test_names_empty_skips():
    result = sorted(parse_test_names("up_down_consistency,foo\n\n\nbar\n"))

    expected_result = ["bar", "foo", "up_down_consistency"]
    assert expected_result == result


class Test__TestCollector:
    def test_all_enabled(self):
        test_collector = _TestCollector.collect()
        result = [t.name for t in test_collector.tests()]

        expected_result = [
            "model_definitions_match_ddl",
            "single_head_revision",
            "up_down_consistency",
            "upgrade",
        ]
        assert expected_result == result

    def test_include_specified_invalid(self):
        test_collector = _TestCollector.collect()
        test_collector.include("foo", "bar")

        with pytest.raises(ValueError) as e:
            test_collector.tests()
        assert "bar, foo" in str(e.value)

    def test_include_specified(self):
        test_collector = _TestCollector.collect()
        test_collector.include("single_head_revision", "upgrade")

        result = [t.name for t in test_collector.tests()]

        expected_result = ["single_head_revision", "upgrade"]
        assert expected_result == result

    def test_exclude_specified_invalid(self):
        test_collector = _TestCollector.collect()
        test_collector.exclude("foo", "bar")

        with pytest.raises(ValueError) as e:
            test_collector.tests()
        assert "bar, foo" in str(e.value)

    def test_exclude_specified(self):
        test_collector = _TestCollector.collect()
        test_collector.exclude("single_head_revision", "upgrade")

        result = [t.name for t in test_collector.tests()]

        expected_result = [
            "model_definitions_match_ddl",
            "up_down_consistency",
        ]
        assert expected_result == result

    def test_include_experimental(self):
        test_collector = _TestCollector.collect().include_experimental(
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
    def test_disabled_cli(self, testdir):
        testdir.copy_example("test_no_data")
        result = testdir.runpytest("-vv")
        stdout = result.stdout.str()
        print(stdout)

        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_include_cfg(self, testdir):
        testdir.copy_example("test_no_data")
        testdir.makefile(".ini", pytest="[pytest]\npytest_alembic_include=single_head_revision\n")
        result = testdir.runpytest("--test-alembic", "-vv")
        stdout = result.stdout.str()
        print(stdout)

        assert result.ret == 0
        assert "1 passed" in stdout

    def test_exclude_cfg(self, testdir):
        testdir.copy_example("test_no_data")
        testdir.makefile(".ini", pytest="[pytest]\npytest_alembic_exclude=single_head_revision\n")
        result = testdir.runpytest("--test-alembic", "-vv")
        stdout = result.stdout.str()
        print(stdout)

        assert result.ret == 0
        assert "3 passed" in stdout

    def test_included_tests_start_with_tests(self, testdir):
        testdir.copy_example("test_no_data")
        result = testdir.runpytest("--test-alembic", "-vv")
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
            assert f"tests::pytest_alembic::{test}" in stdout
        assert "4 passed" in stdout

    def test_alternative_test_folter(self, testdir):
        testdir.copy_example("test_no_data")
        testdir.makefile(".ini", pytest="[pytest]\npytest_alembic_tests_folder=foo\n")
        result = testdir.runpytest("--test-alembic", "-vv")
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
            assert f"foo::pytest_alembic::{test}" in stdout
        assert "4 passed" in stdout
