from pytest_alembic.config import Config
from pytest_alembic.revision_data import RevisionData, RevisionSpec


def test_from_config_empty() -> None:
    config = Config()
    RevisionData.from_config(config)


def test_from_config_empty_data() -> None:
    config = Config({"before_revision_data": {}, "at_revision_data": {}})
    RevisionData.from_config(config)


def test_revision_spec_input() -> None:
    """Assert an already-parsed `RevisionSpec` is accepted as configuration.

    Passed as the dataclass fields rather than inside `config_options`: the first
    positional argument of `Config` is `config_options`, so keys placed there never
    reach `before_revision_data`/`at_revision_data` at all.
    """
    before = RevisionSpec({"foo": {"id": 1}})
    at = RevisionSpec({"bar": {"id": 2}})
    config = Config(before_revision_data=before, at_revision_data=at)

    revision_data = RevisionData.from_config(config)

    # `RevisionSpec.parse` hands back the very object it was given, rather than
    # re-wrapping it.
    assert revision_data.before_revision_data is before
    assert revision_data.at_revision_data is at


def test_get_before_single_item() -> None:
    rev = RevisionData(
        before_revision_data=RevisionSpec({"foo": {1: 1}}), at_revision_data=RevisionSpec({})
    )
    result = list(rev.get_before("foo"))

    expected_result = [{1: 1}]
    assert expected_result == result


def test_get_before_multiple_items() -> None:
    rev = RevisionData(
        before_revision_data=RevisionSpec({"foo": [{1: 1}, {2: 2}]}),
        at_revision_data=RevisionSpec({}),
    )
    result = list(rev.get_before("foo"))

    expected_result = [{1: 1}, {2: 2}]
    assert expected_result == result


def test_get_at_single_item() -> None:
    rev = RevisionData(
        before_revision_data=RevisionSpec({}), at_revision_data=RevisionSpec({"foo": {1: 1}})
    )
    result = list(rev.get_at("foo"))

    expected_result = [{1: 1}]
    assert expected_result == result


def test_get_at_multiple_items() -> None:
    rev = RevisionData(
        before_revision_data=RevisionSpec({}),
        at_revision_data=RevisionSpec({"foo": [{1: 1}, {2: 2}]}),
    )
    result = list(rev.get_at("foo"))

    expected_result = [{1: 1}, {2: 2}]
    assert expected_result == result
