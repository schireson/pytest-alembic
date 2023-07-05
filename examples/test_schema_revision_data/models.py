from sqlalchemy import Column, types

try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Foo(Base):
    __tablename__ = "foo"
    __table_args__ = {"schema": "meow"}

    id = Column(types.Integer(), autoincrement=True, primary_key=True)
