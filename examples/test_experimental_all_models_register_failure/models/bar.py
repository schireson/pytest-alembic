import sqlalchemy
from sqlalchemy import Column, types

from models import Base


class Bar(Base):
    __tablename__ = "bar"

    id = Column(types.Integer(), autoincrement=True, primary_key=True)
