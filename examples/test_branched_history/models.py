import sqlalchemy
from sqlalchemy import Column, types
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CreatedAt(Base):
    __tablename__ = "foo"

    id = Column(types.Integer(), autoincrement=True, primary_key=True)

    created_at = sqlalchemy.Column(
        sqlalchemy.types.DateTime(timezone=True),
        server_default=sqlalchemy.text("'2020-01-01'"),
        nullable=False,
    )


class Bar(Base):
    __tablename__ = "bar"

    id = Column(types.Integer(), autoincrement=True, primary_key=True)
