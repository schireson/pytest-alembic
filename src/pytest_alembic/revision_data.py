"""The data a user asks to be inserted at given points in the history.

A migration that works on an empty table does not necessarily work on a populated
one. :class:`RevisionSpec` is the parsed form of the ``before_revision_data`` and
``at_revision_data`` config options, and :class:`RevisionData` is the pair of them
the runner consults as it steps through revisions.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_alembic.config import Config


@dataclass
class RevisionSpec:
    """Describe a set of valid database data at a set of revisions."""

    data: dict[str, dict | list[dict]]

    @classmethod
    def parse(cls, data: "RevisionSpec | dict[str, dict | list[dict]] | None"):
        """Parse a raw dict structure into a `RevisionSpec`."""
        if not data:
            return cls({})

        if isinstance(data, RevisionSpec):
            return data

        return cls(data)

    def get(self, revision: str) -> dict | list[dict]:
        """Get the database data described at a particular revision."""
        return self.data.get(revision, [])


@dataclass
class RevisionData:
    """Describe the data which should exist at given revisions when performing upgrades."""

    before_revision_data: RevisionSpec
    at_revision_data: RevisionSpec

    @classmethod
    def from_config(cls, config: "Config"):
        """Produce a `RevisionData` from raw configuration from :func:`alembic_config`."""
        return cls(
            before_revision_data=RevisionSpec.parse(config.before_revision_data),
            at_revision_data=RevisionSpec.parse(config.at_revision_data),
        )

    def get(self, revision_data: dict | list[dict]):
        """Yield `revision_data` as individual rows, whether it is one row or many.

        A single dict is a common enough shorthand for "one row" that both forms are
        accepted everywhere; this is where the two are levelled out.
        """
        if isinstance(revision_data, dict):
            yield revision_data
        else:
            yield from revision_data

    def get_before(self, revision: str) -> list[dict]:
        """Yield the individual data insertions which should occur before the given revision."""
        before_revision_data = self.before_revision_data.get(revision)
        return list(self.get(before_revision_data))

    def get_at(self, revision: str) -> dict | list[dict]:
        """Yield individual data insertions which should occur upon reaching the given revision."""
        at_revision_data = self.at_revision_data.get(revision)
        return list(self.get(at_revision_data))
