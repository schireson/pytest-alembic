import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

_RE_REVISION_PATTERN = r"-> ([a-zA-Z0-9]*)"


@dataclass
class AlembicHistory:
    revisions: List[str]
    revision_indices: Dict[str, int]
    revisions_by_index: Dict[int, str]

    @classmethod
    def parse(cls, raw_history: Iterable[str]) -> "AlembicHistory":
        """Extract the set of migration revision hashes from the result of an `alembic history` command.
        """
        revision_hashes = ["base"]
        for line in raw_history:
            match = re.search(_RE_REVISION_PATTERN, line)
            if not match:
                continue

            revision_hashes.append(match.group(1))
        revision_hashes.append("head")

        revisions = revision_hashes
        revision_indices = {revision: i for i, revision in enumerate(revisions)}
        revisions_by_index = {v: k for k, v in revision_indices.items()}
        return cls(revisions, revision_indices, revisions_by_index)

    def validate_revision(self, revision):
        valid_revision = revision in self.revision_indices
        if not valid_revision:
            raise ValueError(f"Revision {revision} is not a valid revision in alembic's history")

    def previous_revision(self, revision: str) -> Optional[str]:
        self.validate_revision(revision)
        revision_index = self.revision_indices[revision]
        return self.revisions_by_index.get(revision_index - 1)

    def next_revision(self, revision: str) -> Optional[str]:
        self.validate_revision(revision)
        revision_index = self.revision_indices[revision]
        return self.revisions_by_index.get(revision_index + 1)
