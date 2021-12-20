from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import alembic.config


@dataclass
class Config:
    """Pytest-alembic configuration options.

    - `config_options`: Meant to simplify the creation of ``alembic.config.Config``
       objects. Supply keys common to customization in alembic configuration. For
       example:

       - file/config_file_name (commonly alembic.ini)
       - script_location
       - sqlalchemy.url
       - target_metadata
       - process_revision_directives
       - include_schemas

    - Both `before_revision_data` and `at_revision_data` are described in detail
      in :ref:`Custom data`.

    - :code:`minimum_downgrade_revision` can be used to set a lower bound on the
      **downgrade** migrations which are run built-in tests like ``test_up_down_consistency``
      and ``test_downgrade_leaves_no_trace``.

    For example:
        >>> import pytest

        >>> @pytest.fixture
        ... def alembic_config():
        ...    return Config(minimum_downgrade_revision='abcde12345')

        This would essentially short-circuit and avoid running the downgrade
        migrations **including and below** this migration.

    .. note::

       If a downgrade raises a ``NotImplementedError``, it will have the same effect
       as a ``minimum_downgrade_revision``, but will emit a warning suggesting
       the use of this feature instead.
    """

    config_options: Dict[str, Any] = field(default_factory=dict)
    alembic_config: Optional[alembic.config.Config] = None

    before_revision_data: Optional[Union[Dict, "RevisionSpec"]] = None
    at_revision_data: Optional[Union[Dict, "RevisionSpec"]] = None

    minimum_downgrade_revision: Optional[str] = None

    @classmethod
    def from_raw_config(
        cls, raw_config: Union[Dict[str, Any], alembic.config.Config, "Config", None] = None
    ):
        """Adapt between pre-produced alembic config and raw config options.

        Allows one to specify raw pytest-alembic config options through raw dictionary,
        as well as being flexible enough to allow a literal alembic Config object.

        Examples:
            >>> Config.from_raw_config()
            Config(config_options={}, alembic_config=None, before_revision_data=None, at_revision_data=None, minimum_downgrade_revision=None)

            >>> Config.from_raw_config({'minimum_downgrade_revision': 'abc123'})
            Config(config_options={}, alembic_config=None, before_revision_data=None, at_revision_data=None, minimum_downgrade_revision='abc123')

            >>> Config.from_raw_config(Config(minimum_downgrade_revision='abc123'))
            Config(config_options={}, alembic_config=None, before_revision_data=None, at_revision_data=None, minimum_downgrade_revision='abc123')
        """
        if raw_config is None:
            return cls()

        if isinstance(raw_config, alembic.config.Config):
            return cls(alembic_config=raw_config)

        if isinstance(raw_config, Config):
            return raw_config

        before_data = raw_config.pop("before_revision_data", None)
        at_data = raw_config.pop("at_revision_data", None)
        minimum_downgrade_revision = raw_config.pop("minimum_downgrade_revision", None)
        return cls(
            config_options=raw_config,
            alembic_config=None,
            before_revision_data=before_data,
            at_revision_data=at_data,
            minimum_downgrade_revision=minimum_downgrade_revision,
        )

    def make_alembic_config(self, stdout):
        file = (
            self.config_options.get("file")
            or self.config_options.get("config_file_name")
            or "alembic.ini"
        )

        alembic_config = self.config_options.get("alembic_config")

        if not alembic_config and self.alembic_config:
            alembic_config = self.alembic_config
            alembic_config.stdout = stdout
        else:
            alembic_config = alembic.config.Config(file, stdout=stdout)

        sqlalchemy_url = self.config_options.get("sqlalchemy.url")
        if sqlalchemy_url:
            alembic_config.set_main_option("sqlalchemy.url", sqlalchemy_url)

        # Only set script_location if set.
        script_location = self.config_options.get("script_location")
        if script_location:
            alembic_config.set_section_option("alembic", "script_location", script_location)
        elif not alembic_config.get_section_option("alembic", "script_location"):
            # Or in the event that it's not set after already having loaded the config.
            alembic_config.set_main_option("script_location", "migrations")

        target_metadata = self.config_options.get("target_metadata")
        alembic_config.attributes["target_metadata"] = target_metadata

        process_revision_directives = self.config_options.get("process_revision_directives")
        alembic_config.attributes["process_revision_directives"] = process_revision_directives

        include_schemas = self.config_options.get("include_schemas", True)
        alembic_config.attributes["include_schemas"] = include_schemas

        return alembic_config


def duplicate_alembic_config(config: alembic.config.Config):
    return alembic.config.Config(
        config.config_file_name,
        ini_section=config.config_ini_section,
        output_buffer=config.output_buffer,
        stdout=config.stdout,
        cmd_opts=config.cmd_opts,
        config_args=config.config_args,
        attributes=config.attributes,
    )


# isort: split
from pytest_alembic.revision_data import RevisionSpec  # noqa
