import pytest


def run_test(testdir):
    testdir.copy_example()
    result = testdir.runpytest("--test-alembic", "-vv")

    stdout = result.stdout.str()
    print(stdout)
    return result, stdout


def successful_test_run(testdir, num_tests=4):
    result, stdout = run_test(testdir)

    assert result.ret == 0
    assert f"{num_tests} passed" in stdout
    return stdout


def test_no_data(testdir):
    successful_test_run(testdir)


def test_basic_revision_upgrade_data(testdir):
    successful_test_run(testdir)


def test_complex_revision_upgrade_data(testdir):
    successful_test_run(testdir)


def test_schema_revision_data(testdir):
    """Assert that revision data handles schema names included in the table name."""
    successful_test_run(testdir, num_tests=3)


def test_migrate_up_to(testdir):
    result = successful_test_run(testdir, num_tests=5)
    assert "test_migrate_up_to_specific_revision" in result


def test_migrate_up_before(testdir):
    result = successful_test_run(testdir, num_tests=5)
    assert "test_migrate_up_before_specific_revision" in result


def test_migrate_down_before(testdir):
    result = successful_test_run(testdir, num_tests=5)
    assert "test_migrate_down_before_specific_revision" in result


def test_process_revision_directives(testdir):
    result, stdout = run_test(testdir)
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    assert "1 failed, 3 passed" in stdout
    assert "Exception: foo" in stdout
