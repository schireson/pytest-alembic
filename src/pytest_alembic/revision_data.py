from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class RevisionSpec:
    """Describe a set of valid database data at a set of revisions."""

    data: Dict[str, Union[Dict, List[Dict]]]

    @classmethod
    def parse(cls, data: Union[None, "RevisionSpec", Dict[str, Union[Dict, List[Dict]]]]):
        """Parse a raw dict structure into a `RevisionSpec`."""
        if not data:
            return cls({})

        if isinstance(data, RevisionSpec):
            return data

        return cls(data)

    def get(self, revision: str) -> Union[Dict, List[Dict]]:
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

    def get(self, revision: str, revision_data: Union[Dict, List[Dict]]):
        if isinstance(revision_data, Dict):
            yield revision_data
        else:
            for item in revision_data:
                yield item

    def get_before(self, revision: str) -> Union[Dict, List[Dict]]:
        """Yield the individual data insertions which should occur before the given revision."""
        before_revision_data = self.before_revision_data.get(revision)
        return self.get(revision, before_revision_data)

    def get_at(self, revision: str) -> Union[Dict, List[Dict]]:
        """Yield the individual data insertions which should occur upon reaching the given revision."""
        at_revision_data = self.at_revision_data.get(revision)
        return self.get(revision, at_revision_data)


# isort: split
from pytest_alembic.config import Config  # noqa
