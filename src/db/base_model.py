from typing import Any, Dict

from sqlalchemy import select, MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base, declared_attr

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class _Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    async def _select(cls, db: AsyncSession, **kwargs):
        query = select(cls).filter_by(**kwargs)
        result = await db.execute(query)
        return result

    @classmethod
    async def select_one_or_none(
        cls,
        db: AsyncSession,
        **kwargs,
    ):
        result = await cls._select(db, **kwargs)
        return result.scalar_one_or_none()

    @classmethod
    async def select_one(cls, db: AsyncSession, **kwargs):
        result = await cls._select(db, **kwargs)
        return result.scalar_one()

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        instance = cls(**kwargs)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @classmethod
    async def update(cls, db: AsyncSession, *, data: Dict[Any, Any], **kwargs):
        instance = await cls.select_one_or_none(db, **kwargs)
        if instance:
            for k, v in data.items():
                setattr(instance, k, v)
            await db.commit()

    __allow_unmapped__ = True


BaseModel = declarative_base(metadata=metadata, cls=_Base)
