from pytest_alembic.revision_data import RevisionData, RevisionSpec


def test_from_config_empty():
    RevisionData.from_config({})
    RevisionData.from_config({"before_revision_data": {}, "at_revision_data": {}})


def test_revision_spec_input():
    RevisionData.from_config(
        {"before_revision_data": RevisionSpec({}), "at_revision_data": RevisionSpec({})}
    )


def test_get_before_single_item():
    rev = RevisionData(before_revision_data={"foo": {1: 1}}, at_revision_data={})
    result = list(rev.get_before("foo"))

    expected_result = [{1: 1}]
    assert expected_result == result


def test_get_before_multiple_items():
    rev = RevisionData(before_revision_data={"foo": [{1: 1}, {2: 2}]}, at_revision_data={})
    result = list(rev.get_before("foo"))

    expected_result = [{1: 1}, {2: 2}]
    assert expected_result == result


def test_get_at_single_item():
    rev = RevisionData(before_revision_data={}, at_revision_data={"foo": {1: 1}})
    result = list(rev.get_at("foo"))

    expected_result = [{1: 1}]
    assert expected_result == result


def test_get_at_multiple_items():
    rev = RevisionData(before_revision_data={}, at_revision_data={"foo": [{1: 1}, {2: 2}]})
    result = list(rev.get_at("foo"))

    expected_result = [{1: 1}, {2: 2}]
    assert expected_result == result
