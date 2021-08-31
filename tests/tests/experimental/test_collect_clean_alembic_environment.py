import json
from dataclasses import dataclass

import pytest
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from pytest_alembic.tests.experimental.collect_clean_alembic_environment import (
    environment_context_fn,
    get_referrer_module,
    identify_modules,
)


class MigrationContext:
    def __init__(self, target_metdata):
        self.opts = {"target_metadata": target_metdata}


class Test_environment_context_fn:
    def test_no_target_metadata(self, capsys):
        context = MigrationContext(target_metdata=None)
        environment_context_fn(None, context)
        output = capsys.readouterr().out

        result = json.loads(output)
        assert result == {
            "modules": [],
            "tables": [],
        }

    def test_output(self, capsys):
        class Target:
            tables = {"t1": None}

        context = MigrationContext(target_metdata=Target())
        environment_context_fn(None, context)
        output = capsys.readouterr().out

        result = json.loads(output)
        assert result == {
            "modules": [],
            "tables": ["t1"],
        }


class Test_identify_modules:
    def test_has_model_base_metadata(self):
        metadata = MetaData()
        declarative_base(metadata=metadata)
        modules = list(identify_modules(metadata))
        assert modules == []

    def test_has_model_base(self):
        Base = declarative_base()
        modules = list(identify_modules(Base))
        assert modules == []

    metadata = MetaData()
    _refers_to_metadata = [metadata]

    def test_just_metadata(self):
        modules = list(identify_modules(self.metadata))
        assert modules == []


@dataclass
class Loader:
    name: str


class Test_get_referrer_module:
    @pytest.mark.parametrize(
        "name, loader_name", ((None, []), ("__main__", []), ("env_py", []), ("meow", ["meow"]))
    )
    def test_get_referer(self, name, loader_name):
        referrer = {"__loader__": Loader(name)}
        actual_loader_name = list(get_referrer_module(referrer))
        assert actual_loader_name == loader_name
