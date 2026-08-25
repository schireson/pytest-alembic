from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Any

import pytest
from alembic.script import revision

from pytest_alembic.history import AlembicHistory


@dataclass
class Revision:
    revision: str


@dataclass
class RevisionMap(revision.RevisionMap):
    history: list[Revision]

    @classmethod
    def from_strs(cls, strs: Sequence[Sequence[Any]]) -> "RevisionMap":
        return cls(history=[Revision(r) for r, _ in strs])

    def iterate_revisions(self, *_args: Any, **_kwargs: Any) -> Iterator[Any]:
        yield from self.history


def test_parse_head_revision() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)

    expected_result = ["base", "bar", "bax", "baz", "heads"]
    assert alembic_history.revisions == expected_result


def test_validate_revision() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", None]])
    alembic_history = AlembicHistory.parse(revision_map)

    with pytest.raises(ValueError, match="asdf"):
        alembic_history.validate_revision("asdf")


def test_previous_revision() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.previous_revision("bax")

    assert result == "bar"


def test_previous_revision_base() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.previous_revision("base")

    assert result is result


def test_next_revision() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.next_revision("bax")

    assert result == "baz"


def test_next_revision_head() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.next_revision("heads")

    assert result is None


def test_revision_range_to_head() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.revision_range("bar", "head")

    expected_result = ["bar", "bax", "baz", "heads"]
    assert expected_result == result


def test_revision_range_from_base() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.revision_range("base", "bax")

    expected_result = ["base", "bar", "bax"]
    assert expected_result == result


def test_revision_window() -> None:
    revision_map = RevisionMap.from_strs([["baz", "bax"], ["bax", "bar"], ["bar", None]])
    alembic_history = AlembicHistory.parse(revision_map)
    result = alembic_history.revision_window("base", "baz")

    expected_result = [("base", "bar"), ("bar", "bax"), ("bax", "baz")]
    assert expected_result == result
