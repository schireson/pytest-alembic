import pytest


def run_test(testdir, test_alembic=True):
    args = ["--test-alembic", "-vv"]
    if not test_alembic:
        args = ["-vv", "conftest.py"]

    testdir.copy_example()
    result = testdir.runpytest(*args)

    stdout = result.stdout.str()
    print(stdout)
    return result, stdout


def successful_test_run(testdir, num_tests=4, test_alembic=True):
    result, stdout = run_test(testdir, test_alembic=test_alembic)

    assert result.ret == 0
    assert f"{num_tests} passed" in stdout
    return stdout


def test_no_data(testdir):
    successful_test_run(testdir)


def test_empty_history(testdir):
    successful_test_run(testdir, num_tests=3)


def test_alternative_script_location(testdir):
    successful_test_run(testdir)


def test_manual_alembic_config(testdir):
    successful_test_run(testdir)


def test_default_script_location(testdir):
    successful_test_run(testdir)


def test_basic_revision_upgrade_data(testdir):
    successful_test_run(testdir)


def test_complex_revision_upgrade_data(testdir):
    successful_test_run(testdir)


def test_multiple_schemata(testdir):
    """Assert support for multi-history projects.

    Given the way pytest fixtures and test collection seem to work, for this
    test, we cannot automatically collect the tests and run them against a given
    "runner" fixture. Therefore, we wont use the "--test-alembic" flag.
    """
    successful_test_run(testdir, num_tests=8, test_alembic=False)


def test_schema_revision_data(testdir):
    """Assert that revision data handles schema names included in the table name."""
    successful_test_run(testdir, num_tests=3)


def test_branched_history(testdir):
    """Branched history can be navigated, when there's no mergepoint present."""
    successful_test_run(testdir, num_tests=4)


def test_branched_history_with_mergepoint(testdir):
    """Branched history can be navigated, when there's a mergepoint present."""
    successful_test_run(testdir, num_tests=5)


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
