import collections
import itertools
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from alembic.script.revision import RevisionMap


@dataclass
class AlembicHistory:
    """A linear, indexable view of alembic's revision history.

    Alembic's own ``RevisionMap`` is a graph keyed by revision hash. This flattens it
    into an ordered list bracketed by the two sentinel revisions ``base`` and ``heads``,
    which is what makes "the revision before this one" and "every revision between
    these two" cheap to answer.

    Examples:
        >>> from alembic.script.revision import Revision, RevisionMap
        >>> revision_map = RevisionMap(
        ...     lambda: [
        ...         Revision("a1", None),
        ...         Revision("b2", "a1"),
        ...         Revision("c3", "b2"),
        ...     ]
        ... )
        >>> history = AlembicHistory.parse(revision_map)

        The sentinels bookend the real revisions, oldest first:

        >>> history.revisions
        ['base', 'a1', 'b2', 'c3', 'heads']

        >>> history.previous_revision("b2")
        'a1'
        >>> history.next_revision("b2")
        'c3'

        Both sentinels are addressable, and ``head`` is accepted as an alias of
        ``heads``:

        >>> history.next_revision("heads") is None
        True
        >>> history.previous_revision("base") is None
        True
        >>> history.revision_range("a1", "head")
        ['a1', 'b2', 'c3', 'heads']
    """

    map: RevisionMap
    revisions: List[str]
    revision_indices: Dict[str, int]
    revisions_by_index: Dict[int, str]

    @classmethod
    def parse(cls, revision_map: RevisionMap) -> "AlembicHistory":
        """Extract the set of migration revision hashes from alembic's notion of the history.

        The resulting list is ordered oldest-to-newest and padded with the ``base`` and
        ``heads`` sentinels, so index arithmetic is enough to walk it.

        Examples:
            >>> from alembic.script.revision import Revision, RevisionMap
            >>> history = AlembicHistory.parse(
            ...     RevisionMap(lambda: [Revision("a1", None), Revision("b2", "a1")])
            ... )
            >>> history.revisions
            ['base', 'a1', 'b2', 'heads']
            >>> history.revision_indices["a1"]
            1
        """
        revision_hashes = ["heads"]

        history = revision_map.iterate_revisions("heads", "base")
        for script in history:
            revision = script.revision
            revision_hashes.append(revision)
        revision_hashes.append("base")

        revisions = list(reversed(revision_hashes))
        revision_indices = {revision: i for i, revision in enumerate(revisions)}
        revisions_by_index = {v: k for k, v in revision_indices.items()}
        return cls(
            map=revision_map,
            revisions=revisions,
            revision_indices=revision_indices,
            revisions_by_index=revisions_by_index,
        )

    def validate_revision(self, revision):
        # Given that 'heads' seems to be strictly more powerful, coerce singular 'head'
        # to 'heads'.
        if revision == "head":
            revision = "heads"

        if revision not in self.revision_indices:
            message = f"Revision {revision} is not a valid revision in alembic's history"
            raise ValueError(message)
        return revision

    def previous_revision(self, revision: str) -> Optional[str]:
        revision = self.validate_revision(revision)
        revision_index = self.revision_indices[revision]
        return self.revisions_by_index.get(revision_index - 1)

    def next_revision(self, revision: str) -> Optional[str]:
        revision = self.validate_revision(revision)
        revision_index = self.revision_indices[revision]
        return self.revisions_by_index.get(revision_index + 1)

    def revision_range(self, current_revision: str, dest_revision: str) -> List[str]:
        current_revision = self.validate_revision(current_revision)
        dest_revision = self.validate_revision(dest_revision)
        start_index = self.revision_indices[current_revision]
        end_index = self.revision_indices[dest_revision]
        return [self.revisions[index] for index in range(start_index, end_index + 1)]

    def revision_window(self, current_revision: str, dest_revision: str) -> List[Tuple[str, str]]:
        revision_range = self.revision_range(current_revision, dest_revision)
        return list(
            zip(
                *(
                    collections.deque(itertools.islice(it, i), 0) or it
                    for i, it in enumerate(itertools.tee(revision_range, 2))
                )
            )
        )
