import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.test.conftest import app
from src.user import User
from src.utils.helpers import hash_password


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """create a test user"""
    hashed_password = hash_password("testpass")
    test_user = User(username="testuser", email="test@example.com", password=hashed_password)
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    yield test_user
    # Cleanup
    await db_session.delete(test_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """check api of create user"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/user/create/",
            json={"username": "newuser", "password": "newpass", "email": "newuser@example.com"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "Successfully created user" in data['content']
        # Cleanup
        result = await db_session.execute(select(User).filter_by(username="newuser"))
        user = result.scalar_one_or_none()
        if user:
            await db_session.delete(user)
            await db_session.commit()


@pytest.mark.asyncio
async def test_get_users(test_user, db_session: AsyncSession):
    """test list of users from db"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/user/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert any(user['username'] == test_user.username for user in users)


@pytest.mark.asyncio
async def test_get_user(test_user, db_session: AsyncSession):
    """check single user instance"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get(f"/user/{test_user.id}/")
        assert response.status_code == 200
        user = response.json()
        assert user['username'] == test_user.username


@pytest.mark.asyncio
async def test_login(test_user, db_session: AsyncSession):
    """test auth api"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/auth/login",
            data={"username": test_user.username, "password": "testpass"},
        )
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
