from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=settings.ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)
Session = async_scoped_session(
    sessionmaker(engine, class_=AsyncSession, expire_on_commit=False),
    scopefunc=current_task,
)
