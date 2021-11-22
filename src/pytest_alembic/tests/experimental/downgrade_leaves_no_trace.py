from typing import List, Optional, Set, Tuple

from sqlalchemy import MetaData

from pytest_alembic.plugin.error import AlembicTestFailure
from pytest_alembic.runner import MigrationContext

try:
    from sqlalchemy.ext.declarative import DeclarativeMeta
except ImportError:  # pragma: no cover
    from sqlalchemy.declarative import DeclarativeMeta


def test_downgrade_leaves_no_trace(alembic_runner: MigrationContext, alembic_engine):
    """Assert that all tables defined on your `MetaData`, are imported in the `env.py`.

    """
    original_metadata = MetaData()
    original_metadata.reflect(alembic_engine)

    alembic_runner.migrate_up_one()

    upgrade_metadata = MetaData()
    upgrade_metadata.reflect(alembic_engine)

    alembic_runner.migrate_down_one()

    downgrade_metadata = MetaData()
    downgrade_metadata.reflect(alembic_engine)

    # old_tables = {k: v for k, v in old_metadata.tables.items()}
    # new_tables = {k: v for k, v in new_metadata.tables.items() if k != 'alembic_version'}

    import pdb; pdb.set_trace()
    if new_tables:
        tables = ', '.join(new_tables.keys())
        raise AlembicTestFailure(
            f"{new_tables}"
        )

    raise
