import pytest
import sqlalchemy

sqlalchemy_version = getattr(sqlalchemy, "__version__", "1.3")
supports_asyncio = sqlalchemy_version.startswith(("1.4", "2."))
is_sqlalchemy_2 = sqlalchemy_version.startswith("2.")

requires_asyncio_support = pytest.mark.skipif(
    not supports_asyncio,
    reason="Requires asyncio support",
)
requires_sqlalchemy_2 = pytest.mark.skipif(not is_sqlalchemy_2, reason="Requires v2")
