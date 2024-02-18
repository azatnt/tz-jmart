from sqlalchemy import Column, Integer, String, UniqueConstraint

from src.common.models import IdAbstractModel, CreatedUpdateAbstractModel


class User(IdAbstractModel, CreatedUpdateAbstractModel):
    __tablename__ = 't_user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)

    __table_args__ = (UniqueConstraint(username, ),)
