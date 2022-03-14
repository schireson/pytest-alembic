import importlib
import json
import logging
import pkgutil
import re
import subprocess  # nosec
from typing import List, Optional, Set, Tuple

from sqlalchemy import MetaData

from pytest_alembic.plugin.error import AlembicTestFailure
from pytest_alembic.runner import MigrationContext

try:
    from sqlalchemy.ext.declarative import DeclarativeMeta
except ImportError:  # pragma: no cover
    from sqlalchemy.declarative import DeclarativeMeta

try:
    from sqlalchemy.ext.asyncio import AsyncEngine
except ImportError:
    AsyncEngine = None


log = logging.getLogger(__name__)


def test_all_models_register_on_metadata(
    alembic_runner: MigrationContext,
    model_package: Optional[str] = None,
    offline: bool = False,
    async_: bool = None,
):
    """Assert that all tables defined on your `MetaData`, are imported in the `env.py`.

    We'll call a "bare import", the minimum import of the model base/MetaData which is
    typically performed in the `env.py`. Generally this might look something like:

    >>>
    >> from foo.models import Base
    >> target_metadata = Base.metadata
    >> ...
    >> context.configure(..., target_metadata=target_metadata)

    You'll notice here, that if `foo.models` does not, itself, import a theoretical
    `foo.models.bar` module, then that model will fail to register on the metadata
    and as far as alembic's `--autogenerate` feature goes, it does not exist.

    Generally one might notice this as an `--autogenerate` run dropping tables for
    which you have table definitions, at which point you'll go back and make sure
    to import said model somewhere in the normal loading process for `foo.models`.

    Thus this test compares such an import against the opposite scenario, one where
    every single possible module has been imported, and we therefore "**know**" that
    all defined models/tables will be attached to the MetaData. If there's a
    difference in the set of tables on the MetaData, then we have an issue!

    **Note** This test is distinct from the `test_model_definitions_match_ddl`
    test because imports can have side-effects. Thus when normal tests run in the
    context of your test run, you may have already imported models from modules
    transitively somewhere else in tree of imports required to run your tests.

    Therefore this test goes to lengths to collect a clean python interpreter
    which **only** imports the portion of code which would have been imported by
    the `env.py` itself.

    Arguments:
        alembic_runner: The alembic runner instance used to run the test.
        model_package: An optional way to explicitly the package in which models
            reside, in the event that automatic detection fails.
        offline: Whether to run the internal migration step as offline. This can
            be useful, depending on how your env.py is set up, to avoid executing
            certain portions of your env.py, if they're incompatible with execution
            in the context of this test.
        async_: Whether to produce an async engine in the internal engine creation
            step. Defaults to `None` (i.e. automatic detection).
    """
    # If `async_` is None, then we should automatically detect whether to run in
    # async mode. If `AsyncEngine` is None, then we're not running on a version
    # of sqlalchemy which supports it.
    if (
        async_ is None
        and AsyncEngine is not None
        and isinstance(alembic_runner.connection, AsyncEngine)
    ):
        async_ = True

    modules, bare_tables = get_bare_import_tableset(
        str(alembic_runner.connection.url),
        async_=bool(async_),
        offline=offline,
    )
    if model_package:
        modules = [model_package]

    full_tables = get_full_tableset(*modules)

    if bare_tables != full_tables:
        diff = bare_tables.symmetric_difference(full_tables)
        diff_str = ", ".join(diff)
        raise AlembicTestFailure(
            "There was a difference detected between the set of tables registered on your "
            "`MetaData` during the course of loading your `env.py` compared with the set of "
            f"tables registered after importing all modules below the provided '{model_package}' "
            "module/package.\n\n"
            "This commonly happens if you are missing an import path from the root of your "
            "models/MetaData to some set of models defined elsewhere. Given that your `env.py` "
            "likely only directly imports your model base or MetaData, this can be a problem! "
            "As far as alembic is concerned, affected tables do not exist, and will likely "
            "be indicated by alembic to be dropped, should you attempt a `revision --autogenerate`"
            "command.\n\n"
            f"The following tables are affected: {diff_str}."
        )


def get_bare_import_tableset(
    url: str, offline: bool = False, async_: bool = False
) -> Tuple[List[str], Set[str]]:
    """Get the set of tables which would have been added to the metadata on a bare ma.models import.

    Importantly, this cannot simply import the MetaData directly, as that may have already
    had side-effects performed on it such that it's no longer representative of if one were to
    directly import the MetaData alone.

    Thus, we start a python subprocess which does the most minimal import we can perform to extract the MetaData,
    and return the set of tables attached to it.
    """

    command = [
        "python",
        "-m",
        "pytest_alembic.tests.experimental.collect_clean_alembic_environment",
        url,
        str(offline.real),
        str(async_.real),
    ]
    try:
        result = subprocess.run(  # nosec
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as e:  # pragma: no cover
        raise AlembicTestFailure(e.stderr)

    parsed_result = parse_collection_output(result.stdout)
    tablenames = set(parsed_result["tables"])
    modules = sorted(parsed_result["modules"])
    return modules, tablenames


def parse_collection_output(raw_output: str):
    # The default env.py offline execution mode, emits extra output that is
    # irrelevant to the expected output that a script execution would normally
    # produce, so we surround it with sentinel content.
    match = re.match(r"<pytest-alembic>(.*)</pytest-alembic>", raw_output)
    if match:
        return json.loads(match.group(1))

    # Indicative of a bug in the implementation of the subprocess code!
    raise RuntimeError(raw_output)


def get_full_tableset(*module_names: str) -> Set[str]:
    """Get the set of full set of tables which are defined.

    The theory is that if we import every module in the tree below ma.models, we should
    cause the import side-effect of all models being attached to the model base.

    Once done, we should end up with the theoretical maximum of tables included in the MetaData.
    """
    metadata = None
    for module_name in module_names:
        modules = traverse_modules(module_name)
        try:
            module, *_ = modules
        except ValueError:
            raise AlembicTestFailure(f"Invalid module name: {module_name}")

        for item in module.__dict__.values():
            if isinstance(item, MetaData):
                metadata = item
                break
            if isinstance(item, DeclarativeMeta):
                metadata = item.metadata
                break

    if metadata is None:
        raise AlembicTestFailure(
            "Unable to locate a MetaData reference in the local context of your `env.py`. This "
            "test requires a local reference to either a `DeclarativeMeta` (i.e. declarative model "
            "base), or a `MetaData` to exist in your `env.py`."
        )

    tables = metadata.tables
    tablenames = set(tables.keys())
    return tablenames


def traverse_modules(
    package_name: str,
    import_module=importlib.import_module,
    walk_packages=pkgutil.walk_packages,
):
    """Dynamically traverse the tree of packages below a given root and import them.

    Note this will perform the import of each module, which is an operation which can
    cause side-effects!
    """

    try:
        package = import_module(package_name)
    except ImportError:
        return

    if package.__package__:
        if not hasattr(package, "__path__"):
            return

        package_path = package.__path__
        for _, name, is_package in walk_packages(package_path):
            full_name = f"{package.__name__}.{name}"

            try:
                yield import_module(full_name)
            except ImportError:
                continue

            if is_package:
                yield from traverse_modules(full_name)

    else:
        name = package.__name__
        yield import_module(name)
