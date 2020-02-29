from dataclasses import dataclass
from io import StringIO

import alembic
from alembic.config import Config


@dataclass
class CommandExecutor:
    alembic_config: Config
    stdout: StringIO
    stream_position: int

    @classmethod
    def from_config(cls, config):
        file = config.get("file", "alembic.ini")
        script_location = config.get("script_location", "migrations")
        target_metadata = config.get("target_metadata")
        process_revision_directives = config.get("process_revision_directives")
        include_schemas = config.get("include_schemas", True)

        stdout = StringIO()
        alembic_config = Config(file, stdout=stdout)
        alembic_config.set_main_option("script_location", script_location)

        alembic_config.attributes["target_metadata"] = target_metadata
        alembic_config.attributes["process_revi"] = process_revision_directives
        alembic_config.attributes["include_schemas"] = include_schemas

        return cls(alembic_config=alembic_config, stdout=stdout, stream_position=0)

    def configure(self, **kwargs):
        for key, value in kwargs.items():
            self.alembic_config.attributes[key] = value

    def run_command(self, command, *args, **kwargs):
        self.stream_position = self.stdout.tell()

        executable_command = getattr(alembic.command, command)
        executable_command(self.alembic_config, *args, **kwargs)

        self.stdout.seek(self.stream_position)
        return self.stdout.readlines()
