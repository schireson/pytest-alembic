import sqlalchemy
from sqlalchemy import Column, types

try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Foo(Base):
    __tablename__ = "foo"

    id = Column(types.Integer(), autoincrement=True, primary_key=True)

    created_at = sqlalchemy.Column(
        sqlalchemy.types.DateTime(timezone=True),
        server_default=sqlalchemy.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


class Bar(Base):
    __tablename__ = "bar"

    id = Column(types.Integer(), autoincrement=True, primary_key=True)
    foo_id = Column(types.Integer(), nullable=False)
