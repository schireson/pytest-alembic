from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class RevisionData:
    before_revision_data: Dict[str, Union[Dict, List[Dict]]]
    at_revision_data: Dict[str, Union[Dict, List[Dict]]]

    @classmethod
    def from_config(cls, config: Dict):
        return cls(
            before_revision_data=config.get("before_revision_data", {}),
            at_revision_data=config.get("at_revision_data", {}),
        )

    def get(self, revision: str, revision_data: Union[Dict, List[Dict]]):
        if isinstance(revision_data, Dict):
            yield revision_data
        else:
            for item in revision_data:
                yield item

    def get_before(self, revision: str):
        before_revision_data = self.before_revision_data.get(revision, [])
        return self.get(revision, before_revision_data)

    def get_at(self, revision: str):
        at_revision_data = self.at_revision_data.get(revision, [])
        return self.get(revision, at_revision_data)
