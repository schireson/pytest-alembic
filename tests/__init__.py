import pytest
import sqlalchemy

sqlalchemy_version = getattr(sqlalchemy, "version", "1.3")
supports_asyncio = sqlalchemy_version.startswith(("1.4", "2."))

requires_asyncio_support = pytest.mark.skipif(
    not supports_asyncio,
    reason="Requires asyncio support",
)
