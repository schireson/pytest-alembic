import logging
import warnings

import pytest
from alembic.autogenerate.api import AutogenContext
from alembic.autogenerate.render import _render_cmd_body

from pytest_alembic.plugin.error import AlembicTestFailure

log = logging.getLogger(__name__)


NOT_IMPLEMENTED_WARNING = (
    "The {revision} downgrade raised `NotImplementedError`, which short-circuited the downgrade "
    "operation and may have passed the test. If intended, and downgrades can not safely be performed "
    "below this migration, see 'minimum_downgrade_revision' configuration to avoid this warning."
)


@pytest.mark.alembic
def test_single_head_revision(alembic_runner):
    """Assert that there only exists one head revision.

    We're not sure what realistic scenario involves a diverging history to be desirable. We
    have only seen it be the result of uncaught merge conflicts resulting in a diverged history,
    which lazily breaks during deployment.
    """
    heads = alembic_runner.heads
    head_count = len(heads)

    if head_count != 1:
        heads = "\n".join([h.strip() for h in heads])
        raise AlembicTestFailure(
            "Expected 1 head revision, found {}".format(head_count),
            context=[("Heads", heads)],
        )


@pytest.mark.alembic
def test_upgrade(alembic_runner):
    """Assert that the revision history can be run through from base to head."""
    try:
        alembic_runner.migrate_up_to("heads")
    except RuntimeError as e:
        raise AlembicTestFailure(
            "Failed to upgrade to the head revision. This means the historical chain from an "
            "empty database, to the current revision is not possible.",
            context=[("Alembic Error", str(e))],
        )


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

            if not migration_is_empty:
                raise AlembicTestFailure(
                    "The models decribing the DDL of your database are out of sync with the set of "
                    "steps described in the revision history. This usually means that someone has "
                    "made manual changes to the database's DDL, or some model has been changed "
                    "without also generating a migration to describe that change.",
                    context=[
                        (
                            "The upgrade which would have been generated would look like",
                            rendered_upgrade,
                        )
                    ],
                )

    test_upgrade(alembic_runner)
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
        try:
            alembic_runner.migrate_up_to(revision)
        except Exception as e:
            raise AlembicTestFailure(
                "Failed to upgrade through each revision individually.",
                context=[("Failing Revision", revision), ("Alembic Error", str(e))],
            )

    # Skip the `heads` revision. Caused by new alembic warning in 1.6.x.
    down_revisions = list(reversed(alembic_runner.history.revisions[:-1]))

    index = 0
    for index, revision in enumerate(down_revisions):
        if alembic_runner.config.minimum_downgrade_revision == revision:
            # If there is a minimum_downgrade_revision, stop downgrading here.
            break

        try:
            alembic_runner.migrate_down_to(revision)
        except NotImplementedError:
            # In the event of a `NotImplementedError`, we should have the same semantics,
            # as-if `minimum_downgrade_revision` was specified, but we'll emit a warning
            # to suggest that feature is used instead.
            warnings.warn(NOT_IMPLEMENTED_WARNING.format(revision=revision))
            break

        except Exception as e:
            raise AlembicTestFailure(
                "Failed to downgrade through each revision individually.",
                context=[("Failing Revision", revision), ("Alembic Error", str(e))],
            )

    # We should only upgrade as far as we successfully downgraded.
    down_revisions = down_revisions[:index]

    for revision in reversed(down_revisions):
        try:
            alembic_runner.migrate_up_to(revision)
        except Exception as e:
            raise AlembicTestFailure(
                (
                    "Failed to upgrade through each revision individually after performing a "
                    "roundtrip upgrade -> downgrade -> upgrade cycle."
                ),
                context=[("Failing Revision", revision), ("Alembic Error", str(e))],
            )
