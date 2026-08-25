import pytest

from tests import requires_asyncio_support


def run_pytest(
    pytester: pytest.Pytester,
    *,
    success: bool = True,
    passed: int = 4,
    skipped: int = 0,
    failed: int = 0,
    test_alembic: bool = True,
    args: list[str] | None = None,
) -> pytest.HookRecorder:
    if not args:
        args = [
            "--test-alembic",
            "--alembic-tests-path",
            "conftest.py",
            "-vv",
            "-s",
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


def assert_has_test(result: pytest.HookRecorder, test_name: str) -> None:
    report = result.matchreport(test_name)
    assert report is not None


def assert_failed_test_has_content(result: pytest.HookRecorder, *, test: str, content: str) -> None:
    report = result.matchreport(test)
    # `AlembicTestFailure` carries its own rendered context on `exce`; anything else
    # reports through the plain longrepr.
    exce = getattr(report.longrepr, "exce", None)
    if exce is not None:
        assert content in str(exce)
    else:
        assert content in str(report.longrepr)


def test_no_data(pytester: pytest.Pytester) -> None:
    run_pytest(pytester)


def test_empty_history(pytester: pytest.Pytester) -> None:
    run_pytest(pytester, passed=5)


def test_alternative_script_location(pytester: pytest.Pytester) -> None:
    run_pytest(pytester)


def test_manual_alembic_config(pytester: pytest.Pytester) -> None:
    run_pytest(pytester)


def test_default_script_location(pytester: pytest.Pytester) -> None:
    run_pytest(pytester)


def test_basic_revision_upgrade_data(pytester: pytest.Pytester) -> None:
    run_pytest(pytester)


def test_complex_revision_upgrade_data(pytester: pytest.Pytester) -> None:
    run_pytest(pytester)


def test_multiple_schemata(pytester: pytest.Pytester) -> None:
    """Assert support for multi-history projects.

    Given the way pytest fixtures and test collection seem to work, for this
    test, we cannot automatically collect the tests and run them against a given
    "runner" fixture. Therefore, we won't use the "--test-alembic" flag.
    """
    run_pytest(pytester, passed=8, test_alembic=False)


def test_schema_revision_data(pytester: pytest.Pytester) -> None:
    """Assert that revision data handles schema names included in the table name."""
    run_pytest(pytester, passed=3)


def test_branched_history(pytester: pytest.Pytester) -> None:
    """Branched history can be navigated, when there's no mergepoint present."""
    run_pytest(pytester, passed=4)


def test_branched_history_with_mergepoint(pytester: pytest.Pytester) -> None:
    """Branched history can be navigated, when there's a mergepoint present."""
    run_pytest(pytester, passed=5)


def test_ambiguous_downgrade_history(pytester: pytest.Pytester) -> None:
    """Branched history with ambiguous relative downgrades runs through default tests."""
    run_pytest(pytester, passed=4)


def test_migrate_up_to(pytester: pytest.Pytester) -> None:
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_migrate_up_to_specific_revision")


def test_migrate_up_before(pytester: pytest.Pytester) -> None:
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_migrate_up_before_specific_revision")


def test_migrate_down_before(pytester: pytest.Pytester) -> None:
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_migrate_down_before_specific_revision")


def test_process_revision_directives(pytester: pytest.Pytester) -> None:
    result = run_pytest(pytester, success=False, passed=3, failed=1)
    assert_failed_test_has_content(
        result, test="test_model_definitions_match_ddl", content="Exception: foo"
    )


def test_experimental_all_models_register(pytester: pytest.Pytester) -> None:
    """Assert the all-models-register test works when loading from a Base directly."""
    result = run_pytest(pytester, passed=1, test_alembic=False)
    assert_has_test(result, "test_all_models_register_on_metadata")


def test_experimental_all_models_register_metadata(pytester: pytest.Pytester) -> None:
    """Assert the all-models-register test works when loading from a metadata directly."""
    result = run_pytest(pytester, passed=1, test_alembic=False)
    assert_has_test(result, "test_all_models_register_on_metadata")


def test_experimental_all_models_register_failure(pytester: pytest.Pytester) -> None:
    """Assert the all-models-register test fails when there are missing models."""
    result = run_pytest(pytester, success=False, passed=0, failed=1, test_alembic=False)
    assert_has_test(result, "test_all_models_register_on_metadata")
    assert_failed_test_has_content(
        result, test="test_all_models_register_on_metadata", content="'models'"
    )
    assert_failed_test_has_content(
        result, test="test_all_models_register_on_metadata", content=": bar"
    )


def test_experimental_all_models_register_no_metadata(pytester: pytest.Pytester) -> None:
    """Assert the all-models-register test fails when there is no metadata in-context."""
    result = run_pytest(pytester, success=False, passed=0, failed=1, test_alembic=False)
    assert_failed_test_has_content(
        result,
        test="test_all_models_register_on_metadata",
        content="Unable to locate a MetaData",
    )


def test_experimental_all_models_register_automatic(pytester: pytest.Pytester) -> None:
    """Assert the all-models-register test is collected when included through automatic test insertion.

    I.e. through use of pytest_alembic_include_experimental, rather than a manually
    written test.
    """
    result = run_pytest(pytester, passed=5, test_alembic=True)
    assert_has_test(result, "test_all_models_register_on_metadata")


def test_consistency_doesnt_roundtrip(pytester: pytest.Pytester) -> None:
    """Assert a up/down consistency fails if a migration cannot rountrip up -> down -> up."""
    result = run_pytest(pytester, success=False, passed=3, failed=1)
    assert_failed_test_has_content(
        result, test="test_up_down_consistency", content="after performing a roundtrip"
    )


def test_downgrade_leaves_no_trace_success(pytester: pytest.Pytester) -> None:
    """Assert the all-models-register test is collected when included through automatic test insertion.

    I.e. through use of pytest_alembic_include_experimental, rather than a manually
    written test.
    """
    result = run_pytest(pytester, passed=5)
    assert_has_test(result, "test_downgrade_leaves_no_trace")


def test_downgrade_leaves_no_trace_failure(pytester: pytest.Pytester) -> None:
    """Assert the all-models-register test is collected when included through automatic test insertion."""
    result = run_pytest(pytester, success=False, passed=0, failed=1)
    assert_failed_test_has_content(
        result,
        test="test_downgrade_leaves_no_trace",
        content="difference between the pre-'bbbbbbbbbbbb'-upgrade `MetaData`",
    )


def test_minimum_downgrade_revision(pytester: pytest.Pytester) -> None:
    """Assert the minimum_downgrade_revision config option is abided."""
    run_pytest(pytester, passed=5)


def test_unimplemented_downgrade_warning(pytester: pytest.Pytester) -> None:
    """Assert `NotImplementedError` raised during downgrade passes but emits a warning."""
    result = run_pytest(pytester, passed=5)

    warnings = result.getcalls("pytest_warning_recorded")
    assert len(warnings) == 2

    for warning in warnings:
        assert warning.warning_message.category is UserWarning

        warning_str = str(warning.warning_message.message)
        assert "NotImplementedError" in warning_str
        assert "minimum_downgrade_revision" in warning_str


def test_failing_downgrade(pytester: pytest.Pytester) -> None:
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


@requires_asyncio_support
def test_async_sqlalchemy(pytester: pytest.Pytester) -> None:
    """Assert pytest-alembic works with async manually adapted sqlalchemy engine."""
    run_pytest(pytester, passed=4)


@requires_asyncio_support
def test_async_sqlalchemy_native(pytester: pytest.Pytester) -> None:
    """Assert pytest-alembic works with native async sqlalchemy engine.

    Additionally includes the experimental tests which perform in-test data
    insertion, to ensure the whole plugin API works with asyncio.
    """
    run_pytest(pytester, passed=6)


@requires_asyncio_support
def test_experimental_all_models_register_async(pytester: pytest.Pytester) -> None:
    """Assert all_models_register_on_metadata runs with async_ param."""
    run_pytest(pytester, passed=1, test_alembic=False)


def test_experimental_all_models_register_offline(pytester: pytest.Pytester) -> None:
    """Assert all_models_register_on_metadata runs with offline param."""
    run_pytest(pytester, passed=1, test_alembic=False)


def test_experimental_all_models_register_namespace_package(pytester: pytest.Pytester) -> None:
    """Assert all_models_register_on_metadata with namespace packages."""
    pytester.syspathinsert(pytester.path)
    run_pytest(pytester, passed=5)


def test_generate_revision(pytester: pytest.Pytester) -> None:
    """Assert history is refreshed when generating a revision in a test."""
    run_pytest(pytester, passed=3)


def test_skip_revision(pytester: pytest.Pytester) -> None:
    """Assert a revision can be skipped through configuring the "skip_revisions" config."""
    run_pytest(pytester, passed=4)


def test_pytest_alembic_tests_path(pytester: pytest.Pytester) -> None:
    """Assert the pytest_alembic_tests_path can be overridden."""
    run_pytest(pytester, passed=4, args=["-vv", "--test-alembic", "tests_"])


def test_version_table_schema(pytester: pytest.Pytester) -> None:
    """Assert the setting the version_table_schema option functions correctly."""
    run_pytest(pytester, passed=5)


def test_branched_history_before_upgrade_data(pytester: pytest.Pytester) -> None:
    """Assert branched upgrade data is only inserted once per migration."""
    run_pytest(pytester, passed=4)


def test_multiple_heads(pytester: pytest.Pytester) -> None:
    """Assert `single_head_revision` fails, and reports the heads, when history has diverged."""
    result = run_pytest(pytester, success=False, passed=0, failed=1)
    assert_failed_test_has_content(
        result, test="test_single_head_revision", content="Expected 1 head revision, found 2"
    )
    assert_failed_test_has_content(result, test="test_single_head_revision", content="Heads")


def test_model_definitions_out_of_sync(pytester: pytest.Pytester) -> None:
    """Assert `model_definitions_match_ddl` fails, and renders the diff, when models drift."""
    result = run_pytest(pytester, success=False, passed=2, failed=1)
    assert_failed_test_has_content(
        result,
        test="test_model_definitions_match_ddl",
        content="out of sync with the set of",
    )
    assert_failed_test_has_content(
        result,
        test="test_model_definitions_match_ddl",
        content="create_table",
    )


def test_failing_upgrade(pytester: pytest.Pytester) -> None:
    """Assert a migration failing on upgrade is reported per-revision by up/down consistency."""
    result = run_pytest(pytester, success=False, passed=1, failed=3)
    assert_failed_test_has_content(
        result,
        test="test_up_down_consistency",
        content="Failed to upgrade through each revision individually",
    )
    assert_failed_test_has_content(result, test="test_up_down_consistency", content="bbbbbbbbbbbb")
