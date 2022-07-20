from dataclasses import dataclass
from typing import List

import pytest
from alembic.script import revision

from pytest_alembic.history import AlembicHistory


@dataclass
class Revision:
    revision: str


@dataclass
class RevisionMap(revision.RevisionMap):
    history: List[Revision]

    @classmethod
    def from_strs(cls, strs):
        return cls(history=[Revision(r) for r, _ in strs])

    def iterate_revisions(self, _, __):
        yield from self.history


def test_parse_head_revision():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)

    expected_result = ["base", "bar", "bax", "baz", "heads"]
    assert alembic_history.revisions == expected_result


def test_validate_revision():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", None]])
    alembic_history = AlembicHistory.parse(revision_map)

    with pytest.raises(ValueError) as e:
        alembic_history.validate_revision("asdf")
    assert "asdf" in str(e.value)


def test_previous_revision():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.previous_revision("bax")

    assert "bar" == result


def test_previous_revision_base():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.previous_revision("base")

    assert result is result


def test_next_revision():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.next_revision("bax")

    assert "baz" == result


def test_next_revision_head():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.next_revision("heads")

    assert result is None


def test_revision_range_to_head():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.revision_range("bar", "head")

    expected_result = ["bar", "bax", "baz", "heads"]
    assert expected_result == result


def test_revision_range_from_base():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.revision_range("base", "bax")

    expected_result = ["base", "bar", "bax"]
    assert expected_result == result


def test_revision_window():
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.revision_window("base", "baz")

    expected_result = [("base", "bar"), ("bar", "bax"), ("bax", "baz")]
    assert expected_result == result
