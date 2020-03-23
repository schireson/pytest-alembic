import pytest
from pytest_alembic.plugin.plugin import parse_raw_test_names, enabled_test_names


def test_parse_raw_test_names_empty_skips():
    result = parse_raw_test_names("up_down_consistency,foo\n\n\nbar\n")

    expected_result = ["up_down_consistency", "foo", "bar"]
    assert expected_result == result


class Test_enabled_test_names:
    def test_all_enabled(self):
        result = enabled_test_names({"foo", "bar", "baz"})

        expected_result = {"foo", "bar", "baz"}
        assert expected_result == result

    def test_include_specified_invalid(self):
        with pytest.raises(ValueError) as e:
            enabled_test_names({"foo", "bar", "baz"}, "what,the")
        assert "the, what" in str(e.value)

    def test_include_specified(self):
        result = enabled_test_names({"foo", "bar", "baz"}, "bar,baz")

        expected_result = {"bar", "baz"}
        assert expected_result == result

    def test_exclude_specified_invalid(self):
        with pytest.raises(ValueError) as e:
            enabled_test_names({"foo", "bar", "baz"}, None, "what,the")
        assert "the, what" in str(e.value)

    def test_exclude_specified(self):
        result = enabled_test_names({"foo", "bar", "baz"}, None, "bar,baz")

        expected_result = {"foo"}
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
