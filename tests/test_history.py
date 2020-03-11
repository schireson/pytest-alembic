import pytest

from pytest_alembic.history import AlembicHistory


def test_parse_head_revision():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))

    expected_result = ["base", "bar", "bax", "baz", "head"]
    assert alembic_history.revisions == expected_result


def test_parse_head_skip_invalid():
    alembic_history = AlembicHistory.parse(("bax -> baz,", "wtf", "<base> -> bax,"))

    expected_result = ["base", "bax", "baz", "head"]
    assert alembic_history.revisions == expected_result


def test_validate_revision():
    alembic_history = AlembicHistory.parse(("bax -> baz,", "wtf", "<base> -> bax,"))

    with pytest.raises(ValueError) as e:
        alembic_history.validate_revision("asdf")
    assert "asdf" in str(e.value)


def test_previous_revision():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))
    result = alembic_history.previous_revision("bax")

    assert "bar" == result


def test_previous_revision_base():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))
    result = alembic_history.previous_revision("base")

    assert result is result


def test_next_revision():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))
    result = alembic_history.next_revision("bax")

    assert "baz" == result


def test_next_revision_head():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))
    result = alembic_history.next_revision("head")

    assert result is None


def test_revision_range_to_head():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))
    result = alembic_history.revision_range("bar", "head")

    expected_result = ["bar", "bax", "baz", "head"]
    assert expected_result == result


def test_revision_range_from_base():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))
    result = alembic_history.revision_range("base", "bax")

    expected_result = ["base", "bar", "bax"]
    assert expected_result == result


def test_revision_window():
    alembic_history = AlembicHistory.parse(("bax -> baz (head),", "bar -> bax,", "<base> -> bar,"))
    result = alembic_history.revision_window("base", "baz")

    expected_result = [("base", "bar"), ("bar", "bax"), ("bax", "baz")]
    assert expected_result == result
