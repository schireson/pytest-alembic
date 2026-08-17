from dataclasses import dataclass
from typing import Any, ClassVar, Optional

import pytest
from sqlalchemy import MetaData

try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base


from pytest_alembic.tests.experimental.all_models_register_on_metadata import (
    parse_collection_output,
)
from pytest_alembic.tests.experimental.collect_clean_alembic_environment import (
    environment_context_fn,
    get_referrer_module,
    identify_modules,
)


class MigrationContext:
    def __init__(self, target_metdata: Any) -> None:
        self.opts = {"target_metadata": target_metdata}


class Test_environment_context_fn:
    def test_no_target_metadata(self, capsys: pytest.CaptureFixture[str]) -> None:
        context = MigrationContext(target_metdata=None)
        environment_context_fn(None, context)
        output = capsys.readouterr().out

        result = parse_collection_output(output)
        assert result == {
            "modules": [],
            "tables": [],
        }

    def test_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        class Target:
            tables: ClassVar[dict] = {"t1": None}

        context = MigrationContext(target_metdata=Target())
        environment_context_fn(None, context)
        output = capsys.readouterr().out

        result = parse_collection_output(output)
        assert result == {
            "modules": [],
            "tables": ["t1"],
        }


class Test_identify_modules:
    def test_has_model_base_metadata(self) -> None:
        metadata = MetaData()
        declarative_base(metadata=metadata)
        modules = list(identify_modules(metadata))
        assert modules == []

    def test_has_model_base(self) -> None:
        Base = declarative_base()
        modules = list(identify_modules(Base))
        assert modules == []

    metadata = MetaData()
    _refers_to_metadata: ClassVar = [metadata]

    def test_just_metadata(self) -> None:
        modules = list(identify_modules(self.metadata))
        assert modules == []


@dataclass
class Loader:
    name: Optional[str]


class Test_get_referrer_module:
    @pytest.mark.parametrize(
        ("name", "loader_name"),
        [
            (None, []),
            ("__main__", []),
            ("env_py", []),
            ("meow", ["meow"]),
        ],
    )
    def test_get_referer(self, name: Optional[str], loader_name: list) -> None:
        referrer = {"__loader__": Loader(name)}
        actual_loader_name = list(get_referrer_module(referrer))
        assert actual_loader_name == loader_name
