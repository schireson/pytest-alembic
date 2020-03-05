from pytest_mock_resources import create_postgres_fixture

pytest_plugins = "pytester"

db = create_postgres_fixture()
