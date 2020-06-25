import logging

import pytest
from alembic.autogenerate.api import AutogenContext
from alembic.autogenerate.render import _render_cmd_body

log = logging.getLogger(__name__)


@pytest.mark.alembic
def test_single_head_revision(alembic_runner):
    """Assert that there only exists one head revision.

    We're not sure what realistic scenario involves a diverging history to be desirable. We
    have only seen it be the result of uncaught merge conflicts resulting in a diverged history,
    which lazily breaks during deployment.
    """
    head_count = alembic_runner.heads

    assert len(head_count) <= 1  # nosec


@pytest.mark.alembic
def test_upgrade(alembic_runner):
    """Assert that the revision history can be run through from base to head.
    """
    alembic_runner.migrate_up_to("head")


@pytest.mark.alembic
def test_model_definitions_match_ddl(alembic_runner):
    """Assert that the state of the migrations matches the state of the models describing the DDL.

    In general, the set of migrations in the history should coalesce into DDL which is described
    by the current set of models. Therefore, a call to `revision --autogenerate` should always
    generate an empty migration (e.g. find no difference between your database (i.e. migrations
    history) and your models).
    """

    def verify_is_empty_revision(migration_context, __, directives):
        script = directives[0]

        migration_is_empty = script.upgrade_ops.is_empty()
        if not migration_is_empty:
            autogen_context = AutogenContext(migration_context)
            rendered_upgrade = _render_cmd_body(script.upgrade_ops, autogen_context)

            assert migration_is_empty, (  # nosec
                "The models decribing the DDL of your database are out of sync with the set of "
                "steps described in the revision history. This usually means that someone has "
                "made manual changes to the database's DDL, or some model has been changed "
                "without also generating a migration to describe that change.\n\n"
                "The upgrade which would have been generated would look like:\n\n{}".format(
                    rendered_upgrade
                )
            )

    alembic_runner.migrate_up_to("head")
    alembic_runner.generate_revision(
        message="test revision",
        autogenerate=True,
        process_revision_directives=verify_is_empty_revision,
    )


@pytest.mark.alembic
def test_up_down_consistency(alembic_runner):
    """Assert that all downgrades succeed.

    While downgrading may not be lossless operation data-wise, there’s a theory of database
    migrations that says that the revisions in existence for a database should be able to go
    from an entirely blank schema to the finished product, and back again.

    Individually upgrade to ensure that it's clear which revision caused the failure.
    """
    for revision in alembic_runner.history.revisions:
        alembic_runner.migrate_up_to(revision)

    for revision in reversed(alembic_runner.history.revisions):
        alembic_runner.migrate_down_to(revision)
