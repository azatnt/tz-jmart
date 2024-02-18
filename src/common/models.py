from sqlalchemy import Column, Integer, DateTime

from src.core.config import settings
from src.db.base_model import BaseModel
from src.utils import timezone


class IdAbstractModel(BaseModel):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    __table_args__ = {"schema": settings.DB_SCHEMA}


class CreatedUpdateAbstractModel(BaseModel):
    __abstract__ = True

    created_at = Column(DateTime, default=timezone.now)
    updated_at = Column(DateTime, default=timezone.now, onupdate=timezone.now)
