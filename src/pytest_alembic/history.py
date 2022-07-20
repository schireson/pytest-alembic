import collections
import itertools
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from alembic.script.revision import RevisionMap


@dataclass
class AlembicHistory:
    map: RevisionMap
    revisions: List[str]
    revision_indices: Dict[str, int]
    revisions_by_index: Dict[int, str]

    @classmethod
    def parse(cls, revision_map: RevisionMap) -> "AlembicHistory":
        """Extract the set of migration revision hashes from alembic's notion of the history."""
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
            raise ValueError(f"Revision {revision} is not a valid revision in alembic's history")
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
            zip(  # type: ignore
                *(
                    collections.deque(itertools.islice(it, i), 0) or it
                    for i, it in enumerate(itertools.tee(revision_range, 2))
                )
            )
        )
