import subprocess

import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.config import Config
from httpx import AsyncClient
from src.user import routers as user_router, User
from src.auth import routers as auth_router
from src.utils.helpers import hash_password

config = Config(".env")

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{'postgres'}:{'12345'}"
    f"@db_test/{'test_jmart_db'}"
)


def create_app():
    app = FastAPI()
    app.include_router(user_router.router, prefix="/user", tags=["user"])
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    return app


app = create_app()


@pytest_asyncio.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_session_factory(db_engine):
    async_session_factory = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session_factory


@pytest_asyncio.fixture
async def db_session(db_session_factory):
    async with db_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
def run_migrations():
    subprocess.run(["alembic", "upgrade", "head"], check=True)


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    hashed_password = hash_password("testpass")
    test_user = User(username="testuser", email="test@example.com", password=hashed_password)
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user
