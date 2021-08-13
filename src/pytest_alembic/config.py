from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING, Union

import alembic.config

if TYPE_CHECKING:
    from pytest_alembic.revision_data import RevisionSpec


@dataclass
class Config:
    """Adapt between pre-produced alembic config and raw config options.

    Allows one to specify raw pytest-alembic config options through raw dictionary,
    as well as being flexible enough to allow a literal alembic Config object.
    """

    config_options: Dict[str, Any] = field(default_factory=dict)
    alembic_config: Optional[alembic.config.Config] = None

    before_revision_data: Optional[Union[Dict, "RevisionSpec"]] = None
    at_revision_data: Optional[Union[Dict, "RevisionSpec"]] = None

    @classmethod
    def from_raw_config(cls, raw_config: Union[Dict[str, Any], alembic.config.Config, None] = None):
        if raw_config is None:
            return cls()

        if isinstance(raw_config, alembic.config.Config):
            return cls(alembic_config=raw_config)

        before_data = raw_config.pop("before_revision_data", None)
        at_data = raw_config.pop("at_revision_data", None)
        return cls(
            config_options=raw_config,
            alembic_config=None,
            before_revision_data=before_data,
            at_revision_data=at_data,
        )

    def make_alembic_config(self, stdout):
        file = self.config_options.get("file", "alembic.ini")
        alembic_config = self.config_options.get("alembic_config")

        if not alembic_config and self.alembic_config:
            alembic_config = self.alembic_config
            alembic_config.stdout = stdout
        else:
            alembic_config = alembic.config.Config(file, stdout=stdout)

        script_location = self.config_options.get("script_location")
        target_metadata = self.config_options.get("target_metadata")
        process_revision_directives = self.config_options.get("process_revision_directives")
        include_schemas = self.config_options.get("include_schemas", True)

        # Only set script_location if set.
        if script_location:
            alembic_config.set_section_option("alembic", "script_location", script_location)
        elif not alembic_config.get_section_option("alembic", "script_location"):
            # Or in the event that it's not set after already having loaded the config.
            alembic_config.set_main_option("script_location", "migrations")

        alembic_config.attributes["target_metadata"] = target_metadata
        alembic_config.attributes["process_revision_directives"] = process_revision_directives
        alembic_config.attributes["include_schemas"] = include_schemas
        return alembic_config
