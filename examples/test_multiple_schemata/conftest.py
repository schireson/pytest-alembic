from pytest_alembic import tests
from pytest_alembic.plugin.fixtures import create_alembic_fixture

alembic1 = create_alembic_fixture()
alembic2 = create_alembic_fixture({"file": "alembic2.ini"})


def script_location(fixture):
    return fixture.command_executor.alembic_config.get_main_option("script_location")


def test_single_head_revision(alembic1):
    tests.test_single_head_revision(alembic1)
    assert script_location(alembic1) == "migrations"


def test_upgrade(alembic1):
    tests.test_upgrade(alembic1)
    assert script_location(alembic1) == "migrations"


def test_model_definitions_match_ddl(alembic1):
    tests.test_model_definitions_match_ddl(alembic1)
    assert script_location(alembic1) == "migrations"


def test_up_down_consistency(alembic1):
    tests.test_up_down_consistency(alembic1)
    assert script_location(alembic1) == "migrations"


def test_single_head_revision2(alembic2):
    tests.test_single_head_revision(alembic2)
    assert script_location(alembic2) == "migrations2"


def test_upgrade2(alembic2):
    tests.test_upgrade(alembic2)
    assert script_location(alembic2) == "migrations2"


def test_model_definitions_match_ddl2(alembic2):
    tests.test_model_definitions_match_ddl(alembic2)
    assert script_location(alembic2) == "migrations2"


def test_up_down_consistency2(alembic2):
    tests.test_up_down_consistency(alembic2)
    assert script_location(alembic2) == "migrations2"
