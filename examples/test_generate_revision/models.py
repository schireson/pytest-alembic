from sqlalchemy import Column, types
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Foo(Base):
    __tablename__ = "foo"

    id = Column(types.Integer(), primary_key=True)
