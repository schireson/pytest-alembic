"""Collect module and table information from the env.py context.

This module is executed within a subprocess in order to maintain a clean
python import state. Thus the `print` statements are the mechanism through
through which this script communicates the environment state back to the
parent process.
"""
import gc
import json
import os
import sys

from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory

try:
    from sqlalchemy.ext.declarative import DeclarativeMeta
except ImportError:  # pragma: no cover
    from sqlalchemy.declarative import DeclarativeMeta


def run():  # pragma: no cover
    """Execute alembic in order to spin up the alembic environment.

    Cannot be covered with coverage due to the subprocess environment in which it's
    executed.
    """
    _, url, offline_str, async_str = sys.argv
    offline = bool(int(offline_str))
    async_ = bool(int(async_str))

    config = Config("alembic.ini")
    config.set_section_option(config.config_ini_section, "sqlalchemy.url", url)

    try:
        config.attributes["connection"] = create_connectable(url, async_)
    except Exception:  # nosec
        pass

    script = ScriptDirectory.from_config(config)

    with EnvironmentContext(config, script, fn=environment_context_fn, as_sql=offline):
        script.run_env()


def create_connectable(url, async_=False):
    if async_:
        from sqlalchemy.ext.asyncio import create_async_engine

        connectable = create_async_engine(url)
    else:
        from sqlalchemy import create_engine

        connectable = create_engine(url).connect()
    return connectable


def environment_context_fn(_, migration_context):
    """Print out the alembic environment context (given an alembic migration context)."""
    target_metadata = migration_context.opts["target_metadata"]
    if target_metadata:
        tables = list(target_metadata.tables)
        modules = list(identify_modules(target_metadata))
    else:
        tables = []
        modules = []

    result = {
        "modules": modules,
        "tables": tables,
    }

    # Remember, given that we're in a subprocess, `print` is our output mechanism.
    output = json.dumps(result)
    print(f"<pytest-alembic>{output}</pytest-alembic>")

    return []


def identify_modules(target_metadata):
    """Find all model referrers of the alembic `target_metadata`."""
    for referrer in gc.get_referrers(target_metadata):
        dict_referrer = isinstance(referrer, dict)
        if not dict_referrer:
            continue

        model_base = get_model_base(referrer, target_metadata)
        if model_base:
            for referrer in gc.get_referrers(model_base):
                yield from get_referrer_module(referrer)

        yield from get_referrer_module(referrer)


def get_model_base(referrer, target_metadata):
    """Find all model referrers of any model base referents of the `target_metadata`."""
    metadata = referrer.get("metadata")
    if not metadata or metadata is not target_metadata:
        return

    for referrer in gc.get_referrers(referrer):
        if isinstance(referrer, DeclarativeMeta):
            return referrer


def get_referrer_module(referrer):
    """Distinguish actual candidate modules from those which cannot be modules.

    Namely: non-modules, alembic-related things, scripts and such.
    """
    dict_referrer = isinstance(referrer, dict)

    loader = dict_referrer and referrer.get("__loader__")
    loader_name = getattr(loader, "name", None)

    if loader_name in {None, "__main__", "env_py"}:
        return

    # If we've already ruled out the main and/or env.py,
    # then this is likely the module we want.
    yield loader_name


if __name__ == "__main__":
    if os.environ.get("COVERAGE_PROCESS_START"):
        import coverage

        coverage.process_startup()

    run()
