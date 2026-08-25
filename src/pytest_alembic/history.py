"""A flattened, ordered view of the migration history.

Alembic addresses revisions by hash and relates them as a graph. Nearly every
built-in test, though, wants to walk the history one step at a time — "the revision
after this one", "every revision between these two" — so :class:`AlembicHistory`
flattens that graph into a list once and answers those questions by index.
"""

import itertools
from dataclasses import dataclass

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
    revisions: list[str]
    revision_indices: dict[str, int]
    revisions_by_index: dict[int, str]

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
        """Normalise `revision` and assert that it exists in this history.

        ``head`` is accepted as an alias of ``heads``, which is strictly more general, so
        callers need not care which spelling a user wrote.

        Args:
            revision: A revision hash, or one of the ``base``/``head``/``heads``
                sentinels.

        Returns:
            The revision, with ``head`` coerced to ``heads``.

        Raises:
            ValueError: If the revision is not in this history. This is usually a typo in
                the test, or a revision that was deleted from the migrations directory.
        """
        # Given that 'heads' seems to be strictly more powerful, coerce singular 'head'
        # to 'heads'.
        if revision == "head":
            revision = "heads"

        if revision not in self.revision_indices:
            message = f"Revision {revision} is not a valid revision in alembic's history"
            raise ValueError(message)
        return revision

    def previous_revision(self, revision: str) -> str | None:
        """Return the revision immediately before `revision`, or ``None`` at ``base``."""
        revision = self.validate_revision(revision)
        revision_index = self.revision_indices[revision]
        return self.revisions_by_index.get(revision_index - 1)

    def next_revision(self, revision: str) -> str | None:
        """Return the revision immediately after `revision`, or ``None`` at ``heads``."""
        revision = self.validate_revision(revision)
        revision_index = self.revision_indices[revision]
        return self.revisions_by_index.get(revision_index + 1)

    def revision_range(self, current_revision: str, dest_revision: str) -> list[str]:
        """Return every revision from `current_revision` to `dest_revision`, inclusive.

        Both ends are validated, so an unknown revision raises rather than yielding a
        silently empty range. The bounds are expected in history order; a destination
        below the start produces an empty list rather than a reversed one.
        """
        current_revision = self.validate_revision(current_revision)
        dest_revision = self.validate_revision(dest_revision)
        start_index = self.revision_indices[current_revision]
        end_index = self.revision_indices[dest_revision]
        return [self.revisions[index] for index in range(start_index, end_index + 1)]

    def revision_window(self, current_revision: str, dest_revision: str) -> list[tuple[str, str]]:
        """Return the consecutive ``(from, to)`` pairs across a range of revisions.

        This is the shape the up/down tests iterate: each pair is one migration step, so
        a failure can name both the revision it was leaving and the one it was heading
        for.

        Examples:
            >>> from alembic.script.revision import Revision, RevisionMap
            >>> history = AlembicHistory.parse(
            ...     RevisionMap(lambda: [Revision("a1", None), Revision("b2", "a1")])
            ... )
            >>> history.revision_window("base", "heads")
            [('base', 'a1'), ('a1', 'b2'), ('b2', 'heads')]
        """
        revision_range = self.revision_range(current_revision, dest_revision)
        return list(itertools.pairwise(revision_range))
