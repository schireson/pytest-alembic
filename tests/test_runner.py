import pytest


def run_pytest(pytester, *, success=True, passed=4, skipped=0, failed=0, test_alembic=True):
    args = [
        "--test-alembic",
        "-vv",
    ]
    if not test_alembic:
        args = ["-vv", "conftest.py"]

    pytester.copy_example()
    result = pytester.inline_run(*args)

    expected_return = (
        (pytest.ExitCode.OK if passed or skipped or failed else pytest.ExitCode.NO_TESTS_COLLECTED)
        if success
        else pytest.ExitCode.TESTS_FAILED
    )
    assert result.ret == expected_return

    result.assertoutcome(passed=passed, skipped=skipped, failed=failed)
    return result


def assert_has_test(result, test_name: str):
    report = result.matchreport(test_name)
    assert report is not None


def assert_failed_test_has_content(result, *, test: str, content: str):
    report = result.matchreport(test)
    if hasattr(report.longrepr, "exce"):
        assert content in str(report.longrepr.exce)
    else:
        assert content in str(report.longrepr)


def test_no_data(pytester):
    run_pytest(pytester)


def test_empty_history(pytester):
    run_pytest(pytester, passed=5)


def test_alternative_script_location(pytester):
    run_pytest(pytester)


def test_manual_alembic_config(pytester):
    run_pytest(pytester)


def test_default_script_location(pytester):
    run_pytest(pytester)


def test_basic_revision_upgrade_data(pytester):
    run_pytest(pytester)


def test_complex_revision_upgrade_data(pytester):
    run_pytest(pytester)


def test_multiple_schemata(pytester):
    """Assert support for multi-history projects.

    Given the way pytest fixtures and test collection seem to work, for this
    test, we cannot automatically collect the tests and run them against a given
    "runner" fixture. Therefore, we wont use the "--test-alembic" flag.
    """
    run_pytest(pytester, passed=8, test_alembic=False)


def test_schema_revision_data(pytester):
    """Assert that revision data handles schema names included in the table name."""
    run_pytest(pytester, passed=3)


def test_branched_history(pytester):
    """Branched history can be navigated, when there's no mergepoint present."""
    run_pytest(pytester, passed=4)


def test_branched_history_with_mergepoint(pytester):
    """Branched history can be navigated, when there's a mergepoint present."""
    run_pytest(pytester, passed=5)


def test_migrate_up_to(pytester):
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_migrate_up_to_specific_revision")


def test_migrate_up_before(pytester):
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_migrate_up_before_specific_revision")


def test_migrate_down_before(pytester):
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_migrate_down_before_specific_revision")


def test_process_revision_directives(pytester):
    result = run_pytest(pytester, success=False, passed=3, failed=1)
    assert_failed_test_has_content(
        result, test="test_model_definitions_match_ddl", content="Exception: foo"
    )


def test_experimental_all_models_register(pytester):
    """Assert the all-models-register test works when loading from a Base directly."""
    result = run_pytest(pytester, passed=1, test_alembic=False)
    assert_has_test(result, "test_all_models_register_on_metadata")


def test_experimental_all_models_register_metadata(pytester):
    """Assert the all-models-register test works when loading from a metadata directly."""
    result = run_pytest(pytester, passed=1, test_alembic=False)
    assert_has_test(result, "test_all_models_register_on_metadata")


def test_experimental_all_models_register_failure(pytester):
    """Assert the all-models-register test fails when there are missing models."""
    result = run_pytest(pytester, success=False, passed=0, failed=1, test_alembic=False)
    assert_has_test(result, "test_all_models_register_on_metadata")
    assert_failed_test_has_content(
        result, test="test_all_models_register_on_metadata", content="'models'"
    )
    assert_failed_test_has_content(
        result, test="test_all_models_register_on_metadata", content=": bar"
    )


def test_experimental_all_models_register_no_metadata(pytester):
    """Assert the all-models-register test fails when there is no metadata in-context."""
    result = run_pytest(pytester, success=False, passed=0, failed=1, test_alembic=False)
    assert_failed_test_has_content(
        result, test="test_all_models_register_on_metadata", content="Unable to locate a MetaData"
    )


def test_experimental_all_models_register_automatic(pytester):
    """Assert the all-models-register test is collected when included through automatic test insertion.

    I.e. through use of pytest_alembic_include_experimental, rather than a manually
    written test.
    """
    result = run_pytest(pytester, passed=5, test_alembic=True)
    assert_has_test(result, "test_all_models_register_on_metadata")


def test_consistency_doesnt_roundtrip(pytester):
    """Assert a up/down consistency fails if a migration cannot rountrip up -> down -> up."""
    result = run_pytest(pytester, success=False, passed=3, failed=1)
    assert_failed_test_has_content(
        result, test="test_up_down_consistency", content="after performing a roundtrip"
    )


def test_downgrade_leaves_no_trace_success(pytester):
    """Assert the all-models-register test is collected when included through automatic test insertion.

    I.e. through use of pytest_alembic_include_experimental, rather than a manually
    written test.
    """
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_downgrade_leaves_no_trace")


def test_downgrade_leaves_no_trace_failure(pytester):
    """Assert the all-models-register test is collected when included through automatic test insertion."""
    result = run_pytest(pytester, success=False, passed=0, failed=1)
    assert_failed_test_has_content(
        result,
        test="test_downgrade_leaves_no_trace",
        content="difference between the pre-'bbbbbbbbbbbb'-upgrade `MetaData`",
    )


def test_minimum_downgrade_revision(pytester):
    """Assert the minimum_downgrade_revision config option is abided."""
    run_pytest(pytester, passed=5)


def test_unimplemented_downgrade_warning(pytester):
    """Assert `NotImplementedError` raised during downgrade passes but emits a warning."""
    result = run_pytest(pytester, passed=5)

    warnings = result.getcalls("pytest_warning_recorded")
    assert len(warnings) == 2

    for warning in warnings:
        assert warning.warning_message.category == UserWarning

        warning_str = str(warning.warning_message.message)
        assert "NotImplementedError" in warning_str
        assert "minimum_downgrade_revision" in warning_str


def test_failing_downgrade(pytester):
    """Assert failing downgrade, fails test."""
    result = run_pytest(pytester, passed=3, failed=2, success=False)
    assert_failed_test_has_content(
        result,
        test="test_up_down_consistency",
        content="Failed to downgrade through each revision",
    )
    assert_failed_test_has_content(
        result,
        test="test_downgrade_leaves_no_trace",
        content="Something went wrong",
    )
