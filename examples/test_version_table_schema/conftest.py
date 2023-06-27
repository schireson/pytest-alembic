from pytest_mock_resources import create_postgres_fixture, Statements

alembic_engine = create_postgres_fixture(Statements("CREATE SCHEMA version_table_schema"))
