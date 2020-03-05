def successful_test_run(testdir):
    testdir.copy_example()
    result = testdir.runpytest("--test-alembic", "-vv")

    stdout = result.stdout.str()
    print(stdout)

    assert result.ret == 0
    assert "4 passed" in stdout


def test_no_data(testdir):
    successful_test_run(testdir)


def test_basic_revision_upgrade_data(testdir):
    successful_test_run(testdir)


def test_complex_revision_upgrade_data(testdir):
    successful_test_run(testdir)
